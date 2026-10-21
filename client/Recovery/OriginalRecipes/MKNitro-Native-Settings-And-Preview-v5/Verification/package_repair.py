from pathlib import Path
import ast,struct,shutil,sys,hashlib,json,zipfile
ROOT=Path('/workspace/scratch/e221e6641538')
sys.path.insert(0,'/tmp')
from unpack import dec,unpack
U16=lambda b,p:struct.unpack_from('>H',b,p)[0]
for filename,names in [('/tmp/build_patch.py',['pack']),('/tmp/package_font.py',['yaz']),(str(ROOT/'work/v4/build_assets.py'),['expand_variants'])]:
 tree=ast.parse(Path(filename).read_text())
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),filename,'exec'))
ui=ROOT/'patch-work-v5/UIAssets'
original_ui=ROOT/'patch-work-v3/UIAssets'
shutil.copytree(original_ui,ui,dirs_exist_ok=True)
radios=expand_variants('RadioBase',[(f'Row{i}',5) for i in (6,7)])
options=expand_variants('RadioOption',[(f'Row{i}Option{j}',20+j) for i in (6,7) for j in range(4)])
assert radios==[f'Row{i}' for i in range(8)]
assert options==[f'Row{i}Option{j}' for i in range(8) for j in range(4)]
# Row6/Row7 are absent in the supplied UI but requested by the actual settings
# constructor. Added variants retain native local child coordinates and animation.
f=ui/'control/ctrl/RadioBase.brctr';b=bytearray(f.read_bytes());sub=U16(b,14);start=sub+U16(b,sub)
for row in (6,7):
 for off in (16,36):struct.pack_into('>f',b,start+row*60+off,140.-row*40.)
f.write_bytes(b)
changed=[]
for f in sorted(ui.rglob('*')):
 if f.is_file() and f.read_bytes()!=(original_ui/f.relative_to(ui)).read_bytes():changed.append(f.relative_to(ui).as_posix())
assert changed==['control/ctrl/RadioBase.brctr','control/ctrl/RadioOption.brctr']
root=ROOT/'deliverables/MKNitro-Native-Settings-And-Preview-v5'
mod=root/'MarioKartNitro_Test'
(mod/'Binaries').mkdir(parents=True,exist_ok=True);(mod/'Assets').mkdir(exist_ok=True)
shutil.copy2(ROOT/'work/v5/Code.pul',mod/'Binaries/Code.pul')
raw=pack(ui);packed=yaz(raw);assert dec(packed)==raw
(mod/'Assets/UIAssets.szs').write_bytes(packed)
verified=ROOT/'verify/v5/UIAssets';unpack(packed,verified)
for f in ui.rglob('*'):
 if f.is_file():assert f.read_bytes()==(verified/f.relative_to(ui)).read_bytes()
checks={'changed_UI_resources':changed,'radio_variants':radios,'option_variants':options,'archive_roundtrip':'pass','static_rel_sha256':hashlib.sha256((ROOT/'upload/StaticR(1).rel').read_bytes()).hexdigest(),'static_rel_distributed':False,'original_code_sha256':hashlib.sha256((ROOT/'upload/Code(2).pul').read_bytes()).hexdigest()}
verification=root/'Verification';verification.mkdir(exist_ok=True)
(verification/'Assets.json').write_text(json.dumps(checks,indent=2))
for name in ('build_repair.py','verify_native.py','native_rel.py','package_repair.py','manifest.json','verification.json','layout_wrapper.asm','visibility.asm','state_check.asm','state_switch.asm','ResetPosition.asm','SetPreviewVisibility.asm','DriverSwitch.asm','NoteUpdate.asm','VehicleUpdate.asm'):
 shutil.copy2(ROOT/'work/v5'/name,verification/name)
(root/'README.txt').write_text('''MKNitro native settings and character-preview repair v5 (PAL)

INSTALL
Fully stop Dolphin, then merge MarioKartNitro_Test from this ZIP into your
existing MarioKartNitro_Test folder. Replace BOTH files:
  Binaries/Code.pul
  Assets/UIAssets.szs
Start normally, without loading a save state.

This replaces v4 whether or not you already applied the recovery ZIP.
Keep your current XML. Do not install StaticR.rel into your mod; the supplied
clean module was used for analysis and native execution checks only.
Your sea, sky, fonts, badges and earlier online-menu positions are retained.

SETTINGS
The v4 mistake was writing the same values into four different transform
records. They are local, inherited, animation-offset and final transforms.
Writing absolute positions into the animation record applied the offset twice;
children also retained their old inherited positions.

v5 changes only each active row's local position and uniform scale, then calls
the native ControlGroup::ResetControlsPosition routine. That function rebuilds
the label, radio choices, arrows and nested value-control transforms together.
The original animation offsets and opacity remain intact. Each page uses its
actual radio/scroller count. Radio rows 6 and 7 and their option variants are
added because the code requests them but the supplied UI archive lacks them.
No settings values, options, messages or save data are removed or reassigned.

CHARACTERS
The v4 global vehicle-vtable visibility guard is removed.
On Cup Select and Course Select, the existing NoteModelControl preview path now
requests a standing idle driver and a hidden vehicle together. Its native state
comparison also recognizes the idle state, so it does not reload the character
and restart the animation every frame. Vehicle selection keeps its native
riding state and vehicle visibility. Other page owners keep their original path.
This intentionally provides a standing character preview on the course pedestal.

VERIFICATION AND LIMITS
Based on the exact uploaded pre-v4 Code(2).pul, SHA256:
5fe4083a44008ac5536e727b87999c03cea8597fb5d8da4120b45a66b60b2342
Only the PAL code block is modified. NTSC-U/J blocks remain byte-identical.
The original code/relocations are preserved except the SettingsPanel entry
branch and three additional hooks at verified native NoteModelControl sites.
Old BSS addresses are preserved as explicit zero-filled code data. Runtime
allocation grows by roughly 1.3 KiB; the larger file is mostly zero padding.

164 native integration cases passed at two dynamic code addresses. They execute
the real recursive UI transform routines, the native course-preview state path,
native driver state switching and native visibility management. Tests cover all
17 settings definitions with nested controls, four player slots, repeated frames,
course-to-vehicle transitions and return to course selection. Resource loading,
graphics/animation service boundaries and existing settings message setup are
stubbed; actual game/model rendering and full Dolphin boot are NOT tested here.
Archive repacking and decompression checks passed. This is a targeted repair
verified against the supplied native code, not a claim of in-game validation.

FIRST IN-GAME CHECK
Open Sound/Menu settings, then Knockout and both Race settings pages. Confirm
labels, choices, arrows and values align and controller/pointer navigation works.
Select a character and bike, enter course selection and check the standing pose.
Go back to vehicle selection, then return to courses. Complete a race with the
character/bike that previously showed the wheel and return to course selection.

DEVELOPMENT FILES
Verification contains the build/analysis scripts and selected native traces.
They require the referenced source, original uploads, extraction workspace and
Python dependencies; they are not an end-user installer. The original REL is
not bundled and has not been modified.
''')
hashes=[]
for f in sorted(root.rglob('*')):
 if f.is_file():hashes.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(root).as_posix())
(root/'SHA256SUMS.txt').write_text('\n'.join(hashes)+'\n')
out=root.with_suffix('.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,6) as z:
 for f in sorted(root.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(root))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert z.read('MarioKartNitro_Test/Binaries/Code.pul')==(ROOT/'work/v5/Code.pul').read_bytes()
 assert z.read('MarioKartNitro_Test/Assets/UIAssets.szs')==packed
print('Verified package',out,out.stat().st_size)
