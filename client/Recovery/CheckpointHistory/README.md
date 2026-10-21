# MKNitro Pulsar + NitroIntegrity source checkpoint

Updated 11 October 2026. The merged project now compiles and links successfully
for PAL, USA and Japan with the supplied CodeWarrior compiler and Kamek 2.0.
This is a source checkpoint, **not an installable release**. The experimental
binary has not been run in Dolphin or on a console, and parity work remains.

## Current baseline

The newly uploaded Code.pul is byte-identical to Code(10).pul and the recovered
VR-profile-ID-fix binary. The two older builds provide source/toolchain inputs.
Current assets and configuration come from the user's Nitropack release; no
older pack assets are substituted here. The unchanged reference code SHA-256:

`0f5364590f8ec8164f06a934666bdbd9252b87edf7d31c79bf93e189f30c15bc`

## Source changes

- NitroIntegrity: 23 selected PAL instruction checks, local item/physics
  diagnostics, existing Pulsar lifecycle hooks, and the existing online-auth hook.
  Audit mode remains enabled; runtime approval remains false. No automatic bans.
- Recovered v9 character/vehicle loader source, pending skin refresh ownership,
  correct vehicle-field offset, preserved riding states, and voting pose updates
  before scene calculation. Missing Halloween kart archives use native fallbacks.
- Online request memory: persistent 256 KiB native MEM2 expanded heap reserved
  before BootHook dispatch; original allocator remains first choice; fallback
  allocations are tracked and freed through their owning heap. The pool uses
  16 tracking slots, 128 KiB allocation limit and native mutex support.
- Leaderboard: static 16 KiB receive buffer, stage diagnostics and Mii validation.
  The callback now copies into a bounded completion buffer and leaves parsing,
  entry ownership and Mii updates on the menu thread. Page re-entry waits for
  an outstanding callback instead of recycling its context or receive buffer.
- Latest PAL profile-ID limit, public VS rating persistence, native VR/BR display
  source ports, Online TT routing, Nitro settings-name migration and save paths.
- Current main-settings and player-coloured item-frame hook source ports.
- v9 stale-item-icon handling and recovered menu/Discord source changes.

Historical v5/v9.1/v9.2 native repairs were checked against the actual current
code. Thirteen hook sites were absent there, so those historical registrations
remain commented out instead of silently restoring superseded behaviour.

## What remains

The native-write comparison finds 1,193 current sites and 1,190 rebuilt sites.
Three current hooks are still missing: `0x8081ee34`, `0x8059e598` and
`0x808d3cdc`. The instruction at `0x807e2714` also differs. See
`Verification/native-hook-comparison.json`. Matching hook addresses would still
not prove matching internal code, menus, animations or online behaviour.

The 11 October crash screenshot is cropped. Its visible stack includes model
visibility/clipping and scene updates; the exception type, failing instruction
and fault address are missing. It does not establish a specific damaged model,
heap exhaustion or a faulty anti-cheat check. A full report and the preceding
game action are needed to diagnose that crash.

## Verification

- Actual PowerPC compile/link: PAL, USA, Japan. See `Verification/powerpc-build.log`.
- NitroIntegrity policy and adapter host tests: passed, including audit and
  enforcement-gate paths; original 23-site baseline overlap checks passed.
- Integration host tests: passed for auth ordering, profile-ID boundary,
  mocked Mii validation and settings-name migration.
- The real NHTTP pool source passed mocked-native allocator tests for failed
  initialization cleanup, one-time reserve, limits, slot exhaustion/reuse,
  allocation failure recovery and correct free ownership under ASan/UBSan.
  LeakSanitizer was disabled because this environment cannot inspect `/proc`.
- The compiled candidate's PAL patch table overlaps none of the 23 selected
  instruction checks. This does not test downloaded server payload changes.

No new loader, pack assets or server build registration was installed or changed.
The new asynchronous leaderboard flow and preview behaviour still require runtime
validation. PAL instructions must be reviewed with the real online payload before
any enforcement build. USA/Japan compile success does not establish runtime support.

## Rebuilding

The existing `.env` selects `MKNITRO_SERVER` and
`MKNITRO_AC_ENFORCE_INTEGRITY=0`. On Windows/MSYS2, use the supplied toolchain and
`make`; loader generation is separate. On Linux this build used the official
wibo x86_64 1.2.0 runner and Treeki/Kamek linux-x64 release 2026-02-24. Pass
absolute runner/linker paths as command-line Make variables:

```sh
make -j4 CC='/path/to/wibo ./toolchain/codewarrior/mwcceppc.exe' \
  AS='/path/to/wibo ./toolchain/codewarrior/mwasmeppc.exe' \
  KAMEK='/path/to/linux/Kamek'
bash NitroIntegrity/tests/run.sh
python3 Verification/check_integration.py
python3 Verification/check_nhttp_pool.py
```

`Reference/` preserves the user's input. `Experimental/` holds the compiled
inspection candidate and map. `Recovery/` holds provenance, historic recipes
and the diff from the recovered v5 source. Historical recipe READMEs describe
their own old builds; this root README defines the current checkpoint status.
