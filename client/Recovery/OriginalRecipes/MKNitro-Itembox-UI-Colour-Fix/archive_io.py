from pathlib import Path
import struct
U=lambda b,p:struct.unpack_from('>I',b,p)[0]
def dec(d):
 if d[:4]!=b'Yaz0':return d
 size=U(d,4);out=bytearray();p=16
 while len(out)<size:
  c=d[p];p+=1
  for i in range(8):
   if len(out)>=size:break
   if c&(128>>i):out.append(d[p]);p+=1
   else:
    a,b=d[p:p+2];p+=2;dist=((a&15)<<8|b)+1;n=a>>4
    if n==0:n=d[p]+18;p+=1
    else:n+=2
    for _ in range(n):out.append(out[-dist])
 return bytes(out)
def files(d):
 d=dec(d);r=U(d,4);cnt=U(d,r+8);st=r+12*cnt;stack=[(cnt,'')];out={}
 for i in range(1,cnt):
  while i>=stack[-1][0]:stack.pop()
  a,b,c=struct.unpack_from('>III',d,r+12*i);p=st+(a&0xffffff);name=d[p:d.index(0,p)].decode();path=stack[-1][1]+'/'+name
  if a>>24:stack.append((c,path))
  else:out[Path(path.lstrip('/')).as_posix()]=d[b:b+c]
 return out
 defunused=0
def unpack(data,dest):
 for n,b in files(data).items():
  p=Path(dest)/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def pack(folder):
 folder=Path(folder);e=[]
 def walk(p,parent):
  i=len(e);e.append([1,p.name,parent,0,p])
  for sub in sorted(p.iterdir(),key=lambda q:q.name):
   if sub.is_dir():walk(sub,i)
   else:e.append([0,sub.name,0,sub.stat().st_size,sub])
  e[i][3]=len(e)
 walk(folder,0);e[0][1]='';strings=bytearray();offs=[]
 for x in e:offs.append(len(strings));strings+=x[1].encode()+b'\0'
 hs=len(e)*12+len(strings);ds=(32+hs+31)&~31;b=bytearray(ds);struct.pack_into('>4I',b,0,0x55aa382d,32,hs,ds);b[32+len(e)*12:32+hs]=strings
 for i,x in enumerate(e):
  if x[0]:o=x[2]
  else:o=len(b);b+=x[4].read_bytes();b+=bytes(-len(b)%32)
  struct.pack_into('>3I',b,32+12*i,(x[0]<<24)|offs[i],o,x[3])
 return bytes(b)
def yaz(b):return b'Yaz0'+struct.pack('>I',len(b))+bytes(8)+b''.join(b'\xff'+b[i:i+8] for i in range(0,len(b),8))
def sections(b):
 p=16
 while p<len(b):
  n=U(b,p+4);yield bytearray(b[p:p+n]);p+=n
 assert p==len(b)
def label(s):return bytes(s[12:36]).split(b'\0')[0].decode()
