"""Execute the actual PPC predicate, license lookup and profile allocation."""
import random, struct, sys
from pathlib import Path
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN
from unicorn.ppc_const import *
sys.path.insert(0,str(Path(__file__).resolve().parent/'Verification'))
from code_tools import parse,u
root=Path(__file__).resolve().parent
old=parse(root/'Game/Code-previous.pul'); new=parse(root/'Game/Code.pul')
assert old[1:]==new[1:]
assert old[0][2]==new[0][2]
allowed={0x586b2,0x586b3,0x586ba,0x586bb}
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old[0][1],new[0][1])))
class Machine:
 def __init__(self,blocks,base):
  self.base=base; self.x=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
  self.x.mem_map(0x80000000,0x1800000)
  _,raw,cmd=blocks[0]; c=bytearray(raw)
  for t,a,v,_,_ in cmd:
   if a>=len(c):continue
   target=v[0] if v[0]>=0x80000000 else base+v[0]
   if t==1:struct.pack_into('>I',c,a,target)
   elif t==4:struct.pack_into('>H',c,a,target&65535)
   elif t==6:struct.pack_into('>H',c,a,((target+32768)>>16)&65535)
   elif t==10:struct.pack_into('>I',c,a,(u(c,a)&0xfc000003)|((target-base-a)&0x3fffffc))
  self.x.mem_write(base,bytes(c));self.mgr=0x81300000
  self.w(0x809bd748,self.mgr)
 def w(self,a,v):self.x.mem_write(a,struct.pack('>I',v&0xffffffff))
 def word(self,a):return u(self.x.mem_read(a,4),0)
 def call(self,off,*args):
  self.x.reg_write(UC_PPC_REG_1,0x817ff000);self.x.reg_write(UC_PPC_REG_LR,0x81700000)
  for r in range(14,32):self.x.reg_write(UC_PPC_REG_0+r,0x70000000+r)
  for i,v in enumerate(args):self.x.reg_write(UC_PPC_REG_3+i,v&0xffffffff)
  self.x.emu_start(self.base+off,0x81700000,count=10000)
  assert self.x.reg_read(UC_PPC_REG_PC)==0x81700000
  assert all(self.x.reg_read(UC_PPC_REG_0+r)==0x70000000+r for r in range(14,32))
  return self.x.reg_read(UC_PPC_REG_3)
checks=0
rng=random.Random(6124)
ids=[0,1,603318948,999999998,999999999,1000000000,1000000002,1000000149,1999999998,1999999999,2000000000,2147483647,0xffffffff]
ids += [rng.randrange(0,2**32) for _ in range(300)]
for base in (0x803992e0,0x81000000):
 a,b=Machine(old,base),Machine(new,base)
 for pid in ids:
  assert a.call(0x586b0,pid)==int(0<pid<1000000000)
  assert b.call(0x586b0,pid)==int(0<pid<2000000000)
  checks+=2
 for license_id in range(4):
  pid=1000000002+license_id
  for m in (a,b):m.w(m.mgr+0x900c+license_id*0x93f0,pid)
  assert a.call(0x588cc,license_id)==0
  assert b.call(0x588cc,license_id)==pid
  assert a.call(0x58858,pid,1)==0
  entry=b.call(0x58858,pid,1)
  assert entry!=0 and b.word(entry)==pid
  assert b.call(0x58858,pid,0)==entry
  checks+=5
 for m in (a,b):assert m.call(0x588cc,4)==0;checks+=1
print(f'{checks} actual PowerPC checks passed at two load addresses. No live race test performed.')
