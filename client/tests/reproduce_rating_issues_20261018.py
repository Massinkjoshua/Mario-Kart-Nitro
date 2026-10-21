#!/usr/bin/env python3
"""Defensive offline review of pinned candidate; controlled native APIs. GPLv3.
No live traffic, user save writes or server changes.
"""
import argparse,hashlib,json,math,re,struct,sys,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.source_root/'tests'));sys.path.insert(0,str(a.source_root/'scripts'))
from recovered_remaining_ppc import Controlled
from recovered_runtime_ppc import reg
from leaderboard_parser_ppc import install_libc,cbytes
from unicorn.ppc_const import UC_PPC_REG_FPR1,UC_PPC_REG_MSR
raw=a.candidate.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='71af89931375f4fc46782401e54c243bee8fc657b8fb44d4fe6f52e627ac3075'
sm={m[2]:int(m[1],16)for line in a.map.read_text().splitlines()if(m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',line))}
def sym(prefix):
 found=[v for k,v in sm.items()if k.startswith(prefix+'__')];assert len(found)==1,prefix
 return found[0]
def fput(h,v):h.cpu.reg_write(UC_PPC_REG_FPR1,struct.unpack('>Q',struct.pack('>d',v))[0])
def fget(h):return struct.unpack('>d',struct.pack('>Q',h.cpu.reg_read(UC_PPC_REG_FPR1)))[0]
def machine(base):
 h=Controlled(raw,base);h.cpu.reg_write(UC_PPC_REG_MSR,0x2000);h.word(0x80000000,0x524d4350);return h
records=[]
for base in (0x81000000,0x81200000):
 for overlap in (False,True):
  h=machine(base);install_libc(h);h.word(0x809bd748,0x81600000)
  h.word(0x8160900c,101);h.word(0x8160900c+0x93f0,202)
  requests=[];saves=[];body=b'{"found":1,"vr":12000,"br":9000}'
  def snprintf():
   dst,n,fmt,domain,pid=h.registers(5);value=h.string(fmt).replace('%s',h.string(domain)).replace('%ld',str(pid)).encode();h.cpu.mem_write(dst,value[:n-1]+b'\0');h.result(len(value))
  def create():
   url,method,buf,size,callback,ctx=h.registers(6)
   requests.append({'url_at_creation':h.string(url),'buffer':buf,'callback':callback,'ctx':ctx,'ctx_at_creation':h.data(ctx,12).hex()});h.result(0x81640000+len(requests)*0x100)
  def bodyall():
   response,out=h.registers(2);h.word(out,0x81650000);h.result(len(body))
  def strstr():
   text,needle=h.registers(2);pos=cbytes(h,text).find(cbytes(h,needle));h.result(0 if pos<0 else text+pos)
  def strtol():
   text,end,radix=h.registers(3);assert radix==10
   b=cbytes(h,text);m=re.match(rb'[ \t\r\n]*[+-]?[0-9]+',b);value=int(m[0])if m else 0;h.word(end,text+len(m[0])if m else text);h.result(value&0xffffffff)
  h.handlers.update({base+sym('PrepareNHTTPRequest'):lambda:h.result(1),base+sym('NHTTPAlloc'):lambda:h.result(0x81630000),base+sym('GetUserVR'):lambda:fput(h,50),base+sym('GetUserBR'):lambda:fput(h,50),0x80011938:snprintf,0x801d8ff8:create,0x801d925c:lambda:h.result(1),0x801d937c:bodyall,0x801d92f8:lambda:None,0x800135f0:strstr,0x80015350:strtol,base+sym('SaveProfileVR'):lambda:saves.append(('VR',h.registers(1)[0],fget(h))),base+sym('SaveProfileBR'):lambda:saves.append(('BR',h.registers(1)[0],fget(h)))})
  h.run(sym('BeginLoginRatingDownload'),101,0)
  if overlap:h.run(sym('BeginLoginRatingDownload'),202,1)
  h.cpu.mem_write(0x81650000,body+b'\0');r=requests[0]
  h.run(r['callback']-base,0,0x81640100,r['ctx'])
  expect=202 if overlap else 101
  assert saves==[('VR',expect,120.0),('BR',expect,90.0)],saves
  if overlap:assert requests[0]['ctx']==requests[1]['ctx']and requests[0]['buffer']==requests[1]['buffer']
  records.append({'base':hex(base),'case':'overlapping_login_reply_targets_new_profile'if overlap else'single_login_targets_correct_profile','requests':requests,'reply_belongs_to_profile':101,'saves_called':saves})
 # Synthetic rating file is read via mocked IO; actual compiled Load and GetUserVR run.
 for label,value in [('valid',50.0),('negative',-5.0),('above_max',10001.0),('nan',float('nan')),('infinity',float('inf'))]:
  h=machine(base);h.word(0x809bd748,0x81600000);h.word(0x8160900c,101)
  h.word(base+sm['sInstance__Q26Pulsar2IO'],0x81630000);h.word(0x81630000,0x81631000)
  for off,addr in [(8,0x80003000),(0x24,0x80003004),(0x34,0x80003008)]:h.word(0x81631000+off,addr)
  blob=b'RRRT'+struct.pack('>HHiffI',1,1,101,value,50.0,1);position=[0]
  def read():
   this,n,out=h.registers(3);chunk=blob[position[0]:position[0]+n];position[0]+=len(chunk);h.cpu.mem_write(out,chunk);h.result(len(chunk))
  h.cpu.mem_write(0x81640000,b'/test/RRRating.pul\0')
  # File-static GetPath offset is pinned to this exact reviewed binary.
  h.handlers={base+0x34ce0:lambda:h.result(0x81640000),0x80003000:lambda:h.result(1),0x80003004:read,0x80003008:lambda:None}
  h.run(sym('GetUserVR'),0);actual=fget(h)
  assert (math.isnan(actual)if math.isnan(value)else actual==value),(label,actual)
  records.append({'base':hex(base),'case':'rating_file_'+label,'returned_rating':str(actual),'invalid_value_rejected':False if label!='valid'else None})
 # Candidate packet guard only: native downstream parsing is intercepted, not assumed unsafe.
 for label,actual_size,sections,bad_crc in [('valid_header',16,[16,0,0,0,0,0,0,0],False),('section_exceeds_received_length',16,[16,32,0,0,0,0,0,0],False),('individual_size_exceeds_capacity',16,[16,65,0,0,0,0,0,0],False),('bad_crc',16,[16,0,0,0,0,0,0,0],True)]:
  h=machine(base);controller=0x81600000;packet=0x81630000;holders=0x81640000;h.word(controller+0x150,holders)
  for i in range(8):h.word(holders+i*4,holders+0x100+i*0x10);h.word(holders+0x104+i*0x10,64)
  payload=struct.pack('>II8B',0x52414345,0,*sections);crc=zlib.crc32(payload);h.cpu.mem_write(packet,payload);h.word(packet+4,crc^(1 if bad_crc else 0))
  forwarded=[]
  def crcfn():ptr,n=h.registers(2);h.result(zlib.crc32(h.data(ptr,n)))
  h.handlers={0x801d1ca0:crcfn,0x80659a84:lambda:forwarded.append(h.registers(4))}
  h.run(sym('CheckPacket'),controller,packet,actual_size,0,0)
  expect=label in ('valid_header','section_exceeds_received_length');assert bool(forwarded)==expect
  records.append({'base':hex(base),'case':'packet_'+label,'forwarded_to_native':bool(forwarded),'disconnect_mask':h.read(controller+0x25b0),'native_parser_executed':False})
 print('Reproduced second-pass findings and controls at',hex(base),flush=True)
a.report.write_text(json.dumps({'candidate_sha256':sha,'records':records,'limits':['Compiled PAL functions at two bases; IO, NHTTP, libc and selected accessors controlled','No actual save file modified or live network used','Overlap test assumes a second login request begins before the first callback completes','Packet guard forwarding does not prove a downstream crash; native parser not executed']},indent=2)+'\n')
