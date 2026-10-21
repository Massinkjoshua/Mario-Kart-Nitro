#!/usr/bin/env python3
"""Restore and rebuild the uploaded experimental audit candidate. GPLv3.
Requires Python 3.9+, make and the documented authorised toolchain. No install,
network download, release reference, server or current pack modification.
"""
import argparse,base64,hashlib,json,shlex,shutil,subprocess,tempfile
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
EXPECTED_CODE='8155c33e2798ed75c45c35161c93e98156869f873d84cda7aab351ea6f76a9d4'
EXPECTED_MAP='63c7114f84dd01fc80e64496d8ddc805d37b4f9128eabdbe2af83ff62be18b40'
EXPECTED_COMPILER='0515a708c5f3e51cab79ed3a16f1d712569ef2e19dcee6f4c14ef6dccd213e3f'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(text):
 p=PurePosixPath(text)
 if p.is_absolute()or '..'in p.parts or '\\'in text:raise ValueError('Invalid relative path')
 return str(p)
def restore(output):
 output=Path(output).absolute()
 if output.exists()or output.is_symlink():raise FileExistsError('Use a new output folder: '+str(output))
 manifest=json.loads((HERE/'source-manifest.json').read_text());checked=[];seen=set();source=(HERE/'Source').resolve()
 for rec in manifest['files']:
  rel=safe(rec['path']);stored=(source/safe(rec['stored_path'])).resolve()
  if not stored.is_relative_to(source)or rel in seen:raise ValueError('Input escapes Source or duplicate output')
  seen.add(rel);data=stored.read_bytes()
  if rec['encoding']=='base64':data=base64.b64decode(data.strip(),validate=True)
  elif rec['encoding']!='raw':raise ValueError('Unsupported encoding')
  if len(data)!=rec['bytes']or hashlib.sha256(data).hexdigest()!=rec['sha256']:raise ValueError('Source hash mismatch: '+rel)
  checked.append((rel,data))
 output.parent.mkdir(parents=True,exist_ok=True);output.mkdir()
 for rel,data in checked:
  p=output/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 return output,len(checked)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--restore-only',action='store_true');p.add_argument('--compiler',type=Path);p.add_argument('--assembler',type=Path);p.add_argument('--linker',type=Path);p.add_argument('--runner',type=Path);p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
 if not a.restore_only:
  for tool in ('compiler','assembler','linker'):
   if getattr(a,tool)is None:p.error('--'+tool+' is required for a build')
  if sha(a.compiler)!=EXPECTED_COMPILER:raise ValueError('Unexpected CodeWarrior compiler; use the documented checksum')
 output,count=restore(a.output)
 if a.restore_only:print('Restored',count,'verified files to',output);return
 order=json.loads((HERE/'object-order.json').read_text());expected={'build/kamek.o'}|{'build/'+str(x.relative_to(output).with_suffix('.o'))for x in(output/'PulsarEngine').rglob('*')if x.suffix in('.cpp','.S')}
 if order[0]!='build/kamek.o'or set(order)!=expected or len(set(order))!=len(order):raise ValueError('Invalid object list')
 runner=[str(a.runner.resolve())]if a.runner else[]
 command=['make','-j'+str(max(1,a.jobs)),'all','CC='+shlex.join(runner+[str(a.compiler.resolve())]),'AS='+shlex.join(runner+[str(a.assembler.resolve())]),'KAMEK='+shlex.quote(str(a.linker.resolve())),'MKNITRO_AC_MODE=0','SECURE=.nitro_no_external_sources','OBJS='+' '.join(order[1:])]
 with(output/'reproduction-build.log').open('w')as log:subprocess.run(command,cwd=output,stdout=log,stderr=subprocess.STDOUT,check=True)
 code,mapsha=sha(output/'build/Code.pul'),sha(output/'build/Code.map');passed=code==EXPECTED_CODE and mapsha==EXPECTED_MAP
 record={'passed':passed,'source_files_verified':count,'explicit_object_order_count':len(order),'code_sha256':code,'map_sha256':mapsha,'compiler_sha256':sha(a.compiler),'assembler_sha256':sha(a.assembler),'linker_sha256':sha(a.linker),'compiled_reference_used_as_build_input':False,'audit_mode':True,'scope':'Uploaded experimental checkpoint only; not Code(10) or latest release'}
 (output/'reproduction-verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
 if not passed:raise SystemExit('Output differs from expected experimental candidate; inspect report.')
if __name__=='__main__':main()
