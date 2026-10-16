#!/usr/bin/env python3
"""Assemble the recovered final PAL edits on the exact October binary baseline.

This intentionally requires a labelled reference binary. It is not a clean
compile of the core and must not be described as complete Corresponding Source.
The output can establish exact reproduction of these final edits alone.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from nitro_formats import COMMANDS, kamek


def digest(data):
    return hashlib.sha256(data).hexdigest()


def describe(command):
    return dict(operation=command['command'], absolute=command['absolute'],
                address=f"0x{command['address']:08x}",
                values=[f'0x{value:08x}' for value in command['values']])


def serialize(command):
    operation = next(key for key, name in COMMANDS.items() if name == command['operation'])
    address = int(command['address'], 0)
    header = (operation << 24) | (0xfffffe if command['absolute'] else address)
    words = [header] + ([address] if command['absolute'] else [])
    words += [int(value, 0) for value in command['values']]
    return struct.pack('>' + 'I' * len(words), *words)


def rebuild(baseline):
    try:
        from keystone import Ks, KS_ARCH_PPC, KS_MODE_PPC32, KS_MODE_BIG_ENDIAN
    except ImportError as exc:
        raise SystemExit('Install requirements-recovery.txt before assembling this recipe.') from exc
    settings = json.loads((HERE / 'patch.json').read_text())
    if digest(baseline) != settings['baseline_sha256']:
        raise ValueError('Wrong baseline: final PAL patches require the exact labelled Code(10) reference.')
    parsed = kamek(baseline)
    pal = parsed['regions'][0]
    assert pal['region'] == 'P' and pal['bss_size'] == 0
    start = pal['offset']
    code = bytearray(baseline[start + 32:start + 32 + pal['code_size']])
    assembler = Ks(KS_ARCH_PPC, KS_MODE_PPC32 | KS_MODE_BIG_ENDIAN)
    for patch in settings['code_patches']:
        instruction = bytes(assembler.asm(patch['assembly'], addr=patch['offset'])[0])
        assert len(instruction) == 4
        code[patch['offset']:patch['offset'] + 4] = instruction
    append = settings['append_start']
    if append < len(code):
        raise ValueError('Assembly overlaps baseline code')
    code += bytes(append - len(code))
    code += bytes(assembler.asm((HERE / 'latest_pal.asm').read_text(), addr=append)[0])
    assert len(code) == settings['palette_offset']
    palette = json.loads((HERE / 'drift_colours.json').read_text())['characters']
    assert len(palette) == 48
    for index, character in enumerate(palette):
        assert character['character_id'] == index and len(character['tables']) == 51
        for colour in character['tables']:
            rgb = bytes.fromhex(colour)
            assert len(rgb) == 3
            code += rgb
    for name in settings['effect_prefixes']:
        encoded = name.encode('ascii') + b'\0'
        assert len(encoded) <= 16
        code += encoded.ljust(16, b'\0')
    commands = [describe(command) for command in pal['commands']]
    for edit in reversed(settings['command_edits']):
        assert commands[edit['start']:edit['end']] == edit['expected']
        commands[edit['start']:edit['end']] = edit['replacement']
    header = bytearray(baseline[start:start + 32])
    struct.pack_into('>I', header, 12, len(code))
    section = bytes(header) + bytes(code) + b''.join(map(serialize, commands))
    sizes = parsed['declared_region_sizes'][:]
    sizes[0] = len(section)
    result = struct.pack('>4I', *sizes) + section + baseline[start + pal['size']:]
    checked = kamek(result)
    assert result[16 + sizes[0]:] == baseline[start + pal['size']:]
    report = dict(baseline_sha256=digest(baseline), output_sha256=digest(result),
                  recorded_release_sha256=settings['target_sha256'],
                  matches_recorded_release=digest(result) == settings['target_sha256'],
                  pal_commands=len(checked['regions'][0]['commands']),
                  usa_japan_unchanged=True, full_core_rebuilt_from_source=False,
                  gameplay_tested=False)
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=HERE.parent / 'Reference/Code-10-UNCHANGED.pul')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Choose a new output filename; this tool does not overwrite releases.')
    result, report = rebuild(args.baseline.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
