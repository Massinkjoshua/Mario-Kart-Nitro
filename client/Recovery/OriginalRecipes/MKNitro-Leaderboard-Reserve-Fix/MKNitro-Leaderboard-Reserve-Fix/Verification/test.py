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
assert [(t,o,v) for t,o,v,_,_ in old[0][2] if o not in [0x4a0b8,0x5dab0]]==[(t,o,v) for t,o,v,_,_ in new[0][2][:len(old[0][2])] if o not in [0x4a0b8,0x5dab0]]
dol=Path(dolpath).read_bytes();unpack=lambda b,o:struct.unpack_from('>I',b,o)[0]
class Machine:
 def __init__(self,blocks,base,limit):
  self.x=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);x=self.x;x.mem_map(0x80000000,0x1800000)
  for i in range(18):
   o,a,n=[unpack(dol,j+i*4) for j in [0,0x48,0x90]]
   if n:x.mem_write(a,dol[o:o+n])
  x.reg_write(UC_PPC_REG_13,0x8038cc00);x.reg_write(UC_PPC_REG_2,0x8038efa0)
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
   assert not self.lock;self.lock=1;prior=self.interrupts;self.interrupts=0;self.ret(prior)
  elif a==0x801a65d4:
   assert self.lock;self.lock=0;self.interrupts=self.r(3);self.ret()
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
checks=0
for base in [0x80500000,0x81000000]:
 m=Machine(old,base,16000);assert m.start()==8;assert m.word(m.context+0x7d8)==1;checks+=1
 for limit in [0,16000,1000000]:
  m=Machine(new,base,limit);assert m.start()==1;assert any(e[0]=='send' for e in m.events)
  assert bytes(m.x.mem_read(base+0x92fd4+0x48,100)).split(b'\0')[0]==b'http://play.mknitro.com/api/leaderboard/in-game?page=1'
  checks+=1
 # Exhaustion, full reuse, alignment, mixed free and preserved interrupt state.
 m=Machine(new,base,0);pool=base+labels['pool'];metadata=base+labels['metadata']
 m.x.mem_write(pool+524288,b'CANARY!!')
 assert not m.alloc(524289) and not m.alloc(1,64);checks+=2
 for flag in [0,1]:
  m.interrupts=flag;p=m.alloc(524288);assert p==pool and m.interrupts==flag;assert not m.alloc(1)
  m.free(p);assert m.interrupts==flag and bytes(m.x.mem_read(metadata,256))==bytes(256);checks+=3
 rng=random.Random(817);live=[]
 for i in range(400):
  if live and rng.random()<0.45:
   p,n=live.pop(rng.randrange(len(live)));m.free(p)
  else:
   n=rng.randint(1,70000);p=m.alloc(n,rng.choice([4,8,16,32]))
   if p:
    assert p%32==0 and pool<=p and p+n<=pool+524288
    assert all(p+n<=q or q+k<=p for q,k in live),'Overlapping allocations'
    live.append((p,n))
 for p,n in live:m.free(p)
 assert bytes(m.x.mem_read(metadata,256))==bytes(256);assert bytes(m.x.mem_read(pool+524288,8))==b'CANARY!!';checks+=400
 # Native failure cleanup releases every reserve allocation on malformed URL.
 for i in range(50):
  assert m.create(b'invalid://test/leaderboard')==0
  assert m.message()=='Create: URL'
  assert bytes(m.x.mem_read(metadata,256))==bytes(256)
  checks+=1
 p=m.alloc(524288);assert m.create(b'http://play.mknitro.com/api/leaderboard/in-game?page=1')==0
 assert m.message()=='Create: memory';m.free(p);checks+=1
 # Startup guard reuses the initialized library, and propagates fresh-start failures.
 m=Machine(new,base,0);args=(base+0x5da24,base+0x5da54,17)
 assert m.call(base+labels['startup'],*args)==0 and not m.startup_calls
 for result in [0,0xffffffff]:
  m.w(m.context+0x7cc,0);m.startup_result=result
  assert m.call(base+labels['startup'],*args)==result and m.startup_calls[-1]==args
  checks+=1
 # Normal allocations/frees continue through the original EGG heap.
 m=Machine(new,base,1000000);p=m.alloc(32864);assert 0x81400000<=p<0x81700000;m.free(p)
 assert ('free',p) in m.events and bytes(m.x.mem_read(base+labels['metadata'],256))==bytes(256);checks+=1
print('PASS:',checks,'checks; native old failure/new success, native error cleanup, pool exhaustion/reuse, register and interrupt preservation, mixed heap routing, non-PAL unchanged.')
print('DOL SHA256:',hashlib.sha256(dol).hexdigest())
