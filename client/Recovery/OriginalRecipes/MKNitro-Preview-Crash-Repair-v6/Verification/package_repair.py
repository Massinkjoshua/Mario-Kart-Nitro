from pathlib import Path
import hashlib,json,struct,subprocess,sys,shutil,zipfile
ROOT=Path('/workspace/scratch/e221e6641538');work=ROOT/'work/crash-repair'
out=ROOT/'deliverables/MKNitro-Preview-Crash-Repair-v6';out.mkdir(parents=True,exist_ok=True)
mod=out/'MarioKartNitro_Test'
for d in ('Binaries','Assets'):(mod/d).mkdir(parents=True,exist_ok=True)
shutil.copy2(work/'Code.pul',mod/'Binaries/Code.pul')
ui=ROOT/'deliverables/MKNitro-Native-Settings-And-Preview-v5/MarioKartNitro_Test/Assets/UIAssets.szs'
assert ui.is_file()
shutil.copy2(ui,mod/'Assets/UIAssets.szs')
verification=out/'Verification';verification.mkdir(exist_ok=True)
base=(ROOT/'work/v5/Code.pul').read_bytes();new=(work/'Code.pul').read_bytes();length=struct.unpack_from('>I',base)[0]
assert new[:4]==struct.pack('>I',length+12)
assert new[4:16+length]==base[4:16+length]
assert new[16+length:16+length+12]==struct.pack('>III',0x20fffffe,0x80542310,0x3f400012)
assert new[16+length+12:]==base[16+length:]
# Record the negative control; the fault must match the user's PC exactly.
p=subprocess.run([sys.executable,str(work/'reproduce_loader.py')],capture_output=True,text=True,cwd=ROOT)
assert p.returncode!=0 and 'PC=8006dd0c' in p.stdout and "'size': 800" in p.stdout and "'returned': 0" in p.stdout
(verification/'Original-heap-crash.txt').write_text(p.stdout+p.stderr)
reports=[json.loads(f.read_text()) for f in sorted(work.glob('load-*.json'))]
assert len(reports)==12 and all(not r['null_allocations'] for r in reports)
assert all(r['heap_bytes']==0x121000 for r in reports)
lifecycle=json.loads((work/'lifecycle.json').read_text())
assert len(lifecycle)==4 and all(r['all_native_heap_memory_recovered'] for r in lifecycle)
report={'negative_control':'Original 0xE1000 heap reproduces invalid write at PC 0x8006dd0c after an 800-byte native allocation returns null.',
 'positive_controls':reports,'native_heap_lifecycle':lifecycle,
 'code_delta':'Exactly one appended PAL Kamek WRITE32 command and the outer PAL-block length. All existing v5 code, commands and other regions are unchanged.',
 'ui_identical_to_v5':True,'main_dol_sha256':hashlib.sha256((ROOT/'upload/main(2).dol').read_bytes()).hexdigest(),
 'static_rel_sha256':hashlib.sha256((ROOT/'upload/StaticR(1).rel').read_bytes()).hexdigest(),
 'limits':['Unicorn execution harness, not Dolphin or real hardware.',
 'Archive I/O supplies bytes from the uploaded v9 assets. Scene/renderer structures are fixtures.',
 'Paired-single identity/copy math is implemented by host equivalents; fog registration and scene/unlock predicates are replaced at their boundaries.',
 'Native EGG/MEM allocation, ScnMdl construction, ModelDirector initialization, scene insertion and draw-priority writes execute from the supplied binaries.',
 'Preview test covers primary vehicle models; single-player thumbnail rendering uses a separate heap and is not exercised.',
 'Heap lifecycle tests use an 8 MiB parent fixture; available memory in the complete themed menu has not been measured.',
 'Driver skin changes, animation rendering and race transitions still require a fresh Dolphin run.']}
(verification/'Verification.json').write_text(json.dumps(report,indent=2)+'\n')
for f in ['manifest.json','build_repair.py','native_dol.py','native_probe.py','reproduce_loader.py','verify_lifecycle.py','package_repair.py']:
 shutil.copy2(work/f,verification/f)
(verification/'MenuKartPreviewHeap.cpp').write_text('''// Source equivalent of the v6 crash-repair delta. Add to the existing project
// when rebuilding it. This is not a complete replacement for the v5 UI hooks.
// Addresses below are PAL. The distributed Code.pul changes PAL only.
#include <kamek.hpp>

// ArchiveMgr::InitAllkartArchivesLoaders reserves one heap per local player.
// These heaps hold both the decompressed allkart archive and runtime models.
// fk-7's 897952-byte archive starves the original 0xE1000-byte heap: the native
// 800-byte ScnMdl allocation fails, then SetPriorityDrawOpa writes through null.
// 0x121000 adds 256 KiB per local player while retaining native heap ownership
// and cleanup. The following addi r3,r26,0x1000 instruction remains unchanged.
kmWrite32(0x80542310, 0x3F400012); // lis r26,0x12 (was lis r26,0x0e)
''')
(out/'README.txt').write_text('''Mario Kart Nitro - Preview Crash Repair v6 (PAL)

INSTALL
1. Fully stop Dolphin.
2. Back up your current MarioKartNitro_Test/Binaries/Code.pul and
   MarioKartNitro_Test/Assets/UIAssets.szs.
3. Merge this package's MarioKartNitro_Test folder into your existing folder
   under Dolphin Emulator/Load/riivolution. Replace the two matching files.
   Do not create a second MarioKartNitro_Test folder inside the existing one.
4. Start the game normally, without restoring a save state.

The correct installed files are:
  MarioKartNitro_Test/Binaries/Code.pul
  MarioKartNitro_Test/Assets/UIAssets.szs

This package includes the v5 settings and course-preview changes. UIAssets.szs
is byte-identical to v5. The current font, ranks, online icons, sea, sky, title,
character assets, XML, Loader.pul and Config.pul are retained.
You do not install main.dol or StaticR.rel; they were used for diagnosis only.

REPAIR
The log shows Funky's seventh skin loading fk-7-allkart.szs before the crash.
Its decompressed archive uses 897952 bytes of the original 921600-byte heap.
That same heap must also hold runtime vehicle models and animation objects.
Native-code execution reproduced the screenshot's exact fault: an 800-byte
ScnMdl allocation returns null and SetPriorityDrawOpa writes to address 0xD0
at PC 0x8006DD0C.

The PAL patch raises this preview heap to 1183744 bytes. This adds 256 KiB per
local player, at most 1 MiB for four local players. It preserves native cleanup.
Relative to v5, the binary adds exactly one instruction-write patch; existing
settings/preview hooks and all other region blocks are unchanged.

VALIDATION AND FIRST GAME CHECK
The same native loading test completes with all twelve primary vehicle models.
The supplied fk-7, fk-8 and kt-5 archives pass normal/battle allocation tests
with one/four screen settings. Repeated native heap initialization and reset
recover all memory in the test fixture. Detailed coverage and limits are in
Verification/Verification.json.

A full Dolphin boot was not available here. First, cycle through Funky's skins
past slot 7, enter vehicle selection, press Back, and repeat once. Then check
King Boo's new skin and the return from a race to course selection. If another
crash occurs, keep its screenshot and the new Dolphin log.

The earlier recovery ZIP removes recent UI/code changes but retains the same
old small preview heap, so it is not a fix for this particular allocation crash.

Verification scripts are development records using the build workspace and
uploaded binaries; they are not installation tools. No original game executable
or StaticR.rel is redistributed in this package.
''')
checks=[]
for p in sorted(mod.rglob('*')):
 if p.is_file():checks.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(out)))
(out/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
archive=out.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(out))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert z.read('MarioKartNitro_Test/Binaries/Code.pul')==new
 assert z.read('MarioKartNitro_Test/Assets/UIAssets.szs')==ui.read_bytes()
 assert not any(n.endswith(('.dol','.rel')) for n in z.namelist())
print('Packaged',archive,archive.stat().st_size,'bytes; Code + UI verified; no game binaries included.')
