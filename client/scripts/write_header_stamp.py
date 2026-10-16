"""Track header changes without breaking make on supplied filenames with spaces."""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parent.parent;digest=hashlib.sha256()
for folder in ['PulsarEngine','GameSource','KamekInclude','Loader']:
    for p in sorted((root/folder).rglob('*')):
        if p.is_file()and p.suffix in ('.hpp','.h','.inc'):
            digest.update(str(p.relative_to(root)).encode());digest.update(b'\0');digest.update(p.read_bytes())
path=root/'build/header-stamp';text=digest.hexdigest()+'\n'
path.parent.mkdir(exist_ok=True)
if not path.exists()or path.read_text()!=text:path.write_text(text)
