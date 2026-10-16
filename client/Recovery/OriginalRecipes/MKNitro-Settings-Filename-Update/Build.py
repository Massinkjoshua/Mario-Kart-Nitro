from pathlib import Path
import struct,ast,json,shutil
from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
R=Path('/workspace/scratch/e221e6641538');W=R/'work/settings-rename';O=R/'deliverables/MKNitro-Settings-Filename-Update';O.mkdir(exist_ok=True)
u32=lambda b,p:struct.unpack_from('>I',b,p)[0]
t=ast.parse((R/'work/v4/build_code.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='commands'],type_ignores=[]),'p','exec'))
ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
def asm(s):return bytes(ks.asm(s)[0])
def cmd(t,a,v):return struct.pack('>II',(t<<24)|a,v)
base=(R/'upload/Code(4).pul').read_bytes();lengths=struct.unpack_from('>4I',base);blocks=[];reports=[];pos=16
for region,length in zip(['PAL','USA','Japan','Korea'],lengths):
 if not length:blocks.append(b'');continue
 b=base[pos:pos+length];pos+=length;h=bytearray(b[:32]);size=u32(h,12);code=bytearray(b[32:32+size]);oldcmd=b[32+size:];parsed=commands(oldcmd)
 assert code[0x2038:0x203c]==asm('addi 7,31,288')
 assert code[0xd3b8:0xd3bc]==asm('bctrl')
 assert not any(a in [0x2038,0xd3b8] for t,a,v in parsed)
 code+=bytes(u32(h,8));code+=bytes(-len(code)%4);nameoff=len(code);code+=b'MKNitroGameSettings.pul\0';code+=bytes(-len(code)%4)
 setteroff=len(code);setter=bytearray(asm('lis 7,0;addi 7,7,0;blr'));code+=setter
 relocs=cmd(6,setteroff+2,nameoff)+cmd(4,setteroff+6,nameoff)
 fallbackoff=len(code)
 # First try the new path. On failure, open the legacy file using a local
 # path, leaving Mgr::filePath unchanged so normal saving migrates to new.
 stores=';'.join(f'li 9,{v};stb 9,{i}(8)' for i,v in enumerate(b'RRGameSettings.pul\0'))
 body=f'''stwu 1,-128(1);mflr 0;stw 0,132(1);stw 31,124(1);stw 30,120(1);stw 29,116(1)
 mr 31,3;mr 30,4;mr 29,5
 bctrl
 cmpwi 3,0;bne finish
 addi 7,1,8;li 6,0;li 8,0
 copy_path:cmplwi 6,64;bge no_legacy
 lbzx 9,30,6;stbx 9,7,6
 cmpwi 9,47;bne no_slash
 add 8,7,6;addi 8,8,1
 no_slash:cmpwi 9,0;beq copied
 addi 6,6,1;b copy_path
 copied:cmpwi 8,0;beq no_legacy
 subf 10,7,8;cmplwi 10,{64-len(b'RRGameSettings.pul'+bytes([0]))};bgt no_legacy
 {stores}
 mr 3,31;addi 4,1,8;mr 5,29
 lwz 12,0(31);lwz 12,8(12);mtctr 12;bctrl
 b finish
 no_legacy:li 3,0
 finish:lwz 29,116(1);lwz 30,120(1);lwz 31,124(1);lwz 0,132(1);mtlr 0;addi 1,1,128;blr'''
 payload=asm(body);code+=payload
 for site,target in [(0x2038,setteroff),(0xd3b8,fallbackoff)]:struct.pack_into('>I',code,site,0x48000001|((target-site)&0x3fffffc))
 # Only the two documented instructions change in the original code/data.
 changes=[i for i in range(0,size,4) if code[i:i+4]!=b[32+i:32+i+4]];assert changes==[0x2038,0xd3b8],changes
 struct.pack_into('>II',h,8,0,len(code));new=bytes(h)+code+oldcmd+relocs;commands(oldcmd+relocs);blocks.append(new)
 reports.append({'region':region,'original_size':size,'new_size':len(code),'name_offset':nameoff,'setter_offset':setteroff,'fallback_offset':fallbackoff,'added_relocations':commands(relocs),'modified_instructions':changes,'old_commands_preserved':True})
 (W/(region+'-fallback.bin')).write_bytes(payload)
out=struct.pack('>4I',*[len(b) for b in blocks])+b''.join(blocks);dest=O/'MarioKartNitro_Test/Binaries/Code.pul';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(out);(W/'metadata.json').write_text(json.dumps(reports));(O/'Migration-hook.asm').write_text(body)
(O/'README.txt').write_text('MARIO KART NITRO - SETTINGS FILENAME UPDATE\n\nINSTALL\nFully close Dolphin. Back up and replace MarioKartNitro_Test/Binaries/Code.pul using this file. No XML or asset changes are required. Start without a save state. For the release ZIP include this new Code.pul.\n\nBEHAVIOUR\nNew saves use MKNitroGameSettings.pul. If it cannot be opened, the initial settings load tries RRGameSettings.pul in the same directory. Existing settings/progress load through the original validation and are written to the new file by normal initialization. The old file is retained as a backup. If neither exists, original defaults are created. The new settings file takes priority whenever it can be opened. Invalid/version-incompatible files follow the original validation/reset rules. Legacy RRSettings.pul trophy migration is unchanged.\n\nDOLPHIN LOCATION\nOpen Dolphin File > Open User Folder, then Wii/shared2/Pulsar. Search its distribution subfolders for RRGameSettings.pul or MKNitroGameSettings.pul. This is separate from Load/riivolution. The exact distribution subfolder comes from ConfigRT.pul. SD-based installations use their existing mod save location.\n\nPRESERVED\nBuilt from the uploaded Code(4).pul, including the corrected item-box hook. Original commands and all unrelated code/data are preserved. Filename/fallback edits apply to the existing PAL, USA, and Japanese blocks; no Korean block is added. This does not complete other regional compatibility fixes.\n\nRELEASE CLEANUP\nDo not bundle your personal settings or progress files. Keep Config.pul, ConfigRT.pul, Code.pul, Loader.pul, and required mod assets. If your ZIP contains only Load/riivolution assets, NAND settings are outside it. Review any Ghosts/Trophies folders for personal records before release.\n\nVALIDATION\nSee Verification.json for serialized-relocation and native helper checks. No Dolphin gameplay test is claimed. Verify your existing selected HUD colour/settings persist after installation, change one setting, restart, and confirm it persists.\n')
shutil.copy2(__file__,O/'Build.py');print(json.dumps(reports))
