from pathlib import Path
import sys,re,struct,json,collections,bisect
sys.path.insert(0,str(Path(__file__).parent/'lib'))
from nitro_formats import kamek

def load(binary,mapfile):
 d=binary.read_bytes();r=kamek(d)['regions'][0];assert r['region']=='P', 'PAL section required';raw=d[r['offset']+32:r['offset']+32+r['code_size']];symbols=[]
 for line in mapfile.read_text().splitlines():
  m=re.match(r'\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]+)\s+(.+)',line)
  if m:symbols.append((int(m[1],16),int(m[2],16),m[3]))
 text_end=next(a for a,s,n in symbols if n=='_e_text');text=[x for x in symbols if x[1]and x[0]<text_end and not x[2].startswith('_f_')]
 return dict(raw=raw,region=r,syms=symbols,functions=text,byname={n:(a,s) for a,s,n in text},relocs={c['address']:c for c in r['commands']if not c['absolute']})

def norm(obj,start,size):
 b=bytearray(obj['raw'][start:start+size]);targets=[]
 for a,c in obj['relocs'].items():
  if not start<=a<start+size:continue
  kind=c['command_id'];off=a-start
  if kind in (4,5,6):b[off:off+2]=b'\0\0'
  elif kind==1:b[off:off+4]=b'\0'*4
  elif kind==10:
   w=struct.unpack_from('>I',b,off)[0];struct.pack_into('>I',b,off,w&0xfc000003)
  else:continue
  targets.append((off,kind,c['values'][0]))
 for off in range(0,len(b)-3,4):
  a=start+off
  if a in obj['relocs']:continue
  w=struct.unpack_from('>I',b,off)[0];op=w>>26
  if op==18:
   disp=w&0x03fffffc;disp=disp-0x4000000 if disp&0x2000000 else disp
   target=disp if w&2 else a+disp
   if not start<=target<start+size:
    struct.pack_into('>I',b,off,w&0xfc000003);targets.append((off,'branch',target))
  # Conditional branches retained exactly; they should stay within a function.
 return bytes(b),targets

def target_labels(obj, target, function_start, function_size):
 if target >= 0x80000000:
  return {('native', target)}
 if function_start <= target < function_start + function_size:
  return {('self', target-function_start)}
 return {(name,size,target-start) for start,size,name in obj['syms']
         if size and not name.startswith(('_f_', '_e_')) and start<=target<start+size}


def compare(left,right):
 rows=[]
 for a,size,name in left['functions']:
  if name not in right['byname']:rows.append(dict(name=name,status='no_original_symbol',size=size));continue
  b,rs=right['byname'][name]
  if size!=rs:rows.append(dict(name=name,status='size_differs',size=size,original_size=rs));continue
  ln,lt=norm(left,a,size);rn,rt=norm(right,b,size)
  row=dict(name=name,size=size,left_offset=a,right_offset=b)
  if ln!=rn:
   row.update(status='body_differs',normalized_word_differences=sum(ln[i:i+4]!=rn[i:i+4]for i in range(0,size,4)))
  elif [(o,k)for o,k,t in lt]!=[(o,k)for o,k,t in rt]:
   row.update(status='relocation_layout_differs')
  else:
   unresolved=[];different=[]
   for (off,kind,lval),(_,_,rval) in zip(lt,rt):
    ll=target_labels(left,lval,a,size);rl=target_labels(right,rval,b,size)
    if not ll or not rl:unresolved.append(dict(offset=off,kind=kind,left=lval,right=rval))
    elif not ll.intersection(rl):different.append(dict(offset=off,kind=kind,left=lval,right=rval,left_labels=sorted(ll,key=str),right_labels=sorted(rl,key=str)))
   row.update(status='target_differs' if different else 'target_unresolved' if unresolved else 'body_and_targets_match',target_count=len(lt))
   if different:
    def without_size(label):return label if label[0]in('native','self')else(label[0],label[2])
    if all({without_size(t)for t in item['left_labels']}&{without_size(t)for t in item['right_labels']} for item in different):row['status']='referenced_symbol_size_differs'
    row['different_targets']=different
   if unresolved:row['unresolved_targets']=unresolved
  rows.append(row)
 return dict(summary=dict(collections.Counter(r['status']for r in rows)),rows=rows)

if __name__=='__main__':
 import argparse,hashlib
 p=argparse.ArgumentParser(description='Compare named PAL text symbols; this is not whole-release source certification.')
 p.add_argument('--candidate',type=Path,required=True);p.add_argument('--candidate-map',type=Path,required=True)
 p.add_argument('--reference',type=Path,required=True);p.add_argument('--reference-map',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 args=p.parse_args();left=load(args.candidate,args.candidate_map);right=load(args.reference,args.reference_map)
 report=compare(left,right)
 report['inputs']={name:{'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}for name,path in [('candidate',args.candidate),('candidate_map',args.candidate_map),('reference',args.reference),('reference_map',args.reference_map)]}
 report['method']='Named text-symbol comparison. Only explicit Kamek relocation fields and out-of-function unconditional branch displacements are masked. Local/conditional branches and instruction flags remain exact. Each masked target must resolve to the same named/sized symbol plus offset, the same offset in the compared function, or exactly the same native address. Unresolved references are not treated as matches.'
 report['limits']=['PAL text symbols only; no data/BSS/full-command-stream or runtime proof','Symbol maps must belong to their respective binaries; map ownership is an input assumption','Matching named targets do not prove the referenced implementations match','No claim of complete Corresponding Source']
 args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary']))
