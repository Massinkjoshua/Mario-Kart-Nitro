#!/usr/bin/env python3
"""Reproduce review findings in the delivered PAL candidate. Native APIs controlled.
Run with --source-root (published client), --candidate (Code.pul), --map (Code.map).
Requires unicorn 2.1.4. GPL-3.0-or-later.
"""
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.source_root/'tests'));sys.path.insert(0,str(a.source_root/'scripts'))
from recovered_remaining_ppc import Controlled
from recovered_runtime_ppc import reg
from leaderboard_parser_ppc import install_libc
from unicorn.ppc_const import UC_PPC_REG_FPR1, UC_PPC_REG_MSR
raw=a.candidate.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='71af89931375f4fc46782401e54c243bee8fc657b8fb44d4fe6f52e627ac3075'
sm={m[2]:int(m[1],16)for line in a.map.read_text().splitlines()if(m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',line))}
def sym(prefix):
 found=[(k,v) for k,v in sm.items()if k.startswith(prefix+'__')]
 if len(found)>1:found=[(k,v)for k,v in found if '17VRLeaderboardPage' in k]
 assert len(found)==1,prefix
 return found[0][1]
records=[]
for base in (0x81000000,0x81200000):
 h=Controlled(raw,base);s=base+sym('s_fetchState');page=0x81610000
 # Offsets verified against the relocated candidate's OnUpdate/StartFetch.
 inflight=s+0x8148;ready=s+0x8149;response_generation=s+0x814c;response_error=s+0x8154
 def setup(state,cur_page=5,button=0x41):
  h.cpu.mem_write(s,b'\0'*0x8158);h.cpu.mem_write(page,b'\0'*0x100)
  h.word(s,state);h.byte(s+4,1);h.word(s+0x28,10);h.byte(page+0xac,cur_page);h.word(s+0x2c,2)
  h.word(0x809c1e38,0x81620000);h.word(0x81620044,0x81621000);h.word(0x81621004,0x81622000);h.word(0x81622000,0x81623000);h.word(0x81623010,0x80003000)
  h.cpu.mem_write(0x8162102e,struct.pack('>H',button));h.cpu.mem_write(0x81621046,b'\0\0')
  h.handlers={0x80003000:lambda:(h.calls.append(('controller_type',)),h.result(3)),base+sym('ApplyResults'):lambda:h.calls.append(('apply_results',)),base+sym('ApplyError'):lambda:h.calls.append(('apply_error',)),base+sym('ResetRowsToLoading'):lambda:h.calls.append(('loading',)),base+sym('StartFetch'):lambda:h.calls.append(('start_fetch',)),0x80602cf8:lambda:h.calls.append(('page_sound',))}
 # Control: left works in the ready state; same input ignored in error state.
 setup(2);_,calls=h.run(sym('OnUpdate'),page);assert h.data(page+0xac,1)==b'\x04' and ('controller_type',)in calls
 records.append({'base':hex(base),'case':'ready_left_control','page_after':4,'calls':calls})
 setup(3);_,calls=h.run(sym('OnUpdate'),page);assert h.data(page+0xac,1)==b'\x05' and calls==[]
 records.append({'base':hex(base),'case':'error_blocks_left','page_after':5,'calls':calls})
 # Valid empty server response is passed to the REAL compiled JSON parser.
 setup(1);install_libc(h);h.word(s+8,0x81640000);h.word(s+0x1c,7);h.word(response_generation,7);h.byte(ready,1);h.word(response_error,0)
 h.cpu.mem_write(s+0x4040,b'{"players":[],"success":true}\0');_,calls=h.run(sym('OnUpdate'),page)
 assert h.read(s)==3 and ('apply_error',)in calls and ('controller_type',)not in calls
 records.append({'base':hex(base),'case':'valid_empty_response_becomes_error','state_after':h.read(s),'calls':calls})
 # Ready page 50 blocks right even though the API accepts further pages.
 setup(2,49,0x22);_,calls=h.run(sym('OnUpdate'),page);assert h.data(page+0xac,1)==b'\x31' and ('start_fetch',)not in calls
 records.append({'base':hex(base),'case':'page_50_ceiling','page_after':49,'calls':calls})
 # Pending old request: no clock/retry in WAITING, even with old start time.
 setup(4);h.byte(inflight,1);h.word(s+0x10,0);h.word(s+0x14,1)
 h.handlers[0x801aad5c]=lambda:(_ for _ in()).throw(AssertionError('Unexpected clock check'))
 for i in range(120):
  _,calls=h.run(sym('OnUpdate'),page);assert h.read(s)==4 and calls==[]
 records.append({'base':hex(base),'case':'waiting_has_no_timeout_or_retry_while_request_pending','updates':120,'state_after':4})
 # Real matchmaking, valid internal rating 50 = displayed/QR2 VR 5,000.
 # The documented 40k higher-room exclusion should remove 700k when a 5k room exists.
 h=Controlled(raw,base);h.cpu.reg_write(UC_PPC_REG_MSR,0x2000);h.word(0x8038630c,0x81600000);h.word(0x816006dc,0x81601000);h.word(0x809bd748,0x81602000);h.cpu.mem_write(0x81602036,b'\0\0');h.word(0x809c20d8,0)
 rooms={0x81610000:{'ev':5000,'numplayers':5},0x81611000:{'ev':700000,'numplayers':5}};order=list(rooms);removed=[]
 def getint():
  server,key,default=h.registers(3);h.result(rooms[server].get(h.string(key),default)&0xffffffff)
 def setint():
  server,key,value=h.registers(3);rooms[server][h.string(key)]=struct.unpack('>i',struct.pack('>I',value))[0]
 def vr():h.cpu.reg_write(UC_PPC_REG_FPR1,struct.unpack('>Q',struct.pack('>d',50.0))[0])
 def sort():order.sort(key=lambda x:rooms[x]['dwc_eval'])
 def remove():
  room=h.registers(2)[1];removed.append(room);order.remove(room)
 # IsInfiniteMatchmakingEnabled is a file-static function at this candidate offset.
 h.handlers={base+0x2ce28:lambda:h.result(0),base+sym('GetUserVR'):vr,0x8011e488:lambda:h.result(len(order)),0x8011e480:lambda:h.result(order[h.registers(2)[1]]),0x8011d2b0:getint,0x8011d1e4:setint,0x8011e490:sort,0x8011e384:remove}
 h.run(sym('CustomRandomizeServers'));assert not removed and len(order)==2;assert rooms[0x81610000]['dwc_eval']==-6;assert rooms[0x81611000]['dwc_eval']==22239994;assert order[0]==0x81610000
 records.append({'base':hex(base),'case':'higher_room_cap_uses_wrong_display_scale','player_internal_rating':50,'player_displayed_vr':5000,'near_room_vr':5000,'far_room_vr':700000,'removed_rooms':removed,'retained_room_vr':[rooms[x]['ev']for x in order],'actual_threshold':4005000,'documented_40000_displayed_vr_threshold':45000,'control_nearest_room_still_sorts_first':True})
 print('Reproduced candidate edge cases at',hex(base),flush=True)
report={'candidate_sha256':sha,'reproduced':True,'records':records,'limits':['PAL isolated compiled functions; game/native/controller/server APIs mocked','WAITING finding assumes an old callback remains pending; actual native timeout behavior is not established','No assertion that the user experienced any of these cases; no live server changed']}
a.report.write_text(json.dumps(report,indent=2)+'\n')
