"""Keep a useful version label when building this recovered archive outside git."""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = "nitro-reconstruction-20261009"
if (root / ".git").exists():
    result = subprocess.run(
        ["git", "describe", "--always", "--dirty", "--match", "NOT A TAG"],
        cwd=root, text=True, capture_output=True, check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        version = result.stdout.strip()
content = '#include "Version.hpp"\n\nwchar_t *GIT_COMMIT = L' + json.dumps(version) + ';\n'
destination = root / "PulsarEngine/Version.cpp"
if not destination.exists() or destination.read_text() != content:
    destination.write_text(content)
