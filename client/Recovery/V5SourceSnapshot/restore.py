#!/usr/bin/env python3
"""Restore the supplied v5 source exactly from this repository. GPLv3.
Only manifest-listed, hash-verified files are copied into a new directory.
No network, compiler, binary patch, game install or credentials are used.
"""
import argparse,base64,hashlib,json,os,shutil,tempfile
from pathlib import Path,PurePosixPath

def safe_relative(text):
 p=PurePosixPath(text)
 if p.is_absolute()or '..'in p.parts or not p.parts or '\\'in text:raise ValueError('Unsafe manifest path')
 return p

def restore(destination):
 here=Path(__file__).resolve().parent;repo=here.parents[2]
 doc=json.loads((here/'manifest.json').read_text());assert doc['format']==1
 destination=Path(destination).absolute()
 if destination.exists()or destination.is_symlink():raise FileExistsError('Choose a new output folder: '+str(destination))
 destination.parent.mkdir(parents=True,exist_ok=True)
 checked=[];seen=set()
 for record in doc['files']:
  rel=safe_relative(record['path']);source=safe_relative(record['source'])
  if str(rel)in seen:raise ValueError('Duplicate output path')
  seen.add(str(rel));src=(repo/str(source)).resolve()
  if not src.is_relative_to(repo):raise ValueError('Input escapes repository')
  data=src.read_bytes()
  if record['encoding']=='base64':data=base64.b64decode(data.strip(),validate=True)
  elif record['encoding']!='raw':raise ValueError('Unknown encoding')
  if len(data)!=record['bytes']or hashlib.sha256(data).hexdigest()!=record['sha256']:
   raise ValueError('Source hash mismatch: '+record['source'])
  checked.append((str(rel),data))
 stage=Path(tempfile.mkdtemp(prefix='.nitro-v5-',dir=destination.parent))
 try:
  for rel,data in checked:
   target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  # mkdir claims the destination without overwriting an existing folder.
  destination.mkdir()
  try:
   for child in stage.iterdir():shutil.move(str(child),destination/child.name)
  except BaseException:
   shutil.rmtree(destination);raise
 finally:shutil.rmtree(stage,ignore_errors=True)
 return {'files':len(checked),'bytes':sum(len(data)for _,data in checked),'output':str(destination)}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
 print(json.dumps(restore(parser.parse_args().output),indent=2))
