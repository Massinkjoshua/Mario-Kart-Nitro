from pathlib import Path
import ast,struct,json,hashlib,shutil
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
R=Path('/workspace/scratch/e221e6641538');W=R/'work/license-v9_2';O=R/'deliverables/MKNitro-License-Visibility-Fix-v9.2';O.mkdir(exist_ok=True)
u32=lambda b,p=0:struct.unpack_from('>I',b,p)[0]
p32=lambda v:struct.pack('>I',v)
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
asm=lambda s:bytes(ks.asm(s)[0])
def load(reg,value):return f'lis {reg},{value>>16}; ori {reg},{reg},{value&65535}'
def cmd(t,a,v):return p32((t<<24)|0xfffffe)+p32(a)+p32(v)
t=ast.parse((R/'work/v4/build_code.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='commands'],type_ignores=[]),'parser','exec'))
b=(R/'deliverables/MKNitro-Menu-And-BackModel-Fixes-v9.1/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();length=u32(b);block=b[16:16+length];h=bytearray(block[:32]);size=u32(h,12);assert u32(h,8)==0
code=bytearray(block[32:32+size]);oldcmd=block[32+size:];site=0x805edc3c;assert not any(a==site for t,a,v in commands(oldcmd))
# Values taken directly from the working title layout. Pane runtime transform fields
# 0x2c..0x50 correspond to BRLYT offsets36..75.
ref=(R/'work/menu-v9/Title/button/blyt/common_w076_license_icon_center.brlyt').read_bytes();p=16;panes={}
while p<len(ref):
 s=ref[p:p+u32(ref,p+4)];p+=len(s)
 if s[:4]==b'pic1':
  name=s[12:36].split(b'\0')[0].decode()
  if name in ['mii','nitro_mii_frame']:panes[name]=s[36:76]
assert len(panes)==2
body=['stwu 1,-48(1)','mflr 0','stw 0,52(1)','li 0,1','stb 0,1608(31)', # page.recordsButton+isHidden
      'lwz 0,1296(31)','cmpwi 0,0','beq finish'] # card layout root:0x454+0xa8+0x14
for i,(name,values) in enumerate(panes.items()):
 ns=(name.encode()+b'\0').ljust(16,b'\0');assert len(ns)==16
 for j in range(4):body += [load(0,u32(ns,j*4)),f'stw 0,{8+j*4}(1)']
 body += ['addi 3,31,1276','addi 4,1,8',load(12,0x805e8368),'mtctr 12','bctrl','cmpwi 3,0',f'beq next{i}']
 for j in range(10):body += [load(0,u32(values,j*4)),f'stw 0,{44+j*4}(3)']
 body += [f'next{i}:']
body += ['finish:','lwz 0,52(1)','mtlr 0','addi 1,1,48','lwz 0,20(1)','blr']
payload=asm(';\n'.join(body));off=len(code);code+=payload
struct.pack_into('>I',h,12,len(code));extra=cmd(65,site,off);newblock=bytes(h)+code+oldcmd+extra
out=p32(len(newblock))+b[4:16]+newblock+b[16+length:]
assert bytes(code[:size])==block[32:32+size];assert out[16+len(newblock):]==b[16+length:]
f=O/'MarioKartNitro_Test/Binaries/Code.pul';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(out)
(W/'hook.bin').write_bytes(payload);(O/'License-activation-hook.asm').write_text('\n'.join(body)+'\n')
manifest={'region':'PAL','hook_site':hex(site),'hook_offset':off,'hook_size':len(payload),'prior_code_preserved':True,'prior_commands_preserved':True,'other_regions_preserved':True,'pane_reference':{k:struct.unpack('>10f',v) for k,v in panes.items()},'full_game_rendering_tested':False}
(O/'Verification.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(__file__,O/'Build.py');print(manifest)
