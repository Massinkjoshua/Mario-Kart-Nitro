#!/usr/bin/env python3
"""Generate the skin/effect RGB table from editable project data; GPLv3.
Mario Kart Nitro source recovery, 16 October 2026.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent


def main():
    rows = json.loads((ROOT / 'Project/DriftColours.json').read_text())['characters']
    assert len(rows) == 48
    lines = ['// Generated from Project/DriftColours.json; edit that file.',
             'static const u8 kSkinDriftColours[CHARACTER_COUNT][TABLE_COUNT][3] = {']
    for index, row in enumerate(rows):
        assert row['character_id'] == index and len(row['tables']) == 51
        colours = []
        for colour in row['tables']:
            rgb = bytes.fromhex(colour)
            assert len(rgb) == 3
            colours.append('{' + ', '.join(str(channel) for channel in rgb) + '}')
        lines.append('    { // character ' + str(index))
        lines.extend('        ' + ', '.join(colours[part:part + 6]) + ',' for part in range(0, 51, 6))
        lines.append('    },')
    lines.append('};')
    content = '\n'.join(lines) + '\n'
    path = ROOT / 'PulsarEngine/CustomCharacters/DriftColours.inc'
    if not path.exists() or path.read_text() != content:
        path.write_text(content)


if __name__ == '__main__':
    main()
