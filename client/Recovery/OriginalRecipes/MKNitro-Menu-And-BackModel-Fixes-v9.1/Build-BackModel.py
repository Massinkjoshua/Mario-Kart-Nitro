from pathlib import Path
import struct,sys,shutil,json,hashlib,zipfile,ast
R=Path('/workspace/scratch/e221e6641538');O=R/'deliverables/MKNitro-Menu-And-BackModel-Fixes-v9.1'
shutil.copytree(R/'deliverables/MKNitro-License-And-Item-Fixes-v9',O,dirs_exist_ok=True)
sys.path.insert(0,str(R/'work/v5'));import native_rel as nr
sys.path.insert(0,str(R/'work/crash-repair'));from native_probe import Runtime
from unicorn.ppc_const import *
patches=[0x805fb7d4,0x8084db24,0x8084fad4]
f=O/'MarioKartNitro_Test/Binaries/Code.pul';b=f.read_bytes();size=struct.unpack_from('>I',b)[0]
extra=b''
for a in patches:
 assert nr.read(a,4)==bytes.fromhex('38800002')
 extra+=struct.pack('>III',0x20fffffe,a,0x38800000)
out=struct.pack('>I',size+len(extra))+b[4:16+size]+extra+b[16+size:]
assert out[4:16+size]==b[4:16+size] and out[16+size+len(extra):]==b[16+size:]
f.write_bytes(out)
rt=Runtime();control=0x817a01c8
for a in patches:
 rt.uc.mem_write(a,bytes.fromhex('38800000'))
 for prev in [-1,0,2]:
  rt.uc.mem_write(control+0x174,struct.pack('>i',prev))
  rt.uc.reg_write(UC_PPC_REG_3,control)
  rt.uc.emu_start(a,a+8,count=100)
  assert rt.rd(control+0x178)==0
  assert rt.uc.mem_read(control+0x17e,1)==bytes([int(prev!=0)])
# RequestModel's hide sentinel stays native and functional.
rt.call(0x805f2e84,control,0xffffffff);assert rt.rd(control+0x178)==0xffffffff
(O/'BackModel-verification.json').write_text(json.dumps({'patch_sites':[hex(a) for a in patches],'native_request_tests':9,'hide_sentinel_preserved':True,'previous_v9_bytes_preserved':True,'full_game_render_tested':False},indent=2))
shutil.copy2(__file__,O/'Build-BackModel.py')
readme=O/'README.txt'
prior=readme.read_text() if readme.exists() else ''
readme.write_text('MKNitro menu and BackModel fixes v9.1 (PAL)\n\nBack up the three destination files, then merge MarioKartNitro_Test into your active mod folder and replace the matching files:\nBinaries/Code.pul\nMenuRace/MenuOther.szs\nMenuRace/Title.szs\n\nFully stop Dolphin and boot normally, without restoring a save state. No XML or BackModel.szs replacement is needed.\n\nBackModel change: VS initialization and VS menu requests now select the same stopwatch/logo slot as the working custom Single Player menu, instead of the native flag slot. Includes multiplayer VS requests for consistency. Other modes and the hide request are unchanged. Native execution checks confirm slot selection and transition flags; Dolphin rendering has not been tested here. Test a VS race, return to course selection, then back out and repeat.\n\nIncludes the preceding license-menu fixes (title-sized Mii, Records disabled/hidden, button panels, readable heading/help backing, smaller title settings emblem) and removal of additive item-roulette whitening.\n\n'+prior)
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(O)) for p in sorted((O/'MarioKartNitro_Test').rglob('*')) if p.is_file())+'\n')
z=O.with_suffix('.1.zip') if False else Path(str(O)+'.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for p in sorted(O.rglob('*')):
  if p.is_file():a.write(p,p.relative_to(O))
print(z)
print((O/'BackModel-verification.json').read_text())
