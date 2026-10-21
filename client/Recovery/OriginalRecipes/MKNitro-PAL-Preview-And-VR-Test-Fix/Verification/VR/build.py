import sys,struct,hashlib,json
from pathlib import Path
sys.path.insert(0,'work')
from code_tools import parse,u
src=Path('upload/Code(5).pul');blocks=parse(src); b,old,cmds=blocks[0]
assert len(old)==794312 and u(b,8)==0
# Verify rating getters against recovered source build, allowing branch displacements.
base=parse('work/baseline/MKNitro_Combined_Update_v9/Install/Binaries/Code.pul')[0][1]
for a,c in [(0x32850,0x58e70),(0x328bc,0x58edc)]:
 for off in range(0,0x6c,4):
  x=u(base,a+off);y=u(old,c+off)
  assert x==y or x>>26==y>>26==18
assert not any(a in (0x80662d80,0x80662dc4) for _,a,_,_,_ in cmds)
code=bytearray(old);helpers=[]
for target,getter,field in [(0x80662d80,0x58e70,0xc0),(0x80662dc4,0x58edc,0xc2)]:
 start=len(code)
 words=[0x9421ffe0,0x7c0802a6,0x90010024,0x93e1001c,0x7c7f1b78,
        0x3c60809c,0x8063d748,0x2c030000,0x41820024,
        0xa8630036,0x28030003,0x41810018,
        0x48000001|((getter-(start+48))&0x03fffffc),
        0xfc00081e,0xd8010008,0x8001000c,0xb01f0000|field,
        0x83e1001c,0x80010024,0x7c0803a6,0x38210020,0x4e800020]
 code+=struct.pack('>'+str(len(words))+'I',*words)
 helpers.append({'native':target,'getter':getter,'offset':start,'field':field,'size':len(words)*4})
header=bytearray(b[:32]);struct.pack_into('>I',header,12,len(code));commands=b[32+len(old):]
for h in helpers:commands+=struct.pack('>III',0x40fffffe,h['native'],h['offset'])
newpal=bytes(header)+code+commands;newblocks=[newpal]+[x[0] if x else b'' for x in blocks[1:]]
out=struct.pack('>4I',*[len(x) for x in newblocks])+b''.join(newblocks)
Path('work/vr_patch/Code.pul').write_bytes(out)
manifest={'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'helpers':helpers,'region':'PAL','preview_changed':False}
Path('work/vr_patch/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
