#!/usr/bin/env python3
"""Make a PAL instruction audit list. Never modifies the input game or PUL.

Only executable, unrelocated words not written by the supplied PUL are included.
This is an offline baseline, NOT proof that online payloads leave these words alone.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

REL_BASE = 0x805102E0
REL_SHA256 = '16d9d146112541fefea701ecb5bc1a496f9d50e4a752fbb5b6778e7c6399f67d'
DOL_SHA256 = '80d18895b39c63bd80f457398bfcbb91b7d16ac116a41a88967e954080155b05'
COMMAND_LENGTHS = {1:4,4:4,5:4,6:4,10:4,32:4,33:4,34:4,35:8,36:8,37:8,38:8,64:4,65:4}

def u32(data, offset):
    if offset < 0 or offset + 4 > len(data):
        raise ValueError('truncated binary')
    return struct.unpack_from('>I', data, offset)[0]

def pul_writes(data):
    if len(data) < 16:
        raise ValueError('truncated PUL')
    sizes = struct.unpack_from('>4I', data)
    if sum(sizes) + 16 != len(data) or not sizes[0]:
        raise ValueError('invalid PUL sizes or missing PAL module')
    start, end = 16, 16 + sizes[0]
    if data[start:start+8] != b'Kamek\0\0\2':
        raise ValueError('this parser supports Kamek v2 only; do not guess another format')
    code_size = u32(data, start+12)
    pos = start + 32 + code_size
    if pos > end or code_size & 3:
        raise ValueError('invalid Kamek code size')
    writes, count = [], 0
    while pos < end:
        header = u32(data, pos); pos += 4
        cmd, address = header >> 24, header & 0xffffff
        if cmd not in COMMAND_LENGTHS:
            raise ValueError('unsupported Kamek command %d' % cmd)
        absolute = address == 0xfffffe
        if absolute:
            address = u32(data, pos); pos += 4
        size = COMMAND_LENGTHS[cmd]
        if pos + size > end:
            raise ValueError('truncated Kamek command')
        width = 1 if cmd in (34,38) else 2 if cmd in (4,5,6,33,37) else 4
        if absolute:
            writes.append((address, address + width, cmd, u32(data, pos)))
        pos += size
        count += 1
    if pos != end:
        raise ValueError('invalid Kamek boundary')
    return writes, count

def dol_sections(data):
    result = []
    for i in range(18):
        offset, address, size = (u32(data, base+i*4) for base in (0,0x48,0x90))
        if size:
            if offset < 0x100 or offset + size > len(data):
                raise ValueError('invalid DOL section')
            result.append((address, address+size, offset, i < 7))
    return result

def rel_sections_and_relocations(data):
    count, table = u32(data,0xc), u32(data,0x10)
    if count > 256 or table+count*8 > len(data):
        raise ValueError('invalid REL section table')
    sections = []
    for i in range(count):
        raw, size = u32(data,table+i*8), u32(data,table+i*8+4)
        offset = raw & ~3
        if offset and offset+size > len(data):
            raise ValueError('invalid REL section')
        sections.append((offset,size,bool(raw&1)))
    imp, imp_size = u32(data,0x28),u32(data,0x2c)
    if imp_size & 7 or imp+imp_size > len(data):
        raise ValueError('invalid REL import table')
    changed = set()
    for entry in range(imp,imp+imp_size,8):
        pos=u32(data,entry+4); section=None; delta=0; ended=False
        while pos+8 <= len(data):
            step, kind, target_section, addend = struct.unpack_from('>HBBI',data,pos)
            pos += 8
            if kind == 203:
                ended=True; break
            if kind == 202:
                section=target_section; delta=0
                if section >= len(sections): raise ValueError('invalid relocation section')
                continue
            delta += step
            if kind in (0,201): continue
            if section is None: raise ValueError('relocation without target section')
            offset,size,executable=sections[section]
            if not offset: continue
            # Exclude a full word around every real relocation, conservatively.
            if delta >= size: raise ValueError('relocation outside section')
            address=REL_BASE+offset+delta
            changed.update(((address+i)&~3) for i in range(4))
        if not ended: raise ValueError('unterminated REL relocations')
    mapped=[(REL_BASE+o,REL_BASE+o+s,o,x) for o,s,x in sections if o and s]
    return mapped,changed

def inverse_usa_map(text):
    active=False; result=[]
    for line in text.splitlines():
        line=line.split('#',1)[0].strip()
        if line.startswith('['): active=line=='[E]'; continue
        if not active or not line: continue
        match=re.fullmatch(r'([0-9a-fA-F]+)-([0-9a-fA-F]+|\*):\s*([+-])0x([0-9a-fA-F]+)',line)
        if not match: raise ValueError('unsupported versions line '+line)
        low=int(match[1],16); high=0xffffffff if match[2]=='*' else int(match[2],16)
        delta=int(match[4],16)*(1 if match[3]=='+' else -1)
        result.append((low,high,delta))
    if not result: raise ValueError('no USA mapping')
    return result

def pal_candidates(address,mapping):
    return sorted({address-delta for low,high,delta in mapping if low <= address-delta <= high})

def locate(address,sections,data):
    for low,high,offset,executable in sections:
        if low <= address and address+4 <= high:
            return executable,u32(data,offset+address-low)
    return None

def create(dol,rel,pul,versions,targets):
    if hashlib.sha256(dol).hexdigest()!=DOL_SHA256 or hashlib.sha256(rel).hexdigest()!=REL_SHA256:
        raise ValueError('different game inputs: verify their region, base and relocations first')
    writes,command_count=pul_writes(pul)
    dol_sections_=dol_sections(dol)
    rel_sections,relocated=rel_sections_and_relocations(rel)
    mapping=inverse_usa_map(versions)
    accepted={}; decisions=[]
    for target in targets:
        item=dict(target); address=int(target['address'],0); width=target.get('width',4)
        if width not in (1,2,4): raise ValueError('invalid target width')
        if address%width:
            item['status']='excluded: unaligned source address'; decisions.append(item); continue
        candidates=[address] if target['region']=='P' else pal_candidates(address,mapping)
        if len(candidates)!=1:
            item['status']='excluded: ambiguous or absent region mapping'; decisions.append(item); continue
        address=candidates[0] & ~3; item['pal_word']='0x%08x'%address
        result=locate(address,dol_sections_,dol); phase=0
        if result is None: result=locate(address,rel_sections,rel); phase=1
        if result is None or not result[0]:
            item['status']='excluded: not an executable word'; decisions.append(item); continue
        overlaps=[w for w in writes if address < w[1] and address+4 > w[0]]
        if overlaps:
            item['status']='excluded: owned by supplied Nitro PUL'; decisions.append(item); continue
        if address in relocated:
            item['status']='excluded: changed by REL relocation'; decisions.append(item); continue
        item['status']='instruction audit candidate'; item['expected']='0x%08x'%result[1]
        item['phase']='REL' if phase else 'DOL'; decisions.append(item)
        accepted[address]=(result[1],phase,target['purpose'])
    if not accepted: raise ValueError('no audit candidates')
    checks=[{'address':'0x%08x'%a,'expected':'0x%08x'%v,'phase':p,'purpose':s}
            for a,(v,p,s) in sorted(accepted.items())]
    report={'status':'UNVERIFIED RUNTIME BASELINE; AUDIT ONLY',
            'inputs':{'dol_sha256':hashlib.sha256(dol).hexdigest(),
                      'rel_sha256':hashlib.sha256(rel).hexdigest(),
                      'code_sha256':hashlib.sha256(pul).hexdigest(),
                      'versions_sha256':hashlib.sha256(versions.encode()).hexdigest()},
            'pal_kamek_commands':command_count,'checks':checks,'decisions':decisions,
            'limitations':['Only selected code words; no full-file/runtime attestation.',
                           'Region mapping is a candidate port, not semantic validation of every cheat.',
                           'Online payloads and runtime patches require clean-session verification.',
                           'Excluded addresses are coverage gaps, not proof that Nitro prevents cheating.']}
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dol','rel','code','versions','targets','out'): p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    report=create(a.dol.read_bytes(),a.rel.read_bytes(),a.code.read_bytes(),a.versions.read_text(),json.loads(a.targets.read_text()))
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'manifest_review.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['#ifndef NITRO_INTEGRITY_MANIFEST_HPP','#define NITRO_INTEGRITY_MANIFEST_HPP',
           '#include <Security/NitroIntegrity/Policy.hpp>',
           '// GENERATED: selected original code words; live online compatibility is NOT verified.',
           '// Reference Code.pul SHA256: '+report['inputs']['code_sha256'],
           'namespace Pulsar { namespace NitroIntegrity {',
           'static const bool ManifestRuntimeReviewed = false;',
           'static const CheckWord kChecks[] = {']
    for c in report['checks']:
        lines.append('    {%su, %su, %du}, // %s'%(c['address'],c['expected'],c['phase'],c['purpose']))
    lines += ['};','static const unsigned int kCheckCount = sizeof(kChecks) / sizeof(kChecks[0]);','} }','#endif','']
    (a.out/'Manifest.hpp').write_text('\n'.join(lines))
    print(json.dumps({'candidates':len(report['checks']),'pal_commands':report['pal_kamek_commands'],
                      'excluded':sum(x['status']!='instruction audit candidate' for x in report['decisions'])}))

if __name__=='__main__': main()
