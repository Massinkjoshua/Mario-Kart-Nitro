# Complete supplied v5 source restoration

This directory closes the omission of the original supplied v5 source files
from the public recovery project. The snapshot restores all 1,097 files
(4,025,213 bytes) from MKNitro_Menu_Character_Fix_v5/Source, byte-for-byte.

42 files differ from or are absent in the current candidate and are stored in
files/. The other 1,055 are identical existing files in client/. manifest.json
lists every output path, repository input, byte length and SHA-256. The single
binary UI control resource is stored as base64 and decoded during restoration.
Original text, licence and notices are preserved without modification.

From the repository root, run with Python 3.9 or later:

```sh
python3 client/Recovery/V5SourceSnapshot/restore.py --output ../Nitro-v5-original
```

Use a new output folder. The script verifies all inputs before writing, rejects
existing output paths, and copies only the manifest-listed files. It needs no
network access, proprietary tools, precompiled core or live configuration.
VERIFICATION.json records exact path/hash equality against the supplied tree,
including rejection of an existing output folder. All 1,055 shared input blobs
were also checked against the published GitHub tree before this update.

## What this restores

The complete supplied Source directory includes GameSource, PulsarEngine,
KamekInclude, Loader, the supplied Makefiles/scripts, LICENSE and one UI control
resource. It does not invent files absent from that directory, including an
external rr-secure checkout, compiler executables or a historical .env.
The original Makefile generates Version.cpp from git metadata during a build;
keep this restored snapshot intact and build a separate copy for investigations.

Exact source restoration is separate from binary correspondence. The existing
CoreAudit-2026-10-16 report shows that the supplied source/toolchain combination
does not reproduce the bundled v5 binary in full. This snapshot is not certified
as the complete source of the latest release, and it does not resolve the
remaining historical/current client, runtime or asset questions.
