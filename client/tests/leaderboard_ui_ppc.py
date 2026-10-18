#!/usr/bin/env python3
"""Actual released/recovered ApplyError and ApplyResults PPC, controlled UI/RFL.
GPLv3. Text, visibility and Mii bind traces are compared; no real rendering.
"""
import argparse,hashlib,json
from pathlib import Path
from recovered_remaining_ppc import Controlled,ROOT
from leaderboard_network_ppc import symbols
from leaderboard_parser_ppc import RELEASE_SHA,cbytes
from leaderboard_display_ppc import wide

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile-dir',type=Path,default=ROOT/'build/released-leaderboard');a=p.parse_args()
 old=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();new=(a.profile_dir/'Code.pul').read_bytes();assert hashlib.sha256(old).hexdigest()==RELEASE_SHA
 sm=symbols(a.profile_dir/'Code.map')
 def exact(prefix):
  found=[v for k,v in sm.items()if k.startswith(prefix+'__')];assert len(found)==1,prefix;return found[0]
 positions=[{'state':0x92fd4,'error':0x49ebc,'results':0x49b10},{'state':exact('s_fetchState'),'error':exact('ApplyError'),'results':exact('ApplyResults')}]
 executions=0;error_cases=0;result_cases=0
 for base in(0x81000000,0x81200000):
  machines=[(Controlled(old,base),positions[0]),(Controlled(new,base),positions[1])]
  def init(h,pos,page=0,count=0):
   s=base+pos['state'];h.handlers.clear();h.instruction_limit=300000
   h.cpu.mem_write(s,b'\0'*0x38);h.word(s+8,0x81640000);h.word(s+0x30,count)
   h.cpu.mem_write(0x81610000,b'\0'*0x200);h.word(0x81610048,0x81611000);h.word(0x81610078,0x81611200);h.byte(0x816100ac,page)
   for i in range(10):h.word(0x81610050+4*i,0x81620000+i*0x400)
   h.cpu.mem_write(0x81640000,b'\0'*0x1c20);h.cpu.mem_write(0x81670000,b'\0'*0x400)
   for i in range(50):
    entry=0x81640000+i*0x90;h.cpu.mem_write(entry,(f'P{i}'+'\0').encode('utf-16-be'));h.word(entry+0x30,7000+i);h.word(entry+0x34,0 if i%2==0 else i+101);h.byte(entry+0x38,i%2)
   def info():
    ptr=h.registers(1)[0];h.word(ptr+0x9c,0);h.result(ptr)
   def find():
    layout,pane=h.registers(2);h.calls.append(('find',layout,cbytes(h,pane).decode()));h.result(0x81670000)
   def footer():
    row,bmg,info_ptr=h.registers(3);assert bmg==0x2849;h.calls.append(('footer',row,wide(h,h.read(info_ptr+0x9c))))
   def text():
    row,pane,bmg,info_ptr=h.registers(4);assert bmg==0x2849;h.calls.append(('text',row,cbytes(h,pane).decode(),wide(h,h.read(info_ptr+0x9c))))
   def visible():
    row,pane,value=h.registers(3);h.calls.append(('visible',row,cbytes(h,pane).decode(),value))
   def printf():
    dst,n,fmt=h.registers(3);fmt=wide(h,fmt);arg=h.registers(5)[3:]
    if fmt=='#%u':out='#%u'%arg[0]
    elif fmt=='%u':out='%u'%arg[0]
    elif fmt=='< %d/%d >':out='< %d/%d >'%arg
    else:raise AssertionError(('format',fmt))
    assert len(out)<n;h.cpu.mem_write(dst,(out+'\0').encode('utf-16-be'));h.result(len(out))
   def validate():
    ptr=h.registers(1)[0];h.calls.append(('validate',ptr));h.result(h.data(ptr,1)[0])
   h.handlers.update({0x805cd94c:info,0x805e8368:find,0x807e9a38:footer,0x8063dcbc:text,0x8063e54c:visible,0x80017814:printf,0x800cb8b0:validate,0x805fa610:lambda:h.call('load',3),0x8063e3dc:lambda:h.call('bind',5)})
   return s
  messages=['Failed: timeout','Failed: entries','Failed: context','Failed: startup','Failed: workbuf','Failed: create','Failed: send','Failed: response','Failed: entries','Failed: HTTP','Failed: body','Failed: copybuf','Failed: JSON']
  for state in list(range(17))+[0x80000000,0xffffffff]:
   outputs=[]
   for h,pos in machines:
    s=init(h,pos);h.word(s,state);_,calls=h.run(pos['error'],0x81610000);executions+=1
    message=messages[state-3 if 3<=state<=15 else 0];assert [x for x in calls if x[0]=='footer']==[('footer',0x81611000,message)]
    assert len([x for x in calls if x[0]=='text'])==40
    outputs.append(calls)
   assert outputs[0]==outputs[1],('ApplyError',state);error_cases+=1
  for native_error,message in [(1,'Mem: other allocator'),(4,'Create: URL'),(2,'Failed: create')]:
   outputs=[]
   for h,pos in machines:
    state=init(h,pos);h.word(0x816507d8,native_error)
    h.handlers.update({0x801d8ff8:lambda h=h:h.result(0),0x801d9e94:lambda h=h:h.result(0x81650000)})
    creator=0xc65fc if pos is positions[0]else exact('CreateReleasedLeaderboardRequest')
    value,_=h.run(creator,0x81671000,0,0x81672000,0x4000,0x81673000,0x81673100);executions+=1;assert value==0
    h.word(state,8);_,calls=h.run(pos['error'],0x81610000);executions+=1
    assert [x for x in calls if x[0]=='footer']==[('footer',0x81611000,message)]
    outputs.append(calls)
   assert outputs[0]==outputs[1];error_cases+=1
  for page in(0,4,5,49):
   for count in(0,1,9,10,11,49,50):
    outputs=[]
    for h,pos in machines:
     init(h,pos,page,count);_,calls=h.run(pos['results'],0x81610000);executions+=1
     expected_text=[];expected_visible=[];expected_load=[];expected_bind=[];expected_validate=[]
     for i in range(10):
      row=0x81620000+i*0x400;idx=(page%5)*10+i;valid=idx<count
      values=[f'P{idx}','#'+str(idx+101 if idx%2 else page*10+i+1),str(7000+idx),'VR']if valid else['----','','','']
      expected_text.extend(('text',row,pane,value)for pane,value in zip(['player_name','position','total_score','total_point'],values))
      expected_visible.extend(('visible',row,pane,int(valid and idx%2))for pane in['chara_icon','chara_icon_sha'])
      if valid:
       data=0x81640000+idx*0x90+0x38;expected_validate.append(('validate',data))
       if idx%2:
        expected_load.append(('load',(0x81611200,i,data)))
        # The synthetic strings are pointers in different code allocations;
        # compare the bind row/group/index and decode pane names separately.
        expected_bind.extend((row,pane,0x81611200,i,2)for pane in['chara_icon','chara_icon_sha'])
     assert [x for x in calls if x[0]=='text']==expected_text,(page,count,'text')
     assert [x for x in calls if x[0]=='visible']==expected_visible,(page,count,'visibility')
     assert [x for x in calls if x[0]=='load']==expected_load
     assert [x for x in calls if x[0]=='validate']==expected_validate
     binds=[(x[1][0],cbytes(h,x[1][1]).decode(),*x[1][2:])for x in calls if x[0]=='bind'];assert binds==expected_bind
     assert [x for x in calls if x[0]=='footer']==[('footer',0x81611000,f'< {page+1}/50 >')]
     outputs.append([('bind',x[1][0],cbytes(h,x[1][1]).decode(),*x[1][2:])if x[0]=='bind'else x for x in calls])
    assert outputs[0]==outputs[1],('ApplyResults',page,count);result_cases+=1
  print('PASS actual leaderboard UI methods at',hex(base),flush=True)
 report={'passed':True,'executions':executions,'error_cases':error_cases,'result_cases':result_cases,'release_sha256':hashlib.sha256(old).hexdigest(),'source_profile_sha256':hashlib.sha256(new).hexdigest(),'checked':['Real ApplyError and ApplyResults execute with internal helpers','Exact error strings and cleared row text','Page-local entry selection, fallback rank, names/VR/footer text','Invalid Miis hidden and valid Miis loaded and bound','Full canonical UI/native-call trace equality'],'limits':['Native layout, text formatting and RFL APIs controlled; no real rendering','Friend highlighting not exercised: synthetic friend codes are zero','PAL only; not full released-core or game boot']}
 (ROOT/'docs/leaderboard-ui-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'PowerPC UI executions')
if __name__=='__main__':main()
