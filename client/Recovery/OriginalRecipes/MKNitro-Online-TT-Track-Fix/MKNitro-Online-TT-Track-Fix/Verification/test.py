"""Execute actual patched PPC cup selection and restriction functions in Unicorn.
Native online networking/rendering is not simulated. No game files modified.
"""
import json,random,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_PPC,UC_MODE_32,UC_MODE_BIG_ENDIAN
from unicorn.ppc_const import *
from code_tools import parse,u
root=Path(__file__).resolve().parents[1]
old=parse(root/'Game/Code-previous.pul');new=parse(root/'Game/Code.pul')
meta=json.loads((root/'Game/Code.json').read_text())
assert old[1:]==new[1:]
assert [(t,a,v) for t,a,v,_,_ in old[0][2]]==[(t,a,v) for t,a,v,_,_ in new[0][2]]
allowed={p+i for p in (0x2f1c,0x354d0,0x34108) for i in range(4)}
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old[0][1],new[0][1])))
checks=0
class Machine:
 def __init__(self,blocks,base):
  self.base=base;self.x=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
  self.x.mem_map(0x80000000,0x1800000)
  _,raw,cmd=blocks[0];c=bytearray(raw)
  for t,a,v,_,_ in cmd:
   if a>=len(c):continue
   target=v[0] if v[0]>=0x80000000 else base+v[0]
   if t==1:struct.pack_into('>I',c,a,target)
   elif t==4:struct.pack_into('>H',c,a,target&65535)
   elif t==6:struct.pack_into('>H',c,a,((target+32768)>>16)&65535)
   elif t==10:struct.pack_into('>I',c,a,(u(c,a)&0xfc000003)|((target-base-a)&0x3fffffc))
  self.x.mem_write(base,bytes(c))
  self.system=0x81200000;self.controller=0x81210000;self.race=0x81220000;self.cups=0x81230000
  syms={a:v[0] for t,a,v,_,_ in cmd if t==4}
  self.w(base+syms[0x3547a],self.system)
  self.w(0x809c20d8,self.controller);self.w(0x809bd728,self.race)
 def w(self,a,v):self.x.mem_write(a,struct.pack('>I',v&0xffffffff))
 def word(self,a):return u(self.x.mem_read(a,4),0)
 def call(self,a,*args):
  self.x.reg_write(UC_PPC_REG_1,0x817ff000);self.x.reg_write(UC_PPC_REG_LR,0x81700000)
  for r in range(14,32):self.x.reg_write(UC_PPC_REG_0+r,0x70000000+r)
  for i,v in enumerate(args):self.x.reg_write(UC_PPC_REG_3+i,v&0xffffffff)
  self.x.emu_start(self.base+a,0x81700000,count=100000)
  assert self.x.reg_read(UC_PPC_REG_PC)==0x81700000
  assert all(self.x.reg_read(UC_PPC_REG_0+r)==0x70000000+r for r in range(14,32))
  return self.x.reg_read(UC_PPC_REG_3)
 def setup(self,region,room=2,mode=8,active=1):
  self.x.mem_write(self.cups,bytes(0x100))
  self.w(self.system+0x9c,region);self.w(self.system+0x60,1|(1<<8));self.w(self.system+0x64,0)
  self.w(self.controller+0x28,active);self.w(self.controller+0xe8,room)
  self.w(self.race+0x1760,mode)
  self.w(self.cups,0x40);self.w(self.cups+0x20,24);self.w(self.cups+0x24,24)
  self.w(self.cups+0x40,16);self.w(self.cups+0x44,8)

for base in (0x803992e0,0x81000000):
 a,b=Machine(old,base),Machine(new,base)
 # Actual ToggleCTs restores all 24 Nitro cups in OTT; vanilla mode stays vanilla.
 for region in (0xa,0xb,0xc,0xd,0x14,0x15):
  for room in (0,1,2,5,6,7,8):
   for active in (0,1):
    a.setup(region,room,active=active);b.setup(region,room,active=active)
    a.call(0x353ec,a.cups,1);b.call(0x353ec,b.cups,1)
    if region==0xb and room in (2,8) and active:
     assert a.word(a.cups+0x24)==0
     assert b.word(b.cups+0x24)==24 and b.x.mem_read(b.cups+0x1b,1)==b'\0'
    else:assert a.x.mem_read(a.cups,0x100)==b.x.mem_read(b.cups,0x100)
    # Physics predicate has exactly its previous meaning.
    assert a.call(0x1720,a.system)==b.call(0x1720,b.system)
    checks+=2
 # Full cup navigation in OTT now matches the existing Nitro VS behavior.
 for room in (2,8):
  b.setup(0xb,room)
  for cup in range(0x40,0x58):
   for direction in (-2,-1,0,1,2):
    a.setup(0xa,room)
    expected=a.call(0x35994,a.cups,cup,direction)
    actual=b.call(0x35994,b.cups,cup,direction)
    assert actual==expected and 0x40<=actual<0x58,(hex(cup),direction,hex(actual),hex(expected))
    checks+=1
 # Only Nitro VS/OTT region helper accepted; all earlier room/activity/mode gates remain.
 for region in (0,9,10,11,12,13,20,21,255):
  for mode in (1,8):
   b.setup(region,mode=mode)
   assert b.call(0x340a0,mode,b.controller)==int(mode==8 and region in (10,11))
   checks+=1
 # OTT context clears vanilla-only selection, preserves every other restriction.
 rng=random.Random(6124)
 for _ in range(100):
  c1,c2=rng.getrandbits(32),rng.getrandbits(32)
  for m in (a,b):m.w(m.system+0x60,c1);m.w(m.system+0x64,c2)
  a.call(0x16a0,a.system,0);b.call(meta['labels']['ott_rules'],b.system,0)
  assert b.word(b.system+0x60)==a.word(a.system+0x60)&~(1<<18)
  assert b.word(b.system+0x64)==a.word(a.system+0x64)
  checks+=1
print(f'PASS: {checks} PPC checks; OTT cup restoration/navigation, existing mode behavior, physics restrictions and non-PAL/leaderboard byte preservation.')
