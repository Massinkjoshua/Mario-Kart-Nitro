#!/usr/bin/env python3
"""Compare real reconstructed PowerPC hooks with the released PowerPC functions.

Only isolated functions run. Native model loading/rendering/heap calls are
intercepted, so this does not test real game rendering, allocation or gameplay.
Mario Kart Nitro, 16 October 2026; GPLv3.
"""
from pathlib import Path
import json, re, struct, sys
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.ppc_const import UC_PPC_REG_0, UC_PPC_REG_LR, UC_PPC_REG_PC
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from nitro_formats import kamek

def reg(index): return UC_PPC_REG_0 + index

class Harness:
    STOP = 0x80001000
    def __init__(self, data, base):
        self.cpu = Uc(UC_ARCH_PPC, UC_MODE_32 | UC_MODE_BIG_ENDIAN)
        self.cpu.mem_map(0x80000000, 0x1800000)
        self.base = base; self.calls = []; self.player_id = 0
        region = kamek(data)['regions'][0]
        text = data[region['offset']+32:region['offset']+32+region['code_size']]
        self.cpu.mem_write(base, text)
        self.end = base + region['code_size'] + region['bss_size']
        for command in region['commands']:
            if command['absolute']: continue
            address = base + command['address']; value = command['values'][0]
            target = value if value >= 0x80000000 else base + value
            kind = command['command_id']
            if kind == 1: self.word(address, target)
            elif kind in (4,5,6):
                value = (target & 65535) if kind == 4 else ((target >> 16) if kind == 5 else ((target+0x8000) >> 16))
                self.cpu.mem_write(address, struct.pack('>H', value & 65535))
            elif kind in (10,64,65):
                old = self.read(address) if kind == 10 else 0x48000000 | int(kind == 65)
                self.word(address, (old & 0xfc000003) | ((target-address) & 0x03fffffc))
            elif kind in (32,33,34):
                size = {32:4,33:2,34:1}[kind]
                self.cpu.mem_write(address, value.to_bytes(4,'big')[-size:])
            else: raise AssertionError('Unexpected isolated-code relocation: '+str(kind))
        self.cpu.hook_add(UC_HOOK_CODE, self.hook)
    def word(self, address, value): self.cpu.mem_write(address, struct.pack('>I', value))
    def byte(self, address, value): self.cpu.mem_write(address, bytes([value]))
    def read(self, address): return struct.unpack('>I', self.cpu.mem_read(address,4))[0]
    def string(self, address):
        if address == 0: return None
        out = bytearray()
        for i in range(1024):
            value = self.cpu.mem_read(address+i,1)[0]
            if value == 0: return out.decode('ascii')
            out.append(value)
        raise AssertionError('Unterminated diagnostic string')
    def registers(self, count): return tuple(self.cpu.reg_read(reg(i)) for i in range(3,3+count))
    def hook(self, cpu, address, size, user):
        if address == self.STOP: cpu.emu_stop(); return
        if self.base <= address < self.end: return
        if address == 0x807ec7f8:
            cpu.reg_write(reg(3), self.player_id)
        elif address == 0x8063db84:
            self.calls.append(('draw', self.registers(2)))
        elif address == 0x8082f780:
            self.calls.append(('back', self.registers(3)))
        elif address == 0x8055ba64:
            self.calls.append(('exists', self.registers(2))); cpu.reg_write(reg(3),1)
        elif address == 0x8055c0e8:
            self.calls.append(('load', self.registers(4)))
        elif address == 0x80003100:
            self.calls.append(('heap', self.registers(2))); cpu.reg_write(reg(3),0x23450)
        elif address == 0x801a25d0:
            fmt = self.string(cpu.reg_read(reg(3))); kinds = re.findall(r'%([spu])', fmt)
            values = tuple(self.string(cpu.reg_read(reg(4+i))) if kind=='s' else cpu.reg_read(reg(4+i))
                           for i,kind in enumerate(kinds))
            self.calls.append(('report',fmt,values))
        else: raise AssertionError('Unexpected native call '+hex(address))
        cpu.reg_write(UC_PPC_REG_PC, cpu.reg_read(UC_PPC_REG_LR))
    def run(self, offset, *args):
        self.calls = []
        for index in range(32): self.cpu.reg_write(reg(index),0)
        self.cpu.reg_write(reg(1),0x817f0000); self.cpu.reg_write(UC_PPC_REG_LR,self.STOP)
        for index,value in enumerate(args): self.cpu.reg_write(reg(3+index),value)
        self.cpu.emu_start(self.base+offset,self.STOP,count=3000)
        assert self.cpu.reg_read(UC_PPC_REG_PC)==self.STOP, 'Function did not return'
        return self.cpu.reg_read(reg(3)), self.calls[:]

def symbol(name):
    matches = [int(m.group(1),16) for line in (ROOT/'build/Code.map').read_text().splitlines()
               if (m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+(.+)',line)) and m.group(2).startswith(name+'__')]
    assert len(matches)==1,name
    return matches[0]

def main():
    latest=(ROOT/'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes()
    candidate=(ROOT/'build/Code.pul').read_bytes()
    fresh={name:symbol(name) for name in ['RequestReleasedBackModel','SuppressEmptyItemDraw','DrawReleasedItemWindow','LoadReleasedPreviewModel']}
    executions=0
    for base in (0x81000000,0x81200000):
        old,new=Harness(latest,base),Harness(candidate,base)
        for h in (old,new):
            h.word(0x809c3618,0x81620000); h.byte(0x81620010,2); h.word(0x81620014,0x81630000)
        cases=[(20,0,0,0,0,True),(0,0,0,0,0,True),(0,1,0,0,0,False),
               (10,0,0,0,0,True),(10,0,1,0,0,True),(10,0,1,1,0,False),
               (10,1,0,0,0,False),(20,0,0,0,1,False),(0,0,0,0,1,False)]
        for hud,pid,mgr,players in [(0,0,True,True),(3,1,True,True),(4,0,True,True),
                                    (0,2,True,True),(0,0,False,True),(0,0,True,False)]:
            for item,count,golden,timer,spinning,empty in cases:
                expected = empty and hud<4 and pid<2 and mgr and players
                results=[]
                for h,predicate,draw in [(old,0x504fc,0x505e4),(new,fresh['SuppressEmptyItemDraw'],fresh['DrawReleasedItemWindow'])]:
                    h.word(0x809c3618,0x81620000 if mgr else 0);h.word(0x81620014,0x81630000 if players else 0)
                    h.byte(0x81610190,hud);h.player_id=pid
                    player=0x81630000+pid*0x248
                    h.word(player+0x8c,item);h.word(player+0x90,count);h.byte(player+0xa4,golden)
                    h.cpu.mem_write(player+0xaa,struct.pack('>H',timer));h.word(player+0x58,spinning)
                    value,calls=h.run(predicate,0x81610000);assert bool(value)==expected,(hud,pid,item,value,expected)
                    _,draw_calls=h.run(draw,0x81610000,7)
                    assert draw_calls==([] if expected else [('draw',(0x81610000,7))]),draw_calls
                    executions+=2
        for manager,back in [(False,False),(True,False),(True,True)]:
            results=[]
            for h,offset in [(old,0x445e4),(new,fresh['RequestReleasedBackModel'])]:
                h.word(0x8164001c,0x81641000 if back else 0)
                _,calls=h.run(offset,0x81640000 if manager else 0,9);results.append(calls);executions+=1
            assert results[0]==results[1]==([('back',(0x81641000,0,1))]if manager and back else [])
        for scene,manager,name,data in [(True,True,True,True),(False,False,True,True),
                                        (True,True,False,True),(True,True,True,False)]:
            results=[]
            for h,offset in [(old,0x55dc),(new,fresh['LoadReleasedPreviewModel'])]:
                h.word(0x809c1850,0x81650000 if scene else 0);h.word(0x809c1988,0x81640000 if manager else 0)
                h.word(0x81650010,0x81665000);h.word(0x81650018,0x81668000)
                h.word(0x8164003c,0x81666000);h.word(0x8164002c,0x81667000);h.word(0x80386e64,0x81669000)
                for heap in [0x81665000,0x81666000,0x81667000]:
                    h.word(heap,0x81670000);h.cpu.mem_write(heap+0x1c,struct.pack('>H',1))
                h.word(0x81670024,0x80003100);h.cpu.mem_write(0x81678000,b'test_model\0')
                h.word(0x81679000,0x8167a000 if data else 0)
                _,calls=h.run(offset,0x8167b000,0x81678000 if name else 0,0x81679000,0x8167c000)
                results.append(calls);executions+=1
            assert results[0]==results[1],results
    report=dict(passed=True,executions=executions,allocation_bases=['0x81000000','0x81200000'],
                scope='Real released vs compiled reconstructed PowerPC functions; native APIs intercepted.',
                checked=['empty/golden/roulette item drawing and invalid slots/owners','background null checks, fixed model and reanimation','preview diagnostic sequence, heap checks and exact native load arguments'],
                full_gameplay_tested=False)
    (ROOT/'docs/recovered-runtime-emulation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',executions,'isolated PowerPC executions match the released hook behavior at two allocation bases.')

if __name__=='__main__':main()
