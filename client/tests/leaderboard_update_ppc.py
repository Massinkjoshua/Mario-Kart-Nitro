#!/usr/bin/env python3
"""Released/recovered OnUpdate PPC: timeout, one-time UI apply and row sounds.
GPLv3. Controller navigation is disabled by a null SectionMgr; UI/audio native
calls and the unsigned 64-bit division routine are controlled.
"""
import argparse,hashlib,json
from pathlib import Path
from recovered_remaining_ppc import Controlled,ROOT
from recovered_runtime_ppc import reg
from leaderboard_network_ppc import symbols
from leaderboard_parser_ppc import RELEASE_SHA

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile-dir',type=Path,default=ROOT/'build/released-leaderboard');a=p.parse_args()
 old=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();assert hashlib.sha256(old).hexdigest()==RELEASE_SHA
 new=(a.profile_dir/'Code.pul').read_bytes();sm=symbols(a.profile_dir/'Code.map')
 def name(prefix):return sm[prefix+'__Q36Pulsar2UI17VRLeaderboardPageFv']
 states=[{'state':0x92fd4,'update':0x497a0,'apply':0x49b10,'error':0x49ebc},{'state':sm['s_fetchState__Q36Pulsar2UI17VRLeaderboardPage'],'update':name('OnUpdate'),'apply':name('ApplyResults'),'error':name('ApplyError')}]
 cases=[]
 for state in list(range(18))+[0xffffffff]:
  for applied in(0,1):cases.append((state,applied,0,0,0))
 for elapsed in(0,44999,45000,45001,90000):
  for applied in(0,1):cases.append((1,applied,elapsed,0,0))
 for count in(0,1,9,10):
  for duration in(0,1,17,18,19,100):cases.append((2,1,0,count,duration))
 executions=0
 for base in(0x81000000,0x81200000):
  machines=[(Controlled(old,base),states[0]),(Controlled(new,base),states[1])]
  for state,applied,elapsed,count,duration in cases:
   outputs=[]
   for h,pos in machines:
    s=base+pos['state'];h.cpu.mem_write(s,b'\0'*0x38);h.word(s,state);h.byte(s+4,applied);h.word(s+0x28,count);h.word(0x8161001c,duration);h.word(0x809c1e38,0);h.word(0x800000f8,4000000)
    start=1000000;now=start+elapsed*1000;h.word(s+0x10,0);h.word(s+0x14,start)
    def clock(h=h):h.calls.append(('clock',));h.result(now>>32);h.cpu.reg_write(reg(4),now&0xffffffff)
    def divide(h=h):
     high,low,dh,dl=h.registers(4);den=(dh<<32)|dl;assert den!=0
     q=((high<<32)|low)//den;h.result(q>>32);h.cpu.reg_write(reg(4),q&0xffffffff)
    h.handlers={0x801aad5c:clock,0x80021604:divide,base+pos['apply']:lambda h=h:h.call('apply_results',1),base+pos['error']:lambda h=h:h.call('apply_error',1),0x807146a8:lambda h=h:h.call('row_sound',3)}
    _,calls=h.run(pos['update'],0x81610000);executions+=1
    out_state=3 if state==1 and elapsed>45000 else state;out_applied=applied;out_count=count;expected=[('clock',)]if state==1 else[]
    if out_state==2 and not applied:expected.append(('apply_results',(0x81610000,)));out_applied=1;out_count=0
    elif 3<=out_state<0x80000000 and (not applied or state==1 and elapsed>45000):expected.append(('apply_error',(0x81610000,)));out_applied=1
    if out_state==2 and out_applied and out_count<10 and duration>=out_count*2:
     expected.append(('row_sound',(5,0,0x81610000)));out_count+=1
    assert calls==expected,(state,applied,elapsed,count,duration,calls,expected)
    assert h.read(s)==out_state and h.data(s+4,1)==bytes([out_applied])and h.read(s+0x28)==out_count
    outputs.append((calls,h.data(s,0x38)))
   assert outputs[0]==outputs[1]
  print('PASS leaderboard update state machine at',hex(base),flush=True)
 report={'passed':True,'executions':executions,'case_count':len(cases),'release_sha256':hashlib.sha256(old).hexdigest(),'source_profile_sha256':hashlib.sha256(new).hexdigest(),'checked':['45000 ms boundary, including already-applied timeout reset','Ready/error states apply once and numbered errors dispatch','Row sound delay and ten-row completion boundary','Signed enum behavior for invalid state 0xffffffff'],'limits':['PAL isolated OnUpdate, UI/audio and unsigned division controlled','Null SectionMgr bypasses controller navigation; navigation is not verified','No actual asynchronous scheduling or game boot']}
 (ROOT/'docs/leaderboard-update-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'PowerPC update executions')
if __name__=='__main__':main()
