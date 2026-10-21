from pathlib import Path
import struct
from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
ROOT=Path('/workspace/scratch/e221e6641538')
REL_BASE=0x805102e0
BSS_BASE=0x809bd6e0
original=(ROOT/'upload/StaticR(1).rel').read_bytes()
image=bytearray(original)
U32=lambda p:struct.unpack_from('>I',original,p)[0]
sections=[struct.unpack_from('>II',original,U32(0x10)+8*i) for i in range(U32(0xc))]
bases=[(REL_BASE+(off&~1)) if off else (BSS_BASE if i==6 else 0) for i,(off,size) in enumerate(sections)]
for imp in range(U32(0x28),U32(0x28)+U32(0x2c),8):
 module,p=struct.unpack_from('>II',original,imp);section=0;offset=0
 while True:
  delta,typ,target_section,addend=struct.unpack_from('>HBBI',original,p);p+=8;offset+=delta
  if typ==203:break
  if typ==202:section=target_section;offset=0;continue
  if typ in (0,201,204):continue
  where=(sections[section][0]&~1)+offset
  addr=bases[section]+offset
  target=addend+(bases[target_section] if module==1 else 0)
  if typ==1:struct.pack_into('>I',image,where,target)
  elif typ==4:struct.pack_into('>H',image,where,target&65535)
  elif typ==5:struct.pack_into('>H',image,where,(target>>16)&65535)
  elif typ==6:struct.pack_into('>H',image,where,((target+0x8000)>>16)&65535)
  elif typ==10:
   word=struct.unpack_from('>I',image,where)[0]
   struct.pack_into('>I',image,where,(word&0xfc000003)|((target-addr)&0x03fffffc))
  else:raise ValueError((module,typ,hex(addr)))
dis=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN)
def read(addr,size):return bytes(image[addr-REL_BASE:addr-REL_BASE+size])
def dump(start,end,name):
 out='\n'.join(f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in dis.disasm(read(start,end-start),start))
 (ROOT/'work/v5'/f'{name}.asm').write_text(out)
 return out
if __name__=='__main__':
 import sys
 print(dump(int(sys.argv[1],16),int(sys.argv[2],16),sys.argv[3]))
