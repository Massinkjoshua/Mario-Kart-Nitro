# Confirmed client build — 23 October 2026

Build ID: `nitro-ghost-reader-20261023`  
Code.pul SHA-256: `735b7d0e3d674de031325f240dd07eebe7fb2d5d820e7d9c8372eb492fe0e1c2`

The maintainer confirmed the Time Trials correction working in Dolphin and reported that everything worked in their testing. The exact wording and scope are recorded in [runtime-confirmation.json](../Validation/Confirmed-2026-10-23/runtime-confirmation.json). The original automated build report remains unchanged: the build process itself did not run Dolphin.

## Reproduce

Use Linux x86_64, make, Python 3, keystone-engine 0.9.2 and authorised CodeWarrior compiler/assembler executables and their required DLLs. Tool hashes are in [BUILD_RESULT.json](../Validation/Confirmed-2026-10-23/BUILD_RESULT.json). From `client/`:

```sh
python3 -m pip install keystone-engine==0.9.2
python3 scripts/fetch_linux_tools.py
python3 scripts/build_review_candidate.py --compiler tools/codewarrior/mwcceppc.exe --assembler tools/codewarrior/mwasmeppc.exe --linker tools/linux/Kamek --runner tools/linux/wibo --output /tmp/nitro-confirmed-20261023 --version nitro-ghost-reader-20261023 --jobs 4
sha256sum /tmp/nitro-confirmed-20261023/CandidateOverlay/MarioKartNitro_Test/Binaries/Code.pul
```

Choose a new output directory for each build. The recipe builds the engine from source and the released v15 loader from editable assembly; it does not require a precompiled game client as input. All 1,124 source inputs are recorded in the matching manifest.

## Corrections included

- Prevent CodeWarrior's strided Items-button loop from becoming an incorrect contiguous memory clear.
- Restore the working release's hidden character variants and Pauline model routing without changing selection table numbers.
- Preserve the 48-by-51 mini-turbo colour palette verified against the supplied working backup.
- Bound NAND ghost-folder scans by the returned count and allocation; handle empty listings and allocation failures.

The compiled Items-loop check passes. Twelve host tests exercise the actual ghost reader with controlled filesystem and allocation calls under AddressSanitizer and UndefinedBehaviorSanitizer. The original reader reproduces an out-of-bounds read in the empty-folder test. These checks complement the maintainer's Dolphin test; they do not establish testing on Wii, all regions, or the live online server. Runtime assets and older-release source mapping retain their separately documented status.
