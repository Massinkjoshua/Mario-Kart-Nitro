#!/usr/bin/env python3
"""Collect fixed public-input candidates for private review; AGPLv3, 2026-10-16.

Reads no config, database, player state or signing keys. Never publishes files.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import stat
import tarfile

LOCAL_NAMES = ('game_list.tsv', 'translations/gen_translations.lua',
               'translations/utils.lua', 'motd.txt', 'profanity.txt')
EXTERNAL_NAMES = ('multiplier.txt', 'multiplierBeta.txt')
LIMIT = 2 * 1024 * 1024


def read_regular(root, name):
    path = root / name
    if not path.exists() and not path.is_symlink():
        return None
    if path.resolve() != root.resolve() / name:
        raise ValueError('Symlink input refused: ' + name)
    # O_NOFOLLOW also prevents following a substituted final symlink.
    import os
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('Non-regular input refused: ' + name)
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Oversized input refused: ' + name)
    if b'PRIVATE KEY-----' in data:
        raise ValueError('Private-key material refused: ' + name)
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def export(source, external, output):
    source = source.resolve()
    external = external.resolve()
    if not (source / 'go.mod').is_file():
        raise ValueError('Source root must contain go.mod')
    if source == output.resolve() or source in output.resolve().parents:
        raise ValueError('Write outside the source directory')
    files = []
    missing = []
    for root, names, prefix in ((source, LOCAL_NAMES, 'server'),
                                (external, EXTERNAL_NAMES, 'multiplier')):
        for name in names:
            data = read_regular(root, name)
            archive_name = prefix + '/' + name
            if data is None:
                missing.append(archive_name)
            else:
                files.append((archive_name, data))
    manifest = {
        'purpose': 'Private review before any publication; fixed allowlist only.',
        'files': [{'path': n, 'bytes': len(d), 'sha256': digest(d)} for n, d in files],
        'missing': missing,
        'excluded': 'config.xml, keys, certificates, databases, player state, logs and binaries',
    }
    payload = (json.dumps(manifest, indent=2) + '\n').encode()
    # Exclusive create refuses to overwrite an existing file or follow a symlink.
    with output.open('xb') as handle:
        with tarfile.open(fileobj=handle, mode='w:gz') as archive:
            for name, data in files + [('PUBLIC_INPUT_MANIFEST.json', payload)]:
                entry = tarfile.TarInfo(name)
                entry.size = len(data)
                entry.mode = 0o644
                archive.addfile(entry, io.BytesIO(data))
    print(json.dumps({'output': str(output), 'collected': len(files),
                      'missing': missing, 'sha256': digest(output.read_bytes())}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=Path('/opt/mknitro'))
    parser.add_argument('--multiplier-root', type=Path, default=Path('/opt/mknitro-rwfc'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(args.source_root, args.multiplier_root, args.output)
