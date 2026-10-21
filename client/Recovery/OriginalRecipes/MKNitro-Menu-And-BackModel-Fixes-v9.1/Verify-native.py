from pathlib import Path
import struct,sys,ast,json
R=Path('/workspace/scratch/e221e6641538');sys.path.insert(0,str(R/'work/crash-repair'))
from native_probe import Runtime
from unicorn import UC_HOOK_CODE
from unicorn.ppc_const import *
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
rt=Runtime();patches=json.loads((R/'deliverables/MKNitro-License-And-Item-Fixes-v9/Verification.json').read_text())['native_patches'] if (R/'deliverables/MKNitro-License-And-Item-Fixes-v9/Verification.json').exists() else []
assert len(patches)==5
for p in patches:rt.uc.mem_write(int(p['address'],16),bytes(ks.asm(p['new'])[0]))
page=0x817a0000;events=[]
def capture(e,a,n,o):
 events.append([hex(a),hex(e.reg_read(UC_PPC_REG_3)),e.reg_read(UC_PPC_REG_4)]);e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
for addr in [0x805bdaf0,0x807e9a38]:rt.uc.hook_add(UC_HOOK_CODE,capture,begin=addr,end=addr)
rt.call(0x805edbf8,page)
assert events==[['0x805bdaf0',hex(page+0x81c),0],['0x807e9a38',hex(page+0xf28),0x84a]],events
assert rt.rd(page+0x1134)==0xffffffff
# Check actual patched instructions suppress the additive RGB/alpha source.
for site,reg in [(0x807ef204,UC_PPC_REG_6),(0x807ef0a4,UC_PPC_REG_0)]:
 rt.uc.reg_write(UC_PPC_REG_27,255);rt.uc.reg_write(UC_PPC_REG_0,255);rt.uc.emu_start(site,site+4,count=1);assert rt.uc.reg_read(reg)==0
out={'native_onactivate':'passed','initial_selection':'Change Mii','initial_help_id':'0x84a','additive_flash_registers_zeroed':True,'boundaries':'SelectInitial and help-text rendering intercepted; full game rendering not run'}
(R/'deliverables/MKNitro-License-And-Item-Fixes-v9/Native-checks.json').write_text(json.dumps(out,indent=2));print(out)
