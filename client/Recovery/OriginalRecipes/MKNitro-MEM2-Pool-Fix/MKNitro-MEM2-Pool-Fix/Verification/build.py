"""PAL HTTP fallback backed by a reserved MEM2 pool. Input must be the Static-Fix build."""
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
label('alloc');prologue([28,29,30,31]);mr(28,3);mr(29,4);d(36,3,1,8);li(0,1);d(36,0,1,0x10);b('old_alloc',True)
cmpi(3,0);bc('alloc_exit','ne');cmpi(28,0);bc('alloc_exit','eq')
cmpi(29,32);bc('alloc_exit','gt');d(15,4,0,2);cmpl(28,4);bc('alloc_exit','gt')
cmpi(29,4);bc('align_ok','ge');li(29,4)
label('align_ok');li(0,2);d(36,0,1,0x10);ext(0x801a65ac);mr(31,3);ptr(30,'slots');li(6,16)
label('alloc_scan');d(32,0,30,0);cmpi(0,0);bc('reserve_slot','eq');d(14,30,30,8);d(14,6,6,-1);cmpi(6,0);bc('alloc_scan','ne');li(30,0);b('alloc_unlock')
label('reserve_slot');li(0,-1);d(36,0,30,0)
label('alloc_unlock');mr(3,31);ext(0x801a65d4);cmpi(30,0);bc('have_slot','ne');li(3,0);b('alloc_exit')
label('have_slot');li(0,3);d(36,0,1,0x10);ptr(9,'pool');d(32,28,9,0);cmpi(28,0);bc('missing_heap','eq')
# Use the reserved native MEM heap directly; no current-thread heap override.
li(0,4);d(36,0,1,0x10);mr(3,28);d(32,4,1,8);mr(5,29);ext(0x80198d88);b('record_result')
label('missing_heap');li(3,0)
label('record_result');cmpi(3,0);bc('record_nonzero','ne');li(28,0)
label('record_nonzero');d(36,3,1,0xc);ext(0x801a65ac);mr(31,3);d(32,0,1,0xc);d(36,28,30,4);d(36,0,30,0);mr(3,31);ext(0x801a65d4);d(32,3,1,0xc)
label('alloc_exit');cmpi(3,0);bc('alloc_done','ne')
# Capture the latest failed allocation; cleanup frees do not overwrite it.
ptr(9,'failure');d(32,0,1,0x10);d(36,0,9,0);d(32,0,1,8);d(36,0,9,4)
label('alloc_done');epilogue([28,29,30,31])
label('free');cmpi(3,0);bc('free_return','eq');prologue([28,29,30,31]);mr(28,3);ext(0x801a65ac);mr(31,3);ptr(30,'slots');li(6,16)
label('free_scan');d(32,0,30,0);cmp(0,28);bc('free_found','eq');d(14,30,30,8);d(14,6,6,-1);cmpi(6,0);bc('free_scan','ne');li(30,0);b('free_unlock')
label('free_found');d(32,29,30,4);li(0,-1);d(36,0,30,0)
label('free_unlock');mr(3,31);ext(0x801a65d4);cmpi(30,0);bc('normal_free','eq')
mr(3,29);mr(4,28);ext(0x80199038)
ext(0x801a65ac);mr(31,3);li(0,0);d(36,0,30,0);d(36,0,30,4);mr(3,31);ext(0x801a65d4);b('free_exit')
label('normal_free');mr(3,28);b('old_free',True)
label('free_exit');epilogue([28,29,30,31])
label('free_return');emit(0x4e800020)
# Reserve MEM2 before BootHook::Exec and before the menu child heap exists.
# The native RootScene enter call supplies its persistent MEM2 heap in r4.
label('boot');prologue([31]);d(36,3,1,8);d(36,4,1,12);d(36,5,1,16)
mr(3,4);b('init_pool',True)
d(32,3,1,8);d(32,4,1,12);d(32,5,1,16);ext(0x9c);epilogue([31])
label('init_pool');prologue([30,31]);mr(31,3);ptr(9,'pool');d(32,3,9,0);cmpi(3,0);bc('init_exit','ne')
li(0,4);d(36,0,9,4);cmpi(31,0);bc('init_exit','eq')
li(0,1);d(36,0,9,4);d(32,12,31,0);mr(3,31);d(15,4,0,4);li(5,32)
d(32,12,12,0x14);emit(0x7d8903a6);emit(0x4e800421);mr(30,3);cmpi(3,0);bc('init_exit','eq')
# Native MEM expanded heap, with thread-safe attribute 4. No EGG object is fabricated.
d(15,4,0,4);li(5,4);ext(0x80198ca8);cmpi(3,0);bc('init_ok','ne')
ptr(9,'pool');li(0,2);d(36,0,9,4);d(32,12,31,0);mr(3,31);mr(4,30)
d(32,12,12,0x18);emit(0x7d8903a6);emit(0x4e800421);li(3,0);b('init_exit')
label('init_ok');ptr(9,'pool');d(36,3,9,0);li(0,3);d(36,0,9,4)
label('init_exit');epilogue([30,31])
label('create');prologue([31]);ptr(9,'failure');li(0,0);d(36,0,9,0);d(36,0,9,4);ext(0x801d8ff8);mr(31,3);cmpi(3,0);bc('create_exit','ne')
ext(0x801d9e94);d(32,4,3,0x7d8);ptr(5,'create_default');cmpi(4,1);bc('create_memory','eq');cmpi(4,4);bc('create_url','eq');b('create_message')
label('create_memory');ptr(9,'failure');d(32,6,9,0)
# Zero means native memory failure without a failing call to our allocator.
ptr(5,'create_other_text');cmpi(6,0);bc('create_message','eq')
ptr(5,'create_limit_text');cmpi(6,1);bc('create_message','eq')
ptr(5,'create_slots_text');cmpi(6,2);bc('create_message','eq')
ptr(5,'create_noheap_text');cmpi(6,3);bc('create_message','eq')
ptr(5,'create_root_text');d(32,6,9,4);d(15,7,0,1);d(14,7,7,-32672);cmp(6,7);bc('create_message','ne')
ptr(5,'create_root32_text');b('create_message')
label('create_url');ptr(5,'create_url_text')
label('create_message');ptr(4,794676+5*8+4);d(36,5,4,0)
label('create_exit');mr(3,31);epilogue([31])
for name,text in [('create_default','Failed: create'),('create_other_text','Mem: other allocator'),('create_limit_text','Mem: size or align'),('create_slots_text','Mem: tracking full'),('create_noheap_text','Mem: pool missing'),('create_root_text','Mem: pool full'),('create_root32_text','Mem: pool full 32K'),('create_url_text','Create: URL')]:
 label(name);c.extend((text+'\0').encode('utf-16-be'))
while len(c)%32:c.append(0)
label('slots');c.extend(bytes(16*8));label('failure');c.extend(bytes(8));label('pool');c.extend(bytes(8))
for off,t,w,conditional in fix:
 target=labels[t] if isinstance(t,str) else t;delta=target-off
 assert delta%4==0
 assert -32768<=delta<32768 if conditional else -0x2000000<=delta<0x2000000
 struct.pack_into('>I',c,off,w|(delta&(0xfffc if conditional else 0x3fffffc)))
for off,t in [(0x5da24,'alloc'),(0x5da54,'free')]:struct.pack_into('>I',c,off,0x48000000|((labels[t]-off)&0x3fffffc))
newcmd=[]
for t,o,v,_,_ in commands:
 if t==10 and o==0x4a0b8:v=[labels['create']]
 if t==65 and o==0x80543bb4:
  assert v==[0x9c]
  v=[labels['boot']]
 newcmd.append((t,o,v))
newcmd.extend((t,o,[labels[v[0]] if isinstance(v[0],str) else v[0]]) for t,o,v in rel)
reloc=bytearray()
for t,o,v in newcmd:
 reloc+=struct.pack('>I',t<<24|(o if o<0xfffffe else 0xfffffe))
 if o>=0xfffffe:reloc+=struct.pack('>I',o)
 reloc+=struct.pack('>'+len(v)*'I',*v)
header=bytearray(block[:32]);struct.pack_into('>I',header,12,len(c));out=[bytes(header)+c+reloc]+[b[0] if b else b'' for b in blocks[1:]]
output=struct.pack('>4I',*map(len,out))+b''.join(out);dst.write_bytes(output)
manifest={'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(output).hexdigest(),'code_sha1':hashlib.sha1(c).hexdigest(),'labels':labels,'fallback_tracking_slots':16,'maximum_fallback_bytes':131072,'pool_bytes':262144,'pool_init_hook':'RootScene enter 0x80543bb4','region':'PAL','base_build':'Static-Fix'}
dst.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
