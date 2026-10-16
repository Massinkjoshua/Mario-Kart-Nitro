"""Apply observed release-specific native command policy to freshly linked code.

Twelve PAL fixed writes are source-defined here. Seven later PAL-only menu/rating/effect
installations are omitted in USA/Japan, where the supplied release does not
install them. Code/data bytes are never changed by this policy. Internal hook
implementations still require the parity review in SOURCE_STATUS.md.
Modified for Mario Kart Nitro, 16 October 2026; GPLv3.
"""
from pathlib import Path
import argparse, json, struct
from nitro_formats import kamek

POLICY = {
    0x800910B4: (32, 0x480CCE99),
    0x80542310: (32, 0x3F400012),  # each local allkart loader heap: 0x121000
    0x80588894: (32, 0x2C000002),
    0x8058889C: (32, 0x2C000001),
    0x805888A8: (32, 0x4C820020),
    0x80588928: (32, 0xB10300FE),
    0x80588938: (32, 0x2C000000),
    0x8058893C: (32, 0x4D820020),
    0x8058894C: (32, 0x4E800020),
    0x806A2F60: (32, 0x4BFF4674),
    0x806A3004: (32, 0x4BFF45D0),
    0x806A31FC: (32, 0x4BFF458C),
}
APPEND_IF_MISSING = {0x80542310}
REGION_OMISSIONS = {
    'E': {0x80660CE0, 0x8063C284, 0x8063C1F0, 0x807E4AD0, 0x80660C9C, 0x802A2DD4, 0x802A2E48},
    'J': {0x805FD1C4, 0x806623EC, 0x807EE44C, 0x805FD130, 0x80662430, 0x802A2774, 0x802A27E8},
}


def apply(data):
    parsed = kamek(data)
    if parsed['trailing_bytes'] or [r['region'] for r in parsed['regions']] != ['P', 'E', 'J']:
        raise ValueError('Expected complete P/E/J container')
    blocks = []; changes = []
    for region in parsed['regions']:
        if region['version'] != 2:
            raise ValueError('Expected Kamek v2')
        start = region['offset']; commands = bytearray(); seen = set()
        for command in region['commands']:
            address = command['address']; command_id = command['command_id']
            if command['absolute'] and address in REGION_OMISSIONS.get(region['region'], set()):
                changes.append(dict(region=region['region'], action='omit_PAL_only_installation',
                                    address=f'{address:08x}', old_command=command_id))
                continue
            if region['region'] == 'P' and command['absolute'] and address in POLICY:
                if address in seen or len(command['values']) != 1 or command_id not in (32, 64, 65):
                    raise ValueError('Unexpected release policy site shape')
                seen.add(address); new_command, value = POLICY[address]
                commands += struct.pack('>3I', (new_command << 24) | 0xfffffe, address, value)
                changes.append(dict(region='P', action='observed_fixed_write', address=f'{address:08x}',
                                    old_command=command_id, old_value=f"{command['values'][0]:08x}",
                                    new_command=new_command, new_value=f'{value:08x}'))
            else:
                position = command['file_offset']
                words = 1 + int(command['absolute']) + len(command['values'])
                commands += data[position:position + 4 * words]
        if region['region'] == 'P':
            missing = set(POLICY) - seen
            if missing - APPEND_IF_MISSING:
                raise ValueError('Required release policy sites are absent')
            for address in sorted(missing):
                command_id, value = POLICY[address]
                commands += struct.pack('>3I', (command_id << 24) | 0xfffffe, address, value)
                changes.append(dict(region='P', action='append_observed_fixed_write', address=f'{address:08x}',
                                    new_command=command_id, new_value=f'{value:08x}'))
        body = data[start:start + 32 + region['code_size']] + commands
        blocks.append(bytes(body))
    result = struct.pack('>4I', *[len(block) for block in blocks], 0) + b''.join(blocks)
    checked = kamek(result)
    for old, new in zip(parsed['regions'], checked['regions']):
        left = data[old['offset']:old['offset'] + 32 + old['code_size']]
        right = result[new['offset']:new['offset'] + 32 + new['code_size']]
        if left != right:
            raise AssertionError('Policy changed header, code or data')
    return result, changes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('binary', type=Path); parser.add_argument('--report', type=Path)
    args = parser.parse_args(); patched, changes = apply(args.binary.read_bytes()); args.binary.write_bytes(patched)
    if args.report: args.report.write_text(json.dumps(changes, indent=2) + '\n')
    print('Applied 12 observed PAL fixed writes and regional installation policy; code/data unchanged.')
