#!/usr/bin/env python3
"""Four isolated PAL released/source-built functions; GPLv3, 16 October 2026.
Native APIs and selected callees are intercepted. This is not a game boot.
Local binary references are intentionally absent from the public source tree.
"""
import hashlib,json,re
from recovered_remaining_ppc import Controlled,ROOT
from nitro_formats import kamek

def reloc(data,off,size):
 return[c for c in kamek(data)['regions'][0]['commands']if not c['absolute']and off<=c['address']<off+size]
def globals_for(data,off,size):
 return list(dict.fromkeys(c['values'][0]for c in reloc(data,off,size)if c['command_id']==6))
def main():
 old_data=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes();new_data=(ROOT/'build/Code.pul').read_bytes()
 assert hashlib.sha256(old_data).hexdigest()=='58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364'
 mapping={}
 for line in(ROOT/'build/Code.map').read_text().splitlines():
  m=re.match(r'\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]+)\s+(.+)',line)
  if m:mapping[m[3]]=(int(m[1],16),int(m[2],16))
 names={'challenge':'OnChallengeGhostPress__Q36Pulsar2UI14ExpGhostSelectFR10PushButtonUi','replay':'OnWatchReplayPress__Q36Pulsar2UI14ExpGhostSelectFR10PushButtonUi','local':'PatchIsLocalCheck__6PulsarFRCQ24Kart6Player','emulator':'IsEmulator__7DolphinFv','enable':'EnableGhost__Q36Pulsar6Ghosts3MgrFRC14GhostListEntryb','open':'OpenDolphin__7DolphinFv'}
 # Unique normalized v5 map ranges independently located these released functions.
 released={'challenge':(0x17b38,76),'replay':(0x17b84,76),'local':(0x174e4,44),'emulator':(0x15980,56),'enable':(0x168b0,100),'open':(0x158d4,100)}
 fresh={name:mapping[symbol]for name,symbol in names.items()};executions=0
 for base in(0x81000000,0x81200000):
  old,new=Controlled(old_data,base),Controlled(new_data,base)
  pairs=[(old,old_data,released),(new,new_data,fresh)]
  for tag in('challenge','replay'):
   for page in(0,1,2,7):
    for updated in(None,3):
     for hud in(0,1,3,0xffffffff):
      outputs=[];native_targets=[]
      for h,data,positions in pairs:
       off,size=positions[tag];native=[c['values'][0]for c in reloc(data,off,size)if c['command_id']==10];assert len(native)==1 and native[0]>=0x80000000;native_targets+=native
       targets=globals_for(data,off,size);assert len(targets)==1
       h.word(base+targets[0],0x81630000);h.word(0x81601918,0x81640000);h.word(0x8160191c,page)
       def press(h=h):
        h.call('native_'+tag,3)
        if updated is not None:h.word(0x8160191c,updated);h.word(0x81601918,0x81650000)
       h.handlers[native[0]]=press;h.handlers[base+positions['enable'][0]]=lambda h=h:(h.call('enable',3),h.result(1))
       _,calls=h.run(off,0x81600000,0x81620000,hud);executions+=1
       chosen=page if updated is None else updated;list_base=0x81640000 if updated is None else 0x81650000
       assert calls==[('native_'+tag,(0x81600000,0x81620000,hud)),('enable',(0x81630000,list_base+chosen*16,1))],calls
       outputs.append((calls,h.read(0x8160191c),h.read(0x81601918)))
      assert native_targets[0]==native_targets[1] and outputs[0]==outputs[1]
  for page in(0,0x31,0x32,0x33,0x34,0x35,0x95,0xffffffff):
   for local in(0,1):
    outputs=[]
    for h,data,positions in pairs:
     off,size=positions['local'];assert[c['values'][0]for c in reloc(data,off,size)if c['command_id']==10]==[0x80590650]
     h.word(0x809c1e38,0x81660000);h.word(0x81660000,0x81661000);h.word(0x81661000,page)
     h.handlers[0x80590650]=lambda h=h:(h.call('native_local',1),h.result(local))
     value,calls=h.run(off,0x81662000);executions+=1;blocked=0x32<=page<=0x34
     assert value==(0 if blocked else local) and calls==([]if blocked else[('native_local',(0x81662000,))])
     outputs.append((value,calls))
    assert outputs[0]==outputs[1]
  for checked in(0,1):
   for stored in(0,1):
    for detected in(0,1):
     outputs=[]
     for h,data,positions in pairs:
      off,size=positions['emulator'];targets=globals_for(data,off,size);assert len(targets)==2;flag,result=[base+x for x in targets]
      h.byte(flag,checked);h.byte(result,stored)
      def opened(h=h,flag=flag,result=result):
       h.calls.append(('open_dolphin',));h.byte(flag,1);h.byte(result,detected);h.result(3 if detected else 0xffffffff)
      h.handlers[base+positions['open'][0]]=opened
      value,calls=h.run(off);executions+=1
      assert value==(stored if checked else detected) and calls==([]if checked else[('open_dolphin',)])
      outputs.append((value,calls,h.data(flag,1),h.data(result,1)))
     assert outputs[0]==outputs[1]
 report={'passed':True,'executions':executions,'release_sha256':hashlib.sha256(old_data).hexdigest(),'candidate_sha256':hashlib.sha256(new_data).hexdigest(),'allocation_bases':['0x81000000','0x81200000'],'functions':[names[x]for x in('challenge','replay','local','emulator')],'checked':['native callback occurs before reading updated ghost page/list','ghost entry index and EnableGhost arguments','ghost-viewer section boundaries and local-check forwarding','Dolphin cache and simulated open results'],'limits':['Four isolated PAL functions only','Native APIs, EnableGhost and OpenDolphin intercepted; their internals not validated','No invalid-pointer/page-index fuzzing or full-game test','Does not establish complete client Corresponding Source'],'source_files_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()for name in['PulsarEngine/Ghost/UI/ExpGhostSelect.cpp','PulsarEngine/Ghost/UI/EnhancedReplay.cpp','PulsarEngine/Dolphin/DolphinIOS.cpp']}}
 (ROOT/'docs/core-codegen-emulation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',executions,'released/source-built PowerPC executions across four functions at two bases.')
if __name__=='__main__':main()
