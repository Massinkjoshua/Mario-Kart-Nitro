from pathlib import Path
import ast,struct,json,sys
from unicorn import Uc,UC_ARCH_PPC,UC_MODE_PPC32,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.ppc_const import *
from native_rel import image,REL_BASE,BSS_BASE,read
ROOT=Path('/workspace/scratch/e221e6641538')
manifest=json.loads((ROOT/'work/v5/manifest.json').read_text())
data=(ROOT/'work/v5/Code.pul').read_bytes();length=struct.unpack_from('>I',data)[0];block=data[16:16+length]
def u32(b,p=0):return struct.unpack_from('>I',b,p)[0]
def p32(x):return struct.pack('>I',x)
tree=ast.parse((ROOT/'work/v4/verify_code.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_block'],type_ignores=[]),'loader','exec'))
TOTAL=0;report=[]
for base in (0x81000000,0x817f8000):
 code,external=load_block(block,base)
 uc=Uc(UC_ARCH_PPC,UC_MODE_PPC32|UC_MODE_BIG_ENDIAN)
 uc.mem_map(0x80510000,0x400000);uc.mem_write(REL_BASE,bytes(image[:0x3cd0f4]))
 uc.mem_map(0x809b0000,0x20000);uc.mem_map(base,0x100000);uc.mem_write(base,bytes(code))
 uc.mem_map(0x82000000,0x100000)
 uc.reg_write(UC_PPC_REG_MSR,0x2000)
 PAGE=0x82000000;HEAP=0x82010000;SP=0x820f0000;STOP=0x820ff000
 def wr(a,v):uc.mem_write(a,p32(v))
 def rd(a):return u32(bytes(uc.mem_read(a,4)))
 def fl(a):return struct.unpack('>f',uc.mem_read(a,4))[0]
 events=[]
 def entry_hook(e,a,size,_):
  if a==base+0x157dc:
   # Existing OnActivate calls message/controller services; leave them intact in the
   # delivered code and stub their body here. Native transform recursion is NOT stubbed.
   e.reg_write(UC_PPC_REG_1,e.reg_read(UC_PPC_REG_1)+80)
   e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
  elif a in (0x805f56e0,0x805f5958,0x8055f7d8,0x80557234,0x80557360,0x805573cc,0x80830a5c):
   r3=e.reg_read(UC_PPC_REG_3);r4=e.reg_read(UC_PPC_REG_4);r5=e.reg_read(UC_PPC_REG_5)
   if a==0x8055f7d8:
    wr(r3+0x28,r4);events.append(('bind_transformator',r4))
   elif a==0x80557234:
    wr(0x820e0004,0);e.reg_write(UC_PPC_REG_3,0x820e0000)
   elif a==0x80557360:e.reg_write(UC_PPC_REG_3,0)
   elif a==0x805573cc:events.append(('animation_slot',r4))
   elif a==0x80830a5c:events.append(('mesh_visibility',r3,r4))
   else:events.append(('request_character' if a==0x805f56e0 else 'request_kart',r4,r5))
   e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
 uc.hook_add(UC_HOOK_CODE,entry_hook)
 def call(addr,stop=STOP):
  uc.reg_write(UC_PPC_REG_1,SP);uc.reg_write(UC_PPC_REG_LR,stop)
  try:uc.emu_start(addr,stop,count=100000)
  except Exception:
   print('Failed PC',hex(uc.reg_read(UC_PPC_REG_PC)));raise
  assert uc.reg_read(UC_PPC_REG_PC)==stop
  assert uc.reg_read(UC_PPC_REG_1)==SP
 # Execute the game's recursive transform rebuild on real-shaped parent/child trees.
 for aspect in ('4:3','16:9'):
  for pageid in range(17):
   uc.mem_write(PAGE,bytes(0x50000));wr(PAGE+0x6c4,pageid)
   definition=code[0x64a20+pageid*20:0x64a20+(pageid+1)*20]
   radios,scrollers=definition[8],definition[16];count=radios+scrollers
   records=[];nextmem=HEAP
   def alloc(n):
    global nextmem
    a=nextmem;nextmem+=(n+31)&~31;return a
   def init_control(a,parent,x,y,sx=1.,sy=1.):
    uc.mem_write(a+4,struct.pack('>5fB3x',x,y,0.,sx,sy,255))
    uc.mem_write(a+0x34,struct.pack('>5fB3x',0.,0.,0.,1.,1.,255))
    wr(a+0x64,parent);wr(a+0x70,a);wr(a+0x74,PAGE)
    records.append((a,parent,x,y,sx,sy))
   def children(a,items):
    arr=alloc(4*max(1,len(items)));uc.mem_write(arr,b''.join(p32(v) for v in items) if items else p32(0))
    wr(a+0x68,arr);wr(a+0x6c,arr);wr(a+0x70,a);wr(a+0x74,PAGE);wr(a+0x78,len(items))
   roots=[]
   for i in range(8):
    a=PAGE+0x6c8+i*0x298;roots.append(a);init_control(a,PAGE+0x24,0.,140.-32*i)
    opts=[]
    for j in range(4):
     o=alloc(0x17c);init_control(o,a+0x68,-90.+105*j,0.);children(o,[]);opts.append(o)
    children(a,opts)
   for i in range(5):
    a=PAGE+0x1bb0+i*0x5c8;roots.append(a);init_control(a,PAGE+0x24,0.,-75.+32*i)
    opts=[]
    for x in (-120.,225.,67.):
     o=alloc(0x180);init_control(o,a+0x68,x,0.);opts.append(o)
     if x==67.:
      tx=alloc(0x180);init_control(tx,o+0x68,0.,0.);children(tx,[]);children(o,[tx])
     else:children(o,[])
    children(a,opts)
   arr=alloc(4*len(roots));uc.mem_write(arr,b''.join(p32(v) for v in roots));wr(PAGE+0x24,arr);wr(PAGE+0x28,arr);wr(PAGE+0x30,PAGE);wr(PAGE+0x34,len(roots))
   # Initial native transform reset reproduces the original BRCTR positions.
   uc.reg_write(UC_PPC_REG_3,PAGE+0x24);call(0x805c2a5c)
   local_before={a:bytes(uc.mem_read(a+4,24)) for a,*_ in records}
   anim_before={a:bytes(uc.mem_read(a+0x34,24)) for a,*_ in records}
   uc.reg_write(UC_PPC_REG_3,PAGE);uc.reg_write(UC_PPC_REG_31,0x12345678);call(base+0x157d8)
   assert uc.reg_read(UC_PPC_REG_31)==0x12345678
   step=min(40.,224./max(1,count-1));scale=min(1.,step/40.)
   active=roots[:radios]+roots[8:8+scrollers];row_index={a:i for i,a in enumerate(active)}
   expected={}
   for a,parent,x,y,sx,sy in records:
    if a in row_index:y=140.-row_index[a]*step;sx=sy=scale
    else:assert bytes(uc.mem_read(a+4,24))==local_before[a]
    assert bytes(uc.mem_read(a+0x34,24))==anim_before[a]
    owner=rd(parent+8)
    if owner:
     px,py,psx,psy=expected[owner];x=px+x*psx;y=py+y*psy;sx*=psx;sy*=psy
    expected[a]=(x,y,sx,sy)
    actual=(fl(a+0x4c),fl(a+0x50),fl(a+0x58),fl(a+0x5c))
    assert all(abs(v-w)<.0001 for v,w in zip(actual,expected[a])),(pageid,hex(a),actual,expected[a])
   if base==0x81000000 and aspect=='16:9':report.append({'page':pageid,'radio_rows':radios,'scroller_rows':scrollers,'spacing':step,'scale':scale,'native_parent_child_transforms':'pass'})
   TOTAL+=1
 # Patch exactly the three verified PAL instructions in the native image for execution.
 for h in manifest['hooks'].values():
  assert external[h['site']]==(65,h['offset'])
  target=base+h['offset'];wr(h['site'],0x48000001|((target-h['site'])&0x3fffffc))
 assert read(0x805f4718,4)==bytes.fromhex('48001295')
 assert read(0x805f475c,4)==bytes.fromhex('2c000003')
 assert read(0x805f47c8,4)==bytes.fromhex('4823b3b1')
 # Real NoteModelControl visibility/state branch + native SwitchState and native
 # manager visibility functions. Resource requests and graphics/animation services
 # are recorded at their boundary; this is not a renderer or an ISO boot test.
 for ownerid in (0x6e,0x6f,0x83,0x70):
  for hud in range(4):
   uc.mem_write(PAGE,bytes(0x50000));events.clear()
   note=0x82080000;parent=0x82081000;owner=0x82082000;renderer=0x82083000;mgr=0x82084000;drivers=0x82085000;karts=0x82086000;mdl=0x82087000;director=0x82088000;driverarray=0x82089000;kartarray=0x8208a000;vt=0x8208b000
   uc.mem_write(note,bytes(0xc000));wr(note+0x64,parent);wr(parent+0xc,owner);wr(owner+4,ownerid)
   uc.mem_write(note+0x174,bytes([hud]));uc.mem_write(renderer+0x54+hud*12+8,b'\x01')
   wr(0x809c1988,mgr);wr(mgr+0x14,drivers);wr(mgr+0x18,karts);uc.mem_write(mgr+0x20,b'\x01')
   wr(drivers+4,driverarray);wr(drivers+0x18+hud*12,mdl)
   wr(vt+0x14,0x80830a5c)
   for i in range(4):wr(driverarray+0x28*i,vt)
   uc.mem_write(karts+4,b'\x0c\x04');wr(karts+8+hud*16,kartarray);uc.mem_write(karts+0x11+hud*16,b'\x01')
   for i in range(12):wr(kartarray+0x2c*i,vt)
   wr(mdl+4,director);wr(mdl+8,3);wr(mdl+0xc,0x8208c000);wr(mdl+0x10,0x8208d000);wr(director+0x28,0x8208d000)
   uc.reg_write(UC_PPC_REG_27,note);uc.reg_write(UC_PPC_REG_31,renderer);uc.reg_write(UC_PPC_REG_29,0x16);uc.reg_write(UC_PPC_REG_30,12)
   uc.reg_write(UC_PPC_REG_3,renderer);uc.reg_write(UC_PPC_REG_4,hud)
   call(0x805f470c,0x805f47cc)
   course=ownerid in (0x6e,0x6f)
   assert rd(mdl+8)==(0 if course else 3)
   assert bytes(uc.mem_read(drivers+0x14+hud*12,1))==b'\x01'
   assert bytes(uc.mem_read(karts+0x12+hud*16,1))==bytes([0 if course else 1])
   if course:
    assert ('bind_transformator',0x8208c000) in events
    assert [e[1] for e in events if e[0]=='animation_slot']==[0,1,2]
    assert len([e for e in events if e[0]=='request_character'])==1
   else:assert not any(e[0]=='request_character' for e in events)
   # Next frame should retain standing state without re-requesting models or restarting animations.
   events.clear();uc.reg_write(UC_PPC_REG_3,renderer);uc.reg_write(UC_PPC_REG_4,hud)
   call(0x805f470c,0x805f47cc)
   assert not any(e[0] in ('request_character','request_kart','bind_transformator','animation_slot') for e in events)
   assert rd(mdl+8)==(0 if course else 3)
   TOTAL+=2
   if course:
    # Returning to vehicle selection uses its original native path and must
    # restore the riding transformator and vehicle visibility.
    events.clear();uc.reg_write(UC_PPC_REG_30,note);uc.reg_write(UC_PPC_REG_28,0x16)
    call(0x805f3ecc,0x805f3f40)
    assert rd(mdl+8)==2 and rd(director+0x28)==0x8208d000
    assert bytes(uc.mem_read(karts+0x12+hud*16,1))==b'\x01'
    assert ('bind_transformator',0x8208d000) in events
    # Re-entering course selection then restores standing and hides the vehicle.
    events.clear();uc.reg_write(UC_PPC_REG_29,0x16);uc.reg_write(UC_PPC_REG_30,12)
    uc.reg_write(UC_PPC_REG_3,renderer);uc.reg_write(UC_PPC_REG_4,hud)
    call(0x805f470c,0x805f47cc)
    assert rd(mdl+8)==0 and rd(director+0x28)==0x8208c000
    assert bytes(uc.mem_read(karts+0x12+hud*16,1))==b'\x00'
    TOTAL+=2
print('PASS',TOTAL,'native integration cases')
(ROOT/'work/v5/verification.json').write_text(json.dumps({'passed_cases':TOTAL,'native_routines_executed':['UIControl::ResetPosition (0x8063d3cc)','ControlGroup::ResetControlsPosition (0x805c2a5c)','NoteModelControl visibility/state path','MenuDriverModel::SwitchState','MenuModelMgr visibility functions','MenuKartModelMgr::ToggleVisible'],'stubbed_boundaries':['Original custom SettingsPanel message/controller initialization','Resource loads','Graphics mesh visibility and animation service calls'],'not_tested':'Dolphin rendering, full game boot, actual model assets, race-to-menu transition','settings_pages':report},indent=2))
