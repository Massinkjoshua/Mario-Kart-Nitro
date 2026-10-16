from pathlib import Path
import struct,hashlib,json
ROOT=Path('/workspace/scratch/e221e6641538')
base=(ROOT/'work/v5/Code.pul').read_bytes()
assert hashlib.sha256(base).hexdigest()=='7946a60dbaf01bfc77c99d89ce11fcd92c5b0f5f677358087535030a170ffb4a'
length=struct.unpack_from('>I',base)[0]
# Append one PAL WRITE32 command; preserve v5 code, relocation commands,
# settings/preview hooks, constructors, and all other region blocks exactly.
patch=struct.pack('>III',0x20fffffe,0x80542310,0x3f400012)
result=struct.pack('>I',length+len(patch))+base[4:16+length]+patch+base[16+length:]
assert result[4:16+length]==base[4:16+length]
assert result[16+length+len(patch):]==base[16+length:]
(ROOT/'work/crash-repair/Code.pul').write_bytes(result)
manifest={'base_version':'Native Settings and Preview v5','region':'PAL','base_sha256':hashlib.sha256(base).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest(),'native_patch_address':'0x80542310','old_instruction':'0x3f40000e','new_instruction':'0x3f400012','old_heap_bytes':0xe1000,'new_heap_bytes':0x121000,'additional_bytes_per_local_player':0x40000,'max_additional_bytes_four_players':0x100000,'appended_kamek_bytes':len(patch),'existing_code_and_commands_unchanged':True,'other_region_blocks_unchanged':True}
(ROOT/'work/crash-repair/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
