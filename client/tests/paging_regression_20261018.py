#!/usr/bin/env python3
"""Compiled PAL regression fixtures; native UI/HTTP/browser calls mocked. GPLv3.
Private data offsets verified in this candidate's ELF symbol table; hash-pinned.
"""
import argparse,hashlib,json,re,struct,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--map',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
sys.path[:0]=[str(a.source_root/'tests'),str(a.source_root/'scripts')]
from recovered_remaining_ppc import Controlled
from recovered_runtime_ppc import reg
from leaderboard_parser_ppc import install_libc
from unicorn.ppc_const import UC_PPC_REG_FPR1,UC_PPC_REG_MSR
from capstone import Cs,CS_ARCH_PPC,CS_MODE_32,CS_MODE_BIG_ENDIAN
raw=a.candidate.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='25071c02e4a24e99432627165c87d5be212491f931c0d68e36b9e71d11b54dba'
sm={m[2]:int(m[1],16)for l in a.map.read_text().splitlines()if(m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',l))}
def sym(p):
 v=[v for k,v in sm.items()if k.startswith(p+'__')and(p!='OnUpdate'or '17VRLeaderboardPage'in k)];assert len(v)==1,p;return v[0]
records=[]
for base in (0x81000000,0x81200000):
 h=Controlled(raw,base);s=base+sym('s_fetchState');page=0x81610000
 def setup(state=2,cur=5,button=0,entries=50):
  h.cpu.mem_write(s,b'\0'*0x8158);h.cpu.mem_write(page,b'\0'*0x100);h.word(s,state);h.byte(s+4,1);h.word(s+8,0x81640000);h.word(s+0x28,10);h.word(page+0xac,cur);h.word(s+0x2c,cur//5+1);h.word(s+0x30,entries)
  h.word(0x809c1e38,0x81620000);h.word(0x81620044,0x81621000);h.word(0x81621004,0x81622000);h.word(0x81622000,0x81623000);h.word(0x81623010,0x80003000)
  h.cpu.mem_write(0x8162102e,struct.pack('>H',button));h.cpu.mem_write(0x81621046,b'\0\0')
  h.handlers={0x80003000:lambda:h.result(3),base+sym('ApplyResults'):lambda:h.calls.append(('results',)),base+sym('ApplyError'):lambda:h.calls.append(('error',)),base+sym('ResetRowsToLoading'):lambda:h.calls.append(('loading',)),base+sym('StartFetch'):lambda:h.calls.append(('fetch',)),base+sym('OverrideOwnMiiData'):lambda:None,0x80602cf8:lambda:None,0x807146a8:lambda:None}
  install_libc(h)
 def update():return h.run(sym('OnUpdate'),page)[1]
 def record(case):records.append({'base':hex(base),'case':case,'passed':True})
 for state in (2,3):
  setup(state,5,0x41);calls=update();assert h.read(page+0xac)==4 and ('fetch',)in calls;record('left_from_'+str(state))
 setup(3,6,0x22);calls=update();assert h.read(page+0xac)==6 and ('fetch',)in calls;record('error_retry_same_page')
 for cur in (49,255,256,999,4999998):
  setup(2,cur,0x22);update();assert h.read(page+0xac)==cur+1;record('advance_'+str(cur))
 setup(2,4999999,0x22);update();assert h.read(page+0xac)==4999999;record('api_upper_bound')
 for count in (0,1,9,10,11,49,50):
  for cur in range(5):
   setup(2,cur,0x22,count);update();expected=cur+int(count>(cur+1)*10 or count==50);assert h.read(page+0xac)==expected,(cur,count);record('batch_count_%d_page_%d'%(count,cur))
 setup(2,0,0x41);update();assert h.read(page+0xac)==0;record('left_first_page')
 fixtures=[('empty',b'{"players":[],"success":true}',2),('empty_whitespace',b' { "players" : [ ], "success" : true } ',2),('failure',b'{"players":[],"success":false}',3),('missing_success',b'{"players":[]}',3),('missing_players',b'{"success":true}',3),('truncated',b'{"players":[],"success":true',3),('malformed_bool',b'{"players":[],"success":truejunk}',3),('nonarray',b'{"players":null,"success":true}',3),('junk_suffix',b'{"players":[],"success":true}junk',3),('nonempty',b'{"players":[{"name":"A","rank":501}],"success":true}',2)]
 for name,body,expected in fixtures:
  setup(1,50);h.word(s+0x1c,7);h.word(s+0x814c,7);h.word(s+0x8150,11);h.byte(s+0x8149,1);h.cpu.mem_write(s+0x4040,body+b'\0');update();assert h.read(s)==expected,(name,h.read(s));record('response_'+name)
 # Timed out waiting request retains its owned buffer and exposes navigation.
 for state in (1,4):
  setup(state,5);h.byte(s+0x8148,1);h.word(0x800000f8,243000000)
  def clock():h.cpu.reg_write(reg(3),0);h.cpu.reg_write(reg(4),4000000000)
  def div64():
   hi,lo,dhi,dlo=h.registers(4);v=((hi<<32)|lo)//((dhi<<32)|dlo);h.cpu.reg_write(reg(3),v>>32);h.cpu.reg_write(reg(4),v&0xffffffff)
  h.handlers[0x801aad5c]=clock;h.handlers[0x80021604]=div64
  update();assert h.read(s)==3 and h.data(s+0x8148,1)==b'\x01';record('timeout_state_'+str(state))
 # StartFetch waiting path resets timeout but leaves all request-owned data intact.
 setup(3,7);h.byte(s+0x8148,1);h.cpu.mem_write(s+0x34,b'\xa5'*8);h.handlers.pop(base+sym('StartFetch'))
 h.handlers[0x801aad5c]=clock;h.run(sym('StartFetch'),page);assert h.read(s)==4 and h.data(s+0x34,8)==b'\xa5'*8 and h.read(s+0x14)==4000000000;record('waiting_preserves_context')
 # Fresh request invalidates old entry-cache metadata before a startup failure.
 setup(3,5);h.handlers.pop(base+sym('StartFetch'));h.word(0x809bd748,0);h.handlers[0x801aad5c]=clock;h.handlers[base+sym('PreparePersistentNHTTPRequest')]=lambda:h.result(0)
 h.run(sym('StartFetch'),page);assert h.read(s+0x2c)==0 and h.read(s+0x30)==0 and h.read(s)==3;record('failed_fetch_invalidates_cache')
 # Actual StartFetch uses widened page values in outgoing API URLs.
 for cur,api in [(49,10),(50,11),(255,52),(256,52),(4999999,1000000)]:
  setup(3,cur);h.handlers.pop(base+sym('StartFetch'));h.word(0x809bd748,0);urls=[];active=[0]
  def snprintf():
   dst,n,fmt,value=h.registers(4);text=h.string(fmt).replace('%u',str(value)).encode();h.cpu.mem_write(dst,text[:n-1]+b'\0');h.result(len(text))
  def create():urls.append(h.string(h.registers(1)[0]));h.result(0x81660000)
  h.handlers.update({0x801aad5c:clock,base+sym('PreparePersistentNHTTPRequest'):lambda:h.result(1),base+sym('ClearNHTTPAllocationError'):lambda:None,0x80011938:snprintf,0x801d8ff8:create,base+sym('MarkNHTTPRequestActive'):lambda:active.__setitem__(0,active[0]+1),0x801d925c:lambda:h.result(1)})
  h.run(sym('StartFetch'),page);assert urls==['http://play.mknitro.com/api/leaderboard/in-game?page='+str(api)] and active[0]==1 and h.data(s+0x8148,1)==b'\x01';record('url_page_'+str(cur))
 # Exercise real room filtering and sorting with boundary/fallback controls.
 cases=[('boundary',[5000,45000,45001],False,False,[5000,45000]),('far_fallback',[700000],False,False,[700000]),('only_far_rooms',[700000,900000],False,False,[700000,900000]),('battle_unfiltered',[5000,700000],False,True,[5000,700000]),('infinite_near_small',[5000,700000],True,False,[700000]),('full_room_excluded',[5000,700000],False,False,[700000]),('high_player',[1000000],False,False,[1000000])]
 for name,ratings,infinite,battle,expected in cases:
  h=Controlled(raw,base);h.cpu.reg_write(UC_PPC_REG_MSR,0x2000);h.word(0x8038630c,0x81600000);h.word(0x816006dc,0x81601000);h.word(0x809bd748,0x81602000);h.cpu.mem_write(0x81602036,b'\0\0');h.word(0x809c20d8,0x81603000 if battle else 0)
  if battle:h.word(0x816030e8,3)
  rooms={0x81610000+i*0x1000:{'ev':v,'eb':v,'numplayers':5}for i,v in enumerate(ratings)};order=list(rooms)
  if name=='infinite_near_small':rooms[order[0]]['numplayers']=1
  if name=='full_room_excluded':rooms[order[0]]['numplayers']=11
  def getint():
   server,key,default=h.registers(3);h.result(rooms[server].get(h.string(key),default)&0xffffffff)
  def setint():
   server,key,value=h.registers(3);rooms[server][h.string(key)]=struct.unpack('>i',struct.pack('>I',value))[0]
  def vr():h.cpu.reg_write(UC_PPC_REG_FPR1,struct.unpack('>Q',struct.pack('>d',10000.0 if name=='high_player'else 50.0))[0])
  target=next(int(i.op_str,16)for i in Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN).disasm(h.data(base+sym('CustomRandomizeServers'),120),base+sym('CustomRandomizeServers'))if i.mnemonic=='bl')
  h.handlers={target:lambda:h.result(int(infinite)),base+sym('GetUserVR'):vr,base+sym('GetUserBR'):vr,0x8011e488:lambda:h.result(len(order)),0x8011e480:lambda:h.result(order[h.registers(2)[1]]),0x8011d2b0:getint,0x8011d1e4:setint,0x8011e490:lambda:order.sort(key=lambda x:rooms[x]['dwc_eval']),0x8011e384:lambda:order.remove(h.registers(2)[1])}
  h.run(sym('CustomRandomizeServers'));assert [rooms[x]['ev']for x in order]==expected,(name,order);record('rooms_'+name)
 print('PASS',hex(base),flush=True)
a.report.write_text(json.dumps({'candidate_sha256':sha,'passed':True,'executions':len(records),'records':records,'limits':['PAL compiled functions with controlled native calls; not Dolphin/Wii or live HTTP','API page bound is 1,000,000 batches, 50 rows each; no server or website changes']},indent=2)+'\n')
print('PASS',len(records),'scenario executions')
