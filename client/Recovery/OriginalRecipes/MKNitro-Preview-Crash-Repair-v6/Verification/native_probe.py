from pathlib import Path
import sys,struct,json
from unicorn import Uc,UC_ARCH_PPC,UC_MODE_PPC32,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.ppc_const import *
import native_dol as dol
sys.path.insert(0,str(dol.ROOT/'work/v5'))
import native_rel as rel
ROOT=dol.ROOT
u32=lambda b,p=0:struct.unpack_from('>I',b,p)[0]
p32=lambda x:struct.pack('>I',x)
class Runtime:
 def __init__(self):
  self.uc=Uc(UC_ARCH_PPC,UC_MODE_PPC32|UC_MODE_BIG_ENDIAN)
  self.uc.mem_map(0x80000000,0x1800000)
  self.uc.mem_map(0x90000000,0x4000000)
  for off,addr,size in dol.sections:self.uc.mem_write(addr,dol.data[off:off+size])
  self.uc.mem_write(rel.REL_BASE,bytes(rel.image[:0x3cd0f4]))
  self.uc.reg_write(UC_PPC_REG_2,0x8038efa0);self.uc.reg_write(UC_PPC_REG_13,0x8038cc00)
  self.uc.reg_write(UC_PPC_REG_MSR,0x2000)
  self.sp=0x817e0000;self.stop=0x817ff000
  self.wr(0x800000e4,0x817c0000)
  # Unicorn lacks Gekko paired-single math. These two math leaf routines
  # have no allocation or model-lifetime side effects.
  def math_leaf(e,a,n,o):
   dst=e.reg_read(UC_PPC_REG_3)
   if a==0x80199d04:
    e.mem_write(dst,struct.pack('>12f',1,0,0,0,0,1,0,0,0,0,1,0))
   elif a==0x80199d30:
    e.mem_write(e.reg_read(UC_PPC_REG_4),bytes(e.mem_read(dst,48)))
   else:return
   e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
  self.uc.hook_add(UC_HOOK_CODE,math_leaf,begin=0x80199d04,end=0x80199d30)
 def wr(self,a,v):self.uc.mem_write(a,p32(v))
 def rd(self,a):return u32(bytes(self.uc.mem_read(a,4)))
 def call(self,addr,*args):
  for i,arg in enumerate(args):self.uc.reg_write(UC_PPC_REG_3+i,arg&0xffffffff)
  self.uc.reg_write(UC_PPC_REG_1,self.sp);self.uc.reg_write(UC_PPC_REG_LR,self.stop)
  try:self.uc.emu_start(addr,self.stop,count=3000000)
  except Exception as e:raise RuntimeError(f'{e} PC={self.uc.reg_read(UC_PPC_REG_PC):08x} LR={self.uc.reg_read(UC_PPC_REG_LR):08x}')
  assert self.uc.reg_read(UC_PPC_REG_PC)==self.stop,hex(self.uc.reg_read(UC_PPC_REG_PC))
  assert self.uc.reg_read(UC_PPC_REG_1)==self.sp
  return self.uc.reg_read(UC_PPC_REG_3)
if __name__=='__main__':
 rt=Runtime();res=0x90000000;sizeptr=0x817d0000;handle=0x817d0010
 summary=[]
 for f in sorted((ROOT/'work/crash-investigation/fk-7-allkart').glob('*.brres')):
  b=f.read_bytes();p=b.find(b'MDL0')
  if p<0:continue
  rt.uc.mem_write(res,b);rt.wr(handle,res+p)
  # Derive options by executing LoadWithAnm up to native Init.
  obj=0x817d0100;file=0x817d0200;name=0x817d0300
  rt.wr(file,res);rt.uc.mem_write(name,b'menu\0')
  def stop_init(e,a,s,o):
   if a==0x8055baa0:
    rt.options=e.reg_read(UC_PPC_REG_5);e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
  hook=rt.uc.hook_add(UC_HOOK_CODE,stop_init,begin=0x8055baa0,end=0x8055baa0)
  rt.call(0x8055c0e8,obj,name,file,0);rt.uc.hook_del(hook)
  assert rt.rd(obj+0xc)==res+p
  rt.wr(sizeptr,0);ret=rt.call(0x80073470,0,sizeptr,handle,rt.options,1)
  assert ret==0
  row={'file':f.name,'buffer_options':rt.options,'ScnMdl_bytes':rt.rd(sizeptr)};summary.append(row);print(row)
 print('scene_models_minimum',2*sum(r['ScnMdl_bytes'] for r in summary))
 (ROOT/'work/crash-repair/native-model-sizes.json').write_text(json.dumps(summary,indent=2))
 print('createheap',hex(rt.call(0x80198ca8,0x91000000,0xe1000,0)))
 print('alloc archive',hex(rt.call(0x80198d88,0x91000000,897952,32)))
 print('remaining',rt.call(0x80199180,0x91000000,32))
