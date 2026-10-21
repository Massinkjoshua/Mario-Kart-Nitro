#!/usr/bin/env python3
"""Insert source links into the existing website; does not deploy anything."""
from pathlib import Path
import argparse
import hashlib

START = b'    <!-- MKNITRO-SOURCE-CREDITS:START -->'
END = b'    <!-- MKNITRO-SOURCE-CREDITS:END -->'


def patched(original, section):
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1:
            raise ValueError('Ambiguous existing source section; inspect manually')
        begin = original.index(START)
        end = original.index(END, begin) + len(END)
        if original[end:end+2] == b'\r\n':
            end += 2
        elif original[end:end+1] == b'\n':
            end += 1
        return original[:begin] + section + original[end:]
    # Insert only at the existing downloads section; never replace other content.
    anchor = b'    <section class="section" id="downloads">'
    if original.count(anchor) != 1:
        raise ValueError('Expected one downloads section; merge the HTML snippet manually')
    at = original.index(anchor)
    return original[:at] + section + original[at:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index_html', type=Path)
    args = parser.parse_args()
    path = args.index_html.resolve()
    if not path.is_file():
        parser.error('Provide the current project dist/index.html path')
    original = path.read_bytes()
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    section = Path(__file__).with_name('source-credits-section.html').read_bytes()
    section = section.replace(b'\r\n', b'\n').replace(b'\n', newline)
    result = patched(original, section)
    if result == original:
        print('Source and credits section already up to date. No changes.')
        return
    backup_dir = path.parent.parent / 'source-credits-backups'
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / ('index-' + hashlib.sha256(original).hexdigest()[:16] + '.html')
    if backup.exists():
        if backup.read_bytes() != original:
            raise ValueError('Existing backup differs; refusing to overwrite')
    else:
        with backup.open('xb') as stream:
            stream.write(original)
    path.write_bytes(result)
    print('Updated: ' + str(path))
    print('Original backup: ' + str(backup))
    print('Rebuild the existing website Worker and run its checks before publishing.')


if __name__ == '__main__':
    main()
