from pathlib import Path
import struct,ast,sys,shutil,json,hashlib,zipfile,xml.etree.ElementTree as ET
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
from archive_io import *
R=Path('/workspace/scratch/e221e6641538');W=R/'work/settings-oct4';O=R/'deliverables/MKNitro-Main-Settings-v10';O.mkdir(exist_ok=True)
# Re-extract current uploaded assets; never use an older mod baseline.
unpack((R/'upload/Channel.szs').read_bytes(),W/'Channel')
unpack(zipfile.ZipFile(R/'upload/UIAssets.zip').read('UIAssets.szs'),W/'UIAssets')
channel=W/'Channel';ui=W/'UIAssets'
# Option background is separate from License Settings and loaded from Channel.
for n in ['bg/blyt/option_bg.brlyt','bg/anim/option_bg_Loop.brlan','bg/timg/tt_nitro_backrooms_bg.tpl']:
 shutil.copy2(W/'MenuOther'/n,channel/n)
# Remove decorative image strips only inside Channel; text layouts stay intact.
for n in ['option_obi_top','obi_top','obi_bottom']:
 f=channel/'bg/blyt'/(n+'.brlyt');b=f.read_bytes();ss=list(sections(b))
 for s in ss:
  if s[:4]==b'pic1':struct.pack_into('>2f',s,68,0.,0.)
 f.write_bytes(b[:16]+b''.join(ss))
# Reflow both aspect-ratio variants of the shared Pulsar main Options buttons.
f=ui/'button/ctrl/SettingsButton.brctr';b=bytearray(f.read_bytes());sub=struct.unpack_from('>H',b,14)[0];st=struct.unpack_from('>H',b,16)[0];start=sub+struct.unpack_from('>H',b,sub)[0];cnt=struct.unpack_from('>H',b,sub+2)[0];positions={}
for i in range(cnt):
 p=start+60*i;name=bytes(b[st+struct.unpack_from('>H',b,p)[0]:]).split(b'\0')[0].decode()
 for q in [12,32]:
  if name=='ChannelInstall':struct.pack_into('>5f',b,p+q,-5000,0,0,0,0)
  elif name in ['Rumble','Network','Settings']:
   y={'Rumble':70,'Network':0,'Settings':-70}[name];struct.pack_into('>f',b,p+q+4,y)
 positions[name]=struct.unpack_from('>10f',b,p+12)
f.write_bytes(b)
# Code changes are scoped to PAL Options page. Native load hook keeps r9 argument.
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
def asm(s):return bytes(ks.asm(s)[0])
def load(reg,value):return f'lis {reg},{value>>16}; ori {reg},{reg},{value&65535}'
def p32(v):return struct.pack('>I',v)
def cmd(t,a,v):return struct.pack('>III',(t<<24)|0xfffffe,a,v)
u32=U
t=ast.parse((R/'work/v4/build_code.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='commands'],type_ignores=[]),'parser','exec'))
base=(R/'upload/Code(3).pul').read_bytes();length=U(base,0);oldblock=base[16:16+length];h=bytearray(oldblock[:32]);size=U(h,12);bss=U(h,8);code=bytearray(oldblock[32:32+size]);oldcmd=oldblock[32+size:];parsed=commands(oldcmd)
for site in [0x805fd854,0x805fd8e8]:assert not any(a==site for t,a,v in parsed),hex(site)
sys.path.insert(0,str(R/'work/v5'));import native_rel
assert native_rel.read(0x805fd854,4)==asm('li 9,0')
assert native_rel.read(0x805fd8e8,4)==asm('lwz 0,16(3)')
# Preserve any original BSS addresses if a future baseline includes BSS.
code+=bytes(bss);code+=bytes(-len(code)%4);off=len(code)
body=f'''
stwu 1,-32(1)
mflr 0
stw 0,36(1)
stw 31,28(1)
mr 31,3
li 0,1
stb 0,2348(31)
li 4,-1
stw 4,3428(31)
lwz 0,16(31)
cmpwi 0,0
bne finish
addi 3,31,1028
li 4,0
{load(12,0x805bdaf0)}
mtctr 12
bctrl
finish:
lwz 31,28(1)
lwz 0,36(1)
mtlr 0
addi 1,1,32
blr
'''
payload=asm(body);code+=payload;struct.pack_into('>II',h,8,0,len(code));newcommands=oldcmd+cmd(32,0x805fd854,0x39200001)+cmd(64,0x805fd8e8,off);commands(newcommands)
newblock=bytes(h)+code+newcommands;out=p32(len(newblock))+base[4:16]+newblock+base[16+length:]
assert code[:size]==oldblock[32:32+size];assert out[16+len(newblock):]==base[16+length:]
f=O/'MarioKartNitro_Test/Binaries/Code.pul';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(out)
(W/'options_hook.bin').write_bytes(payload);(O/'Options-hook.asm').write_text(body)
# Add explicit route for Channel archive; leave all existing routes intact.
xml=(R/'upload/MarioKartNitro(3).xml').read_text();tree=ET.fromstring(xml);assert not any(e.get('disc')=='/Scene/UI/Channel.szs' for e in tree.iter('file'))
needle='    <file external="/MarioKartNitro_Test/MenuRace/MenuOther.szs" disc="/Scene/UI/MenuOther.szs" create="true" />';assert xml.count(needle)==1
xml=xml.replace(needle,needle+'\n    <file external="/MarioKartNitro_Test/MenuRace/Channel.szs" disc="/Scene/UI/Channel.szs" create="true" />');ET.fromstring(xml)
(O/'MarioKartNitro.xml').write_text(xml)
# Pack and check each modified archive against its exact source content.
report={'PAL_code_only':True,'original_code_preserved':True,'old_commands_preserved':True,'other_regions_preserved':True,'positions':positions,'hook_offset':off,'hook_bytes':len(payload),'native_patch_sites':['0x805fd854','0x805fd8e8'],'full_game_rendering_tested':False}
for name,folder,old in [('Channel',channel,files((R/'upload/Channel.szs').read_bytes())),('UIAssets',ui,files(zipfile.ZipFile(R/'upload/UIAssets.zip').read('UIAssets.szs')))]:
 packed=yaz(pack(folder));got=files(packed);expected={str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*') if p.is_file()};assert got==expected
 report[name]={'changed_files':[n for n in got if n not in old or got[n]!=old[n]],'all_other_files_preserved':all(n in got and got[n]==b for n,b in old.items() if n not in [x for x in got if x not in old or got[x]!=old[x]]),'archive_roundtrip':True}
 dest=O/'MarioKartNitro_Test'/('MenuRace' if name=='Channel' else 'Assets');dest.mkdir(parents=True,exist_ok=True)
 if name=='Channel':(dest/'Channel.szs').write_bytes(packed)
 else:
  names=zipfile.ZipFile(R/'upload/UIAssets.zip').namelist()
  for n in names:(dest/n).write_bytes(packed)
(O/'Verification.json').write_text(json.dumps(report,indent=2));shutil.copy2(__file__,O/'Build.py');shutil.copy2(W/'archive_io.py',O/'archive_io.py')
print(json.dumps(report,indent=2))
