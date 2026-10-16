from pathlib import Path
import sys,struct,json,hashlib,zipfile,shutil
R=Path('/workspace/scratch/e221e6641538');sys.path.insert(0,str(R/'work/settings-oct4'))
from archive_io import *
W=R/'work/settings-footer-oct4';O=R/'deliverables/MKNitro-Settings-Footer-Fix-v10.1';O.mkdir(exist_ok=True)
baseline=R/'deliverables/MKNitro-Main-Settings-v10/MarioKartNitro_Test/MenuRace/Channel.szs'
old=files(baseline.read_bytes());unpack(baseline.read_bytes(),W/'Channel')
f=W/'Channel/bg/blyt/obi_bottom_message.brlyt';b=f.read_bytes();ss=list(sections(b));changed=[]
for s in ss:
 if s[:4]==b'pic1' and label(s) in ['obi_base_l','obi_base_r','obi_base_c','check']:
  struct.pack_into('>2f',s,68,0.,0.);changed.append(label(s))
assert len(changed)==4
f.write_bytes(b[:16]+b''.join(ss))
packed=yaz(pack(W/'Channel'));new=files(packed)
diff=[n for n in new if new[n]!=old.get(n)];assert diff==['bg/blyt/obi_bottom_message.brlyt'];assert new.keys()==old.keys()
a=list(sections(old[diff[0]]));z=list(sections(new[diff[0]]))
for s,t in zip(a,z):
 if s!=t:
  assert label(s) in changed and s[:68]==t[:68] and s[76:]==t[76:]
assert any(s[:4]==b'txt1' and label(s)=='text' for s in z)
dest=O/'MarioKartNitro_Test/MenuRace/Channel.szs';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(packed)
(O/'README.txt').write_text('MARIO KART NITRO - SETTINGS FOOTER FIX v10.1\n\nInstall after v10. Replace MarioKartNitro_Test/MenuRace/Channel.szs with the included file. Your v10 XML already routes it; no XML or Code.pul replacement is needed. Stop Dolphin completely and boot without a save state.\n\nRemoves the original white bottom strip and checkerboard from the message footer used by the settings category screen. Back and help text are preserved, along with the existing help-text backing. All v10 Channel edits remain included. The shared footer also changes on other screens using this Channel layout.\n\nValidation: the archive round-trip matches the expected contents. Exactly one BRLYT changed, with only the width/height fields of four decorative pictures edited. Every other archive member and text pane is unchanged. Full Dolphin rendering has not been tested.\n\nRollback: restore your v10 Channel.szs.\n')
(O/'Verification.json').write_text(json.dumps({'baseline':'v10 Channel.szs','changed_files':diff,'removed_pictures':changed,'text_preserved':True,'all_other_members_preserved':True,'archive_roundtrip':True,'full_game_rendering_tested':False},indent=2))
shutil.copy2(__file__,O/'Build.py');shutil.copy2(R/'work/settings-oct4/archive_io.py',O/'archive_io.py')
(O/'SHA256SUMS.txt').write_text(hashlib.sha256(packed).hexdigest()+'  MarioKartNitro_Test/MenuRace/Channel.szs\n')
zipout=O.with_suffix('.zip')
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zz:
 for p in sorted(O.rglob('*')):
  if p.is_file():zz.write(p,p.relative_to(O))
print(json.dumps({'output':str(zipout),'size':zipout.stat().st_size,'changed':diff}))
