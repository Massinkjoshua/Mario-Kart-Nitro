#!/usr/bin/env python3
"""Isolated released/rebuilt PowerPC functions, controlled native APIs; GPLv3.
Mario Kart Nitro, 16 October 2026. This does not test a game boot.
"""
import json,struct,sys,hashlib
from unicorn.ppc_const import UC_PPC_REG_PC,UC_PPC_REG_LR
from recovered_runtime_ppc import Harness,symbol,reg,ROOT
sys.path.insert(0,str(ROOT/'scripts'))
from nitro_formats import kamek
class Controlled(Harness):
 def __init__(self,data,base):
  super().__init__(data,base);self.handlers={};self.cpu.mem_map(0x90000000,0x4000000)
 def hook(self,cpu,address,size,user):
  if address in self.handlers:
   self.handlers[address]();cpu.reg_write(UC_PPC_REG_PC,cpu.reg_read(UC_PPC_REG_LR));return
  super().hook(cpu,address,size,user)
 def result(self,value):self.cpu.reg_write(reg(3),value)
 def data(self,address,length):return bytes(self.cpu.mem_read(address,length))
 def call(self,tag,count):self.calls.append((tag,self.registers(count)))
 def run(self,offset,*args):
  self.calls=[]
  for i in range(32):self.cpu.reg_write(reg(i),0)
  self.cpu.reg_write(reg(1),0x817f0000);self.cpu.reg_write(UC_PPC_REG_LR,self.STOP)
  for i,v in enumerate(args):self.cpu.reg_write(reg(i+3),v)
  self.cpu.emu_start(self.base+offset,self.STOP,count=getattr(self,'instruction_limit',100000))
  assert self.cpu.reg_read(UC_PPC_REG_PC)==self.STOP,'Function did not return'
  return self.cpu.reg_read(reg(3)),self.calls[:]
def flag_offset(data,worker):
 r=kamek(data)['regions'][0];raw=data[r['offset']+32:]
 for c in r['commands']:
  a=c['address']
  if not c['absolute']and c['command_id']==4 and worker<=a<worker+100:return c['values'][0]
 raise AssertionError('Missing worker flag relocation')
def main():
 old_data=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();new_data=(ROOT/'build/Code.pul').read_bytes();executions=0
 for base in (0x81000000,0x81200000):
  old,new=Controlled(old_data,base),Controlled(new_data,base)
  for h,skin in [(old,0xcdfc),(new,symbol('RaceSkinTable'))]:
   h.table=0;h.handlers[base+skin]=lambda h=h:h.result(h.table)
   h.handlers[0x80223834]=lambda h=h:h.call('colour',5)
   h.word(0x809bd728,0x81600000);h.byte(0x81600024,12);h.word(0x81610024,2);h.cpu.mem_write(0x81610004,b'rk_miniTurbo\0')
  for char in range(48):
   for table in range(51):
    results=[]
    for h,offset in [(old,0xc6ab8),(new,symbol('ApplySkinDriftColour'))]:
     h.table=table;h.word(0x81600034,char);results.append(h.run(offset,0x81610000)[1]);executions+=1
    assert results[0]==results[1],('palette',char,table,results)
  print('palette passed at',hex(base),flush=True)
  for name in ['rk_driftSpark_1','rk_driftSpark_3','rk_driftSpark_2','rk_purpleTurbo','rk_miniTurbo','unrelated']:
   for char,table,pid,count in [(0,0,0,12),(22,31,11,12),(47,50,0,1),(23,255,0,12),(48,0,0,12),(1,0,12,12),(1,0,-1,12),(1,0,1,1)]:
    results=[]
    for h,offset in [(old,0xc6ab8),(new,symbol('ApplySkinDriftColour'))]:
     h.cpu.mem_write(0x81610004,name.encode()+b'\0');h.word(0x81610024,(pid+2)&0xffffffff);h.table=table
     h.byte(0x81600024,count);h.word(0x81600034+max(pid,0)*0xf0,char);results.append(h.run(offset,0x81610000)[1]);executions+=1
    assert results[0]==results[1],(name,char,table,pid,count,results)
  for manager,section,page,count,fade,globe in [(0x81620000,0x81621000,0x81622000,0,0,True),(0,0,0,0,0,False),(0x81620001,0,0,0,0,False),(0x817fffa0,0,0,0,0,False),(0x81620000,0x81621000,0x81622000,10,0,True),(0x81620000,0x81621000,0x81622000,11,0,True),(0x81620000,0x81621000,0x81622000,0xffffffff,0,True),(0x81620000,0x81621000,0x81622000,0,1,True),(0x81620000,0x81621000,0x81622000,0,0,False),(0x90001000,0x90002000,0x90003000,0,0,True)]:
   for page_id in (0x95,0x87):
    results=[]
    for h,offset in [(old,0xc1acc),(new,symbol('CanContinuePlayerCountRequest'))]:
     h.word(0x809c1e38,manager)
     if manager in (0x81620000,0x90001000):
      h.word(manager,section);h.word(manager+0x30,fade);h.cpu.mem_write(section+0x350,b'\0'*44);h.word(section+0x350+min(count,10)*4,page)
      h.word(section+0x37c,count);h.word(section+0x25c,0x81623000 if globe else 0);h.word(page+4,page_id)
     results.append(h.run(offset)[0]);executions+=1
    assert results[0]==results[1],('guard',manager,count,page_id,results)
  for scenario in ['inactive','bad_scene','bad_match','new_failed','limit_failed','complete_1','complete_3','exit_during_poll','timeout']:
   results=[]
   for h,data,offset in [(old,old_data,0xc18c8),(new,new_data,symbol('StartPlayerCountRequestPAL'))]:
    flag=base+flag_offset(data,offset);h.byte(flag,scenario!='inactive');h.polls=0
    h.word(0x809c1e38,0x81620000);h.word(0x81620000,0x81621000);h.word(0x81620030,scenario=='bad_scene')
    h.cpu.mem_write(0x81621350,b'\0'*44);h.word(0x8162137c,0);h.word(0x8162125c,0x81623000)
    h.word(0x8038630c,0 if scenario=='bad_match'else 0x81630000)
    def create(h=h):
     a=h.registers(7);h.calls.append(('new',h.string(a[0]),h.string(a[1]),a[3:7]));h.result(0 if scenario=='new_failed'else 0x81631000)
    def limit(h=h):
     a=h.registers(7);h.calls.append(('limit',a[:3],h.data(a[3],a[4]),h.string(a[5]),a[6]));h.result(1 if scenario=='limit_failed'else 0)
    def think(h=h):
     h.call('think',1);h.polls+=1
     if(scenario=='complete_1'and h.polls==1)or(scenario=='complete_3'and h.polls==3):h.byte(flag,0)
     if scenario=='exit_during_poll':h.word(0x81620030,1)
    h.handlers[0x8011e038]=create;h.handlers[0x8011e2a0]=limit;h.handlers[0x8011e3c8]=think
    h.handlers[0x8011e11c]=lambda h=h:h.call('free',1);h.handlers[0x800f2510]=lambda h=h:h.call('sleep',1)
    _,calls=h.run(offset,0);assert h.data(flag,1)==b'\0';results.append(calls);executions+=1
   assert results[0]==results[1],('worker',scenario,results)
  print('online worker passed at',hex(base),flush=True)
  # PAL v16 creates the system before refreshing its login region.
  mapping=(ROOT/'build/Code.map').read_text()
  import re
  def exact(name):
   rows=[int(m[1],16)for line in mapping.splitlines()if(m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',line))and m[2]==name]
   assert len(rows)==1,name
   return rows[0]
  for region in (0,10,20,21,99999999):
   for exists in (False,True):
    results=[]
    for h,offset,create,instance in [(old,0x583d0,0x17d4,0x6e9dc),(new,symbol('CreateNitroSystem'),exact('CreateSystem__Q26Pulsar6SystemFv'),exact('sInstance__Q26Pulsar6System'))]:
     h.word(0x80000000,0x524d4350);h.word(base+instance,0x81640000 if exists else 0);h.word(0x8164009c,region)
     h.word(0x80005efc,0);h.cpu.mem_write(0x80384fd0,b'????????')
     h.handlers[base+create]=lambda h=h:h.calls.append(('create_system',))
     def snprintf(h=h):
      dest,length,fmt,value=h.registers(4);assert h.string(fmt)=='%08d'
      text=f'{value:08d}'.encode();h.cpu.mem_write(dest,text[:length-1]+b'\0');h.result(len(text))
     h.handlers[0x80011938]=snprintf
     _,calls=h.run(offset);results.append((calls,h.read(0x80005efc),h.data(0x80384fd0,8)));executions+=1
    assert results[0]==results[1],('region',region,exists,results)
  for h in (old,new):
   h.word(0x809c1e38,0x81620000);h.word(0x81620000,0x81621000);h.word(0x8162137c,0);h.word(0x81621350,0x81622000)
   h.word(0x809c1988,0x81630000);h.byte(0x81630020,1);h.word(0x81630014,0x81631000);h.word(0x81630018,0x81632000)
   h.byte(0x81631008,1);h.word(0x81631018,0x81633000);h.word(0x81633004,0x81635000)
   h.byte(0x81632004,1);h.byte(0x81632005,1);h.word(0x81632008,0x81634000);h.word(0x8163200c,0);h.word(0x81634004,0x81636000)
   for director,wrapper,obj in [(0x81635000,0x81637000,0x81639000),(0x81636000,0x81638000,0x8163b000)]:
    h.word(director+4,0x100000);h.word(director+0x10,wrapper)
    for buf in (0,1):h.word(director+0x14+buf*4,wrapper+buf*0x100);h.word(wrapper+buf*0x100,obj+buf*0x100)
   h.handlers[0x8083275c]=lambda h=h:h.call('native_update',1)
   h.handlers[0x80833474]=lambda h=h:(h.call('selected_kart',3),h.result(0x81634000))
   h.handlers[0x80830c64]=lambda h=h:h.call('prepare_driver',2);h.handlers[0x8082fb78]=lambda h=h:h.call('switch_driver',3)
   h.handlers[0x8006dc20]=lambda h=h:(h.call('matrix',3),h.result(1))
   h.handlers[0x8055f848]=lambda h=h:(h.call('scale_get',1),h.cpu.mem_write(h.registers(2)[1],struct.pack('>3f',1.25,2.5,3.75)))
   h.handlers[0x8055b05c]=lambda h=h:h.calls.append(('scale_set',h.registers(1),h.data(h.registers(2)[1],12).hex()))
   h.handlers[0x80830a5c]=lambda h=h:h.call('visible',2)
  old.word(base+0xc16e4,0x8083275c);old.word(base+0xc04ec,0x80830a5c)
  for page in (0x6e,0x6f,0x95):
   for state in (1,3):
    for invalid in (False,True):
     results=[]
     for h,offset in [(old,0xc0dbc),(new,symbol('UpdateReleasedCourseKart'))]:
      h.word(0x81622004,page);h.word(0x81633008,state);h.word(0x81635004,0 if invalid else 0x100000)
      results.append(h.run(offset,0x81634000)[1]);executions+=1
     assert results[0]==results[1],('course',page,state,invalid,results)
   for pointer in (0x81634000,0x8163402c):
    for visible in (0,1):
     results=[]
     for h,offset in [(old,0xc0310),(new,symbol('ToggleReleasedCourseKart'))]:
      h.word(0x81622004,page);results.append(h.run(offset,pointer,visible)[1]);executions+=1
     assert results[0]==results[1],('visibility',page,pointer,visible,results)
  # Runtime REL installer: reset manually supplied worker pointers first.
  for off in (0xc16e4,0xc16e8,0xc04ec,0xc04f0):old.word(base+off,0)
  for h in (old,new):
   h.instruction_limit=2000000
   h.word(0x80000000,0x524d4350);h.word(0x81660028,1)
   h.handlers[0x8051bed0]=lambda h=h:h.result(0x81660000)
  for repeat in range(2):
   for h,offset,update,toggle in [(old,0xc1650,0xc0dbc,0xc0310),(new,symbol('InstallReleasedCoursePreview'),symbol('UpdateReleasedCourseKart'),symbol('ToggleReleasedCourseKart'))]:
    for off,value in [(-4,0x80831f84),(0,0x80832240),(4,0x8083275c),(8,0x80830a5c),(12,0x8059f4f0)]:h.word(0x80890000+off,value)
    h.run(offset);executions+=1
    assert h.read(0x80890004)==base+update and h.read(0x80890008)==base+toggle,('installer',repeat,hex(offset),hex(h.read(0x80890004)),hex(h.read(0x80890008)))
 report=dict(passed=True,executions=executions,release_sha256=hashlib.sha256(old_data).hexdigest(),candidate_sha256=hashlib.sha256(new_data).hexdigest(),allocation_bases=['0x81000000','0x81200000'],scope='Real released/rebuilt PowerPC functions; native APIs intercepted.',checked=['all 2448 RGB palette entries at both bases','drift whitening, ownership and table bounds','online guard, failures, completion, cancellation and 100-poll timeout','region v16 system creation and login fields','course/cup matrix, scale, driver animation state and selected-kart visibility','REL virtual-table initial installation and restoration'],full_gameplay_tested=False)
 (ROOT/'docs/recovered-remaining-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'PowerPC executions match.')
if __name__=='__main__':main()
