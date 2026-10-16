"""Native PAL request creation + fallback allocator regression tests.
Usage: python3 test.py ORIGINAL_STATIC.pul NEW.pul main.dol
The user's DOL is required but deliberately not redistributed.
OS scheduling/locks, the underlying EGG heap, and HTTP SendAsync are stubbed.
NHTTP context, native request parser/creation, snprintf and patch run as PPC.
"""
import hashlib,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_PPC,UC_MODE_32,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.ppc_const import *
from code_tools import parse
oldpath,newpath,dolpath=sys.argv[1:4];old=parse(oldpath);new=parse(newpath)
meta=json.loads(Path(newpath).with_suffix('.json').read_text());labels=meta['labels']
assert old[1:]==new[1:],'Non-PAL regions changed'
allowed=set(range(0x5da24,0x5da28))|set(range(0x5da54,0x5da58))
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old[0][1],new[0][1])))
assert [(t,o,v) for t,o,v,_,_ in old[0][2] if o not in [0x4a0b8]]==[(t,o,v) for t,o,v,_,_ in new[0][2][:len(old[0][2])] if o not in [0x4a0b8]]
dol=Path(dolpath).read_bytes();unpack=lambda b,o:struct.unpack_from('>I',b,o)[0]
class Machine:
 def __init__(self,blocks,base,limit):
  self.x=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);x=self.x;x.mem_map(0x80000000,0x1800000)
  for i in range(18):
   o,a,n=[unpack(dol,j+i*4) for j in [0,0x48,0x90]]
   if n:x.mem_write(a,dol[o:o+n])
  x.reg_write(UC_PPC_REG_13,0x8038cc00);x.reg_write(UC_PPC_REG_2,0x8038efa0)
  x.mem_map(0x90000000,0x400000)
  self.base=base;self.limit=limit;self.heap=0x81400000;self.events=[];self.lock=0;self.interrupts=1;self.startup_calls=[];self.startup_result=0
  _,raw,commands=blocks[0];c=bytearray(raw)
  for t,o,v,_,_ in commands:
   if o>=len(c):continue
   target=v[0] if v[0]>=0x80000000 else base+v[0]
   if t==1:struct.pack_into('>I',c,o,target)
   elif t==4:struct.pack_into('>H',c,o,target&65535)
   elif t==6:struct.pack_into('>H',c,o,((target+32768)>>16)&65535)
   elif t==10:struct.pack_into('>I',c,o,(unpack(c,o)&0xfc000003)|((target-base-o)&0x3fffffc))
  x.mem_write(base,bytes(c));x.hook_add(UC_HOOK_CODE,self.hook)
  self.context=self.call(0x801d9e94)
  for off,value in [(0x7c4,base+0x5da24),(0x7c8,base+0x5da54),(0x7cc,1)]:self.w(self.context+off,value)
  self.w(0x802a4080+0x24,0x813f0000)
  self.state=base+0x92fd4;self.w(self.state+8,0x81300000)
 def r(self,i):return self.x.reg_read(UC_PPC_REG_0+i)
 def w(self,a,v):self.x.mem_write(a,struct.pack('>I',v&0xffffffff))
 def word(self,a):return unpack(self.x.mem_read(a,4),0)
 def ret(self,n=0):self.x.reg_write(UC_PPC_REG_3,n&0xffffffff);self.x.reg_write(UC_PPC_REG_PC,self.x.reg_read(UC_PPC_REG_LR))
 def hook(self,x,a,size,data):
  if a==0x801d8d30:
   self.startup_calls.append((self.r(3),self.r(4),self.r(5)));self.ret(self.startup_result)
  elif a==0x801aad5c:x.reg_write(UC_PPC_REG_4,0);self.ret()
  elif a==self.base+0x5dacc:self.ret(1)
  elif a==0x80229814:
   n,align=self.r(3),self.r(4);self.heap=(self.heap+align-1)&~(align-1);p=self.heap if n<=self.limit else 0
   if p:self.heap+=n
   self.events.append(('alloc',n,align,p));self.ret(p)
  elif a==0x80229b84:self.events.append(('free',self.r(3)));self.ret()
  elif a==0x801d925c:self.events.append(('send',self.r(3)));self.ret(1)
  elif a==self.base+0x5db28:self.ret()
  elif a in [0x801a7ee4,0x801a7fc0]:self.ret()
  elif a==0x801a65ac:
   self.lock+=1;prior=self.interrupts;self.interrupts=0;self.ret(prior)
  elif a==0x801a65d4:
   assert self.lock;self.lock-=1;self.interrupts=self.r(3);self.ret()
 def call(self,a,*args):
  x=self.x;end=0x81700000;x.reg_write(UC_PPC_REG_1,0x817ff000);x.reg_write(UC_PPC_REG_LR,end)
  for i in range(14,32):x.reg_write(UC_PPC_REG_0+i,0x70000000+i)
  for i,v in enumerate(args):x.reg_write(UC_PPC_REG_3+i,v&0xffffffff)
  x.emu_start(a,end,count=2000000)
  assert x.reg_read(UC_PPC_REG_PC)==end,hex(x.reg_read(UC_PPC_REG_PC))
  assert all(self.r(i)==0x70000000+i for i in range(14,32)),'Callee-saved register changed'
  assert not self.lock
  return self.r(3)
 def alloc(self,n,align=32):return self.call(self.base+0x5da24,n,align)
 def free(self,p):self.call(self.base+0x5da54,p)
 def start(self):self.call(self.base+0x49f3c,0x81200000);return self.word(self.state)
 def create(self,url):
  self.x.mem_write(0x81200000,url+b'\0')
  return self.call(self.base+labels['create'],0x81200000,0,0x81210000,16384,0x81220000,0)
 def message(self):
  p=self.word(self.base+794676+5*8+4)
  return bytes(self.x.mem_read(p,40)).decode('utf-16-be').split('\0')[0]

def setup_mem2(m):
 root=0x90010000
 handle=m.call(0x80198ca8,root+0x38,0x100000-0x38,0)
 assert handle==root+0x38
 m.w(root,0x802a2ff8);m.w(root+0x10,handle);m.w(0x802a409c,root)
 return root

def slots(m):return bytes(m.x.mem_read(m.base+labels['slots'],128))
def total_free(m,root):return m.call(0x80226c88,root)
checks=0
for base in [0x803992e0,0x81000000]:
 m=Machine(old,base,16000);assert m.start()==8;assert m.word(m.context+0x7d8)==1;checks+=1
 for limit in [0,16000,1000000]:
  m=Machine(new,base,limit);root=setup_mem2(m)
  assert m.start()==1 and any(e[0]=='send' for e in m.events)
  assert bytes(m.x.mem_read(base+0x92fd4+0x48,100)).split(b'\0')[0]==b'http://play.mknitro.com/api/leaderboard/in-game?page=1'
  checks+=1
 # Real native MEM2 allocator/free, with all normal heap requests refused.
 m=Machine(new,base,0);root=setup_mem2(m);initial=total_free(m,root)
 assert not m.alloc(131073) and not m.alloc(1,64);checks+=2
 for flag in [0,1]:
  m.interrupts=flag;p=m.alloc(32864);assert 0x90010000<=p<0x90110000 and p%32==0
  assert m.interrupts==flag;m.free(p);assert m.interrupts==flag and slots(m)==bytes(128)
  assert total_free(m,root)==initial;checks+=1
 # Native MEM2 heap out-of-memory releases its reserved tracking slot.
 held=[]
 while True:
  p=m.alloc(131072)
  if not p:break
  held.append(p)
 assert 0<len(held)<16
 for p in held:m.free(p)
 assert slots(m)==bytes(128) and total_free(m,root)==initial;checks+=1
 # Tracking-table exhaustion, then reuse.
 held=[m.alloc(32) for _ in range(16)];assert all(held) and not m.alloc(32)
 for p in held:m.free(p)
 assert slots(m)==bytes(128) and total_free(m,root)==initial;checks+=1
 # Native URL failure cleanup returns all allocations to their own heap.
 for _ in range(50):
  assert not m.create(b'invalid://test/leaderboard')
  assert m.message()=='Create: URL' and slots(m)==bytes(128)
  assert total_free(m,root)==initial;checks+=1
 # Random mixed lifetimes cannot overlap and recover the native heap fully.
 rng=random.Random(32);live=[]
 for _ in range(300):
  if live and rng.random()<.48:
   p,n=live.pop(rng.randrange(len(live)));m.free(p)
  else:
   n=rng.randint(1,65536);align=rng.choice([4,8,16,32]);p=m.alloc(n,align)
   if p:
    assert p%align==0 and all(p+n<=q or q+k<=p for q,k in live)
    live.append((p,n))
  checks+=1
 for p,n in live:m.free(p)
 assert slots(m)==bytes(128) and total_free(m,root)==initial
 # A normal heap allocation still frees through the original path.
 m.limit=1000000;p=m.alloc(32864);assert p>=0x81400000 and p<0x81700000;m.free(p)
 assert ('free',p) in m.events and slots(m)==bytes(128);checks+=1
 # Root unavailable: safe failure and useful native memory error.
 m.limit=0;m.w(0x802a409c,0)
 assert not m.create(b'http://play.mknitro.com/api/leaderboard/in-game?page=1')
 assert m.message()=='Create: memory' and slots(m)==bytes(128);checks+=1
print('PASS:',checks,'checks. Native MEM2 heap creation/allocation/free and NHTTP request creation executed; old allocation failure reproduced; new request reaches send; allocation ownership, OOM, tracking exhaustion, cleanup/reuse, registers and interrupt state checked.')
print('Non-PAL blocks and HTTP startup helper unchanged. Test includes actual logged mod load address 0x803992e0.')
print('OS scheduling/locks and network sending simulated; normal heap constrained. Live Dolphin/network test still required.')
print('DOL SHA256:',hashlib.sha256(dol).hexdigest())
