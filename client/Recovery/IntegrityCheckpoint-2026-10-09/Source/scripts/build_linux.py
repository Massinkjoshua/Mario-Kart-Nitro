#!/usr/bin/env python3
"""Reproduce a clean source candidate using pinned official Linux tool releases."""
import argparse
import hashlib
import re
import subprocess
import tarfile
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WIBO_URL='https://github.com/decompals/wibo/releases/download/1.2.0/wibo-x86_64'
WIBO_SHA='13f86a2d618f0dbe67179d349625345eabf9b46450295cb4c904e49f6aff85af'
KAMEK_URL='https://github.com/Treeki/Kamek/releases/download/2026-02-24/linux-x64.tar.gz'
KAMEK_SHA='48e0b095c9774abae95caa965584f1cd231a52bb23d3c425742649aa7f768b5b'
def fetch(url,path,expected):
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        urllib.request.urlretrieve(url,path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Downloaded tool checksum did not match: '+path.name)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--runtime-dir',type=Path,default=ROOT/'toolchain/linux-runtime')
p.add_argument('--jobs',type=int,default=4)
p.add_argument('--enforce',action='store_true',help='Requires a separately reviewed runtime manifest.')
a=p.parse_args()
if a.enforce and not re.search(r'ManifestRuntimeReviewed\s*=\s*true',
    (ROOT/'PulsarEngine/Security/NitroIntegrity/Manifest.hpp').read_text()):
    raise SystemExit('Enforcement requires the final candidate baseline and clean runtime/payload review; current manifest is unreviewed.')
r=a.runtime_dir.resolve();r.mkdir(parents=True,exist_ok=True)
fetch(WIBO_URL,r/'wibo',WIBO_SHA);(r/'wibo').chmod(0o755)
fetch(KAMEK_URL,r/'kamek-linux.tar.gz',KAMEK_SHA)
with tarfile.open(r/'kamek-linux.tar.gz') as archive:
    archive.extractall(r/'kamek-linux',filter='data')
(r/'kamek-linux/Kamek').chmod(0o755)
subprocess.run(['make','clean'],cwd=ROOT,check=True)
subprocess.run(['make','-j'+str(max(1,a.jobs)),
    'CC='+str(r/'wibo')+' ./toolchain/codewarrior/mwcceppc.exe',
    'AS='+str(r/'wibo')+' ./toolchain/codewarrior/mwasmeppc.exe',
    'KAMEK='+str(r/'kamek-linux/Kamek'),
    'MKNITRO_AC_MODE='+('1' if a.enforce else '0')],cwd=ROOT,check=True)
print('Built reconstruction candidate: '+str(ROOT/'build/Code.pul'))
