"""Check the compiled PPC item-enable loop. Python 3; no emulator required.

Usage: python check_items_stride.py Code.pul Code.map
Place nitro_formats.py alongside this script (included with this check).
This is a focused instruction/write-address check, not a game runtime test.
"""
import json
import re
import struct
import sys
from pathlib import Path

from nitro_formats import kamek


def verify(code_path, map_path):
    data = Path(code_path).read_bytes()
    match = re.search(r'([0-9A-F]+) ([0-9A-F]+) OnActivate__Q36Pulsar2UI14CustomItemPageFv',
                      Path(map_path).read_text())
    if not match:
        raise ValueError('OnActivate symbol is missing')
    start, size = (int(x, 16) for x in match.groups())
    results = []
    for region in kamek(data)['regions']:
        base = region['offset'] + 32
        words = list(struct.unpack('>' + str(size // 4) + 'I', data[base+start:base+start+size]))
        found = []
        for index in range(len(words) - 6):
            a,b,c,d,e,f,g = words[index:index+7]
            count_reg = (a >> 21) & 31
            pointer_reg = (c >> 21) & 31
            page_reg = (c >> 16) & 31
            zero_reg = (d >> 21) & 31
            if a != (14 << 26) | (count_reg << 21) | 20:
                continue
            if b != 0x7c0903a6 | (count_reg << 21):
                continue
            if page_reg == 0 or c != (14 << 26) | (pointer_reg << 21) | (page_reg << 16) | 0x8b9:
                continue
            if d != (14 << 26) | (zero_reg << 21):
                continue
            if e != (38 << 26) | (zero_reg << 21) | (pointer_reg << 16):
                continue
            if f != (14 << 26) | (pointer_reg << 21) | (pointer_reg << 16) | 0x254:
                continue
            if g != 0x4200fff8:  # bdnz back to the byte store
                continue
            found.append(start + index * 4)
        if len(found) != 1:
            raise AssertionError(region['region'] + ': expected one strided 20-store loop, found ' + str(found))
        # Execute the recognized store/stride/CTR loop over a sentinel buffer.
        memory = bytearray([0xa5]) * 0x4000
        pointer, ctr = 0x8b9, 20
        while ctr:
            memory[pointer] = 0
            pointer += 0x254
            ctr -= 1
        writes = [i for i, value in enumerate(memory) if value != 0xa5]
        expected = [0x8b9 + i * 0x254 for i in range(20)]
        assert writes == expected
        assert max(writes) < 0x35b8  # CustomItemPage's allocation
        assert memory[0x3749:0x375d] == bytes([0xa5]) * 20
        results.append(dict(region=region['region'], loop_offset=hex(found[0]),
                            byte_writes=len(writes), first_write=hex(min(writes)),
                            last_write=hex(max(writes)), title_canary_unchanged=True))
    return results


if __name__ == '__main__':
    print(json.dumps(verify(*sys.argv[1:]), indent=2))
