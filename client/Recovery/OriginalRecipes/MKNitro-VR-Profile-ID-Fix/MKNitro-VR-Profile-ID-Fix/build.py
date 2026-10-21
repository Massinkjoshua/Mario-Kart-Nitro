"""Patch the verified PAL profile-ID predicate; keep all other bytes intact."""
import hashlib, json, struct, shutil, zipfile
from pathlib import Path
root = Path(__file__).resolve().parent
src = root/'Game/Code-previous.pul'
if not src.exists(): src = root.parent / 'upload/Code(9).pul'
data = src.read_bytes()
assert hashlib.sha256(data).hexdigest() == 'e0998f60ddaaa328c204dfac53282dbdcb69ff2492842897120215a28051ae9d'
lengths = struct.unpack_from('>4I', data)
offset = 16
blocks = []
for length in lengths:
    blocks.append(data[offset:offset+length])
    offset += length
assert offset == len(data)
pal = bytearray(blocks[0])
predicate = 0x586b0
expected = bytes.fromhex('3c803b9b3863ffff3804c9fe7c030040386000004d810020386000014e800020')
assert pal[32+predicate:32+predicate+32] == expected
struct.pack_into('>I', pal, 32+predicate, 0x3c807736)
struct.pack_into('>I', pal, 32+predicate+8, 0x380493fe)
blocks[0] = bytes(pal)
out = struct.pack('>4I', *lengths) + b''.join(blocks)
assert len(out) == len(data)
changed = [i for i,(a,b) in enumerate(zip(data,out)) if a!=b]
assert all(i in [48+predicate+2,48+predicate+3,48+predicate+10,48+predicate+11] for i in changed)
(root/'Game').mkdir(exist_ok=True)
(root/'Server').mkdir(exist_ok=True)
(root/'Game/Code.pul').write_bytes(out)
(root/'Game/Code-previous.pul').write_bytes(data)
manifest = {'pack_id':10,'version':6124}
for i,key in enumerate(['hash_pal','hash_ntscu','hash_ntscj','hash_ntsck']):
    block = blocks[i]
    size = struct.unpack_from('>I',block,12)[0] if block else 0
    manifest[key] = hashlib.sha1(block[32:32+size]).hexdigest() if block else ''
(root/'Server/approved-build.json').write_text(json.dumps(manifest,indent=2)+'\n')
previous = dict(manifest,hash_pal='1bf62192c476b1b04347bb0bc5831f2810db950c')
(root/'Server/restore-build.json').write_text(json.dumps(previous,indent=2)+'\n')
shutil.copyfile(root.parent/'online-tt-fix/Server/register-build.py',root/'Server/register-build.py')
metadata = {'input_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'PAL_predicate_offset':hex(predicate),'old_reserved_profile_id':1000000000,'new_reserved_profile_id':2000000000,'changed_file_offsets':changed,'approval':manifest}
(root/'checksums.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata,indent=2))
