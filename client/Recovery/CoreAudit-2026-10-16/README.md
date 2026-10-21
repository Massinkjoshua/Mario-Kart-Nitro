# Mario Kart Nitro — client core source audit

16 October 2026. This is an additional audit, not a new game build or a statement
that the licence notice is resolved. No working pack, live service or release was
changed. This package contains no compiled game binaries or proprietary tools.

## Scope and result

The uploaded v5 source was built in isolated directories using the supplied
CodeWarrior 4.3 compiler, wibo 1.2.0 and Kamek 2.0. Its PAL output was compared
with v5's included Install/Binaries/Code.pul using the included Verification map.
Those map/binary associations are assumed from the supplied archive and recorded
by hash. This is NOT a direct comparison with the final latest-release Code.pul.

The older heuristic found v5 binary/map ranges close to the latest release, but
that alone did not prove the included v5 source generated those ranges. This
new audit tests the source-built side first. The default build remains the best
of the four tested settings, and none reproduces the v5 reference exactly.

| Default v5 build, PAL text symbols | Count |
| --- | ---: |
| Instruction bodies and resolvable targets match | 617 |
| Bodies match; referenced symbol sizes differ | 86 |
| Bodies match; at least one target cannot be resolved | 193 |
| Instruction bodies differ at equal size | 92 |
| Function sizes differ | 386 |
| Total compared source text symbols | 1374 |

The 86 cases refer to the same named symbols/offsets but fail the stricter size
check. They are not proved different behavior and are not counted as verified.
193 unresolved cases are not silently accepted. Each report includes all rows.
No percentage of the entire current mod is inferred from these counts.

## Compiler-setting checks

| Variant | Body and resolvable targets match |
| --- | ---: |
| Original default -opt all / -inline auto, no explicit processor override | 617 |
| Add -proc gekko | 422 |
| Add -ipa file | 609 |
| Add -opt space after -opt all | 360 |

These variants were hypotheses checked against evidence, not changes applied to
the public source recipe. Changing these flags alone did not close the gap.
Every variant used a separate build directory. The host-only Makefile adjustment
was python -> python3 for combine_bin.py. SECURE pointed at an absent directory,
as no external rr-secure source directory accompanied this v5 snapshot.
No assertion is made about unprovided external inputs of the original build.

## Comparison method

Only explicit Kamek relocation fields and unconditional branches leaving a
function are masked in instruction-body comparison. Local/conditional branch
displacements and instruction flags remain exact. Every masked target must then
resolve to the same named/sized symbol plus offset, the same offset within the
compared function, or the identical native game address. Data/BSS, the complete
installation command stream and game behavior are outside this audit.
A matching named callee does not prove that callee's implementation matches.

Fault checks confirmed that changing a native call target is rejected, and that
a changed conditional-branch displacement is retained as a difference.

## Reuse

Run with Python 3 and the binaries/maps you are authorised to inspect:

```sh
python3 compare_named.py --candidate /path/to/source-build/Code.pul \
  --candidate-map /path/to/source-build/Code.map \
  --reference /path/to/v5/Install/Binaries/Code.pul \
  --reference-map /path/to/v5/Verification/Code.map --output comparison.json
```

The parser is bundled in lib/nitro_formats.py. Input SHA-256 values are recorded
in each report; source-manifest.json fingerprints the original v5 source files.
The comparator requires a PAL section and does not overwrite either input.

## Next source work

Use unresolved-functions.csv as the queue. First establish the exact original
compiler/link command, tool versions and any source/preprocessor inputs omitted
from the v5 archive. Then review actual body/size differences against source,
without forcing output to agree by masking more fields. Only after establishing
that source-to-v5 relationship should verified correspondences be carried forward
to the latest release and the older public 1.0 binary.

Prior recovered client patches and loader verification retain their original
scope. Full client Corresponding Source, historical version coverage, asset
permissions and game/runtime tests remain open. Website publication can proceed
separately without deploying any of these audit builds.
