from pathlib import Path
import ast,struct,hashlib,json
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
ROOT=Path('/workspace/scratch/e221e6641538')
SRC=ROOT/'work/MKNitro_v9_Character_Preview_Repair/MKNitro_Combined_Update_v9/Source'
original=(ROOT/'upload/Code(2).pul').read_bytes()
assert hashlib.sha256(original).hexdigest()=='5fe4083a44008ac5536e727b87999c03cea8597fb5d8da4120b45a66b60b2342'
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
def asm(s,addr=0):return bytes(ks.asm(s,addr)[0])
def p32(x):return struct.pack('>I',x)
def u32(b,p):return struct.unpack_from('>I',b,p)[0]
def cmd(t,a,v):return p32(t<<24|(a if a<0x1000000 else 0xfffffe))+(p32(a) if a>=0x1000000 else b'')+p32(v)
def branch(target,source,link=False):return p32(0x48000000|int(link)|((target-source)&0x3fffffc))
def load(reg,value):return f'lis {reg},{(value+0x8000)>>16}; addi {reg},{reg},{(value&65535)-65536 if value&32768 else value&65535}'
tree=ast.parse((ROOT/'work/v4/build_code.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='commands'],type_ignores=[]),'commands','exec'))
lengths=struct.unpack_from('>4I',original)
block=original[16:16+lengths[0]]
header=bytearray(block[:32]);old_size=u32(header,12);old_bss=u32(header,8)
code=bytearray(block[32:32+old_size]);old_commands=block[32+old_size:];parsed=commands(old_commands)
assert old_size==449976 and old_bss==333304
assert code[0x157d8:0x157dc]==asm('stwu 1,-80(1)')
code+=bytes(old_bss);code+=bytes((-len(code))%32)
start=len(code)
wrapper='''
 stwu 1,-32(1); mflr 0; stw 0,36(1); stw 31,28(1); mr 31,3
 bl original_entry
 lwz 0,1732(31); cmplwi 0,17; bge finish
 mulli 0,0,20
 lis 12,0x1357; addi 12,12,0x2468; add 12,12,0
 lbz 6,8(12); lbz 7,16(12)
 cmplwi 6,8; bgt finish; cmplwi 7,5; bgt finish
 add 0,6,7; slwi 0,0,6
 lis 9,0x1357; addi 9,9,0x2468; add 9,9,0
 lwz 10,0(9); addi 9,9,4
 addi 3,31,1736; li 4,0
 radio_loop:
 cmplw 4,6; bge scroll_start
 lwz 11,0(9); stw 11,8(3); stw 10,16(3); stw 10,20(3)
 addi 3,3,664; addi 9,9,4; addi 4,4,1; b radio_loop
 scroll_start:
 addi 3,31,7088; li 4,0
 scroll_loop:
 cmplw 4,7; bge rebuild
 lwz 11,0(9); stw 11,8(3); stw 10,16(3); stw 10,20(3)
 addi 3,3,1480; addi 9,9,4; addi 4,4,1; b scroll_loop
 rebuild:
 addi 3,31,36
 lis 12,0x805c; ori 12,12,0x2a5c; mtctr 12; bctrl
 finish:
 lwz 31,28(1); lwz 0,36(1); mtlr 0; addi 1,1,32; blr
 original_entry:
 stwu 1,-80(1); b 0
'''
added=bytearray(asm(wrapper,start));added[-4:]=branch(0x157dc,start+len(added)-4)
relocs=b'';tableoff=start+len(added)
for needle,target in [('lis 12,0x1357; addi 12,12,0x2468',0x64a20),('lis 9,0x1357; addi 9,9,0x2468',tableoff)]:
 p=added.index(asm(needle));added[p+2:p+4]=b'\0\0';added[p+6:p+8]=b'\0\0'
 relocs+=cmd(6,start+p+2,target)+cmd(4,start+p+6,target)
code+=added
for count in range(14):
 step=min(40.,224./max(1,count-1));scale=min(1.,step/40.)
 code+=struct.pack('>16f',scale,*[140.-i*step for i in range(13)],0.,0.)
# NoteModelControl::OnUpdate keeps its control in r27 at all three verified sites.
# Scope to the owning page, not the global top layer (dialogs can cover a course page).
scope='''
 lwz 12,100(27); cmpwi 12,0; beq original
 lwz 12,12(12); cmpwi 12,0; beq original
 lwz 12,4(12); cmpwi 12,110; beq course
 cmpwi 12,111; bne original
 course:
'''
hooks={}
for name,site,body in [
 ('visibility',0x805f4718,scope+'li 6,0\noriginal:\n'+load(12,0x805f59ac)+'; mtctr 12; bctr'),
 ('state_check',0x805f475c,scope+'li 12,0; cmpw 0,12; blr\noriginal:\ncmpwi 0,3; blr'),
 ('state_switch',0x805f47c8,scope+'li 5,0\noriginal:\n'+load(12,0x8082fb78)+'; mtctr 12; bctr')]:
 assert not any(a==site for t,a,args in parsed)
 off=len(code);payload=asm(body,off);code+=payload
 relocs+=cmd(65,site,off);hooks[name]={'site':site,'offset':off,'size':len(payload)}
 (ROOT/'work/v5'/f'{name}.asm').write_text(body+'\n')
code[0x157d8:0x157dc]=branch(start,0x157d8)
assert code[:0x157d8]==block[32:32+0x157d8]
assert code[0x157dc:old_size]==block[32+0x157dc:32+old_size]
assert not any(code[old_size:old_size+old_bss])
struct.pack_into('>II',header,8,0,len(code))
new_block=bytes(header)+code+old_commands+relocs
commands(old_commands+relocs)
output=p32(len(new_block))+original[4:16]+new_block+original[16+lengths[0]:]
assert output[16+len(new_block):]==original[16+lengths[0]:]
(ROOT/'work/v5/Code.pul').write_bytes(output)
(ROOT/'work/v5/layout_wrapper.asm').write_text(wrapper)
manifest={'original_sha256':hashlib.sha256(original).hexdigest(),'output_sha256':hashlib.sha256(output).hexdigest(),'region':'PAL','old_code':old_size,'old_bss':old_bss,'new_code':len(code),'layout_wrapper':start,'table':tableoff,'native_reset_group':0x805c2a5c,'hooks':hooks,'native_visibility':0x805f59ac,'native_switch':0x8082fb78,'unchanged_NTSC_regions':True}
(ROOT/'work/v5/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
