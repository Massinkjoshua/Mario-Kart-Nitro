#!/usr/bin/env python3
"""Compare actual native installations, excluding relocated internal pointers.
Matching installation addresses do not establish matching implementations.
Modified for Mario Kart Nitro, 16 October 2026; GPLv3.
"""
from pathlib import Path
import json
from nitro_formats import kamek, sha

ROOT = Path(__file__).resolve().parent.parent


def main():
    latest = (ROOT / 'CurrentPack/MarioKartNitro_Test/Binaries/Code.pul').read_bytes()
    candidate = (ROOT / 'build/Code.pul').read_bytes()
    reports = []
    for old, new in zip(kamek(latest)['regions'], kamek(candidate)['regions']):
        current = {command['address']: command for command in old['commands'] if command['absolute']}
        rebuilt = {command['address']: command for command in new['commands'] if command['absolute']}
        missing = {hex(key): current[key] for key in current.keys() - rebuilt.keys()}
        extra = {hex(key): rebuilt[key] for key in rebuilt.keys() - current.keys()}
        different = {}
        for key in current.keys() & rebuilt.keys():
            before, after = current[key], rebuilt[key]
            if before['command_id'] != after['command_id'] or (
                before['command_id'] in (32, 33, 34, 36, 37, 38) and before['values'] != after['values']
            ):
                different[hex(key)] = dict(current=[before['command_id'], before['values']],
                                           candidate=[after['command_id'], after['values']])
        reports.append(dict(region=old['region'], current_sites=len(current), rebuilt_sites=len(rebuilt),
                            missing=missing, extra=extra, different_fixed_value_or_opcode=different))
        print(old['region'], 'missing', len(missing), 'extra', len(extra), 'fixed/type differences', len(different))
    report = dict(current_sha256=sha(latest), candidate_sha256=sha(candidate), reports=reports,
                  scope='Native addresses/fixed values only; not implementation parity or runtime validation.')
    (ROOT / 'docs/native-hook-comparison.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
