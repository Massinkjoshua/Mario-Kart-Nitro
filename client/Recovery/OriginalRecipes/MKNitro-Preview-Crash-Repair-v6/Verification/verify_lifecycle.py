from native_probe import *
# Run the real PAL initialization/reset functions, including parent/child EGG
# heap allocations, native mutexes, lists and disposal. Scene lookup is a fixture.
reports=[]
for players in (1,4):
 for scene_heap in (0,1):
  rt=Runtime();rt.call(0x800aef60,0x80384320,0x20)
  parent=rt.call(0x80226a1c,0x92000000,0x800000,0);memheap=rt.rd(parent+0x10)
  scene=0x817b0000;archives=0x817a0000
  rt.wr(scene+0xc94+4*scene_heap,parent)
  rt.wr(0x80542310,0x3f400012)
  def scene_lookup(e,a,n,o):
   e.reg_write(UC_PPC_REG_3,scene);e.reg_write(UC_PPC_REG_PC,e.reg_read(UC_PPC_REG_LR))
  rt.uc.hook_add(UC_HOOK_CODE,scene_lookup,begin=0x8051bed0,end=0x8051bed0)
  start=rt.call(0x80199104,memheap)
  for cycle in range(3):
   rt.call(0x805422cc,archives,players,scene_heap)
   used=start-rt.call(0x80199104,memheap)
   for hud in range(4):
    heap=rt.rd(archives+0x5b0+24*hud)
    assert bool(heap)==(hud<players)
    if heap:
     assert rt.call(0x80226c90,heap,32)>0x120000
   rt.call(0x805423bc,archives)
   assert all(rt.rd(archives+0x5b0+24*hud)==0 for hud in range(4))
   assert rt.rd(archives+0x610)==0
   assert rt.call(0x80199104,memheap)==start
  row={'local_players':players,'scene_heap_index':scene_heap,'cycles':3,'all_native_heap_memory_recovered':True,'allocated_bytes_including_dump_heap':used};reports.append(row);print(row)
(ROOT/'work/crash-repair/lifecycle.json').write_text(json.dumps(reports,indent=2)+'\n')
