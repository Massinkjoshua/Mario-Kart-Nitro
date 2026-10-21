"""Create an isolated SD-root candidate; never change the reference or live pack."""
from pathlib import Path
import argparse, hashlib, json, shutil

def stage(root, output, use_build=True):
    output=output.resolve()
    if output.exists(): raise ValueError('Output already exists; choose a new folder.')
    snapshot=(root/'CurrentPack').resolve()
    if output==root.resolve() or snapshot in output.parents:
        raise ValueError('Output must be outside the reference snapshot.')
    replacements=[]
    if use_build:
        for name in ['Code.pul','Loader.pul']:
            source=root/'build'/name
            if not source.is_file(): raise ValueError(f'Missing build/{name}; build first.')
            replacements.append((source,Path('MarioKartNitro_Test/Binaries')/name))
    shutil.copytree(snapshot,output)
    for source,rel in replacements: shutil.copy2(source,output/rel)
    if use_build:
        for name in ['config.pul','ConfigRT.pul','ConfigCT.pul','ConfigBT.pul']:
            shutil.copy2(root/'Project'/name,output/'MarioKartNitro_Test/Binaries'/name)
    status=dict(kind='source-build-candidate'if use_build else'uploaded-reference-copy',
        compiled_binaries_used=use_build,matching_latest_release_source_verified=False,
        gameplay_tested=False,missing_upload_folders=['Tracks','CTBRSTM','Ghosts/Experts','Ghosts/ExpertsRT'],
        config_records_preserved=True,alphabetical_padding_corrected=use_build,
        binaries={n:hashlib.sha256((output/'MarioKartNitro_Test/Binaries'/n).read_bytes()).hexdigest()for n in ['Code.pul','Loader.pul']})
    (output/'NITRO_CANDIDATE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
    return status

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--reference-only',action='store_true',help='Copy supplied files without a source build.')
    args=parser.parse_args();root=Path(__file__).resolve().parent.parent
    try:status=stage(root,args.output,not args.reference_only)
    except ValueError as error:parser.error(str(error))
    print('Created isolated '+status['kind']+': '+str(args.output))
    print('Track, music and ghost uploads are still needed for a complete playable pack.')
