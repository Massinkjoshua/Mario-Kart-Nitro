from native_probe import *
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--heap',type=lambda x:int(x,0),default=0xe1000);parser.add_argument('--post',default='fk-7');parser.add_argument('--battle',action='store_true');parser.add_argument('--screens',type=int,default=1);parser.add_argument('--patched',action='store_true');args=parser.parse_args()
rt=Runtime();rt.wr(0x808b4bf0,args.screens)
if args.patched:
 b=(ROOT/'work/crash-repair/Code.pul').read_bytes();length=u32(b);instruction=u32(b,16+length-4);assert b[16+length-12:16+length]==struct.pack('>III',0x20fffffe,0x80542310,instruction);rt.wr(0x80542310,instruction);args.heap=((instruction&0xffff)<<16)+0x1000
rt.call(0x800aef60,0x80384320,0x20)
heap=rt.call(0x80226a1c,0x91000000,args.heap,0);memheap=rt.rd(heap+0x10)
sceneheap=rt.call(0x80226a1c,0x91400000,0x200000,0)
scnAllocator=rt.call(0x80226c04,sceneheap,28,4);rt.call(0x8020f62c,scnAllocator,sceneheap,32)
manager=0x817b0000;renderer=0x817b1000;fakevt=0x817b2000
rt.wr(0x809c1850,manager);rt.wr(manager,0x808b4ad0);rt.wr(manager+0x10,heap)
rt.wr(manager+0x30,renderer);rt.wr(renderer+0xb4,fakevt);rt.wr(fakevt+0x18,0x8023cec8)
rt.wr(renderer+0xc8,0x817b3000)
rt.wr(renderer+4,0x817b3500)
rt.wr(0x817b3520,0x817b3600)
rt.wr(renderer+0xc4,0x817b3100);rt.wr(0x817b3104,0x817b3200)
rt.wr(manager+0x3c,0x817b3300);rt.wr(0x817b3300,0x817b3400)
for off,link in [(0x44,0x1c),(0x58,0x2c),(0x64,0x34),(0x70,0x2c)]:rt.call(0x800aef60,manager+off,link)
for i in range(2):
 root=rt.call(0x8006e390,scnAllocator,0,128);rt.wr(manager+0x28+4*i,root)
menumgr=0x817b4000;drivers=0x817b4100;karts=0x817b4200
rt.wr(0x809c1988,menumgr);rt.wr(menumgr+0x14,drivers);rt.wr(menumgr+0x18,karts)
rt.wr(drivers+0x18,22);rt.wr(karts+0x14,2)
# I/O is replaced by the supplied decompressed archive. No allocations are mocked.
sys.path.insert(0,'/tmp');from unpack import dec
archive_path=ROOT/f'work/crash-investigation/MKNitro_Combined_Update_v9/Install/Characters/VariantAllKart/{args.post}-allkart{"_BT" if args.battle else ""}.szs'
raw=dec(archive_path.read_bytes());rawptr=rt.call(0x80226c04,heap,len(raw),32);assert rawptr
rt.uc.mem_write(rawptr,raw)
root=u32(raw,4);count=u32(raw,root+8);strings=root+12*count
entries={}
for i in range(1,count):
 typ,off,size=struct.unpack_from('>III',raw,root+12*i)
 if typ>>24:continue
 p=strings+(typ&0xffffff);name=raw[p:raw.index(0,p)].decode()
 entries[name]=(rawptr+off,size)
rt.current_res=0;allocs=[];failed=[];last_request={}
# Hardware/scene predicates and fog registration are outside this allocation test.
def boundary(e,a,n,o):
 r3=e.reg_read(UC_PPC_REG_3)
 if a==0x8081e548:
  rt.wr(r3+4,rt.current_res);e.reg_write(UC_PPC_REG_3,1)
 elif a==0x808605fc:e.reg_write(UC_PPC_REG_3,2)
 elif a==0x80860a8c:e.reg_write(UC_PPC_REG_3,0)
 elif a==0x8081cfb4:e.reg_write(UC_PPC_REG_3,1)
 elif a==0x8022eaa4:pass
 elif a==0x80198d88:
  last_request.update(heap=r3,size=e.reg_read(UC_PPC_REG_4),alignment=e.reg_read(UC_PPC_REG_5));return
 elif a==0x80198e24:
  allocs.append({**last_request,'returned':r3})
  if r3==0:failed.append(allocs[-1])
  return
 else:return
 e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
rt.uc.hook_add(UC_HOOK_CODE,boundary)
array=rt.call(0x80226c04,heap,(len(entries)-1)*0x2c+16,4)
results=[]
try:
 for i,name in enumerate(sorted(n for n in entries if n!='driver_anim.brres')):
  rt.current_res=entries[name][0];obj=array+16+0x2c*i
  rt.call(0x80831f60,obj)
  ret=rt.call(0x80831fc4,obj,0,22,i,heap,128,128)
  director=rt.rd(obj+4);models=[rt.rd(rt.rd(director+0x14+j*4)) for j in range(2)]
  assert all(models)
  remaining=rt.call(0x80199180,memheap,32)
  row={'vehicle':name,'remaining':remaining,'scene_models':[hex(m) for m in models]};results.append(row);print(row,flush=True)
except Exception as e:
 print('FAIL',name,str(e),'remaining',rt.call(0x80199180,memheap,32),'failed_allocations',failed,flush=True)
 print('registers',[(i,hex(rt.uc.reg_read(UC_PPC_REG_0+i))) for i in range(3,13)])
 raise
print('ALL_LOADED',args.post,'heap',args.heap,'remaining',remaining,'allocation_calls',len(allocs),'failures',failed)
assert not failed
report={'post':args.post,'battle':args.battle,'screens':args.screens,'heap_bytes':args.heap,'remaining_bytes':remaining,'allocation_calls':len(allocs),'vehicles':len(results),'null_allocations':failed}
(ROOT/'work/crash-repair'/f'load-{args.post}-{int(args.battle)}-{args.screens}.json').write_text(json.dumps(report,indent=2)+'\n')
