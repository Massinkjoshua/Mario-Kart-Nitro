import sys,struct,json
from pathlib import Path
sys.path.insert(0,'work');from code_tools import *
blocks=parse('work/preview_patch/Code.pul');b,orig,cmds=blocks[0];c=bytearray(orig)
# Put the voting-pose update in the existing pre-CalcMain reload phase.
for off in [0x9b8c,0x9b98]:
 assert (u(c,off)&0xfc000003)==0x48000001
 assert not any(a==off for _,a,_,_,_ in cmds)
 struct.pack_into('>I',c,off,0x60000000)
def emit(words):
 off=len(c);c.extend(struct.pack('>'+str(len(words))+'I',*words));return off
def branch(at,to,link=False):struct.pack_into('>I',c,at,0x48000000|((to-at)&0x3fffffc)|int(link))
phase=emit([0x9421fff0,0x7c0802a6,0x90010014,0,0x80010014,0x7c0803a6,0x38210010,0x48000000]);branch(phase+12,0x794c,True)
# r3=drivers, r4=hud; caller has validated both. Reuse its prepared controller.
prepare=emit([0x1ca4000c,0x7ca32a14,0x80a50018,0x80a50010,0x2c050000,0x4c820020,
 0x9421ffe0,0x7c0802a6,0x90010024,0x90610008,0x9081000c,0x3c60809c,0x80631988,0,
 0x80610008,0x8081000c,0x80010024,0x7c0803a6,0x38210020,0x48000000])
branch(prepare+52,0x6b1c,True)
# Existing relocation destinations are modified, preserving every other command.
oldcalc=next(v[0] for t,a,v,_,_ in cmds if t==10 and a==0x7848)
stream=bytearray(b[32+len(orig):]);startcmd=32+len(orig)
for t,a,v,s,e in cmds:
 if t==10 and a in [0x7848,0x7a60]:
  target=phase if a==0x7848 else prepare;struct.pack_into('>I',stream,e-startcmd-4,target)
stream+=struct.pack('>II',0x0a000000|(phase+28),oldcalc)
stream+=struct.pack('>II',0x0a000000|(prepare+76),0x80830c64)
header=bytearray(b[:32]);struct.pack_into('>I',header,12,len(c));parts=[bytes(header)+c+stream]+[x[0] if x else b'' for x in blocks[1:]]
Path('work/preview_crash/Code.pul').write_bytes(struct.pack('>4I',*[len(x) for x in parts])+b''.join(parts))
Path('work/preview_crash/offsets.json').write_text(json.dumps({'phase':phase,'prepare':prepare,'calc':oldcalc}))
print('Moved voting allocation out of MenuUpdate; reuse controller; unlock using existing reload helper only before missing-controller creation.')
