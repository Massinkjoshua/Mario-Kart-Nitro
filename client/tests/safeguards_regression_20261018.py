#!/usr/bin/env python3
"""Regression checks for packet envelopes, rating request ownership and saves.
Runs compiled PAL code; native calls controlled. GPLv3. No network or disk save writes.
"""
import argparse,hashlib,json,math,random,re,struct,sys,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
sys.path[:0]=[str(a.source_root/'tests'),str(a.source_root/'scripts')]
from recovered_remaining_ppc import Controlled
from leaderboard_parser_ppc import install_libc,cbytes
from unicorn.ppc_const import UC_PPC_REG_FPR1,UC_PPC_REG_MSR
from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
raw=a.candidate.read_bytes();sm={m[2]:int(m[1],16)for line in a.map.read_text().splitlines()if(m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',line))}
def sym(prefix):
 v=[v for k,v in sm.items()if k.startswith(prefix+'__')];assert len(v)==1,prefix;return v[0]
def fput(h,v):h.cpu.reg_write(UC_PPC_REG_FPR1,struct.unpack('>Q',struct.pack('>d',v))[0])
def fget(h):return struct.unpack('>d',struct.pack('>Q',h.cpu.reg_read(UC_PPC_REG_FPR1)))[0]
def machine(base):
 h=Controlled(raw,base);h.cpu.reg_write(UC_PPC_REG_MSR,0x2000);h.word(0x80000000,0x524d4350);return h
records=[]
for base in (0x81000000,0x81200000):
 # Request lifecycle: the callback must only publish; frame code alone may save.
 cases=['single','overlap','same_profile_overlap','local_rating_changed','licence_changed','send_failure','response_failure','missing_found','invalid_found','invalid_vr','negative_vr','oversized_vr','trailing_junk','oversized_body','not_found','null_response','queued_after_failure']
 for case in cases:
  h=machine(base);install_libc(h);h.word(0x809bd748,0x81600000);h.word(0x8160900c,101);h.word(0x8160900c+0x93f0,202)
  requests=[];saves=[];reports=[];count=[0];vr=[50.0]
  body=[b'{"found":1,"vr":12000,"br":9000}']
  modifications={'missing_found':b'{"vr":12000,"br":9000}','invalid_found':b'{"found":10,"vr":12000,"br":9000}','invalid_vr':b'{"found":1,"vr": null,"br":9000}','negative_vr':b'{"found":1,"vr":-1,"br":9000}','oversized_vr':b'{"found":1,"vr":1000001,"br":9000}','trailing_junk':b'{"found":1,"vr":12000oops,"br":9000}','oversized_body':b' '*256,'not_found':b'{"found":0}'}
  if case in modifications:body[0]=modifications[case]
  def snprintf():
   dst,n,fmt,domain,pid=h.registers(5);value=h.string(fmt).replace('%s',h.string(domain)).replace('%ld',str(pid)).encode();h.cpu.mem_write(dst,value[:n-1]+b'\0');h.result(len(value))
  def create():
   url,method,buf,size,callback,ctx=h.registers(6);requests.append({'url':h.string(url),'buffer':buf,'callback':callback,'ctx':ctx,'snapshot':h.data(ctx,20)});h.result(0x81640000+len(requests)*0x100)
  def send():
   assert count[0]==1,'Request must be counted before dispatch';h.result(0xffffffff if case=='send_failure'else 1)
  def finish():count[0]-=1;assert count[0]>=0
  def bodyall():
   response,out=h.registers(2);h.word(out,0x81650000);h.result(len(body[0]))
  def strstr():
   text,needle=h.registers(2);pos=cbytes(h,text).find(cbytes(h,needle));h.result(0 if pos<0 else text+pos)
  def strtol():
   text,end,radix=h.registers(3);assert radix==10;m=re.match(rb'[ \t\r\n]*[+-]?[0-9]+',cbytes(h,text));value=int(m[0])if m else 0;h.word(end,text+len(m[0])if m else text);h.result(max(-2147483648,min(2147483647,value))&0xffffffff)
  h.handlers.update({base+sym('PrepareNHTTPRequest'):lambda:h.result(1),base+sym('NHTTPAlloc'):lambda:h.result(0x81630000),base+sym('GetUserVR'):lambda:fput(h,vr[0]),base+sym('GetUserBR'):lambda:fput(h,50),0x80011938:snprintf,0x801d8ff8:create,0x801d925c:send,0x801d937c:bodyall,0x801d92f8:lambda:None,0x800135f0:strstr,0x80015350:strtol,base+sym('MarkNHTTPRequestActive'):lambda:count.__setitem__(0,count[0]+1),base+sym('FinishNHTTPRequest'):finish,base+sym('SaveProfileVR'):lambda:saves.append(('VR',h.registers(1)[0],fget(h))),base+sym('SaveProfileBR'):lambda:saves.append(('BR',h.registers(1)[0],fget(h))),base+sym('ReportCurrentRatings'):lambda:reports.append(h.registers(1)[0]),0x801a65ac:lambda:h.result(1),0x801a65d4:lambda:None})
  h.run(sym('BeginLoginRatingDownload'),101,0);assert len(requests)==1
  if case=='send_failure':assert count[0]==0;h.run(sym('ProcessLoginRatingDownloads'));assert not saves;records.append({'case':case,'base':hex(base),'passed':True});continue
  queued=case in ('overlap','same_profile_overlap','queued_after_failure')
  if queued:
   h.run(sym('BeginLoginRatingDownload'),101 if case=='same_profile_overlap'else 202,0 if case=='same_profile_overlap'else 1)
   assert len(requests)==1 and h.data(requests[0]['ctx'],20)==requests[0]['snapshot'],'Context changed while owned'
  if case=='local_rating_changed':vr[0]=51.0
  if case=='licence_changed':h.word(0x8160900c,303)
  def complete(r,result=0,response=0x81640100):
   h.cpu.mem_write(0x81650000,body[0]+b'\0');h.run(r['callback']-base,result,response,r['ctx']);assert count[0]==0
  complete(requests[0],1 if case in ('response_failure','queued_after_failure')else 0,0 if case=='null_response'else 0x81640100)
  assert not saves and not reports,'Callback must not perform save IO or reporting'
  h.run(sym('ProcessLoginRatingDownloads'))
  if queued:
   assert len(requests)==2 and count[0]==1 and not saves
   body[0]=b'{"found":1,"vr":34000,"br":12000}';complete(requests[1]);assert not saves
   h.run(sym('ProcessLoginRatingDownloads'));expected=101 if case=='same_profile_overlap'else 202
   assert saves==[('VR',expected,340.0),('BR',expected,120.0)]
  elif case=='single':assert saves==[('VR',101,120.0),('BR',101,90.0)]
  elif case=='not_found':assert not saves and reports==[0]
  else:assert not saves and not reports,(case,saves,reports)
  records.append({'case':case,'base':hex(base),'passed':True,'requests':len(requests),'save_calls':saves})
 # Derive private Load/GetPath addresses from real branch instructions, not stale offsets.
 for label,value,br,expected in [('valid',50.0,50.0,50.0),('minimum',1.,1.,1.),('maximum',10000.,10000.,10000.),('negative',-5.,50.,50.),('above_max',10001.,50.,50.),('nan',float('nan'),50.,50.),('infinity',float('inf'),50.,50.),('invalid_br',100.,float('nan'),50.)]:
  h=machine(base);h.word(0x809bd748,0x81600000);h.word(0x8160900c,101);h.word(base+sm['sInstance__Q26Pulsar2IO'],0x81630000);h.word(0x81630000,0x81631000)
  for off,addr in [(8,0x80003000),(0x24,0x80003004),(0x34,0x80003008)]:h.word(0x81631000+off,addr)
  d=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN)
  def firstcall(addr):return next(int(i.op_str,16)for i in d.disasm(h.data(addr,0x90),addr)if i.mnemonic=='bl')
  getpath=firstcall(firstcall(base+sym('GetUserVR')))
  blob=b'RRRT'+struct.pack('>HHiffI',1,1,101,value,br,1);position=[0]
  def read():
   this,n,out=h.registers(3);chunk=blob[position[0]:position[0]+n];position[0]+=len(chunk);h.cpu.mem_write(out,chunk);h.result(len(chunk))
  h.cpu.mem_write(0x81640000,b'/test/RRRating.pul\0');h.handlers={getpath:lambda:h.result(0x81640000),0x80003000:lambda:h.result(1),0x80003004:read,0x80003008:lambda:None}
  h.run(sym('GetUserVR'),0);assert fget(h)==expected,(label,fget(h));records.append({'case':'save_'+label,'base':hex(base),'passed':True,'returned':fget(h)})
 # Packet envelope: no network traffic. Valid sections, padding, truncation, CRC and context cases.
 packet_cases=[('valid_header',16,[16,0,0,0,0,0,0,0],True),('valid_sections',48,[16,32,0,0,0,0,0,0],True),('padding',64,[16,32,0,0,0,0,0,0],True),('truncated',16,[16,32,0,0,0,0,0,0],False),('bad_capacity',81,[16,65,0,0,0,0,0,0],False),('bad_header_size',16,[0,0,0,0,0,0,0,0],False),('short0',0,[16,0,0,0,0,0,0,0],False),('short8',8,[16,0,0,0,0,0,0,0],False),('short15',15,[16,0,0,0,0,0,0,0],False),('oversize',0x5000,[16,0,0,0,0,0,0,0],False),('bad_crc',16,[16,0,0,0,0,0,0,0],False),('bad_buffer_index',16,[16,0,0,0,0,0,0,0],False),('null_split',16,[16,0,0,0,0,0,0,0],False),('null_holder',16,[16,0,0,0,0,0,0,0],False),('aid11',16,[16,0,0,0,0,0,0,0],True),('aid12',16,[16,0,0,0,0,0,0,0],False),('null_controller',16,[16,0,0,0,0,0,0,0],False)]
  # deterministic random section combinations and truncated companions
 rng=random.Random(1810)
 for i in range(50):
  sections=[16]+[rng.randrange(0,33)for _ in range(7)];size=sum(sections);packet_cases.extend([(f'valid_random_{i}',size,sections,True),(f'truncated_random_{i}',size-1,sections,False)])
 for label,size,sections,expected in packet_cases:
  h=machine(base);controller=0x81600000;packet=0x81630000;holders=0x81640000;aid=11 if label=='aid11'else 12 if label=='aid12'else 0
  h.word(controller+0x150+min(aid,11)*4,0 if label=='null_split'else holders);h.word(controller+0x279c+min(aid,11)*32,2 if label=='bad_buffer_index'else 0)
  for i in range(8):h.word(holders+i*4,0 if label=='null_holder'and i==0 else holders+0x100+i*0x10);h.word(holders+0x104+i*0x10,64)
  payload=struct.pack('>II8B',0x52414345,0,*sections)+bytes(max(0,size-16));crc=zlib.crc32(payload[:size]);h.cpu.mem_write(packet,payload);h.word(packet+4,crc^(label=='bad_crc'))
  forwarded=[];crc_calls=[]
  def crcfn():
   ptr,n=h.registers(2);crc_calls.append(n);h.result(zlib.crc32(h.data(ptr,n)))
  h.handlers={0x801d1ca0:crcfn,0x80659a84:lambda:forwarded.append(h.registers(4))}
  # For an undersized envelope the pointer is intentionally invalid: no header read is permitted.
  ptr=0 if size<16 else packet
  h.run(sym('CheckPacket'),0 if label=='null_controller'else controller,ptr,size,0,aid)
  assert bool(forwarded)==expected,(label,forwarded)
  if label.startswith('short')or label in ('truncated','oversize','bad_header_size','aid12','null_controller')or label.startswith('truncated_random'):assert not crc_calls,label
  if aid<12 and label!='null_controller':assert h.read(controller+0x25b0)==(0 if expected else 1<<aid),label
  if crc_calls:assert h.read(packet+4)==crc^(label=='bad_crc')
  records.append({'case':'packet_'+label,'base':hex(base),'passed':True,'forwarded':bool(forwarded)})
 print('PASS safeguards at',hex(base),flush=True)
report={'passed':True,'candidate_sha256':hashlib.sha256(raw).hexdigest(),'scenario_records':len(records),'records':records,'limits':['PAL isolated compiled routines; native HTTP, IO, libc and rating accessors controlled','No full Dolphin/Wii/online session or live server changes','Packet downstream processing intercepted; does not prove immunity to every malformed packet','Server rating-sync handlers remain unresolved; leaderboard issues unchanged']}
a.report.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(records),'scenario records')
