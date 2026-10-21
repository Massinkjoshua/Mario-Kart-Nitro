#!/usr/bin/env python3
"""Read-only source/export verification helper; GNU AGPLv3, 16 October 2026.

Run on the actual server with its source root and running PID. No service is
changed. Secret configuration, databases, keys, logs and save files are excluded.
Review the export before publishing, including any credentials embedded in code.
"""
from pathlib import Path
import argparse, hashlib, io, json, tarfile

SOURCE_SUFFIXES = {'.go', '.mod', '.sum', '.sql', '.md', '.rst', '.h', '.hpp',
                   '.c', '.cpp', '.S', '.s', '.asm', '.sh', '.py'}
SOURCE_NAMES = {'LICENSE', 'COPYING', 'NOTICE', 'AUTHORS', 'Makefile', 'Dockerfile'}
EXCLUDED = {'.git', 'state', 'logs', 'log', 'keys', 'certs', 'certificates',
            'backup', 'backups', '__pycache__', 'node_modules'}


def sha(data): return hashlib.sha256(data).hexdigest()


def running_binary_sha(pid):
    executable = Path('/proc') / str(pid) / 'exe'
    try:
        with executable.open('rb') as handle:
            return hashlib.file_digest(handle, 'sha256').hexdigest()
    except OSError as error:
        raise ValueError('Cannot read the running executable. Run under the server owner/root account with /proc access.') from error


def export(source, pid, output):
    source = source.resolve()
    if not source.is_dir() or not (source / 'go.mod').is_file():
        raise ValueError('Source root must contain the running server project go.mod')
    if output.exists(): raise ValueError('Choose a new output filename')
    if source == output.resolve() or source in output.resolve().parents:
        raise ValueError('Write the export outside the source directory')
    binary_sha = running_binary_sha(pid)
    rows = []; files = []
    for path in sorted(source.rglob('*')):
        rel = path.relative_to(source)
        if path.is_symlink() or not path.is_file(): continue
        if any(part.lower() in EXCLUDED or part.startswith('.') or 'backup' in part.lower()
               for part in rel.parts): continue
        if path.suffix not in SOURCE_SUFFIXES and path.name not in SOURCE_NAMES: continue
        if path.suffix == '.sql' and path.name != 'schema.sql' and not any(
            part.lower() in {'schema', 'migrations'} for part in rel.parts[:-1]
        ): continue
        data = path.read_bytes()
        if b'-----BEGIN PRIVATE KEY-----' in data or b'-----BEGIN RSA PRIVATE KEY-----' in data:
            raise ValueError('Private-key material found; export refused: ' + str(rel))
        files.append((str(rel), data)); rows.append(dict(path=str(rel), bytes=len(data), sha256=sha(data)))
    if not any(row['path'] == 'go.mod' for row in rows): raise ValueError('No module source selected')
    manifest = dict(export_date_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                    running_pid=pid, running_executable_sha256=binary_sha, files=rows,
                    running_binary_rebuilt_from_this_source=False,
                    excluded='Private configs, keys, database/player data, logs, hidden files and backups.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, 'w:gz') as archive:
        for name, data in files + [('SOURCE_EXPORT_MANIFEST.json', (json.dumps(manifest, indent=2)+'\n').encode())]:
            info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))
    print(json.dumps(dict(output=str(output), source_files=len(rows), executable_sha256=binary_sha,
                          archive_sha256=sha(output.read_bytes())), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.pid <= 0: parser.error('PID must identify the running NitroWFC server')
    export(args.source_root, args.pid, args.output)
