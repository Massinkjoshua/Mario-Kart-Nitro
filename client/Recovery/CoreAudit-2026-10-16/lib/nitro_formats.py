#!/usr/bin/env python3
"""Read-only Pulsar/Kamek/U8 comparison against user-supplied source archives.

Formats are read from the supplied Config.hpp/Info.hpp/kamekLoader.cpp.
This is an inspection tool, not a compiler, emulator, or compliance certificate.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import struct
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def u16(data, off):
    return struct.unpack_from('>H', data, off)[0]


def u32(data, off):
    return struct.unpack_from('>I', data, off)[0]


def bmg(data):
    if data[:8] != b'MESGbmg1':
        raise ValueError('Not a BMG')
    length = u32(data, 8)
    pos = 32
    sections = {}
    for _ in range(u32(data, 12)):
        size = u32(data, pos + 4)
        if size < 8 or pos + size > length:
            raise ValueError('BMG section bounds')
        sections[data[pos:pos+4]] = pos
        pos += size
    inf, dat = sections[b'INF1'], sections[b'DAT1']
    mid = sections.get(b'MID1')
    count, entry_size = u16(data, inf+8), u16(data, inf+10)
    rows = []
    for i in range(count):
        entry = inf+16+i*entry_size
        cursor = dat+8+u32(data, entry)
        raw = bytearray()
        clean = bytearray()
        controls = []
        while cursor+2 <= length:
            unit = data[cursor:cursor+2]
            if unit == b'\0\0':
                break
            if unit == b'\0\x1a':
                span = data[cursor+2]
                if span < 4 or cursor+span > length:
                    raise ValueError('BMG control bounds')
                chunk = data[cursor:cursor+span]
                controls.append(chunk.hex())
                raw.extend(chunk)
                cursor += span
            else:
                clean.extend(unit)
                raw.extend(unit)
                cursor += 2
        rows.append(dict(id=u32(data,mid+16+i*4) if mid else i,
                         text=clean.decode('utf-16-be',errors='replace'),
                         attributes=data[entry+4:entry+entry_size].hex(),
                         controls=controls,raw_hex=raw.hex()))
    return dict(length=length,count=count,entry_size=entry_size,
                sections={k.decode():v for k,v in sections.items()},messages=rows)


def config(data):
    if data[:4] != b'PULS':
        raise ValueError('Not a Pulsar config')
    info, cups, msg = struct.unpack_from('>3I',data,8)
    if data[info:info+4] != b'INFO' or data[cups:cups+4] != b'CUPS':
        raise ValueError('Config section magic')
    out = dict(version=u32(data,4),mod_folder=data[20:36].split(b'\0')[0].decode(),
               offsets=dict(INFO=info,CUPS=cups,BMG=msg))
    p=info+12
    out['info']=dict(room_key=f'{u32(data,p):08x}',prob100cc=u32(data,p+4),
                     prob150cc=u32(data,p+8),region=u32(data,p+12),
                     track_blocking_raw=u32(data,p+16),
                     trophies=bool(data[p+20]),has200cc=bool(data[p+21]),
                     ultra_miniturbos=bool(data[p+22]),feather=bool(data[p+23]),
                     mega_thundercloud=bool(data[p+24]),cup_icons=u16(data,p+25),
                     choose_next_timer=data[p+27],reserved_hex=data[p+28:p+68].hex())
    out['info']['remaining_probability']=100-u32(data,p+4)-u32(data,p+8)
    cup_count=u16(data,cups+12)
    stored=((cup_count+1)//2)*8
    variants=u32(data,cups+24)
    out.update(cups=cup_count,visible_tracks=cup_count*4,stored_tracks=stored,
               regular_mode=data[cups+14],total_variants=variants,
               trophy_counts=list(struct.unpack_from('>4H',data,cups+16)))
    messages=bmg(data[msg:])
    md={x['id']:x for x in messages['messages']}
    out['bmg']=messages
    out['tracks']=[]
    for i in range(stored):
        pos=cups+28+i*8
        name=md.get(0x20000+i,{})
        out['tracks'].append(dict(index=i,cup=i//4,cup_name=md.get(0x10000+i//4,{}).get('text'),
            name=name.get('text'),course_slot=data[pos],music_slot=data[pos+1],
            variants=u16(data,pos+2),crc32=f'{u32(data,pos+4):08x}',
            attributes=name.get('attributes'),controls=name.get('controls')))
    alpha=cups+28+stored*8+variants*2
    out['alphabetical_order']=list(struct.unpack_from('>'+str(stored)+'H',data,alpha)) if stored else []
    out['alphabetical_permutation_valid']=sorted(out['alphabetical_order'])==list(range(stored))
    out['file_section']=data[msg+messages['length']:].decode('utf-8',errors='replace')
    return out


COMMANDS={1:'Addr32',4:'Addr16Lo',5:'Addr16Hi',6:'Addr16Ha',10:'Rel24',
          32:'Write32',33:'Write16',34:'Write8',35:'CondWritePointer',
          36:'CondWrite32',37:'CondWrite16',38:'CondWrite8',64:'Branch',65:'BranchLink'}


def kamek(data):
    sizes=struct.unpack_from('>4I',data)
    pos=16
    regions=[]
    for label,size in zip('PEJK',sizes):
        if not size:
            continue
        raw=data[pos:pos+size]
        if len(raw)!=size or raw[:6]!=b'Kamek\0':
            raise ValueError('Kamek region bounds/magic')
        version=u16(raw,6)
        bss,code,ctor_start,ctor_end,declared,pad=struct.unpack_from('>6I',raw,8)
        if 32+code>len(raw):
            raise ValueError('Kamek code bounds')
        part=dict(region=label,offset=pos,size=size,version=version,bss_size=bss,
                  code_size=code,ctor_start=ctor_start,ctor_end=ctor_end,
                  declared_length=declared,sha256=sha(raw),text_sha256=sha(raw[32:32+code]))
        commands=[]
        cursor=32+code
        # Only v2 command semantics are established by the supplied loader source.
        if version==2:
            while cursor<len(raw):
                start=cursor
                header=u32(raw,cursor);cursor+=4
                cmd,address=header>>24,header&0xffffff
                if cmd not in COMMANDS:
                    raise ValueError(f'Unknown command {cmd} at {cursor:x}')
                absolute=address==0xfffffe
                if absolute:
                    address=u32(raw,cursor);cursor+=4
                count=2 if cmd in [35,36,37,38] else 1
                values=list(struct.unpack_from('>'+str(count)+'I',raw,cursor));cursor+=4*count
                commands.append(dict(file_offset=pos+start,region_offset=start,command=COMMANDS[cmd],
                                     command_id=cmd,absolute=absolute,address=address,values=values))
            if cursor!=len(raw):raise ValueError('Kamek command end')
        part['commands']=commands
        part['command_counts']=dict(collections.Counter(x['command'] for x in commands))
        regions.append(part)
        pos+=size
    return dict(regions=regions,declared_region_sizes=list(sizes),file_size=len(data),
                declared_end=pos,trailing_bytes=len(data)-pos,
                trailing_sha256=sha(data[pos:]) if pos<len(data) else None)


def yaz0(data):
    if data[:4]!=b'Yaz0':return data
    size=u32(data,4);out=bytearray();pos=16
    while len(out)<size:
        code=data[pos];pos+=1
        for bit in range(7,-1,-1):
            if len(out)>=size:break
            if code&(1<<bit):out.append(data[pos]);pos+=1
            else:
                a,b=data[pos:pos+2];pos+=2
                distance=((a&15)<<8)|b
                length=a>>4
                if not length:length=data[pos]+0x12;pos+=1
                else:length+=2
                start=len(out)-distance-1
                if start<0:raise ValueError('Yaz0 invalid distance')
                # Backreferences can overlap: repeat the already-existing
                # distance-sized pattern, rather than copying byte by byte.
                pattern=bytes(out[start:start+length])
                out.extend((pattern*((length+len(pattern)-1)//len(pattern)))[:length])
    if len(out)!=size:raise ValueError('Yaz0 decompressed size')
    return bytes(out)


def u8_entries(data):
    if data[:4]!=b'U\xaa8-':return None
    root=u32(data,4);count=u32(data,root+8);strings=root+count*12
    stack=[('',count)];files={}
    for i in range(1,count):
        while i>=stack[-1][1]:stack.pop()
        node=root+i*12;header=u32(data,node);is_dir=header>>24
        npos=strings+(header&0xffffff)
        end=data.index(0,npos)
        name=data[npos:end].decode('utf-8',errors='replace')
        path=(stack[-1][0]+'/'+name).lstrip('/')
        if is_dir:stack.append((path,u32(data,node+8)))
        else:
            off,size=u32(data,node+4),u32(data,node+8)
            if off+size>len(data):raise ValueError('U8 file bounds')
            files[path]=data[off:off+size]
    return files


def strings(data):
    result=[]
    for m in re.finditer(rb'[\x20-\x7e]{5,}',data):
        result.append(dict(offset=m.start(),encoding='ascii',text=m.group().decode()))
    for parity in [0,1]:
        pattern=rb'(?:\x00[\x20-\x7e]){5,}'
        for m in re.finditer(pattern,data[parity:]):
            result.append(dict(offset=m.start()+parity,encoding='utf-16-be',text=m.group().decode('utf-16-be')))
    return result


def asset(path,include_tokens=True):
    original=path.read_bytes();decoded=yaz0(original);files=u8_entries(decoded)
    out=dict(size=len(original),sha256=sha(original),compression='Yaz0' if original[:4]==b'Yaz0' else 'none',
             decoded_size=len(decoded),decoded_sha256=sha(decoded),magic=decoded[:4].hex())
    if files is None:return out
    rows=[]
    for name,data in sorted(files.items()):
        row=dict(path=name,size=len(data),sha256=sha(data),magic=data[:4].hex())
        if data[:8]==b'MESGbmg1':
            try:row['bmg']=bmg(data)
            except Exception as ex:row['parse_error']=str(ex)
        if data[:4]==b'\x00\x20\xaf\x30':
            try:
                table=u32(data,8);textures=[]
                for i in range(u32(data,4)):
                    h=u32(data,table+i*8)
                    textures.append(dict(height=u16(data,h),width=u16(data,h+2),format=u32(data,h+4)))
                row['textures']=textures
            except Exception as ex:row['parse_error']=str(ex)
        if include_tokens and Path(name).suffix.lower() in ['.brlyt','.brctr','.brlan','.brres']:
            row['strings']=[m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{5,}',data)]
        rows.append(row)
    out['entries']=rows
    out['entry_count']=len(rows)
    return out


def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def csv_write(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

