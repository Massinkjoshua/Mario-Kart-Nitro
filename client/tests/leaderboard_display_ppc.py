#!/usr/bin/env python3
"""Released/source-built leaderboard diagnostics, request creator and Mii guards.
GPLv3. Real PPC runs; native HTTP/state/RFL/layout/rendering are controlled.
"""
import argparse,hashlib,json
from pathlib import Path
from recovered_remaining_ppc import Controlled,ROOT
from leaderboard_network_ppc import symbols
from leaderboard_parser_ppc import RELEASE_SHA,cbytes
from nitro_formats import kamek

def wide(h,address):
 out=[]
 for i in range(128):
  value=int.from_bytes(h.data(address+2*i,2),'big')
  if value==0:return ''.join(out)
  out.append(chr(value))
 raise AssertionError('Unterminated diagnostic text')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile-dir',type=Path,default=ROOT/'build/released-leaderboard');args=p.parse_args()
 old_data=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();assert hashlib.sha256(old_data).hexdigest()==RELEASE_SHA
 new_data=(args.profile_dir/'Code.pul').read_bytes();sm=symbols(args.profile_dir/'Code.map')
 def exact(prefix):
  found=[v for k,v in sm.items()if k.startswith(prefix+'__')];assert len(found)==1,prefix;return found[0]
 nr=kamek(new_data)['regions'][0]
 def getter_global(prefix):
  a=exact(prefix);cmds=[x for x in nr['commands']if not x['absolute']and a<=x['address']<a+16]
  assert len(cmds)==2 and {x['command_id']for x in cmds}=={4,6}and len({x['values'][0]for x in cmds})==1
  return cmds[0]['values'][0]
 old={'error':0xc2004,'create':0xc65fc,'load':0xc68c0,'pane':0xc692c,'visible':0xc6948,'failure':0xc68a0,'failure_bytes':0xc68a4,'state':0x92fd4}
 new={'error':exact('GetReleasedLeaderboardError'),'create':exact('CreateReleasedLeaderboardRequest'),'load':exact('LoadReleasedLeaderboardMii'),'pane':exact('SetReleasedLeaderboardMiiPane'),'visible':exact('SetReleasedLeaderboardMiiVisible'),'failure':getter_global('GetReleasedNHTTPFailureKind'),'failure_bytes':getter_global('GetReleasedNHTTPFailureBytes')}
 expected=['Failed: timeout','Failed: entries','Failed: context','Failed: startup','Failed: workbuf','Failed: create','Failed: send','Failed: response','Failed: entries','Failed: HTTP','Failed: body','Failed: copybuf','Failed: JSON']
 executions=0;diagnostic_cases=0;creator_cases=0;mii_sequences=0
 for base in(0x81000000,0x81200000):
  machines=[(Controlled(old_data,base),old),(Controlled(new_data,base),new)]
  def error(h,pos,state):
   nonlocal executions
   if pos is old:
    h.word(base+pos['state'],state);record,_=h.run(pos['error']);ptr=h.read(record+4)
   else:ptr,_=h.run(pos['error'],state)
   executions+=1;return wide(h,ptr)
  for state in list(range(17))+[0x7fffffff,0x80000000,0xffffffff]:
   outputs=[error(h,pos,state)for h,pos in machines];index=state-3 if 3<=state<=15 else 0
   assert outputs==[expected[index]]*2,(state,outputs);diagnostic_cases+=1
  # The native create callback injects recorded allocator failure AFTER the
  # wrapper clears it, just as a real failed allocation would do.
  scenarios=[(False,1,0,0,'Mem: other allocator'),(False,1,1,0,'Mem: size or align'),(False,1,2,0,'Mem: tracking full'),(False,1,3,0,'Mem: pool missing'),(False,1,4,32864,'Mem: pool full 32K'),(False,1,4,4096,'Mem: pool full'),(False,1,9,123,'Mem: pool full'),(False,4,0,0,'Create: URL'),(False,2,0,0,'Failed: create'),(False,0,0,0,'Failed: create'),(False,0xffffffff,0,0,'Failed: create')]
  for success,native_error,kind,size,message in scenarios:
   for final_success in(False,True):
    outputs=[]
    for h,pos in machines:
     h.handlers.clear();h.cpu.mem_write(0x81620000,b'http://synthetic.invalid/path\0');h.word(0x816507d8,native_error)
     h.word(base+pos['failure'],99);h.word(base+pos['failure_bytes'],88)
     returns=[False,final_success];traces=[]
     for return_success in returns:
      def create(h=h,pos=pos):
       assert h.read(base+pos['failure'])==0 and h.read(base+pos['failure_bytes'])==0
       h.calls.append(('native_create',h.registers(6)))
       h.word(base+pos['failure'],kind);h.word(base+pos['failure_bytes'],size);h.result(0x81660000 if return_success else 0)
      def work(h=h):h.calls.append(('native_work',));h.result(0x81650000)
      h.handlers.update({0x801d8ff8:create,0x801d9e94:work})
      result,calls=h.run(pos['create'],0x81620000,0,0x81630000,0x4000,0x81640000,0x81641000);executions+=1
      assert result==(0x81660000 if return_success else 0)
      assert calls==[('native_create',(0x81620000,0,0x81630000,0x4000,0x81640000,0x81641000))]+([]if return_success else[('native_work',)])
      text=error(h,pos,8);assert text==message,(native_error,kind,size,text,message)
      traces.append((result,calls,text,h.read(base+pos['failure']),h.read(base+pos['failure_bytes'])))
     outputs.append(traces)
    assert outputs[0]==outputs[1];creator_cases+=1
  # Check valid -> invalid -> valid row reuse and both icon bindings. RFL's
  # documented BOOL outputs are exercised as 0/1; actual RFL internals are mocked.
  for sequence in[(0,),(1,),(1,0,1),(0,1,0)]:
   for exists in(False,True):
    for index in(0,9):
     outputs=[]
     for h,pos in machines:
      h.handlers.clear();h.cpu.mem_write(0x81632000,b'chara_icon\0');h.cpu.mem_write(0x81632100,b'chara_icon_sha\0');events=[]
      for valid in sequence:
       def check(h=h):h.call('validate',1);h.result(valid)
       h.handlers.update({0x800cb8b0:check,0x805fa610:lambda h=h:h.call('load_mii',3),0x8063e3dc:lambda h=h:h.call('bind_mii',5),0x805e8368:lambda h=h:(h.call('find_pane',2),h.result(0x81634000 if exists else 0)),0x8063e54c:lambda h=h:h.call('visible',3)})
       _,calls=h.run(pos['load'],0x81630000,index,0x81633000);executions+=1
       assert calls==[('validate',(0x81633000,))]+([('load_mii',(0x81630000,index,0x81633000))]if valid else[]);events.append(calls)
       for pane in(0x81632000,0x81632100):
        _,calls=h.run(pos['pane'],0x81631000,pane,0x81630000,index,2);executions+=1
        assert calls==([('bind_mii',(0x81631000,pane,0x81630000,index,2))]if valid else[]);events.append(calls)
        for requested in(0,1):
         _,calls=h.run(pos['visible'],0x81631000,pane,requested);executions+=1
         assert calls==[('find_pane',(0x816310a8,pane))]+([('visible',(0x81631000,pane,valid))]if exists else[]);events.append(calls)
      outputs.append(events)
     assert outputs[0]==outputs[1];mii_sequences+=1
  print('PASS diagnostics/creator/Mii wrappers at',hex(base),flush=True)
 report={'passed':True,'executions':executions,'diagnostic_cases':diagnostic_cases,'creator_sequences':creator_cases,'mii_reuse_sequences':mii_sequences,'release_sha256':hashlib.sha256(old_data).hexdigest(),'source_profile_sha256':hashlib.sha256(new_data).hexdigest(),'allocation_bases':['0x81000000','0x81200000'],'functions':['GetReleasedLeaderboardError','CreateReleasedLeaderboardRequest','LoadReleasedLeaderboardMii','SetReleasedLeaderboardMiiPane','SetReleasedLeaderboardMiiVisible'],'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((ROOT/'Recovery/ReleasedLeaderboard/PulsarEngine').rglob('*'))if p.is_file()},'limits':['Isolated PAL functions; not full game or complete released-core reconstruction','Native creator/work-state and RFL/layout/rendering APIs intercepted','Actual pool allocator source executes only its clear/getter paths here; allocation outcomes are synthetic','Mii validity BOOL tested as canonical 0/1 only','Entire ApplyResults/ApplyError integration and UI rendering are not executed by this harness']}
 (ROOT/'docs/leaderboard-display-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'PowerPC executions')
if __name__=='__main__':main()
