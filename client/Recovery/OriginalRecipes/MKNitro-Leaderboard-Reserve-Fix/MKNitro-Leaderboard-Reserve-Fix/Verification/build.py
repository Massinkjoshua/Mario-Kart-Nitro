"""PAL HTTP allocation reserve. Input must be the Static-Fix build."""
import struct,json,hashlib,sys
from pathlib import Path
from code_tools import parse
src,dst=map(Path,sys.argv[1:3]); raw=src.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='96c2e5c145d0de4fbfe16aebb649f3b5d77065d8b40867c2b146603730529dc0'
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
while len(c)%32:emit(0)
label('old_alloc');c.extend(original[0x5da24:0x5da54]);rel.append((10,labels['old_alloc']+0x28,[0x80229814]))
label('old_free');c.extend(original[0x5da54:0x5da78]);rel.append((10,labels['old_free']+0x1c,[0x80229b84]))
label('alloc');prologue([28,29,30,31]);mr(28,3);mr(29,4);b('old_alloc',True)
cmpi(3,0);bc('alloc_exit','ne');cmpi(28,0);bc('alloc_exit','eq')
cmpi(29,32);bc('alloc_exit','gt');d(15,4,0,8);cmpl(28,4);bc('alloc_exit','gt')
d(14,28,28,8191);srwi(28,28,13);ext(0x801a65ac);mr(30,3);li(31,0)
ptr(9,'metadata');ptr(10,'pool');li(6,0);li(7,0)
label('scan');cmpi(6,64);bc('unlock','ge');shift(11,6,2)
emit(0x7c00002e|8<<21|9<<16|11<<11) # lwzx r8,r9,r11
cmpi(8,0);bc('occupied','ne');d(14,7,7,1);cmp(7,28);bc('found','eq');b('advance')
label('occupied');li(7,0)
label('advance');d(14,6,6,1);b('scan')
label('found');d(14,6,6,1);sub(6,28,6);shift(11,6,2);add(9,9,11);d(36,28,9,0)
d(14,7,28,-1);li(8,-1)
label('mark');cmpi(7,0);bc('result','eq');d(14,9,9,4);d(36,8,9,0);d(14,7,7,-1);b('mark')
label('result');shift(6,6,13);add(31,10,6)
label('unlock');mr(3,30);ext(0x801a65d4);mr(3,31)
label('alloc_exit');epilogue([28,29,30,31])
label('free');ptr(4,'pool');sub(5,4,3);d(15,6,0,8);cmpl(5,6);bc('old_free','ge')
d(28,5,0,8191);bc('free_return','ne');prologue([30,31]);srwi(30,5,13);ext(0x801a65ac);mr(31,3)
ptr(4,'metadata');shift(5,30,2);add(4,4,5);d(32,5,4,0);cmpi(5,0);bc('free_unlock','eq')
li(6,64);cmpl(5,6);bc('free_unlock','gt');add(6,5,30);cmpi(6,64);bc('free_unlock','gt');li(0,0)
label('clear');d(36,0,4,0);d(14,4,4,4);d(14,5,5,-1);cmpi(5,0);bc('clear','ne')
label('free_unlock');mr(3,31);ext(0x801a65d4);epilogue([30,31])
label('free_return');emit(0x4e800020)
# Native Startup allocates a worker stack and resets lists on every call.
# Skip a redundant startup while the actual library initialized flag is set.
label('startup');prologue([28,29,30]);mr(28,3);mr(29,4);mr(30,5)
ext(0x801d9e94);d(32,0,3,0x7cc);cmpi(0,0);bc('startup_needed','eq');li(3,0);b('startup_exit')
label('startup_needed');mr(3,28);mr(4,29);mr(5,30);ext(0x801d8d30)
label('startup_exit');epilogue([28,29,30])
# Retain the stage diagnostic, but distinguish the native creation error.
label('create');prologue([31]);ext(0x801d8ff8);mr(31,3);cmpi(3,0);bc('create_exit','ne')
ext(0x801d9e94);d(32,4,3,0x7d8);ptr(5,'create_default');cmpi(4,1);bc('create_memory','eq');cmpi(4,4);bc('create_url','eq');b('create_message')
label('create_memory');ptr(5,'create_mem_text');b('create_message')
label('create_url');ptr(5,'create_url_text')
label('create_message');ptr(4,794676+5*8+4);d(36,5,4,0)
label('create_exit');mr(3,31);epilogue([31])
for name,text in [('create_default','Failed: create'),('create_mem_text','Create: memory'),('create_url_text','Create: URL')]:
 label(name);c.extend((text+'\0').encode('utf-16-be'))
while len(c)%32:c.append(0)
label('metadata');c.extend(bytes(64*4));label('pool');c.extend(bytes(512*1024))
for off,t,w,conditional in fix:
 target=labels[t] if isinstance(t,str) else t;delta=target-off
 assert delta%4==0
 assert -32768<=delta<32768 if conditional else -0x2000000<=delta<0x2000000
 struct.pack_into('>I',c,off,w|(delta&(0xfffc if conditional else 0x3fffffc)))
for off,t in [(0x5da24,'alloc'),(0x5da54,'free')]:struct.pack_into('>I',c,off,0x48000000|((labels[t]-off)&0x3fffffc))
newcmd=[]
for t,o,v,_,_ in commands:
 if t==10 and o==0x4a0b8:v=[labels['create']]
 if t==10 and o==0x5dab0:v=[labels['startup']]
 newcmd.append((t,o,v))
newcmd.extend((t,o,[labels[v[0]] if isinstance(v[0],str) else v[0]]) for t,o,v in rel)
reloc=bytearray()
for t,o,v in newcmd:
 reloc+=struct.pack('>I',t<<24|(o if o<0xfffffe else 0xfffffe))
 if o>=0xfffffe:reloc+=struct.pack('>I',o)
 reloc+=struct.pack('>'+len(v)*'I',*v)
header=bytearray(block[:32]);struct.pack_into('>I',header,12,len(c));out=[bytes(header)+c+reloc]+[b[0] if b else b'' for b in blocks[1:]]
output=struct.pack('>4I',*map(len,out))+b''.join(out);dst.write_bytes(output)
manifest={'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(output).hexdigest(),'code_sha1':hashlib.sha1(c).hexdigest(),'labels':labels,'reserve_bytes':524288,'region':'PAL','base_build':'Static-Fix'}
dst.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
