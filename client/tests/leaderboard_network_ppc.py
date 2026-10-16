#!/usr/bin/env python3
"""Released PAL request functions versus recovered source, controlled callees.
GPLv3. Does not execute real HTTP, allocator internals, rendering or a game boot.
"""
import argparse,hashlib,json,re
from recovered_remaining_ppc import Controlled,ROOT
from recovered_runtime_ppc import reg
from leaderboard_parser_ppc import install_libc,cbytes,RELEASE_SHA

def symbols(path):
 out={}
 for line in path.read_text().splitlines():
  m=re.match(r'\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]+)\s+(.+)',line)
  if m:out[m[3]]=int(m[1],16)
 return out

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--profile-dir',type=__import__('pathlib').Path,default=ROOT/'build/released-leaderboard');args=parser.parse_args();profile=args.profile_dir
 released=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();assert hashlib.sha256(released).hexdigest()==RELEASE_SHA
 recovered=(profile/'Code.pul').read_bytes();sm=symbols(profile/'Code.map')
 def exact(prefix):
  found=[v for k,v in sm.items()if k.startswith(prefix+'__')];assert len(found)==1,prefix;return found[0]
 old={'state':0x92fd4,'start':0x49f3c,'received':0x4a140,'activate':0x4965c,'deactivate':0x4971c,'prepare':0x5dacc,'mark':0x5db28,'finish':0x5db3c,'alloc':0x5da24,'free':0x5da54,'override':0x4a610,'reset':0x49a90,'url':0x48,'create':0xc65fc}
 new={'state':exact('s_fetchState'),'start':exact('StartFetch'),'received':exact('OnLeaderboardReceived'),'activate':sm['OnActivate__Q36Pulsar2UI17VRLeaderboardPageFv'],'deactivate':sm['OnDeactivate__Q36Pulsar2UI17VRLeaderboardPageFv'],'prepare':exact('PreparePersistentNHTTPRequest'),'mark':exact('MarkNHTTPRequestActive'),'finish':exact('FinishNHTTPRequest'),'alloc':exact('NHTTPAlloc'),'free':exact('NHTTPFree'),'override':exact('OverrideOwnMiiData'),'reset':exact('ResetRowsToLoading'),'url':0x4060,'create':0x801d8ff8}
 executions=0;case_names=[]
 for base in(0x81000000,0x81200000):
  machines=[(Controlled(released,base),old),(Controlled(recovered,base),new)]
  def init(h,pos):
   h.handlers.clear();install_libc(h);h.instruction_limit=2000000;s=base+pos['state'];h.cpu.mem_write(s,b'\0'*0x48)
   h.word(s+8,0x81600000);h.word(s+0x1c,7);h.word(s+0x2c,9);h.word(s+0x30,42);h.byte(s+4,1)
   h.cpu.mem_write(0x81600000,b'\xa5'*0x1c20);h.word(0x809bd748,0)
   h.cpu.mem_write(0x81620000,b'\0'*0x200);h.cpu.mem_write(0x81630000,b'\0'*0x10000)
   return s
  for page in(0,4,5,49):
   for scenario in('requesting','null_page','null_entries','startup_failure','create_failure','send_failure','success','license_0','license_3','reused_buffer'):
    results=[]
    for h,pos in machines:
     s=init(h,pos);h.byte(0x816200ac,page)
     if scenario=='requesting':h.word(s,1)
     if scenario=='null_entries':h.word(s+8,0)
     if scenario=='reused_buffer':h.word(s+0x40,0x81640000);h.cpu.mem_write(0x81640000,b'\xff'*0x4000)
     if scenario.startswith('license_'):
      license_id=int(scenario[-1]);h.word(0x809bd748,0x81650000);h.cpu.mem_write(0x81650036,license_id.to_bytes(2,'big'))
     def clock(h=h):h.calls.append(('time',));h.result(0x123);h.cpu.reg_write(reg(4),0x456)
     def key(h=h):h.call('friend_key',1);h.result(0x12);h.cpu.reg_write(reg(4),0x34567890)
     def prepare(h=h,s=s):
      assert h.registers(1)==(s+0x18,);h.calls.append(('prepare',));h.byte(s+0x18,scenario!='startup_failure');h.result(scenario!='startup_failure')
     def snprintf(h=h):
      dst,n,fmt,value=h.registers(4);assert cbytes(h,fmt)==b'http://play.mknitro.com/api/leaderboard/in-game?page=%u';assert n==256
      text=('http://play.mknitro.com/api/leaderboard/in-game?page=%u'%value).encode();h.cpu.mem_write(dst,text+b'\0');h.result(len(text))
     def create(h=h,s=s,pos=pos):
      url,method,buf,n,callback,ctx=h.registers(6)
      assert callback==base+pos['received']and ctx==s+0x38
      assert n==0x4000 and method==0 and buf%32==0 and h.data(buf,n)==b'\0'*n
      assert h.read(ctx)==8 and h.read(ctx+4)==page//5+1
      h.calls.append(('create',cbytes(h,url).decode(),method,n));h.result(0 if scenario=='create_failure'else 0x81670000)
     def send(h=h):h.call('send',1);h.result(0xffffffff if scenario=='send_failure'else 7)
     h.handlers.update({0x801aad5c:clock,0x800ec6bc:key,base+pos['prepare']:prepare,0x80011938:snprintf,(base+pos['create']if pos['create']<0x80000000 else pos['create']):create,0x801d925c:send,base+pos['mark']:lambda h=h:h.calls.append(('mark',))})
     h.run(pos['start'],0 if scenario=='null_page'else 0x81620000);executions+=1
     expected={'requesting':1,'null_page':5,'null_entries':5,'startup_failure':6,'create_failure':8,'send_failure':9}.get(scenario,1)
     assert h.read(s)==expected,(scenario,h.read(s))
     if scenario in('requesting','null_page','null_entries'):assert h.calls==[]
     else:
      assert h.read(s+0x1c)==8 and h.data(0x81600000,0x1c20)==b'\0'*0x1c20
      assert h.data(s+0x10,8)==bytes.fromhex('0000012300000456')
      if scenario.startswith('license_'):
       assert ('friend_key',(0x81650000+int(scenario[-1])*0x93f0+0x8ff0,))in h.calls,(scenario,h.calls)
       assert h.data(s+0x20,8)==bytes.fromhex('0000001234567890')
      if scenario in('success','license_0','license_3','reused_buffer'):assert h.calls[-2:]==[('send',(0x81670000,)),('mark',)]
      elif scenario=='send_failure':assert h.calls[-1]==('send',(0x81670000,))and h.data(s+0x18,1)==b'\0'
     # Pointer addresses differ between allocations; compare semantic state and trace.
     results.append((h.data(s,8),h.data(s+0x10,0x30),h.calls))
    assert results[0]==results[1],(scenario,page,'start mismatch')
    case_names.append(f'start:{page}:{scenario}')
  callback_cases=['null_context','stale_generation','null_response','stale_null_response','missing_entries','http_error','null_body','empty_body','negative_length','allocation_failure','empty_array','one_entry','fifty_entries']
  for scenario in callback_cases:
   results=[]
   for h,pos in machines:
    s=init(h,pos);h.word(s,1);h.word(s+0x38,6 if scenario in('stale_generation','stale_null_response')else 7);h.word(s+0x3c,3)
    if scenario=='missing_entries':h.word(s+8,0)
    payload=json.dumps([{'name':f'P{i}','vr':7000+i,'friendCode':'1234-5678-9012'}for i in range(50 if scenario=='fifty_entries'else 1)]).encode()
    if scenario=='empty_array':payload=b'[]'
    h.cpu.mem_write(0x81630000,payload+b'\0');h.word(s+0x20,0x12);h.word(s+0x24,0x34567890)
    def body(h=h):
     response,out=h.registers(2);assert response==0x81670000;h.calls.append(('body',))
     h.word(out,0 if scenario=='null_body'else 0x81630000);h.result(0 if scenario=='empty_body'else 0xffffffff if scenario=='negative_length'else len(payload))
    def allocate(h=h):h.call('alloc',2);h.result(0 if scenario=='allocation_failure'else 0x81640000)
    def free(h=h):
     h.call('free',1);assert h.data(0x81640000,len(payload)+1)==payload+b'\0'
    h.handlers.update({base+pos['finish']:lambda h=h:h.calls.append(('finish',)),0x801d92f8:lambda h=h:h.call('destroy',1),0x801d937c:body,base+pos['alloc']:allocate,base+pos['free']:free,base+pos['override']:lambda h=h:h.call('override',4)})
    response=0 if scenario in('null_response','stale_null_response')else 0x81670000
    h.run(pos['received'],9 if scenario=='http_error'else 0,response,0 if scenario=='null_context'else s+0x38);executions+=1
    state={'null_context':1,'stale_generation':1,'stale_null_response':1,'null_response':10,'missing_entries':11,'http_error':12,'null_body':13,'empty_body':13,'negative_length':13,'allocation_failure':14,'empty_array':15,'one_entry':2,'fifty_entries':2}[scenario]
    assert h.read(s)==state,(scenario,h.read(s),state);assert h.calls[0]==('finish',)
    assert sum(call[0]=='destroy'for call in h.calls)==int(response!=0)
    if scenario in('one_entry','fifty_entries','empty_array'):
     count=50 if scenario=='fifty_entries'else 1 if scenario=='one_entry'else 0
     assert h.read(s+0x30)==count and h.read(s+0x2c)==3
     assert [c[0]for c in h.calls]==['finish','body','alloc','destroy','free']+(['override']if count else[])
     if count:
      assert h.calls[-1]==('override',(0x81600000,count,0x12,0x34567890))and h.data(s+4,1)==b'\0'
    results.append((h.data(s,0x40),h.data(0x81600000,0x1c20),h.calls))
   assert results[0]==results[1],(scenario,'callback mismatch')
   case_names.append('callback:'+scenario)
  for entries in(0,0x81600000):
   for generation in(0,7,0xffffffff):
    results=[]
    for h,pos in machines:
     s=init(h,pos);h.word(s+8,entries);h.word(s+0x1c,generation);h.word(s+0x20,1);h.word(s+0x24,2);h.word(s+0x28,8)
     h.handlers[0x80229ee0]=lambda h=h:h.call('delete_entries',1)
     h.run(pos['deactivate'],0x81620000);executions+=1
     assert h.calls==[('delete_entries',(entries,))]
     assert h.read(s+0x1c)==(generation+1)&0xffffffff
     for offset in(0,8,0x20,0x24,0x28,0x2c,0x30):assert h.read(s+offset)==0
     results.append((h.data(s,0x40),h.calls))
    assert results[0]==results[1]
    case_names.append(f'deactivate:{entries}:{generation}')
  for scenario in('existing_entries','allocate_entries','missing_heap','allocation_failure'):
   results=[]
   for h,pos in machines:
    s=init(h,pos)
    if scenario!='existing_entries':h.word(s+8,0)
    h.word(0x802a40a4,0 if scenario=='missing_heap'else 0x81671000)
    h.handlers[base+pos['reset']]=lambda h=h:h.call('reset_rows',1)
    h.handlers[base+pos['start']]=lambda h=h:h.call('start_fetch',1)
    h.handlers[0x80602cf8]=lambda h=h:h.call('sound',3)
    h.handlers[0x80229e04]=lambda h=h:(h.call('new_entries',3),h.result(0 if scenario=='allocation_failure'else 0x81600000))
    h.run(pos['activate'],0x81620000);executions+=1
    assert h.read(s)==(4 if scenario in('missing_heap','allocation_failure')else 0)
    assert h.calls[0]==('reset_rows',(0x81620000,))
    if scenario in('existing_entries','allocate_entries'):assert h.calls[-2:]==[('sound',(0x81620000,7,0xffffffff)),('start_fetch',(0x81620000,))]
    results.append((h.data(s,0x40),h.data(0x816200a8,8),h.calls))
   assert results[0]==results[1],(scenario,'activate mismatch')
   case_names.append('activate:'+scenario)
  print('PASS released request flow at',hex(base),flush=True)
 report={'passed':True,'executions':executions,'distinct_cases':len(set(case_names)),'cases':sorted(set(case_names)),'release_sha256':hashlib.sha256(released).hexdigest(),'recovered_profile_sha256':hashlib.sha256(recovered).hexdigest(),'functions':['OnActivate','OnDeactivate','StartFetch','OnLeaderboardReceived'],'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((ROOT/'Recovery/ReleasedLeaderboard/PulsarEngine').rglob('*'))if p.is_file()},'limits':['PAL isolated functions; synthetic responses and controlled native/callee boundaries','Request creation boundary abstracts the released MEM2 wrapper and candidate native creator; their internal parity is not established here','Allocation, request bookkeeping, own-Mii override, UI reset and sound are intercepted','Original historical request ordering is preserved; this does not make it concurrency-safe','Other functions in the recovery module are historical v5 source, not certified latest-release equivalents','Not a complete current client source build or deployable game release']}
 (ROOT/'docs/leaderboard-network-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'PowerPC executions;',len(set(case_names)),'distinct cases')
if __name__=='__main__':main()
