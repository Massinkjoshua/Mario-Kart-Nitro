import importlib.util,json,tempfile,hashlib,sys,types
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).parents[1]/'Server/install.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for mode in ['success','health_failure','backup_failure']:
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp);m.HERE=root/'package';m.HERE.mkdir();m.LIVE=root/'live/wwfc';m.LIVE.parent.mkdir();m.CONFIG=m.LIVE.parent/'config.xml'
  m.LIVE.write_bytes(b'old executable');m.CONFIG.write_text('<config><databaseName>mknitro</databaseName></config>')
  (m.HERE/'wwfc').write_bytes(b'new executable');(m.HERE/'checksums.json').write_text(json.dumps({'wwfc_sha256':hashlib.sha256(b'new executable').hexdigest()}))
  calls=[];approvals=[];health_calls=[]
  def run(args,**kwargs):
   calls.append(args)
   if args[:2]==['systemctl','show']:return types.SimpleNamespace(stdout='WorkingDirectory=/opt/mknitro\nExecStart='+str(m.LIVE))
   if args[0]=='runuser':
    if mode=='backup_failure':raise RuntimeError('simulated dump failure')
    kwargs['stdout'].write(b'database backup')
   return types.SimpleNamespace(stdout='')
  def health():
   health_calls.append(1)
   if mode=='health_failure' and len(health_calls)==1:raise RuntimeError('simulated health failure')
   return {'success':True,'players':[{'miiData':'present'}]}
  m.run=run;m.health=health;m.approval=lambda restore=False:approvals.append(restore);sys.argv=['install.py']
  failed=False
  try:m.main()
  except RuntimeError:failed=True
  assert failed==(mode!='success')
  assert m.LIVE.read_bytes()==(b'new executable' if mode=='success' else b'old executable')
  assert approvals==([False] if mode=='success' else [True] if mode=='health_failure' else [])
  if mode=='backup_failure':assert not any(c[:2]==['systemctl','stop'] for c in calls)
  else:
   backup=Path((m.HERE/'last-backup.txt').read_text().strip())
   assert (backup/'wwfc').read_bytes()==b'old executable' and (backup/'database.dump').stat().st_size>0
print('PASS: installer backup ordering, successful replacement, failed-health rollback, and abort before service stop when database backup fails. All system/service calls simulated.')

# Exercise the actual health check against a local HTTP server on a random port.
from http.server import HTTPServer,BaseHTTPRequestHandler
import threading
spec2=importlib.util.spec_from_file_location('health_installer',Path(__file__).parents[1]/'Server/install.py')
h=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(h)
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  assert self.path=='/api/leaderboard/in-game?page=1'
  self.send_response(200);self.end_headers();self.wfile.write(b'{"success":true,"players":[]}')
 def log_message(self,*args):pass
server=HTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 with tempfile.TemporaryDirectory() as tmp:
  h.CONFIG=Path(tmp)/'config.xml'
  h.CONFIG.write_text('<config><nasPort>'+str(server.server_port)+'</nasPort></config>')
  assert h.health()=={'success':True,'players':[]}
finally:server.shutdown();server.server_close();thread.join()
print('PASS: actual health request uses nasPort from XML and receives valid JSON over local HTTP.')
