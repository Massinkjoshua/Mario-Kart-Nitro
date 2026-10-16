import sys,struct,json
from pathlib import Path
sys.path.insert(0,'work');from code_tools import parse,u
blocks=parse('work/vr_patch/Code.pul');b,old,cmds=blocks[0];code=bytearray(old)
def write(p,v,expect):
 assert u(code,p)==expect,(hex(p),hex(u(code,p)))
 assert not any(p<=a<p+4 for _,a,_,_,_ in cmds)
 struct.pack_into('>I',code,p,v)
start=len(code)
# Save and restore both native on-vehicle states (2,3).
words=[0x28000002,0x41800014,0x28000003,0x4181000c,0x90010008,0x3b600001,
       0x48000000|((0x73ac-(start+24))&0x3fffffc)]
code+=struct.pack('>7I',*words)
write(0x73a0,0x48000000|((start-0x73a0)&0x3fffffc),0x28000002)
write(0x7488,0x80a10008,0x38a00002)
write(0x6be0,0x38630014,0x3863001c)
header=bytearray(b[:32]);struct.pack_into('>I',header,12,len(code))
parts=[bytes(header)+code+b[32+len(old):]]+[x[0] if x else b'' for x in blocks[1:]]
Path('work/preview_patch/Code.pul').write_bytes(struct.pack('>4I',*[len(x) for x in parts])+b''.join(parts))
Path('work/preview_patch/offsets.json').write_text(json.dumps({'state_trampoline':start,'source':'VR test fix','PAL':True}))
print('Updated field +0x14, preserve vehicle states 2/3; prior VR patch retained.')
