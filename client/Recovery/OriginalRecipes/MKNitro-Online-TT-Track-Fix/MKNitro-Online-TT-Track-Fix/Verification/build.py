"""PAL Online TT: keep OTT rules while selecting the Nitro course list.
Input must be the exact tested Leaderboard-Mii-Fix Code.pul.
"""
import hashlib,json,struct,sys
from pathlib import Path
from code_tools import parse,u
src,dst=map(Path,sys.argv[1:3]);raw=src.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='5104cb1c6ca241db82f4d5d6658e72eeca8bb5b3af622ab192e5bc05422f25af'
blocks=parse(src);block,old,cmds=blocks[0];code=bytearray(old);labels={}
def emit(w):code.extend(struct.pack('>I',w))
def branch(at,to,link=False):return 0x48000000|((to-at)&0x3fffffc)|int(link)
while len(code)%4:code.append(0)
# Exact clone of existing restrictions, except REGs is cleared rather than set.
labels['ott_rules']=len(code)
assert u(old,0x16a4)==0x3cc0fce8 and u(old,0x16c0)==0x64e50006
code.extend(old[0x16a0:0x16ec])
struct.pack_into('>I',code,labels['ott_rules']+4,0x3cc0fce4)
struct.pack_into('>I',code,labels['ott_rules']+0x20,0x64e50002)
# This check is used ONLY by ToggleCTs; physics IsVanillaMode is unchanged.
labels['vanilla_tracks_only']=len(code)
emit(0x8003009c)  # lwz r0, netMgr.region(r3)
emit(0x2800000b)  # cmplwi r0, 0xb
emit(0x4082000c)  # bne original IsVanillaMode
emit(0x38600000)  # li r3, 0
emit(0x4e800020)
emit(branch(len(code),0x1720))
# Existing Nitro VS navigation/random helper now also admits OTT region 0xb.
# Its original online/public-VS/room checks still run before this tail.
labels['nitro_region_tail']=len(code)
emit(0x2000000b)  # subfic r0,r0,11 (unsigned 11-region is 0 or 1)
emit(0x28000001)  # cmplwi r0,1
emit(0x4d810020)  # bgtlr (unsigned region outside 10..11)
emit(0x38600001)
emit(0x4e800020)
patches={0x2f1c:('ott_rules',True),0x354d0:('vanilla_tracks_only',True),0x34108:('nitro_region_tail',False)}
assert u(old,0x2f1c)==branch(0x2f1c,0x16a0,True)
assert u(old,0x354d0)==branch(0x354d0,0x1720,True)
assert u(old,0x34108)==0x2800000a
for at,(label,link) in patches.items():struct.pack_into('>I',code,at,branch(at,labels[label],link))
assert not any(a<=p<a+(4 if t!=4 and t!=6 else 2) for t,a,v,_,_ in cmds for p in patches)
header=bytearray(block[:32]);struct.pack_into('>I',header,12,len(code))
newblocks=[bytes(header)+code+block[32+len(old):]]+[b[0] if b else b'' for b in blocks[1:]]
result=struct.pack('>4I',*map(len,newblocks))+b''.join(newblocks)
dst.write_bytes(result)
meta={'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest(),'code_sha1':hashlib.sha1(code).hexdigest(),'labels':labels,'patched_offsets':[hex(x) for x in patches],'code_length':len(code),'region':'PAL'}
dst.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
approval=json.loads((dst.parent.parent/'Server/restore-build.json').read_text())
approval['hash_pal']=meta['code_sha1']
(dst.parent.parent/'Server/approved-build.json').write_text(json.dumps(approval,indent=2)+'\n')
print(json.dumps(meta,indent=2))
