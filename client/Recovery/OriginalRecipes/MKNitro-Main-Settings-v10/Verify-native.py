from pathlib import Path
import sys,struct,json
from unicorn import UC_HOOK_CODE
from unicorn.ppc_const import *
R=Path('/workspace/scratch/e221e6641538');sys.path.insert(0,str(R/'work/crash-repair'));from native_probe import Runtime
rt=Runtime();helper=0x81600000;page=0x817a0000;rt.uc.mem_write(helper,(R/'work/settings-oct4/options_hook.bin').read_bytes());rt.wr(0x805fd8e8,0x48000000|((helper-0x805fd8e8)&0x3fffffc));rt.wr(0x805fd854,0x39200001);events=[]
def capture(e,a,n,o):
 events.append([e.reg_read(UC_PPC_REG_3),e.reg_read(UC_PPC_REG_4)]);e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
rt.uc.hook_add(UC_HOOK_CODE,capture,begin=0x805bdaf0,end=0x805bdaf0)
for state in [0,1,2]:
 rt.wr(page+0x10,state);rt.wr(page+0xd64,0x1234);rt.uc.mem_write(page+0x92c,b'\0');rt.uc.reg_write(UC_PPC_REG_31,0xabcdef12);events.clear()
 rt.call(0x805fd8e8,page)
 assert bytes(rt.uc.mem_read(page+0x92c,1))==b'\1'
 assert rt.rd(page+0xd64)==0xffffffff
 assert rt.uc.reg_read(UC_PPC_REG_31)==0xabcdef12
 assert events==([[page+0x404,0]] if state==0 else [])
rt.uc.reg_write(UC_PPC_REG_9,0);rt.uc.emu_start(0x805fd854,0x805fd858,count=1);assert rt.uc.reg_read(UC_PPC_REG_9)==1
# Execute the existing compiled loader wrapper and verify inaccessible is forwarded
# unchanged to native PushButton::Load.
b=(R/'upload/Code(3).pul').read_bytes();size=struct.unpack_from('>I',b,28)[0];code=b[48:48+size];wrapper=0x81600000;rt.uc.mem_write(wrapper,code);events2=[]
# Apply the wrapper's Kamek relocations exactly as listed in the current binary.
name=wrapper+409964
rt.uc.mem_write(wrapper+74670,struct.pack('>H',((name+0x8000)>>16)&65535))
rt.uc.mem_write(wrapper+74674,struct.pack('>H',name&65535))
site=wrapper+74676;rt.wr(site,0x48000000|((0x805bd518-site)&0x3fffffc))
def capture_load(e,a,n,o):
 events2.append(e.reg_read(UC_PPC_REG_9));e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
rt.uc.hook_add(UC_HOOK_CODE,capture_load,begin=0x805bd518,end=0x805bd518)
rt.call(wrapper+74668,page+0x8ac,0,0,0,1,0,1)
assert events2==[1]
report={'activation_states_checked':[0,1,2],'channel_hidden':True,'inaccessible_argument_forwarded_by_existing_wrapper':True,'native_next_page_reset_preserved':True,'native_initial_selection_preserved':True,'stack_and_r31_preserved':True,'full_game_rendering_tested':False,'intercepted_boundaries':['SelectInitial','PushButton::Load']}
p=R/'deliverables/MKNitro-Main-Settings-v10/Native-checks.json';p.write_text(json.dumps(report,indent=2));print(report)
