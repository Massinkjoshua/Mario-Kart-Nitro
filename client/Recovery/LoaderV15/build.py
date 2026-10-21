#!/usr/bin/env python3
"""Build the reconstructed released loader from assembly and typed data only.
Mario Kart Nitro, 16 October 2026; GPLv3. No original binary is an input.
"""
from pathlib import Path
import argparse,json,struct,hashlib
HERE=Path(__file__).resolve().parent
FIELDS=['OSReport','OSFatal','DVDConvertPathToEntrynum','DVDFastOpen','DVDReadPrio','DVDClose','sprintf','RKSystem','NETSHA1Init','NETSHA1Update','NETSHA1GetDigest','region','relStart']
def build():
 from keystone import Ks,KS_ARCH_PPC,KS_MODE_PPC32,KS_MODE_BIG_ENDIAN
 d=json.loads((HERE/'loader_data.json').read_text());ks=Ks(KS_ARCH_PPC,KS_MODE_PPC32|KS_MODE_BIG_ENDIAN)
 code=bytes(ks.asm((HERE/'loader_v15.asm').read_text(),addr=int(d['base'],0))[0]);assert len(code)==d['code_bytes']
 out=bytearray(d['bytes']);out[:len(code)]=code
 for item in d['strings']:
  raw=item['text'].encode('ascii')+b'\0';offset=item['offset'];assert len(code)<=offset<d['params_offset']and offset+len(raw)<=d['params_offset'];out[offset:offset+len(raw)]=raw
 for i,item in enumerate(d['params']):
  struct.pack_into('>13I',out,d['params_offset']+52*i,*[int(item['fields'][name],0)for name in FIELDS])
 struct.pack_into('>66I',out,d['jump_table_offset'],*[int(x,0)for x in d['jump_table']])
 struct.pack_into('>5I',out,d['state_offset'],*d['state_words'])
 sha=hashlib.sha256(out).hexdigest()
 return bytes(out),dict(bytes=len(out),sha256=sha,recorded_release_sha256=d['target_sha256'],matches_recorded_release=sha==d['target_sha256'],original_binary_required=False,source='678 editable PowerPC instructions plus typed diagnostics/API tables/jump table/state',original_cpp_source_recovered=False,full_gameplay_tested=False)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--report',type=Path);parser.add_argument('--allow-modified',action='store_true');args=parser.parse_args()
 if args.output.exists():raise SystemExit('Choose a new output filename; released files are not overwritten.')
 data,report=build()
 if not report['matches_recorded_release']and not args.allow_modified:raise SystemExit('Assembly/data differ from the recorded loader. Use --allow-modified for an intentional new build.')
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(data)
 if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
