from pathlib import Path
import ast,struct,shutil,sys,json,hashlib,zipfile
from PIL import Image
R=Path('/workspace/scratch/e221e6641538');W=R/'work/menu-v9';O=R/'deliverables/MKNitro-License-And-Item-Fixes-v9';O.mkdir(exist_ok=True)
sys.path.insert(0,'/tmp');from unpack import dec,unpack
for fn,names in [('/tmp/build_patch.py',['tpl','pack']),('/tmp/package_font.py',['yaz'])]:
 t=ast.parse(Path(fn).read_text());exec(compile(ast.Module(body=[x for x in t.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[]),fn,'exec'))
u16=lambda b,p:struct.unpack_from('>H',b,p)[0]
u32=lambda b,p:struct.unpack_from('>I',b,p)[0]
def sections(b):
 p=16
 while p<len(b):
  n=u32(b,p+4);yield bytearray(b[p:p+n]);p+=n
 assert p==len(b)
def rebuild(b,ss):
 out=bytearray(b[:16])+b''.join(ss);struct.pack_into('>I',out,8,len(out));struct.pack_into('>H',out,14,len(ss));return out
def label(s):return bytes(s[12:36]).split(b'\0')[0].decode()
def floats(s,p,vals):struct.pack_into('>'+str(len(vals))+'f',s,p,*vals)
for name,base in [('MenuOther','unpacked/MenuOther'),('Title','patch-work-v3/Title')]:shutil.copytree(R/base,W/name,dirs_exist_ok=True)
# Match the actual title-screen Mii transform and frame, not an estimated percentage.
title=list(sections((W/'Title/button/blyt/common_w076_license_icon_center.brlyt').read_bytes()))
f=W/'MenuOther/control/blyt/common_w076_license_icon_center.brlyt';b=f.read_bytes();ss=list(sections(b))
for s in ss:
 if s[:4]==b'pic1' and label(s) in ['mii','nitro_mii_frame']:
  source=next(x for x in title if x[:4]==b'pic1' and label(x)==label(s));s[36:76]=source[36:76]
f.write_bytes(rebuild(b,ss))
# Restore a panel independently of the original hidden/animated fuchi pane.
f=W/'MenuOther/button/blyt/common_w097_license_screen_menu.brlyt';b=f.read_bytes();ss=list(sections(b));donor=next(s for s in ss if s[:4]==b'pic1' and label(s)=='fuchi_pattern');plate=bytearray(donor);plate[12:36]=b'nitro_button_panel'.ljust(24,b'\0');plate[8]|=1;plate[10]=255
ss.insert(ss.index(donor),plate);f.write_bytes(rebuild(b,ss))
# Record control is also disabled in native code; zero both aspect transforms.
f=W/'MenuOther/button/ctrl/LicenseManagementButton.brctr';b=bytearray(f.read_bytes());sub=u16(b,14);start=sub+u16(b,sub);st=u16(b,16)
for i in range(u16(b,sub+2)):
 p=start+i*60;name=bytes(b[st+u16(b,p):]).split(b'\0')[0]
 if name==b'Record':
  for q in [12,32]:floats(b,p+q,[-5000,0,0,0,0])
 elif name in [b'ChangeMii',b'Delete']:
  for q in [16,36]:floats(b,p+q,[50 if name==b'ChangeMii' else -50])
f.write_bytes(b)
# Smaller title-screen settings emblem: dimensions are not overwritten by scale animations.
f=W/'Title/button/blyt/open_icon_option.brlyt';b=f.read_bytes();ss=list(sections(b))
for s in ss:
 if s[:4]==b'pic1' and label(s) in ['icon','capsule','icon_shadow_00','icon_light_01','icon_light_02']:
  floats(s,68,[v*.65 for v in struct.unpack_from('>2f',s,68)])
f.write_bytes(rebuild(b,ss))
# Dark backing immediately behind MenuOther headings/help text, sharing their transform.
# Simple material donor is the already-working, unanimated single-texture panel material.
panelss=list(sections((W/'MenuOther/button/blyt/common_w097_license_screen_menu.brlyt').read_bytes()));ma=next(x for x in panelss if x[:4]==b'mat1');idx=13;at=u32(ma,12+idx*4);end=u32(ma,12+(idx+1)*4) if idx+1<u16(ma,8) else len(ma);simplemat=bytearray(ma[at:end])
for basename in ['obi_top_text','obi_bottom_message']:
 f=W/'MenuOther/bg/blyt'/(basename+'.brlyt');b=f.read_bytes();ss=list(sections(b));tx=next((s for s in ss if s[:4]==b'txl1'),None);names=[]
 if tx:
  for i in range(u16(tx,8)):
   p=12+u32(tx,12+i*8);names.append(bytes(tx[p:]).split(b'\0')[0])
 ti=len(names);names.append(b'nitro_readable.tpl');nt=bytearray(b'txl1'+bytes(8));struct.pack_into('>H',nt,8,len(names));nt+=bytes(len(names)*8)
 for i,n in enumerate(names):struct.pack_into('>I',nt,12+i*8,len(nt)-12);nt+=n+b'\0'
 nt+=bytes(-len(nt)%4);struct.pack_into('>I',nt,4,len(nt))
 if tx:ss[ss.index(tx)]=nt
 else:ss.insert(1,nt)
 ma=next(s for s in ss if s[:4]==b'mat1');cnt=u16(ma,8);offsets=[u32(ma,12+4*i) for i in range(cnt)]+[len(ma)];mats=[ma[offsets[i]:offsets[i+1]] for i in range(cnt)];m=bytearray(simplemat);m[:20]=b'nitro_readable'.ljust(20,b'\0');struct.pack_into('>H',m,64,ti);mats.append(m)
 nm=bytearray(b'mat1'+bytes(8));struct.pack_into('>H',nm,8,len(mats));nm+=bytes(4*len(mats))
 for i,m in enumerate(mats):struct.pack_into('>I',nm,12+4*i,len(nm));nm+=m
 struct.pack_into('>I',nm,4,len(nm));ss[ss.index(ma)]=nm
 text=next(s for s in ss if s[:4]==b'txt1' and label(s)=='text');bg=bytearray(plate);bg[12:36]=b'nitro_text_backing'.ljust(24,b'\0');bg[8:12]=text[8:12];bg[36:76]=text[36:76];bg[10]=220
 x,y,z=struct.unpack_from('>3f',bg,36);width,height=struct.unpack_from('>2f',bg,68);x+=-10 if bg[9]%3==0 else 10 if bg[9]%3==2 else 0;floats(bg,36,[x,y,z]);floats(bg,68,[width+20,height+10]);bg[76:92]=bytes([16,9,28,255])*4;struct.pack_into('>H',bg,92,cnt);floats(bg,96,[0,0,1,0,0,1,1,1]);ss.insert(ss.index(text),bg);f.write_bytes(rebuild(b,ss))
(W/'MenuOther/bg/timg/nitro_readable.tpl').write_bytes(tpl(Image.new('RGBA',(4,4),'white')))
# Append small PAL native instruction replacements to the current v6 binary.
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
def asm(s):return bytes(ks.asm(s)[0])
sys.path.insert(0,str(R/'work/v5'));import native_rel
patches=[(0x805eda74,'li 9,0','li 9,1','Check Records input disabled'),(0x805edc24,'addi 3,3,1480','addi 3,3,2076','Initial focus Change Mii'),(0x805edc30,'li 4,2121','li 4,2122','Initial Change Mii help text'),(0x807ef204,'clrlwi 6,27,24','li 6,0','Remove roulette additive white rectangle'),(0x807ef0a4,'clrlwi 0,0,24','li 0,0','Remove item-acquisition additive white rectangle')]
base=(R/'work/crash-repair/Code.pul').read_bytes();length=u32(base,0);extra=bytearray();report=[]
for addr,old,new,why in patches:
 assert native_rel.read(addr,4)==asm(old),(hex(addr),old)
 extra+=struct.pack('>II',0x20fffffe,addr)+asm(new);report.append({'address':hex(addr),'old':old,'new':new,'purpose':why})
code=struct.pack('>I',length+len(extra))+base[4:16+length]+extra+base[16+length:];assert code[4:16+length]==base[4:16+length];assert code[16+length+len(extra):]==base[16+length:]
out=O/'MarioKartNitro_Test/Binaries/Code.pul';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(code)
manifest={'native_patches':report,'v6_code_and_existing_commands_preserved':True,'other_regions_preserved':True,'game_rendering_tested':False}
for name,orig in [('MenuOther',R/'unpacked/MenuOther'),('Title',R/'patch-work-v3/Title')]:
 folder=W/name;raw=pack(folder);packed=yaz(raw);assert dec(packed)==raw;out=O/'MarioKartNitro_Test/MenuRace'/(name+'.szs');out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(packed);verify=W/(name+'-verify');unpack(packed,verify)
 for p in folder.rglob('*'):
  if p.is_file():assert p.read_bytes()==(verify/p.relative_to(folder)).read_bytes()
 manifest[name]={'changed_files':[str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() and (not (orig/p.relative_to(folder)).exists() or p.read_bytes()!=(orig/p.relative_to(folder)).read_bytes())],'archive_roundtrip':True}
(O/'Verification.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(__file__,O/'Build.py');print(json.dumps(manifest,indent=2),flush=True)
