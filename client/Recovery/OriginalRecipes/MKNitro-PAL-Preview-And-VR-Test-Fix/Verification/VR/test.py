import sys,struct,json
from pathlib import Path
sys.path.insert(0,'work')
from code_tools import parse
from unicorn import *
from unicorn.ppc_const import *
old=parse('upload/Code(5).pul');new=parse('work/vr_patch/Code.pul');manifest=json.loads(Path('work/vr_patch/manifest.json').read_text())
assert all(a==b for a,b in zip(old[1:],new[1:]))
assert new[0][1][:len(old[0][1])]==old[0][1]
assert [x[:3] for x in new[0][2][:-2]]==[x[:3] for x in old[0][2]]
passed=0
for base in [0x81000000,0x82000000]:
 for h in manifest['helpers']:
  for license in [-1,0,1,2,3,4]:
   for rating in [1.,50.,50.37,9999.99,10000.]:
    uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    uc.mem_map(base,0x100000);uc.mem_write(base,new[0][1]);uc.mem_map(0x809b0000,0x20000);uc.mem_map(0x83000000,0x10000)
    save=0x83001000;handler=0x83002000;stop=base+0xf0000;stack=0x8300f000
    uc.mem_write(0x809bd748,struct.pack('>I',save));uc.mem_write(save+0x36,struct.pack('>h',license));uc.mem_write(handler,b'\xa5'*0x100)
    # Replace only getter with a test double returning f1. Wrapper conversion/store execute unchanged.
    stub=[0x3c608300,0xc0233000,0x4e800020]
    uc.mem_write(base+h['getter'],struct.pack('>3I',*stub));uc.mem_write(0x83003000,struct.pack('>f',rating))
    uc.reg_write(UC_PPC_REG_MSR,0x2000);uc.reg_write(UC_PPC_REG_1,stack);uc.reg_write(UC_PPC_REG_3,handler);uc.reg_write(UC_PPC_REG_31,0x12345678);uc.reg_write(UC_PPC_REG_LR,stop)
    uc.emu_start(base+h['offset'],stop,count=100)
    actual=bytes(uc.mem_read(handler,0x100));expected=bytearray(b'\xa5'*0x100)
    if 0<=license<=3:struct.pack_into('>H',expected,h['field'],int(rating))
    assert actual==expected,(h,license,rating,actual.hex())
    assert uc.reg_read(UC_PPC_REG_1)==stack
    assert uc.reg_read(UC_PPC_REG_31)==0x12345678
    assert uc.reg_read(UC_PPC_REG_LR)==stop
    passed+=1
print(f'PASS: {passed} PowerPC wrapper execution cases; packet bytes, bounds, registers, two load bases, PAL-only changes.')
Path('work/vr_patch/validation.txt').write_text(f'{passed} PowerPC wrapper execution cases passed. Getter was stubbed; conversion and packet writes executed. Original code and patch commands retained; US/J blocks byte-identical. Not tested in Dolphin or a live online room.\n')
