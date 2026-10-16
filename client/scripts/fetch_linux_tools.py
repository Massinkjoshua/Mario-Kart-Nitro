#!/usr/bin/env python3
"""Fetch checksum-pinned official wibo/Kamek releases for Linux x86_64.
Modified for Mario Kart Nitro, 16 October 2026; GPLv3.
Third-party tools retain their own licences; they are not relicensed here.
"""
from pathlib import Path
import hashlib
import io
import json
import os
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
TOOLS = [
    ('wibo', 'https://github.com/decompals/wibo/releases/download/1.2.0/wibo-x86_64',
     '13f86a2d618f0dbe67179d349625345eabf9b46450295cb4c904e49f6aff85af'),
    ('Kamek', 'https://github.com/Treeki/Kamek/releases/download/2026-02-24/linux-x64.tar.gz',
     '48e0b095c9774abae95caa965584f1cd231a52bb23d3c425742649aa7f768b5b'),
]


def main():
    destination = ROOT / 'tools/linux'
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url, expected in TOOLS:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise SystemExit('Checksum mismatch for ' + name)
        if name == 'Kamek':
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                members = [entry for entry in archive.getmembers()
                           if Path(entry.name).name == 'Kamek' and entry.isfile()]
                if len(members) != 1:
                    raise SystemExit('Unexpected Kamek archive layout')
                data = archive.extractfile(members[0]).read()
        target = destination / name
        if target.exists() and target.read_bytes() != data:
            raise SystemExit('Different local tool already exists: ' + str(target))
        target.write_bytes(data)
        target.chmod(0o755)
        records.append(dict(name=name, download=url, archive_sha256=actual,
                            executable_sha256=hashlib.sha256(data).hexdigest()))
        print('Checksum verified:', name)
    (destination / 'provenance.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    main()
