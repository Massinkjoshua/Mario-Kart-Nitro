import sys,struct
from pathlib import Path
sys.path.insert(0,'work');from code_tools import parse,u
from unicorn import *
from unicorn.ppc_const import *
blocks=parse('work/preview_patch/Code.pul');b,code,cmds=blocks[0]
prior=parse('work/vr_patch/Code.pul');assert blocks[1:]==prior[1:]
assert [x[:3] for x in cmds]==[x[:3] for x in prior[0][2]]
results=[]
for base in [0x81000000,0x82000000]:
 for state in [0,1,2,3,4]:
  for choosing in [False,True]:
   for kart in [0,18,22,34]:
    uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);uc.mem_map(0x80000000,0x1000000);uc.mem_map(base,0x100000);uc.mem_map(0x83000000,0x10000)
    patched=bytearray(code)
    for t,a,v,_,_ in cmds:
     if t==10 and a<len(code):
      target=v[0] if v[0]&0x80000000 else base+v[0]
      struct.pack_into('>I',patched,a,(u(patched,a)&0xfc000003)|((target-base-a)&0x3fffffc))
    uc.mem_write(base,bytes(patched))
    def w(a,v):uc.mem_write(a,struct.pack('>I',v))
    mgr=0x83001000;drivers=0x83002000;model=0x83003000;sectionMgr=0x83004000;section=0x83005000;renderer=0x83006000;page=0x83007000
    w(0x809c1988,mgr);w(mgr+0x14,drivers);uc.mem_write(mgr+0x20,b'\1\1');w(drivers+0x18,model);w(model+8,state);w(model+0x14,99);w(model+0x1c,0xdeadbeef)
    w(0x809c1e38,sectionMgr);w(sectionMgr,section);w(section+0x204,renderer);w(renderer+0x58,kart);w(section+0x1b4,page);w(page+0x914,0x83009000)
    native={a:v[0] for t,a,v,_,_ in cmds if t==10}
    calls=[]
    handlers={base+0xa094:'select',base+0x6b1c:'unlock',base+0x704c:'reload',native[0x73d4]:'setchar',native[0x7438]:'prepare',native[0x748c]:'switch',base+0x7228:'pose',native[0x7420]:'request'}
    for addr in handlers:uc.mem_write(addr,struct.pack('>I',0x4e800020))
    def hook(uc,addr,size,data):
     label=handlers.get(addr)
     if label is None:return
     calls.append(label)
     if label=='select':uc.reg_write(UC_PPC_REG_3,int(choosing))
     if label=='reload':w(model+8,1);uc.reg_write(UC_PPC_REG_3,1)
     if label=='prepare':w(model+0x10,0x8300a000)
     if label=='switch':
      selected=uc.reg_read(UC_PPC_REG_5);assert selected==state,(selected,state);w(model+8,selected)
    uc.hook_add(UC_HOOK_CODE,hook)
    stop=base+0xf0000;stack=0x8300f000;uc.reg_write(UC_PPC_REG_1,stack);uc.reg_write(UC_PPC_REG_LR,stop);uc.reg_write(UC_PPC_REG_3,0);uc.reg_write(UC_PPC_REG_4,3)
    for reg in range(23,32):uc.reg_write(UC_PPC_REG_0+reg,0x12340000+reg)
    uc.emu_start(base+0x7300,stop,count=500)
    expect_riding=not choosing and state in (2,3)
    assert ('switch' in calls)==expect_riding,(state,choosing,calls)
    assert ('request' in calls)==choosing
    assert u(bytes(uc.mem_read(model+0x14,4)),0)==(kart if expect_riding else 99)
    assert u(bytes(uc.mem_read(model+0x1c,4)),0)==0xdeadbeef
    assert uc.reg_read(UC_PPC_REG_1)==stack
    for reg in range(23,32):assert uc.reg_read(UC_PPC_REG_0+reg)==0x12340000+reg
    results.append((state,choosing,kart))
print('PASS',len(results),'reload execution cases: states 0–4, character select, karts/bikes, two code bases; correct field and register preservation.')
Path('work/preview_patch/validation.txt').write_text(f'{len(results)} PowerPC reload-control-flow cases passed. Native model loading/rendering calls mocked; final visual result not tested in Dolphin. Earlier VR helper bytes and all patch commands retained. US/J code blocks unchanged.\n')
