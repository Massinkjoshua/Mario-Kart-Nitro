"""Validate fresh containers and the twelve observed PAL policy sites."""
from pathlib import Path
import json, re
from nitro_formats import kamek, sha
from apply_release_policy import POLICY
root=Path(__file__).resolve().parent.parent
data=(root/'build/Code.pul').read_bytes();parsed=kamek(data)
assert parsed['trailing_bytes']==0
assert [r['region']for r in parsed['regions']]==['P','E','J']
for region in parsed['regions']:
    assert region['version']==2
    assert region['ctor_start']<=region['ctor_end']<=region['code_size']
    assert region['ctor_start']%4==region['ctor_end']%4==0
for address,(cmd,value)in POLICY.items():
    sites=[c for c in parsed['regions'][0]['commands']if c['absolute']and c['address']==address]
    assert len(sites)==1 and sites[0]['command_id']==cmd and sites[0]['values']==[value],hex(address)
loader=(root/'build/Loader.pul').read_bytes()
assert 0<len(loader)<=0x1e00,'Loader exceeds reserved bootstrap area; review layout.'
loader_map=(root/'build/Loader.map').read_text()
entry=[int(m[1],16)for line in loader_map.splitlines()
       if (m:=re.match(r'\s*([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]+\s+.*LoadIntoMKW',line))]
assert len(entry)==1 and entry[0]in (0,0x80004000),'Loader entrypoint is not first in its image.' 
status=dict(powerpc_build_outputs_present=True,structural_checks_passed=True,
    matching_latest_release_source_verified=False,gameplay_tested=False,
    code_sha256=sha(data),loader_sha256=sha(loader),loader_bytes=len(loader),
    regions=[dict(region=r['region'],code_bytes=r['code_size'],commands=len(r['commands']))for r in parsed['regions']])
(root/'build/build-status.json').write_text(json.dumps(status,indent=2)+'\n')
print('PASS: P/E/J containers, command streams, PAL policy and loader size.')
print('These are candidates; latest-release parity and gameplay remain unverified.')
