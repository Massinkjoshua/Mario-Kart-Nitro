#!/usr/bin/env python3
"""Build the isolated released-leaderboard recovery profile. GPLv3.
Requires the normal client to have been built from source first. Does not use
released Code.pul as a build input or install anything into a game pack.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--compiler',required=True,help='Authorised CodeWarrior mwcceppc executable')
 parser.add_argument('--runner',help='Optional Windows executable runner, e.g. wibo')
 parser.add_argument('--linker',required=True,help='Kamek executable')
 parser.add_argument('--output-dir',type=Path,default=ROOT/'build/released-leaderboard')
 args=parser.parse_args();out=args.output_dir.absolute()
 if out.exists():raise FileExistsError('Choose a new output directory; existing outputs are preserved: '+str(out))
 source=ROOT/'Recovery/ReleasedLeaderboard/PulsarEngine/UI/VRLeaderboard/VRLeaderboard.cpp'
 objects=[ROOT/'build/kamek.o']+sorted(x for x in(ROOT/'build/PulsarEngine').rglob('*.o')if x.relative_to(ROOT/'build/PulsarEngine').as_posix()!='UI/VRLeaderboard/VRLeaderboard.o')
 if not objects[0].is_file()or len(objects)<2:raise FileNotFoundError('Build the normal client source first (see client README).')
 out.mkdir(parents=True);obj=out/'VRLeaderboard.o'
 flags=['-I-','-i','KamekInclude','-i','GameSource','-i','Recovery/ReleasedLeaderboard/PulsarEngine','-i','PulsarEngine','-i','Loader','-opt','all','-inline','auto','-enum','int','-fp','hard','-sdata','0','-sdata2','0','-maxerrors','1','-func_align','4','-DMKNITRO_SERVER','-DPULSAR_RANDOM_KEY=0xADD2BFAF']
 compiler=([args.runner]if args.runner else[])+[args.compiler]
 with(out/'build.log').open('w')as log:
  subprocess.run(compiler+flags+['-c','-o',str(obj),str(source)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run([args.linker,*map(str,objects),str(obj),'-dynamic','-externals=GameSource/symbols.txt','-externals=GameSource/anticheat.txt','-versions=GameSource/versions.txt','-output-kamek='+str(out/'Code.$KV$.bin'),'-output-map='+str(out/'Code.map')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 import sys
 subprocess.run([sys.executable,str(ROOT/'scripts/combine_bin.py'),'-p',str(out/'Code.P.bin'),'-e',str(out/'Code.E.bin'),'-j',str(out/'Code.J.bin'),'-o',str(out/'Code.pul')],cwd=ROOT,check=True)
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 report={'purpose':'Isolated request-flow source recovery; not a deployable current release','object_inputs_sha256':{str(x.relative_to(ROOT)):sha(x)for x in objects},'source_sha256':{str(x.relative_to(ROOT)):sha(x)for x in source.parent.iterdir()if x.is_file()},'compiler_sha256':sha(Path(args.compiler)),'code_sha256':sha(out/'Code.pul'),'map_sha256':sha(out/'Code.map'),'released_binary_used_as_build_input':False}
 (out/'build-record.json').write_text(json.dumps(report,indent=2)+'\n');print('Built recovery profile:',out)
if __name__=='__main__':main()
