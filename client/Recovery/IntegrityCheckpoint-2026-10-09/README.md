# Verified source for the uploaded 9 October experimental checkpoint

The operator supplied MKNitro_Pulsar_NitroIntegrity_Source_Checkpoint_Updated.zip
on 16 October 2026. Its README dates it to 9 October and calls its build a
reconstruction candidate. We reproduced that complete experimental candidate
and its linker map byte-for-byte, and repeated the build from this publication's
Source directory with the explicit order in object-order.json.

| Item | SHA-256 |
| --- | --- |
| Uploaded ZIP | edbc7067bc018b55a0a2225d17e5b9c4697f1d449ce0434ca8ed312a2e3fca23 |
| Uploaded/rebuilt candidate | 8155c33e2798ed75c45c35161c93e98156869f873d84cda7aab351ea6f76a9d4 |
| Uploaded/rebuilt linker map | 63c7114f84dd01fc80e64496d8ddc805d37b4f9128eabdbe2af83ff62be18b40 |
| Released Code(10), reference in upload | 0f5364590f8ec8164f06a934666bdbd9252b87edf7d31c79bf93e189f30c15bc |
| Latest supplied released Code.pul | 58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364 |

The reproduced candidate is 1,654,912 bytes: PAL, USA and Japan Kamek modules
are each 551,632 bytes; Korea is absent. The original Makefile relies on unsorted
filesystem discovery. object-order.json fixes the original order of all 187
objects, also recorded in the upload's original clean-build log. This removes
that source of nondeterminism without reading any reference binary during a build.

## Restore and build

From this directory, with Python 3.9+, make and the authorised toolchain:

```sh
python3 rebuild.py --output /path/to/NEW-Nitro-October9 --compiler /path/to/mwcceppc.exe --assembler /path/to/mwasmeppc.exe --runner /path/to/wibo --linker /path/to/Kamek
```

Omit --runner when Windows executables run directly. The verified run used
CodeWarrior Embedded PowerPC 4.3 build 224, wibo 1.2.0 and Kamek 2.0. Compiler,
assembler and linker checksums are in REPRODUCTION.json; rebuild.py checks the
compiler checksum. Source-only restoration is also available:

```sh
python3 rebuild.py --restore-only --output /path/to/NEW-Nitro-October9
```

Use a new output folder. Every source input is hash-verified before copying.
The script selects audit mode, fixes the object order, excludes an unintended
external rr-secure checkout and invokes all rather than install. It produces
Code.pul, Code.map, a log and reproduction-verification.json in the output.
It never downloads tools, uses a precompiled core, installs a pack or registers
a server hash. Copy this whole directory when sharing the build recipe.

## Included and omitted

Source contains 1,136 byte-preserved source/test files (4,143,638 decoded bytes),
including the supplied engine/GameSource/loader headers and code, Makefile,
build flags, original licences, integrity tests/tools and verification scripts.
source-manifest.json records every original path, size and SHA-256. The one
binary UI control resource is stored as base64 and decoded during restoration.
The original .env contains only build-tool paths and audit-mode compile flags.

omitted-inputs.json identifies 201 compiler/toolchain, compiled reference and
historical audit-evidence files excluded from this source snapshot. They are not
build inputs to this recipe. The original README inside Source remains unchanged;
its references to bundled compilers, Reference, Candidate and older Recovery
records describe the original ZIP, not this source-only publication. Integration
checks that explicitly read Reference still require the operator's omitted input.

## Scope and remaining work

On 16 October, the uploaded integrity policy/adapter, integration and HTTP reserve
host tests passed, along with 124 rating and 72 item-window compiled PowerPC cases
with native calls intercepted. On 18 October, the source-only restoration/build
was run again and compared directly with both original candidate and map bytes.
REPRODUCTION.json records this successful source-only build.

This is the source of the uploaded experimental audit candidate, not proof of
source correspondence for Code(10) or the latest release. The ZIP contains
Code(10) only as an unchanged reference. This checkpoint predates later changes
already integrated in the active source candidate. It is preserved separately;
the default engine, enforcement mode, online service and released game pack are
not changed. Its integrity manifest remains unreviewed and audit mode stays on.
Wii/Dolphin runtime, actual online payload behavior, full released-core source
correspondence and asset rights/preferred editable sources remain open.
