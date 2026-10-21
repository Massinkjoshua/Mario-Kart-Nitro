"""PAL leaderboard Mii validation. Input is the working MEM2-Pool-Fix."""
import struct,json,hashlib,sys
from pathlib import Path
from code_tools import parse
src,dst=map(Path,sys.argv[1:3]); raw=src.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='add73ccd21c2d0232cb5592c29799a196d8022be96c158b8bddf2b12402403a8'
blocks=parse(src);block,original,commands=blocks[0];c=bytearray(original);rel=[];labels={};fix=[]
def emit(w):c.extend(struct.pack('>I',w&0xffffffff))
def label(s):labels[s]=len(c)
def d(op,rt,ra,imm):emit(op<<26|rt<<21|ra<<16|(imm&65535))
def li(rt,n):d(14,rt,0,n)
def mr(rt,rs):emit(0x7c000378|rs<<21|rt<<16|rs<<11)
def add(rt,ra,rb):emit(0x7c000214|rt<<21|ra<<16|rb<<11)
def sub(rt,ra,rb):emit(0x7c000050|rt<<21|ra<<16|rb<<11) # rt = rb - ra
def shift(rt,rs,n):emit(0x54000000|rs<<21|rt<<16|n<<11|(31-n)<<1)
def srwi(rt,rs,n):emit(0x54000000|rs<<21|rt<<16|(32-n)<<11|n<<6|31<<1)
def cmpi(r,n):d(11,0,r,n)
def cmpl(r,s):emit(0x7c000040|r<<16|s<<11)
def cmp(r,s):emit(0x7c000000|r<<16|s<<11)
def b(target,lk=False):fix.append((len(c),target,0x48000000|lk,False));emit(0)
def bc(target,cond):fix.append((len(c),target,{'eq':0x41820000,'ne':0x40820000,'ge':0x40800000,'gt':0x41810000,'lt':0x41800000}[cond],True));emit(0)
def ext(target):rel.append((10,len(c),[target]));emit(0x48000001)
def ptr(reg,target):
 rel.append((6,len(c)+2,[target]));d(15,reg,0,0)
 rel.append((4,len(c)+2,[target]));d(14,reg,reg,0)
def prologue(regs):
 d(37,1,1,-0x30);emit(0x7c0802a6);d(36,0,1,0x34)
 for i,r in enumerate(regs):d(36,r,1,0x20+i*4)
def epilogue(regs):
 for i,r in enumerate(regs):d(32,r,1,0x20+i*4)
 d(32,0,1,0x34);emit(0x7c0803a6);d(14,1,1,0x30);emit(0x4e800020)
while len(c)%32:c.append(0)
label('load_mii');prologue([28,29,30]);mr(28,3);mr(29,4);mr(30,5);mr(3,5);ext(0x800cb8b0)
ptr(9,'row_valid');d(36,3,9,0);cmpi(3,0);bc('load_exit','eq')
mr(3,28);mr(4,29);mr(5,30);ext(0x805fa610)
label('load_exit');epilogue([28,29,30])
label('set_mii');ptr(9,'row_valid');d(32,0,9,0);cmpi(0,0);bc('set_return','eq')
rel.append((10,len(c),[0x8063e3dc]));emit(0x48000000)
label('set_return');emit(0x4e800020)
label('visible');ptr(9,'row_valid');d(32,5,9,0)
rel.append((10,len(c),[0x48888]));emit(0x48000000)
label('row_valid');emit(0)
for off,t,w,conditional in fix:
 delta=labels[t]-off
 assert delta%4==0
 struct.pack_into('>I',c,off,w|(delta&(0xfffc if conditional else 0x3fffffc)))
# Visibility helpers are internal direct branches rather than relocation entries.
for off in [0x49e44,0x49e54]:
 assert struct.unpack_from('>I',original,off)[0] == 0x48000001|((0x48888-off)&0x3fffffc)
 struct.pack_into('>I',c,off,0x48000001|((labels['visible']-off)&0x3fffffc))
newcmd=[]
for t,o,v,_,_ in commands:
 if t==10 and o==0x49e04:
  assert v==[0x805fa610];v=[labels['load_mii']]
 if t==10 and o in [0x49e1c,0x49e34]:
  assert v==[0x8063e3dc];v=[labels['set_mii']]
 newcmd.append((t,o,v))
newcmd.extend((t,o,[labels[v[0]] if isinstance(v[0],str) else v[0]]) for t,o,v in rel)
reloc=bytearray()
for t,o,v in newcmd:
 reloc+=struct.pack('>I',t<<24|(o if o<0xfffffe else 0xfffffe))
 if o>=0xfffffe:reloc+=struct.pack('>I',o)
 reloc+=struct.pack('>'+len(v)*'I',*v)
header=bytearray(block[:32]);struct.pack_into('>I',header,12,len(c));out=[bytes(header)+c+reloc]+[b[0] if b else b'' for b in blocks[1:]]
output=struct.pack('>4I',*map(len,out))+b''.join(out);dst.write_bytes(output)
manifest={'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(output).hexdigest(),'code_sha1':hashlib.sha1(c).hexdigest(),'labels':labels,'region':'PAL','base_build':'MEM2-Pool-Fix'}
dst.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
