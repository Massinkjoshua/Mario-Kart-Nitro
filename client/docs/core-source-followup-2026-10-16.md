# Client core source follow-up — 16 October 2026

This update adds verification tools and records. It does not change the engine,
compiled game binaries, installed mod, online policy or server.

## v5 source/build correspondence

Recovery/CoreAudit-2026-10-16 compares a clean build of the uploaded v5 source
with v5's included binary/map. 617 PAL text functions matched both normalized
instructions and resolvable targets. 86 further bodies use the same named
references but their target sizes differ; 193 contain unresolved references;
92 have equal-size body differences; 386 differ in size. This is not a direct
comparison with the final latest release. See that audit's input hashes and limits.

Four full compiler-setting variants did not reproduce v5's bundled binary.
The later focused probe tests 13 settings against 22 named functions in the
single ExpGhostSelect translation unit. None explains the representative
80-byte vs 76-byte ghost challenge function. This does not rule out every build
configuration. No speculative compiler change was applied to the public recipe.

## Additional latest-release behavior comparison

The existing source-built candidate and the latest supplied release were tested
in Unicorn using tests/core_codegen_ppc.py. All 352 real PowerPC executions passed
at bases 0x81000000 and 0x81200000. Source-file hashes in the report match this
public source tree's three relevant C++ files.

Functions exercised:
- ExpGhostSelect::OnChallengeGhostPress
- ExpGhostSelect::OnWatchReplayPress
- Pulsar::PatchIsLocalCheck
- Dolphin::IsEmulator

Checks cover the native callback occurring before ghost-page/list reads,
selected entry indexing and EnableGhost arguments, ghost-viewer section boundary
values and native local-check forwarding, cached Dolphin state and simulated
open outcomes. The test deliberately changes page/list values inside the native
callback to check operation order. Expected results are asserted as well as
released/rebuilt equality.

Native APIs, EnableGhost and OpenDolphin are intercepted; their implementations
are outside these tests. Invalid-pointer/index fuzzing and full-game execution
were not performed. Passing four functions does not prove the rest of the core.
See core-codegen-emulation.json for exact binary/source hashes.

## Run locally with authorised reference inputs

With Unicorn 2.1.4 available to Python, and the existing source-built build/Code.pul
and build/Code.map, place the already-authorised latest reference under
CurrentPack/MarioKartNitro_Test/Binaries/Code.pul, then from client/ run:

```sh
python3 tests/core_codegen_ppc.py
```

The test hashes and checks the known reference before running. The public
source-only tree deliberately does not include that precompiled core input.
The source build and reference remain unchanged; the test writes its JSON report.
The full-client preferred-source, version-coverage, runtime and asset gaps remain.
