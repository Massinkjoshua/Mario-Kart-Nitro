#!/usr/bin/env python3
"""Synthetic response fixtures against released and source-built PAL PPC; GPLv3.
Runs the compiled parser and its internal JSON/base64 helpers. Native libc only
is intercepted. Does not test NHTTP, the UI, real Miis or a game boot.
"""
import base64,hashlib,json,re
from recovered_remaining_ppc import Controlled,ROOT

RELEASE_SHA='58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364'
STRIDE=0x90

def cbytes(h,p):
 out=bytearray()
 for i in range(65536):
  b=h.data(p+i,1)[0]
  if not b:return bytes(out)
  out.append(b)
 raise AssertionError('Unterminated fixture string')

def install_libc(h):
 def memset():
  dst,value,n=h.registers(3);assert n<65536
  h.cpu.mem_write(dst,bytes([value&255])*n);h.result(dst)
 def memcpy():
  dst,src,n=h.registers(3);assert n<65536
  h.cpu.mem_write(dst,h.data(src,n));h.result(dst)
 def strchr():
  src,c=h.registers(2);data=cbytes(h,src)+b'\0';pos=data.find(bytes([c&255]));h.result(0 if pos<0 else src+pos)
 def strncmp():
  a,b,n=h.registers(3);assert n<65536
  result=0
  for i in range(n):
   x,y=h.data(a+i,1)[0],h.data(b+i,1)[0]
   if x!=y:result=x-y;break
   if x==0:break
  h.result(result&0xffffffff)
 h.handlers.update({0x80006038:memset,0x80005f34:memcpy,0x800133f8:strchr,0x800133b8:strncmp,0x80021254:lambda:h.result(len(cbytes(h,h.registers(1)[0])))})

def row(name,vr=0,rank=0,fc=0):return(name,vr,rank,fc)
def main():
 released=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes()
 candidate=(ROOT/'build/Code.pul').read_bytes();assert hashlib.sha256(released).hexdigest()==RELEASE_SHA
 symbol='ParseResponse__Q36Pulsar2UI17VRLeaderboardPageFPCcPQ46Pulsar2UI17VRLeaderboardPage5Entryi'
 matches=[int(m[1],16)for line in(ROOT/'build/Code.map').read_text().splitlines()if(m:=re.match(r'\s*([0-9a-fA-F]{8})\s+[0-9a-fA-F]+\s+(.+)',line))and m[2]==symbol];assert len(matches)==1
 fixtures=[]
 def add(label,text,expected,cap=50,null_json=False,null_out=False):fixtures.append((label,text,expected,cap,null_json,null_out))
 add('null_json','[]',[],null_json=True);add('null_output','[]',[],null_out=True)
 add('zero_capacity','[{"name":"A"}]',[],0);add('negative_capacity','[{"name":"A"}]',[],-1)
 for label,text in [('empty','[]'),('no_array','{}'),('truncated','[{"name":"Lost"'),('missing_name','[{"vr":42}]'),('empty_name','[{"name":""}]')]:add(label,text,[])
 add('fields','[{"name":"Nitro","vr":9999,"rank":12,"friendCode":"1234-5678-9012"}]',[row('Nitro',9999,12,123456789012)])
 add('numeric_friend_code','[{"name":"A","friendCode":123456789012}]',[row('A',fc=123456789012)])
 add('alternate_friend_code','[{"name":"B","friend_code":"1234 5678 9012"}]',[row('B',fc=123456789012)])
 add('priority_friend_code','[{"name":"C","friendCode":2,"friend_code":3}]',[row('C',fc=2)])
 add('invalid_numbers','[{"name":"A","vr":-1,"rank":"bad"}]',[row('A')])
 add('maximum_u32','[{"name":"A","vr":4294967295,"rank":4294967295}]',[row('A',0xffffffff,0xffffffff)])
 add('escaped_quotes_and_braces',json.dumps([{'name':'A"}\\B','vr':7}]),[row('A"}\\B',7)])
 add('escaped_controls',r'[{"name":"A\nB\tC"}]',[row('A\nB\tC')])
 add('unicode_escape_historical_fallback',r'[{"name":"Ren\u00e9"}]',[row('Ren?')])
 add('utf8_historical_fallback','[{"name":"René"}]',[row('Ren??')])
 add('long_name',json.dumps([{'name':'A'*80}]),[row('A'*23)])
 add('skip_nameless',json.dumps([{'vr':1},{'name':'First'},{'name':''},{'name':'Second'}]),[row('First'),row('Second')])
 add('complete_before_truncation','[{"name":"First"},{"name":"Lost"',[row('First')])
 for count,cap in [(1,1),(2,1),(10,10),(50,50),(51,50),(51,3)]:
  add(f'entries_{count}_cap_{cap}',json.dumps([{'name':f'P{i}','rank':i+1}for i in range(count)]),[row(f'P{i}',rank=i+1)for i in range(min(count,cap))],cap)
 mii=bytearray(76);mii[2:2+len('Mii名'.encode('utf-16-be'))]='Mii名'.encode('utf-16-be')
 encoded=base64.b64encode(mii).decode()
 add('synthetic_mii_name_preferred',json.dumps([{'name':'Fallback','miiData':encoded}]),[row('Mii名')])
 add('empty_mii_fallback',json.dumps([{'name':'Fallback','miiData':base64.b64encode(bytes(76)).decode()}]),[row('Fallback')])
 executions=0
 for base in(0x81000000,0x81200000):
  machines=[(Controlled(released,base),0x4a2e0),(Controlled(candidate,base),matches[0])]
  for h,_ in machines:install_libc(h);h.instruction_limit=2000000
  for label,text,expected,cap,null_json,null_out in fixtures:
   outputs=[]
   for h,offset in machines:
    payload=text.encode('utf-8')+b'\0';h.cpu.mem_write(0x81620000,payload)
    # Equal sentinels expose any output/untouched-field differences and writes
    # outside the declared output capacity. A skipped nameless object may reset
    # the current unused entry, which is intentional historical behavior.
    capacity=max(cap,0);size=capacity*STRIDE
    h.cpu.mem_write(0x81600000-32,b'\xa5'*(size+64))
    count,calls=h.run(offset,0 if null_json else 0x81620000,0 if null_out else 0x81600000,cap&0xffffffff);executions+=1
    assert count==len(expected),(label,count,expected)
    assert not calls,(label,calls)
    assert h.data(0x81600000-32,32)==b'\xa5'*32 and h.data(0x81600000+size,32)==b'\xa5'*32,(label,'canary')
    rows=[]
    for i in range(count):
     entry=h.data(0x81600000+i*STRIDE,STRIDE)
     name=entry[:48].decode('utf-16-be').split('\0')[0]
     rows.append(row(name,int.from_bytes(entry[0x30:0x34],'big'),int.from_bytes(entry[0x34:0x38],'big'),int.from_bytes(entry[0x88:0x90],'big')))
    assert rows==expected,(label,rows,expected)
    outputs.append((count,h.data(0x81600000,size)))
   assert outputs[0]==outputs[1],(label,'released/source output mismatch')
  print('PASS parser fixtures at',hex(base),flush=True)
 report={'passed':True,'executions':executions,'fixture_count':len(fixtures),'fixtures':[x[0]for x in fixtures],'release_sha256':hashlib.sha256(released).hexdigest(),'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'release_offset':'0x4a2e0','candidate_offset':hex(matches[0]),'allocation_bases':['0x81000000','0x81200000'],'checked':['Return counts and independently expected names, VR, ranks and friend codes','Full initialized output buffer equality, including Mii data','Output capacity canaries','Compiled internal JSON, base64 and Mii-name helpers execute without interception'],'limits':['Only isolated PAL response parsing; libc intercepted','Synthetic StoreData tests name extraction, not RFL validity or real player data','Historical non-ASCII JSON fallback intentionally preserved','No NHTTP lifecycle, pagination UI, concurrency, full game or complete source claim'],'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in ['PulsarEngine/UI/VRLeaderboard/VRLeaderboard.cpp','PulsarEngine/UI/VRLeaderboard/VRLeaderboard.hpp','PulsarEngine/Network/Json.cpp']}}
 (ROOT/'docs/leaderboard-parser-emulation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS:',executions,'released/source-built PowerPC parser executions')
if __name__=='__main__':main()
