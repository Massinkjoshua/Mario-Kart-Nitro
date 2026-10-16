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
allowed=set(range(0x49e44,0x49e48))|set(range(0x49e54,0x49e58))
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old[0][1],new[0][1])))
changed={0x49e04,0x49e1c,0x49e34}
assert [(t,o,v) for t,o,v,_,_ in old[0][2] if o not in changed]==[(t,o,v) for t,o,v,_,_ in new[0][2][:len(old[0][2])] if o not in changed]
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
  return bytes(self.x.mem_read(p,80)).decode('utf-16-be').split('\0')[0]


import base64
fixtures=json.loads((Path(__file__).parent/'miis.json').read_text())
class MiiMachine(Machine):
 def hook(self,x,a,size,data):
  if a==0x805fa610:
   self.events.append(('load',self.r(3),self.r(4),bytes(x.mem_read(self.r(5),76))));self.ret()
  elif a==0x8063e3dc:
   self.events.append(('pane',*[self.r(i) for i in range(3,8)]));self.ret()
  elif a==self.base+0x48888:
   self.events.append(('visible',self.r(3),self.r(4),self.r(5)));self.ret()
  else:super().hook(x,a,size,data)
checks=0
for base in [0x803992e0,0x81000000]:
 m=MiiMachine(new,base,1000000);source=0x81200000;dest=0x81230000
 raw=json.dumps(fixtures).encode();m.x.mem_write(source,raw+b'\0')
 assert m.call(base+0x4a2e0,source,dest,50)==2;checks+=1
 for i,entry in enumerate(fixtures['players']):
  a=dest+i*0x90;expected=base64.b64decode(entry['miiData'])
  assert bytes(m.x.mem_read(a+0x38,76))==expected
  assert bytes(m.x.mem_read(a,48)).decode('utf-16-be').split('\0')[0]==entry['name']
  assert m.word(a+0x30)==entry['vr']
  assert m.call(0x800cb8b0,a+0x38)==1
  m.call(base+labels['load_mii'],0x81280000,i,a+0x38)
  assert m.events[-1]==('load',0x81280000,i,expected)
  m.call(base+labels['set_mii'],111,222,333,i,2)
  assert m.events[-1]==('pane',111,222,333,i,2)
  m.call(base+labels['visible'],111,222,1)
  assert m.events[-1]==('visible',111,222,1);checks+=7
 # Missing Mii and damaged checksum: never invoke native loading/pane binding.
 for raw in [bytes(76),expected[:-1]+bytes([expected[-1]^1])]:
  m.x.mem_write(source,raw);m.events.clear()
  m.call(base+labels['load_mii'],0x81280000,0,source)
  m.call(base+labels['set_mii'],111,222,333,0,2)
  assert not m.events
  m.call(base+labels['visible'],111,222,1)
  assert m.events==[('visible',111,222,0)];checks+=2
 # Next valid row restores visibility (page reuse).
 m.x.mem_write(source,expected);m.events.clear()
 m.call(base+labels['load_mii'],0x81280000,0,source)
 m.call(base+labels['visible'],111,222,1)
 assert m.events[-1]==('visible',111,222,1);checks+=1
print('PASS:',checks,'checks: actual game JSON/base64 parser, native RFL checksum/face validation, distinct player bytes and names, absent/corrupt Mii suppression, visibility reuse, registers and exact preservation of prior memory fix.')
print('Mii rendering and UI calls intercepted; a live Dolphin test remains necessary.')
