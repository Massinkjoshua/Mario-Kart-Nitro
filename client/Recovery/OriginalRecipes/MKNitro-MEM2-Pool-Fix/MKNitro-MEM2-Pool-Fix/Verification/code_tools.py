import struct
from pathlib import Path
from capstone import *
u=lambda b,p:struct.unpack_from('>I',b,p)[0]
def parse(path):
 d=Path(path).read_bytes();lens=struct.unpack_from('>4I',d);blocks=[];p=16
 for n in lens:
  b=d[p:p+n];p+=n
  if not n:blocks.append(None);continue
  size=u(b,12);cmds=[];c=32+size
  while c<len(b):
   start=c;w=u(b,c);c+=4;t=w>>24;a=w&0xffffff
   if a==0xfffffe:a=u(b,c);c+=4
   count=2 if t in (35,36,37,38) else 1;vs=[u(b,c+4*j) for j in range(count)];c+=4*count
   cmds.append((t,a,vs,start,c))
  blocks.append((b,b[32:32+size],cmds))
 return blocks
cs=Cs(CS_ARCH_PPC,CS_MODE_BIG_ENDIAN|CS_MODE_32)
def dis(code,addr,size):
 for x in cs.disasm(code[addr:addr+size],addr):print(f'{x.address:08x} {x.mnemonic:10} {x.op_str}')
if __name__=='__main__':
 b,c,cmds=parse('upload/Code(5).pul')[0]
 for t,a,vs,_,_ in cmds:
  if 0x8081d000<a<0x80833000 or 0x8051b000<a<0x8051b700 or 0x80553b00<a<0x80555300:print(t,hex(a),[hex(x) for x in vs])
