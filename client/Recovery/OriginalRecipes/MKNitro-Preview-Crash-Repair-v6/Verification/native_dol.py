from pathlib import Path
import struct
from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
ROOT=Path('/workspace/scratch/e221e6641538')
data=(ROOT/'upload/main(2).dol').read_bytes()
u32=lambda b,p:struct.unpack_from('>I',b,p)[0]
sections=[(u32(data,i*4),u32(data,0x48+i*4),u32(data,0x90+i*4)) for i in range(18) if u32(data,0x90+i*4)]
def read(a,n):
 for off,addr,size in sections:
  if addr<=a and a+n<=addr+size:return data[off+a-addr:off+a-addr+n]
 raise ValueError(hex(a))
def dump(a,b,name):
 dis=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN);dis.skipdata=True
 out='\n'.join(f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in dis.disasm(read(a,b-a),a))
 (ROOT/'work/crash-repair'/f'{name}.asm').write_text(out)
 return out
if __name__=='__main__':
 import sys
 print(dump(int(sys.argv[1],16),int(sys.argv[2],16),sys.argv[3]))
