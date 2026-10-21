from pathlib import Path
import ast,sys,struct,shutil,json,zipfile
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
R=Path('/workspace/scratch/e221e6641538');W=R/'work/itembox-colour';O=R/'deliverables/MKNitro-Itembox-UI-Colour-Fix';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'work/settings-oct4'));from archive_io import *
t=ast.parse((R/'work/v4/build_code.py').read_text());u32=U
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='commands'],type_ignores=[]),'parser','exec'))
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
def asm(s):return bytes(ks.asm(s)[0])
def call(a):return f'lis 12,{a>>16};ori 12,12,{a&65535};mtctr 12;bctrl'
def cmd(t,a,v):
 # Small destinations are allocation-relative. The extended-address marker
 # means absolute memory and must only be used for native addresses.
 return struct.pack('>I',(t<<24)|(a if a<0x1000000 else 0xfffffe))+(struct.pack('>I',a) if a>=0x1000000 else b'')+struct.pack('>I',v)
base=(R/'deliverables/MKNitro-Main-Settings-v10/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();length=U(base,0);block=base[16:16+length];h=bytearray(block[:32]);size=U(h,12);code=bytearray(block[32:32+size]);oldcmd=block[32+size:];parsed=commands(oldcmd)
assert not any(a==0x807eede0 for t,a,v in parsed)
code+=bytes(U(h,8));code+=bytes(-len(code)%4);off=len(code)
# Relocatable name references use normal Kamek internal-pointer relocations.
body=f'''stwu 1,-32(1);mflr 0;stw 0,36(1);stw 31,28(1);mr 31,3
{call(0x807ebf20)}
addi 3,31,168
lis 4,0x1357;addi 4,4,0x2468
{call(0x805e8368)}
cmpwi 3,0;beq finish
mr 3,31
lis 4,0x1357;addi 4,4,0x2468
li 5,1
{call(0x807ebf20)}
finish:lwz 31,28(1);lwz 0,36(1);mtlr 0;addi 1,1,32;blr'''
payload=bytearray(asm(body));nameoff=off+len(payload);needle=asm('lis 4,0x1357;addi 4,4,0x2468');relocs=b'';p=0
while True:
 p=payload.find(needle,p)
 if p<0:break
 payload[p+2:p+4]=b'\0\0';payload[p+6:p+8]=b'\0\0'
 relocs+=cmd(6,off+p+2,nameoff)+cmd(4,off+p+6,nameoff);p+=8
assert len(relocs)==32
code+=payload+b'nitro_item_frame\0';code+=bytes(-len(code)%4);struct.pack_into('>II',h,8,0,len(code));newcmd=oldcmd+relocs+cmd(65,0x807eede0,off);commands(newcmd)
newblock=bytes(h)+code+newcmd;out=struct.pack('>I',len(newblock))+base[4:16]+newblock+base[16+length:]
assert code[:size]==block[32:32+size] and out[16+len(newblock):]==base[16+length:]
dest=O/'MarioKartNitro_Test/Binaries/Code.pul';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(out)
for rel in ['MenuRace/Race.szs','Scene/UI/Race.szs']:
 src=R/'deliverables/MKNitro-Menu-Scene-Languages-And-Itembox/MarioKartNitro_Test'/rel
 d=files(src.read_bytes());ss=list(sections(d['game_image/blyt/item_window.brlyt']));frame=[s for s in ss if s[:4]==b'pic1' and label(s)=='nitro_item_frame'];assert len(frame)==1 and frame[0][10]==255
 dst=O/'MarioKartNitro_Test'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
(W/'hook.bin').write_bytes(payload);(W/'metadata.json').write_text(json.dumps({'offset':off,'name_offset':nameoff,'relocations':commands(relocs)}));(O/'Hook.asm').write_text(body)
(O/'README.txt').write_text('MARIO KART NITRO - ITEM BOX UI COLOUR FIX\n\nClose Dolphin, back up the matching files, then merge MarioKartNitro_Test into your mod folder and replace the included Code.pul and both Race.szs copies. Keep the XML from the Menu/Scene language update. Start without a save state.\n\nThe new static item frame now receives the same native HUD colour update as the original frame panes, including the existing selected colour and multiplayer palette handling. The existing roulette highlights remain suppressed. This builds on the supplied Code(3).pul plus the title Settings v10 fix; those original commands and all US/Japanese blocks are preserved. The added item-frame hook targets PAL only. If you have installed a newer Code.pul since v10, do not overwrite it; provide it for merging.\n\nThe frame is checked for existence before applying colour. Native call/argument checks and file checks are recorded in Verification.json. No Dolphin rendering test was available. Test orange and cyan, item roulette/use, and split screen.\n')
shutil.copy2(__file__,O/'Build.py');shutil.copy2(R/'work/settings-oct4/archive_io.py',O/'archive_io.py')
print(json.dumps({'hook_offset':off,'hook_bytes':len(payload),'original_code_preserved':True,'other_regions_preserved':True}))
