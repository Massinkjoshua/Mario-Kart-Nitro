"""Host integration checks; this does not compile the complete Wii/C# projects."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil, struct, subprocess, tempfile
import xml.etree.ElementTree as ET
from nitro_formats import config, kamek
from apply_release_policy import apply, POLICY

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--skip-host-tests',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parent.parent;pack=root/'CurrentPack'
    report=dict(scope='host integrity, config, portable parser, regional release policy and build-script checks',
                powerpc_compile_executed_by_this_suite=False,separate_powerpc_build_report="docs/powerpc-build-status.json",csharp_compile=False,gameplay_tested=False,checks=[])
    def passed(text): print('PASS: '+text,flush=True);report['checks'].append(text)
    manifest=json.loads((root/'docs/current_runtime_manifest.json').read_text())
    for row in manifest:
        data=(pack/row['path']).read_bytes()
        assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
    assert not any('/save/'in x['path']for x in manifest)
    passed(f"{len(manifest)} current runtime file hashes; no save payloads")
    bins=pack/'MarioKartNitro_Test/Binaries'
    configs={name:config((bins/name).read_bytes())for name in ['config.pul','ConfigRT.pul','ConfigCT.pul','ConfigBT.pul']}
    for name,c in configs.items():
        assert c['version']==3,name
        working=config((root/'Project'/name).read_bytes())
        assert working['alphabetical_permutation_valid'],name
        assert working['tracks']==c['tracks'] and working['bmg']==c['bmg'],name
        if c['visible_tracks']:
            assert sorted(c['alphabetical_order'][:108])==list(range(108))
            assert c['alphabetical_order'][108:]==[0,1,2,3]
            assert working['alphabetical_order'][108:]==[108,109,110,111]
        else:assert (root/'Project'/name).read_bytes()==(bins/name).read_bytes()
    for name in ['config.pul','ConfigRT.pul']:
        assert configs[name]['cups']==27 and configs[name]['visible_tracks']==108 and configs[name]['stored_tracks']==112
    assert configs['ConfigCT.pul']['cups']==configs['ConfigBT.pul']['cups']==0
    differences=[a['index']for a,b in zip(configs['config.pul']['tracks'],configs['ConfigRT.pul']['tracks'])
                 if (a['course_slot'],a['music_slot'],a['crc32'])!=(b['course_slot'],b['music_slot'],b['crc32'])]
    assert differences==[32,59,90]
    passed('27 cups, 108 visible tracks, odd-cup padding; all four configs and three record differences preserved')
    resources=root/'PulsarPackCreator/Resources'
    for name in ['Code.pul','Loader.pul']:assert(resources/name).read_bytes()==(bins/name).read_bytes()
    for name in ['CommonAssets.szs','RaceAssets.szs','UIAssets.szs']:
        assert(resources/name).read_bytes()==(pack/'MarioKartNitro_Test/Assets'/name).read_bytes()
    passed('Creator embeds the current supplied engine/loader and three core archives')
    xml=ET.parse(pack/'riivolution/MarioKartNitro.xml').getroot()
    template=ET.fromstring((resources/'Base.xml').read_text().replace('{$pack}','MarioKartNitro_Test'))
    assert ET.tostring(xml)==ET.tostring(template)
    ids={x.get('id')for x in xml.findall('patch')}
    assert all(x.get('id')in ids for x in xml.findall('.//choice/patch'))
    ET.parse(root/'PulsarPackCreator/Pulsar Pack Creator.csproj')
    passed('Creator XML template exactly reproduces current patch definitions')
    runtime=(bins/'Code.pul').read_bytes()
    parsed=kamek(runtime)
    assert [x['region']for x in parsed['regions']]==list('PEJ')and not parsed['trailing_bytes']
    patched,changes=apply(runtime);assert patched==runtime and len(changes)==len(POLICY)
    # A pre-policy link fixture exercises transformation as well as idempotence.
    old_values={0x800910B4:0x10,0x80588894:0x2c000003,0x8058889C:0x2c000003,
                0x805888A8:0x418200a4,0x80588928:0x60000000,0x80588938:0x7c040378,0x8058893C:0x48000010}
    commands=b''.join(struct.pack('>3I',((65 if a==0x800910B4 else 32)<<24)|0xfffffe,a,v)for a,v in {**{a:0 for a in POLICY},**old_values}.items())
    section=b'Kamek\0\0\2'+struct.pack('>6I',0,64,0,0,0,0)+bytes(64)+commands
    fixture=struct.pack('>4I',len(section),len(section),len(section),0)+section*3
    result,changes=apply(fixture);after=kamek(result)
    assert result[16+len(section):]==fixture[16+len(section):]and len(changes)==len(POLICY)
    for c in after['regions'][0]['commands']:
        assert(c['command_id'],c['values'][0])==POLICY[c['address']]
    for invalid in (fixture[:-1],b'',fixture[:20]):
        try:apply(invalid)
        except (ValueError,struct.error):pass
        else:raise AssertionError('Malformed policy input accepted')
    passed('12-site PAL policy transforms a fresh-link fixture, is idempotent on current release, and preserves fixture E/J bytes')
    if not args.skip_host_tests:
        compiler=shutil.which('g++')or shutil.which('clang++')
        if not compiler:raise SystemExit('Native compiler required; use --skip-host-tests for an explicitly limited check.')
        with tempfile.TemporaryDirectory(prefix='nitro-host-check-')as tmp:
            env=os.environ.copy();env['ASAN_OPTIONS']='detect_leaks=0'
            for name,include,source,argv in [
                ('cups',root/'PulsarEngine',root/'tests/cup_order.cpp',[]),
                ('loader',root/'Loader',root/'tests/kamek_validation.cpp',[str(bins/'Code.pul')])]:
                exe=Path(tmp)/name
                subprocess.run([compiler,'-std=c++11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer','-I',str(include),str(source),'-o',str(exe)],check=True)
                alpha=config((root/'Project/ConfigRT.pul').read_bytes())['alphabetical_order']
                text=str(len(alpha))+'\n'+' '.join(map(str,alpha))+'\n'if name=='cups'else''
                subprocess.run([str(exe)]+argv,input=text,text=True,check=True,env=env)
        passed('shared C++ loader parser and cup-order tests with ASan/UBSan; leak checks excluded')
    else:report['host_cpp_tests_skipped']=True
    bash=shutil.which('bash');make=shutil.which('make')
    if bash:subprocess.run([bash,'-n','build_msys2.sh'],cwd=root,check=True)
    if make:
        run=subprocess.run([make,'-n','all','loader','CC=./tools/codewarrior/mwcceppc.exe',
            'AS=./tools/codewarrior/mwasmeppc.exe','KAMEK=./tools/kamek/Kamek.exe'],cwd=root,text=True,capture_output=True,check=True)
        assert '-DMKNITRO_SERVER'in run.stdout and '-DMKNITRO_SINGLE_CONFIG 'not in run.stdout
        assert 'apply_release_policy.py build/Code.pul'in run.stdout
        assert 'NitroLakituDiagnostic.cpp'not in run.stdout
        assert 'build/Loader/mkw.o build/Loader/kamekLoader.o -static=0x80004000'in run.stdout
        (root/'docs/make-dry-run.log').write_text(run.stdout)
    passed('build script syntax and multi-config engine/loader Makefile dry run')
    (root/'docs/validation-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print('This host suite does not invoke the PowerPC compiler; see docs/powerpc-build-status.json for the separate clean build. This suite does not run the WPF build or gameplay; see the separate editor-build status.')

if __name__=='__main__':main()
