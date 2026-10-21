"""Check this source integration and preserved baseline; does not certify a Wii build."""
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def host_check(source, name):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / 'test.cpp').write_text(source)
        subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror',
                        str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
        subprocess.run([str(path / 'test')], check=True)
    print('PASS:', name)

def main():
    module_path = ROOT / 'NitroIntegrity/tools/build_manifest.py'
    spec = importlib.util.spec_from_file_location('manifest', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    baseline = (ROOT / 'Reference/Code-10-UNCHANGED.pul').read_bytes()
    review = json.loads((ROOT / 'PulsarEngine/Security/NitroIntegrity/manifest_review.json').read_text())
    assert hashlib.sha256(baseline).hexdigest() == review['inputs']['code_sha256']
    writes, commands = module.pul_writes(baseline)
    assert commands == 11067
    assert len(review['checks']) == 23
    for check in review['checks']:
        address = int(check['address'], 16)
        assert not any(address < end and address + 4 > start for start, end, *_ in writes)
    print('PASS: exact Code(10) baseline, 11,067 PAL commands, 23 checks without patch overlap')

    auth = (ROOT / 'PulsarEngine/Network/WiiLink.cpp').read_text()
    assert auth.count('Pulsar::NitroIntegrity::CanEnterOnline()') == 1
    hook = auth.index('    0x800ed6e8, 0, void,')
    assert hook < auth.index('Pulsar::NitroIntegrity::CanEnterOnline()') < auth.index('    if (s_payloadReady)', hook)
    config = (ROOT / '.env').read_text()
    assert '-DMKNITRO_SERVER' in config and 'MKNITRO_AC_MODE ?= 0' in config and '-DMKNITRO_AC_ENFORCE_INTEGRITY=$(MKNITRO_AC_MODE)' in config
    assert 'ManifestRuntimeReviewed = false' in (ROOT / 'PulsarEngine/Security/NitroIntegrity/Manifest.hpp').read_text()
    assert 'CheckValidRaw__3RFLFPCQ23RFL9StoreData = 0x800cb8b0' in (ROOT / 'GameSource/symbols.txt').read_text()
    print('PASS: one auth guard before cached-payload login; audit defaults; RFL external declared')

    rating = (ROOT / 'PulsarEngine/Network/Rating/RatingSave.cpp').read_text()
    predicate = function(rating, 'static bool IsUsableProfileId(s32 id)')
    predicate = predicate.replace('*reinterpret_cast<const volatile u32 *>(0x80000000)', 'testDiscId')
    # The only host substitution is the game's disc ID read. The actual function
    # is compiled; expected boundaries are checked against Code(10)'s predicate.
    pal_predicate = baseline[48 + 0x586b0:48 + 0x586b0 + 32]
    assert pal_predicate.hex() == '3c8077363863ffff380493fe7c030040386000004d810020386000014e800020'
    host_check('''#include <cassert>
#include <cstdint>
typedef int32_t s32; typedef uint32_t u32;
#define MKNITRO_SERVER 1
static const s32 RESERVED_PROFILE_ID_BASE = 1000000000;
static u32 testDiscId;
''' + predicate + '''
int main() {
    const s32 ids[] = {-1,0,1,603318948,999999999,1000000000,1000000002,
                       1999999999,2000000000,2147483647};
    for (int region=0;region<3;++region) {
        testDiscId = region==0 ? 0x524d4350u : region==1 ? 0x524d4345u : 0x524d434au;
        for (unsigned int i=0;i<sizeof(ids)/sizeof(ids[0]);++i)
            assert(IsUsableProfileId(ids[i]) == (ids[i]>0 && ids[i]<(region==0?2000000000:1000000000)));
    }
}
''', 'rating source predicate matches the PAL binary limit and preserves USA/Japan limits')

    leaderboard = (ROOT / 'PulsarEngine/UI/VRLeaderboard/VRLeaderboard.cpp').read_text()
    start = leaderboard.index('        const bool validMii =')
    end = leaderboard.index('SetPaneVisibleIfPresent(*rows[i], "chara_icon_sha", validMii);', start)
    block = leaderboard[start:end] + 'SetPaneVisibleIfPresent(*rows[i], "chara_icon_sha", validMii);'
    host_check('''#include <cassert>
struct Store { bool valid; }; struct Entry { Store miiData; };
struct Group { int loads; void LoadMii(int,const Store*) { ++loads; } };
struct Row { int bindings; bool visible; void SetMiiPane(const char*,Group&,int,int) { ++bindings; } };
namespace RFL { bool CheckValidRaw(const Store* s) { return s->valid; } }
void SetPaneVisibleIfPresent(Row& row,const char*,bool visible) { row.visible=visible; }
void populate(Entry* s_entries,Group* miiGroup,Row** rows) { int i=0,idx=0;
''' + block + '''
}
int main() {
    Entry entries[1]={{{false}}}; Group group={0}; Row row={0,true}; Row* rows[]={&row};
    populate(entries,&group,rows); assert(group.loads==0 && row.bindings==0 && !row.visible);
    entries[0].miiData.valid=true;
    populate(entries,&group,rows); assert(group.loads==1 && row.bindings==2 && row.visible);
    entries[0].miiData.valid=false;
    populate(entries,&group,rows); assert(group.loads==1 && row.bindings==2 && !row.visible);
}
''', 'actual Mii row source suppresses invalid entries and restores reused valid rows (native API mocked)')

    settings = (ROOT / 'PulsarEngine/Settings/Settings.cpp').read_text()
    start = settings.index('    bool ret = io->OpenFile(this->filePath, FILE_MODE_READ_WRITE);')
    end = settings.index('    if (!ret) {\n        io->CreateAndOpen', start)
    opening = settings[start:end]
    host_check('''#include <cassert>
#include <cstdio>
#include <string>
#include <vector>
#define MKNITRO_SERVER 1
namespace IOS { const int ipcMaxPath=64; }
enum { FILE_MODE_READ_WRITE=3 };
struct System { std::string folder; const char* GetModFolder() { return folder.c_str(); } };
struct IO {
    int successOn; std::vector<std::string> opened;
    bool OpenFile(const char* path,int) { opened.push_back(path); return int(opened.size())==successOn; }
};
struct Mgr {
    const char* filePath;
    bool open(IO* io,System* system) {
''' + opening + '''
        return ret;
    }
};
int main() {
    System sys={"/Nitro"}; Mgr mgr={"/Nitro/MKNitroGameSettings.pul"};
    IO preferred={1,{}}; assert(mgr.open(&preferred,&sys)); assert(preferred.opened.size()==1);
    IO legacy={2,{}}; assert(mgr.open(&legacy,&sys)); assert(legacy.opened[1]=="/Nitro/RRGameSettings.pul");
    IO missing={0,{}}; assert(!mgr.open(&missing,&sys)); assert(missing.opened.size()==2);
    sys.folder=std::string(100,'a'); IO longPath={0,{}};
    assert(!mgr.open(&longPath,&sys)); assert(longPath.opened.size()==1);
    assert(std::string(mgr.filePath)=="/Nitro/MKNitroGameSettings.pul");
}
''', 'settings open order, legacy fallback, missing files, long path and retained new save destination')
    print('No PowerPC compilation, real RFL rendering, filesystem I/O or live game test is claimed.')

if __name__ == '__main__':
    main()
