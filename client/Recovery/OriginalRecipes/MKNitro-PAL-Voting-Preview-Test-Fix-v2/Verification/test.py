import sys,json,struct
from pathlib import Path
sys.path.insert(0,'work');from code_tools import *
from unicorn import *
from unicorn.ppc_const import *
b,c,cmds=parse('work/preview_crash/Code.pul')[0];meta=json.loads(Path('work/preview_crash/offsets.json').read_text());count=0
for base in [0x81000000,0x82000000]:
 for hud in range(4):
  for existing in [False,True]:
   uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);uc.mem_map(0x80000000,0x1000000);uc.mem_map(base,0x100000);uc.mem_map(0x83000000,0x10000)
   code=bytearray(c)
   for t,a,v,_,_ in cmds:
    if t==10 and a<len(code):
     target=v[0] if v[0]&0x80000000 else base+v[0];struct.pack_into('>I',code,a,(u(code,a)&0xfc000003)|((target-base-a)&0x3fffffc))
   uc.mem_write(base,bytes(code));calls=[]
   def w(a,v):uc.mem_write(a,struct.pack('>I',v))
   drivers=0x83002000;model=0x83003000;mgr=0x83001000
   w(0x809c1988,mgr);w(drivers+0x18+hud*12,model);w(model+0x10,0x83004000 if existing else 0)
   hooks={base+0x6b1c:'unlock',0x80830c64:'prepare',base+0x794c:'vote',meta['calc']:'calc'}
   for addr in hooks:uc.mem_write(addr,struct.pack('>I',0x4e800020))
   def hook(uc,addr,size,data):
    if addr not in hooks:return
    kind=hooks[addr];calls.append(kind)
    if kind=='unlock':assert uc.reg_read(UC_PPC_REG_3)==mgr
    if kind=='prepare':
     assert calls==['unlock','prepare'];assert uc.reg_read(UC_PPC_REG_3)==drivers;assert uc.reg_read(UC_PPC_REG_4)==hud;w(model+0x10,0x83004000)
   uc.hook_add(UC_HOOK_CODE,hook)
   def run(offset):
    uc.reg_write(UC_PPC_REG_1,0x8300f000);uc.reg_write(UC_PPC_REG_3,drivers);uc.reg_write(UC_PPC_REG_4,hud);uc.reg_write(UC_PPC_REG_LR,base+0xf0000);uc.emu_start(base+offset,base+0xf0000,count=100);assert uc.reg_read(UC_PPC_REG_1)==0x8300f000
   run(meta['prepare']);assert calls==([] if existing else ['unlock','prepare'])
   calls.clear();run(meta['prepare']);assert not calls
   run(meta['phase']);assert calls==['vote','calc']
   count+=1
print('PASS',count,'scenarios: missing/existing controller, all four HUD slots, repeat entry, deferred vote-before-CalcMain order, stack restoration, two code bases.')
Path('work/preview_crash/validation.txt').write_text(f'{count} native-helper scenarios passed with allocation/render calls mocked; existing controller reused and missing controller creation preceded by existing heap-unlock helper. Both MenuUpdate calls disabled; voting pose runs before CalcMain instead. No live Dolphin verification.\n')
