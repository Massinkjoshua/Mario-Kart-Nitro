from pathlib import Path
import sys,struct,json,ast
R=Path('/workspace/scratch/e221e6641538');O=R/'deliverables/MKNitro-License-Visibility-Fix-v9.2'
sys.path.insert(0,str(R/'work/crash-repair'));from native_probe import Runtime
from unicorn import UC_HOOK_CODE
from unicorn.ppc_const import *
info=json.loads((O/'Verification.json').read_text());rt=Runtime();page=0x817a0000;hook=0x81600000;miip=0x817b0000;framep=miip+0x1000
rt.uc.mem_write(hook,(R/'work/license-v9_2/hook.bin').read_bytes());rt.wr(0x805edc3c,0x48000001|((hook-0x805edc3c)&0x3fffffc))
# Apply the existing v9 selection/help changes too.
rt.wr(0x805edc24,0x3863081c);rt.wr(0x805edc30,0x3880084a)
events=[];found={'mii':miip,'nitro_mii_frame':framep}
def boundary(e,a,n,o):
 if a==0x805e8368:
  assert e.reg_read(UC_PPC_REG_3)==page+0x454+0xa8
  name=bytes(e.mem_read(e.reg_read(UC_PPC_REG_4),16)).split(b'\0')[0].decode();events.append(name);e.reg_write(UC_PPC_REG_3,found.get(name,0))
 else:events.append(hex(a))
 e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
for a in [0x805e8368,0x805bdaf0,0x807e9a38]:rt.uc.hook_add(UC_HOOK_CODE,boundary,begin=a,end=a)
cases=[]
for state in [0,1]:
 for mode in ['both','missing_frame','missing_both','no_root']:
  found={'mii':miip,'nitro_mii_frame':framep} if mode=='both' else {'mii':miip} if mode=='missing_frame' else {}
  rt.wr(page+0x10,state);rt.wr(page+0x510,0 if mode=='no_root' else 0x817b2000)
  rt.uc.mem_write(page+0x648,b'\0');rt.uc.mem_write(miip,bytes(256));rt.uc.mem_write(framep,bytes(256));events.clear()
  rt.uc.reg_write(UC_PPC_REG_31,0x12345678)
  rt.call(0x805edbf8,page)
  assert rt.uc.reg_read(UC_PPC_REG_31)==0x12345678
  assert rt.uc.mem_read(page+0x648,1)==b'\1'
  for name,addr in found.items():assert bytes(rt.uc.mem_read(addr+0x2c,40))==struct.pack('>10f',*info['pane_reference'][name])
  if mode=='no_root':assert not any(e in ['mii','nitro_mii_frame'] for e in events)
  if state==0:assert events[:2]==['0x805bdaf0','0x807e9a38']
  cases.append({'state':state,'panes':mode,'result':'pass'})
(O/'Native-checks.json').write_text(json.dumps({'cases':cases,'checks':['Records control hidden','Mii/frame exact reference transform','missing pane/root guards','native activation return and r31 preservation'],'intercepted_boundaries':['pane lookup','initial selection','help rendering'],'full_game_rendering_tested':False},indent=2))
print('8 native activation cases passed')
