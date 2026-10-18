"""Validate candidate PUL structure/hooks and execute selected actual PPC code.
Native networking, rendering and rating getters are stubbed. No live game test.
"""
import hashlib
import importlib.util
import json
import struct
from collections import Counter
from pathlib import Path
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.ppc_const import UC_PPC_REG_0, UC_PPC_REG_1, UC_PPC_REG_3, UC_PPC_REG_LR, UC_PPC_REG_PC, UC_PPC_REG_MSR
ROOT=Path(__file__).resolve().parents[1]
def word(raw, off): return struct.unpack_from('>I',raw,off)[0]
def parse(raw):
    sizes=struct.unpack_from('>4I',raw); assert sum(sizes)+16==len(raw)
    blocks=[]; start=16
    widths={1:4,4:4,5:4,6:4,10:4,32:4,33:4,34:4,35:8,36:8,37:8,38:8,64:4,65:4}
    for size in sizes:
        if not size: blocks.append(None); continue
        b=raw[start:start+size]; start+=size
        assert b[:8]==b'Kamek\0\0\2'
        code=b[32:32+word(b,12)]; commands=[]; pos=32+len(code)
        assert 0<=word(b,16)<=word(b,20)<=len(code)
        while pos<len(b):
            header=word(b,pos);pos+=4;t=header>>24;a=header&0xffffff
            assert t in widths
            absolute=a==0xfffffe
            if absolute:a=word(b,pos);pos+=4
            n=widths[t];assert pos+n<=len(b)
            args=struct.unpack_from('>'+str(n//4)+'I',b,pos);pos+=n
            if not absolute:
                target_width=2 if t in [4,5,6,33,37] else 1 if t in [34,38] else 4
                assert a+target_width<=len(code)+word(b,8)
            commands.append((t,a,args,absolute))
        assert pos==len(b)
        blocks.append((b,code,commands))
    return blocks
candidate=(ROOT/'build/Code.pul').read_bytes(); baseline=(ROOT/'Reference/Code-10-UNCHANGED.pul').read_bytes()
new=parse(candidate); old=parse(baseline); b,code,commands=new[0]
absolute=[(t,a,v) for t,a,v,external in commands if external]
assert max(Counter(a for t,a,v in absolute).values())==1
old_addresses={a for t,a,v,external in old[0][2] if external}
new_addresses={a for t,a,v in absolute}
# Only a recovered allocation diagnostic hook remains absent. It is not gameplay.
assert old_addresses-new_addresses=={0x8081ee34}, sorted(old_addresses-new_addresses)
checks=json.loads((ROOT/'PulsarEngine/Security/NitroIntegrity/manifest_review.json').read_text())['checks']
widths={1:4,4:2,5:2,6:2,10:4,32:4,33:2,34:1,35:4,36:4,37:2,38:1,64:4,65:4}
for check in checks:
    addr=int(check['address'],16)
    assert not any(addr < a+widths[t] and addr+4 > a for t,a,v in absolute)
patches={a:(t,v[0]) for t,a,v in absolute}
for address in [0x80543bb4,0x800ed6e8,0x80662d80,0x80662dc4,0x807eede0,0x808d3cdc,0x808d3ce4]: assert address in patches
assert patches[0x807e2714]==(32,0x3bc0001a)
assert patches[0x80542310]==(32,0x3f400012)
# Actual rating getter offsets, from the linker map.
maprows=(ROOT/'build/Code.map').read_text().splitlines()
def symbol(prefix):
    rows=[line.split() for line in maprows if len(line.split())==3 and line.split()[2].startswith(prefix)]
    assert len(rows)==1,(prefix,rows)
    return int(rows[0][0],16)
vr=symbol('GetUserVR__');br=symbol('GetUserBR__')
class Machine:
    def __init__(self,base):
        self.base=base; self.uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);u=self.uc
        u.mem_map(0x80000000,0x1800000);u.mem_map(0x83000000,0x10000)
        relocated=bytearray(code+bytes(word(b,8)))
        for t,a,v,external in commands:
            if external:continue
            target=v[0] if v[0]&0x80000000 else base+v[0]
            if t==1:struct.pack_into('>I',relocated,a,target)
            elif t in (4,5,6):
                value=target if t==4 else target>>16 if t==5 else (target+0x8000)>>16
                struct.pack_into('>H',relocated,a,value&0xffff)
            elif t in (10,64,65):
                opcode=(word(relocated,a)&0xfc000003) if t==10 else (0x48000001 if t==65 else 0x48000000)
                struct.pack_into('>I',relocated,a,opcode|((target-base-a)&0x3fffffc))
            elif t in (32,33,34):
                n=4 if t==32 else 2 if t==33 else 1
                relocated[a:a+n]=(v[0]&((1<<(8*n))-1)).to_bytes(n,'big')
            else:raise AssertionError(('unexpected internal command',t,hex(a)))
        u.mem_write(base,bytes(relocated));u.reg_write(UC_PPC_REG_MSR,0x2000)
    def w(self,a,v):self.uc.mem_write(a,struct.pack('>I',v))
    def call(self,offset,*args):
        u=self.uc;end=0x81700000;stack=0x8300f000
        u.reg_write(UC_PPC_REG_1,stack);u.reg_write(UC_PPC_REG_LR,end)
        for i in range(14,32):u.reg_write(UC_PPC_REG_0+i,0x12340000+i)
        for i,v in enumerate(args):u.reg_write(UC_PPC_REG_3+i,v)
        u.emu_start(self.base+offset,end,count=10000)
        assert u.reg_read(UC_PPC_REG_PC)==end
        assert u.reg_read(UC_PPC_REG_1)==stack and u.reg_read(UC_PPC_REG_LR)==end
        for i in range(14,32):assert u.reg_read(UC_PPC_REG_0+i)==0x12340000+i
count=0
for base in [0x803992e0,0x81000000]:
    m=Machine(base)
    for site,getter,field in [(0x80662d80,vr,0xc0),(0x80662dc4,br,0xc2)]:
        # Getter test double returns f1; wrapper conversion/store is candidate PPC.
        m.uc.mem_write(base+getter,struct.pack('>3I',0x3c608300,0xc0233000,0x4e800020))
        for license_id in [-1,0,1,2,3,4]:
            for rating in [1.,50.,50.37,9999.99,10000.]:
                m.w(0x809bd748,0x83001000)
                m.uc.mem_write(0x83001036,struct.pack('>h',license_id))
                m.uc.mem_write(0x83003000,struct.pack('>f',rating))
                m.uc.mem_write(0x83004000,b'\xa5'*0x100)
                m.call(patches[site][1],0x83004000)
                expected=bytearray(b'\xa5'*0x100)
                if 0<=license_id<=3:struct.pack_into('>H',expected,field,int(rating))
                assert bytes(m.uc.mem_read(0x83004000,0x100))==expected
                count+=1
        m.w(0x809bd748,0);m.uc.mem_write(0x83004000,b'\xa5'*0x100)
        m.call(patches[site][1],0x83004000);assert bytes(m.uc.mem_read(0x83004000,0x100))==b'\xa5'*0x100;count+=1
# Execute the actual item-window draw/empty decision with native getter/draw mocked.
item_cases=0
for base in [0x803992e0,0x81000000]:
    m=Machine(base); events=[]
    for addr in [0x807ec7f8,0x8063db84]:m.uc.mem_write(addr,struct.pack('>I',0x4e800020))
    def hook(u,addr,size,data):
        if addr==0x807ec7f8:u.reg_write(UC_PPC_REG_3,0)
        if addr==0x8063db84:events.append('draw')
    m.uc.hook_add(UC_HOOK_CODE,hook)
    m.w(0x809c3618,0x83001000);m.uc.mem_write(0x83001010,b'\1');m.w(0x83001014,0x83002000)
    for item in [0,10,20]:
        for quantity in [0,1,3]:
            for spinning in [0,1]:
                for golden in [0,1]:
                    events.clear();m.uc.mem_write(0x83003000,bytes(0x1bc));m.uc.mem_write(0x83002000,bytes(0x248))
                    m.w(0x8300208c,item);m.w(0x83002090,quantity);m.w(0x83002058,spinning)
                    m.uc.mem_write(0x830020a4,bytes([golden]));m.uc.mem_write(0x830020aa,struct.pack('>H',100 if golden else 0))
                    m.call(patches[0x808d3cdc][1],0x83003000,0)
                    empty=(item==20 or (quantity==0 and not(item==10 and golden))) and not spinning
                    assert bool(events)==(not empty),(item,quantity,spinning,golden,events)
                    item_cases+=1
report={'candidate_sha256':hashlib.sha256(candidate).hexdigest(),
        'baseline_sha256':hashlib.sha256(baseline).hexdigest(),
        'region_lengths':list(struct.unpack_from('>4I',candidate)),
        'unique_pal_absolute_sites':len(absolute),'selected_manifest_overlap':[],
        'baseline_absolute_site_absent':['0x8081ee34 (allocation diagnostic)'],
        'new_absolute_sites':[hex(a) for a in sorted(new_addresses-old_addresses)],
        'ppc_rating_wrapper_cases':count,'ppc_item_window_cases':item_cases,
        'limitations':['Native calls stubbed; no Dolphin/Wii/network execution.',
                       'Hook address coverage does not prove equivalent hook bodies/assets or complete pack parity.',
                       'Original manifest still targets Code(10); final candidate/runtime baseline review remains required.',
                       'Other regions rebuilt; their runtime behavior has not been validated.']}
(ROOT/'Verification/candidate-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: Kamek v2 modules, unique patch sites, no selected manifest overlap; {count} rating and {item_cases} item-window candidate PowerPC execution cases (native calls mocked).')
