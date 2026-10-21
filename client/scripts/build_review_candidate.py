#!/usr/bin/env python3
"""Build one isolated source-first client/loader candidate and report. GPLv3.
No released engine binary, private runtime pack, server write or installation.
The output must be new. Tools are supplied separately under their own licences.
"""
import argparse,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_VERSION='nitro-source-candidate-20261018'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for flag in ['compiler','assembler','linker']:p.add_argument('--'+flag,type=Path,required=True)
 p.add_argument('--runner',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--version',default=DEFAULT_VERSION);p.add_argument('--jobs',type=int,default=4)
 a=p.parse_args();out=a.output.absolute()
 if out.exists()or out.is_symlink():raise FileExistsError('Choose a new output directory: '+str(out))
 if not a.version or len(a.version)>120 or any(ord(c)<32 for c in a.version):raise ValueError('Use a printable build ID of 1 to 120 characters')
 for tool in [a.compiler,a.assembler,a.linker]+([a.runner]if a.runner else[]):
  if not tool.is_file():raise FileNotFoundError(str(tool))
 import keystone
 out.mkdir(parents=True);work=out/'BuildWork';work.mkdir();reports=out/'Reports';reports.mkdir()
 for name in ['GameSource','PulsarEngine','KamekInclude','Loader','scripts']:
  shutil.copytree(ROOT/name,work/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 shutil.copyfile(ROOT/'Makefile',work/'Makefile')
 for notice in ROOT.iterdir():
  if notice.is_file() and notice.name.startswith(('LICENSE','COPYING','CREDITS','NOTICE','ATTRIBUTION')):shutil.copyfile(notice,work/notice.name)
 (work/'Project').mkdir();shutil.copyfile(ROOT/'Project/DriftColours.json',work/'Project/DriftColours.json')
 loader_source=work/'Recovery/LoaderV15';loader_source.parent.mkdir(parents=True);shutil.copytree(ROOT/'Recovery/LoaderV15',loader_source,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 env=os.environ.copy();env['MKNITRO_BUILD_VERSION']=a.version
 runner=[str(a.runner.resolve())]if a.runner else[]
 command=['make','-j'+str(max(1,a.jobs)),'all','CC='+shlex.join(runner+[str(a.compiler.resolve())]),'AS='+shlex.join(runner+[str(a.assembler.resolve())]),'KAMEK='+shlex.quote(str(a.linker.resolve())),'SECURE=external/not-in-this-isolated-build']
 with(reports/'client-build.log').open('w')as log:subprocess.run(command,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 # Reconstruct the released loader from 678 editable instructions and typed data.
 with(reports/'loader-build.log').open('w')as log:subprocess.run([sys.executable,str(loader_source/'build.py'),'--output',str(work/'build/Loader-v15.pul'),'--report',str(reports/'loader-verification.json')],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 # Validate the source-built P/E/J module and fixed-write policy, using the
 # existing implementation; unlike the broader legacy checker this needs no
 # precompiled runtime pack, C++ loader map, or omitted Creator resources.
 sys.path.insert(0,str(work/'scripts'));from nitro_formats import kamek;from apply_release_policy import POLICY
 code=work/'build/Code.pul';regions=kamek(code.read_bytes());assert not regions['trailing_bytes']and [x['region']for x in regions['regions']]==list('PEJ')
 for reg in regions['regions']:
  assert reg['version']==2 and reg['ctor_start']<=reg['ctor_end']<=reg['code_size']
 for address,(kind,value)in POLICY.items():
  found=[c for c in regions['regions'][0]['commands']if c['absolute']and c['address']==address];assert len(found)==1 and(found[0]['command_id'],found[0]['values'])==(kind,[value])
 loader=json.loads((reports/'loader-verification.json').read_text());assert loader['matches_recorded_release']and not loader['original_binary_required']
 overlay=out/'CandidateOverlay/MarioKartNitro_Test/Binaries';overlay.mkdir(parents=True)
 shutil.copyfile(code,overlay/'Code.pul');shutil.copyfile(work/'build/Loader-v15.pul',overlay/'Loader.pul');shutil.copyfile(work/'build/Code.map',reports/'Code.map')
 manifest=[{'path':str(f.relative_to(work)),'bytes':f.stat().st_size,'sha256':digest(f)}for f in sorted(work.rglob('*'))if f.is_file()and 'build'not in f.relative_to(work).parts and '__pycache__'not in f.parts and f.suffix!='.pyc']
 (reports/'compiled-source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 report={'kind':'source-built-review-candidate','build_id':a.version,'code_sha256':digest(overlay/'Code.pul'),'loader_sha256':digest(overlay/'Loader.pul'),'loader_kind':'exact reconstructed released v15 assembly target','regions':[{'region':x['region'],'code_bytes':x['code_size'],'commands':len(x['commands'])}for x in regions['regions']],'compiler_sha256':digest(a.compiler),'assembler_sha256':digest(a.assembler),'linker_sha256':digest(a.linker),'runner_sha256':digest(a.runner)if a.runner else None,'keystone_version':keystone.__version__,'source_files_hashed':len(manifest),'precompiled_core_used_as_build_input':False,'private_runtime_assets_needed_for_build':False,'source_manifest_sha256':digest(reports/'compiled-source-manifest.json'),'structural_checks_passed':True,'historical_released_core_match':False,'dolphin_or_wii_runtime_tested':False,'server_hash_approved':False,'deployed':False}
 (reports/'BUILD_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'README-FIRST.txt').write_text('Mario Kart Nitro source-built review candidate\n\nBuild ID: '+a.version+'\nThis is a test candidate, not an approved public release.\nCandidateOverlay contains only Code.pul and the reconstructed released Loader.pul.\nUse a separate COPY of the complete current pack and your own legal game image.\nBack up the two original binary files before applying the overlay to that test copy.\nKeep all existing configs, tracks, music, UI and other assets.\nDo not replace the live launcher download or approve an online hash before runtime review.\n\nFirst test offline: launch, licence, characters, vehicles/previews, track selection,\nrace start/finish, items, HUD, music and Time Trials. Then test leaderboard load,\npage changes, backing out/reopening, and a controlled online session after approval.\nRecord the build ID, platform, actions, result and complete crash log if one occurs.\n\nReports/BUILD_RESULT.json binds the binaries to a compiled-source manifest.\nBuildWork contains the source that built this candidate, without proprietary tools.\nThe newer C++ loader remains available in the full source snapshot; this candidate\nuses the reconstructed released v15 assembly loader to keep that component familiar.\n\nMatching source for every older distributed core, asset permissions/preferred inputs,\nand full runtime validation remain separate unfinished work.\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
