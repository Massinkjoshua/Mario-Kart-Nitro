"""Generate version metadata only during a build, including non-git source ZIPs."""
import json
from pathlib import Path
import subprocess

version = 'mknitro-integration-source'
try:
    result = subprocess.run(['git', 'describe', '--always', '--dirty', '--match', 'NOT A TAG'],
                            text=True, capture_output=True)
    if result.returncode == 0:
        version = result.stdout.strip()
except FileNotFoundError:
    pass  # A source archive can be built without installing git.
content = '#include "Version.hpp"\n\nwchar_t *GIT_COMMIT = L' + json.dumps(version) + ';\n'
path = Path('PulsarEngine/Version.cpp')
if not path.exists() or path.read_text() != content:
    path.write_text(content)
