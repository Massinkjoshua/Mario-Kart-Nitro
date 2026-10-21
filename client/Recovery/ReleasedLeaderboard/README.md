# Released PAL leaderboard source recovery

This optional profile reconstructs the supplied release's request lifecycle,
numbered diagnostics, native request-creation error wrapper and Mii guard patches
as editable C++. It builds from source and source-built objects; the released
Code.pul is only an independent comparison input to the tests.

The active candidate retains its queued response processing and extra lifetime
checks. This profile preserves historical sequencing for correspondence work:
callback parsing and active-request bookkeeping after dispatch. It is a separate
recovery build, not a gameplay release or a recommendation to restore those
older lifetime limitations.

## Recovered implementation

- OnActivate/OnDeactivate and StartFetch/OnLeaderboardReceived, reserved aligned
  16 KiB request buffer, request generation and error states 3 through 15.
- The exact diagnostic strings, including allocator-specific creation failures
  and their cached text after a subsequent successful creation.
- Native work-state access through a region-remapped external symbol. The pool
  copy exposes two read-only failure getters for the reconstructed wrapper.
- RFL validation before native Mii loading, guarded pane binding, and visibility
  restoration/hiding when a row is reused. ApplyResults calls these wrappers.
- ApplyError uses the reconstructed error selector; OnUpdate dispatches numbered
  errors, handles the 45,000 ms boundary and maintains the row-sound schedule.

## Build and test

First build the ordinary client source with the authorised CodeWarrior/Kamek
toolchain. Then from client/:

```sh
python3 Recovery/ReleasedLeaderboard/build.py --compiler /path/to/mwcceppc.exe --runner /path/to/wibo --linker /path/to/Kamek
python3 tests/leaderboard_network_ppc.py
python3 tests/leaderboard_display_ppc.py
python3 tests/leaderboard_ui_ppc.py
python3 tests/leaderboard_update_ppc.py
```

Unicorn 2.1.4 is required by the tests. Omit --runner when Windows executables
run directly. The build replaces only the leaderboard and NHTTPPool objects in
this isolated profile. The default output is build/released-leaderboard; use
--output-dir NEW_FOLDER to retain an existing output, and pass that folder to
all tests with --profile-dir NEW_FOLDER. No install/deploy action runs.

Tests require the exact authorised latest reference at
CurrentPack/MarioKartNitro_Test/Binaries/Code.pul (omitted from the public source).
The verified source profile SHA-256 is
5ea566c7f141f923b21d80f07f14c99f8835b2dcdd1f3ac15c3e992f01539a26.

## Verification

1,828 new isolated PowerPC executions passed at bases 0x81000000 and 0x81200000:
1,328 diagnostic/creator/Mii-wrapper executions, 212 actual ApplyError/ApplyResults
executions, and 288 actual OnUpdate executions. The existing 252 request-flow
executions also pass with this expanded profile. See ../../docs/leaderboard-*-emulation.json
and ../../docs/leaderboard-source-progress-2026-10-18.md.

The display tests compare actual released and compiled C++ behavior, including
synthetic memory-allocator failures, failed-creation messages reaching ApplyError,
row page selection, fallback ranks, names/VR/footer text and valid/invalid Mii
reuse. Expectations are asserted independently as well as comparing traces.
The timeout checks cover just below, at and above 45,000 ms and one-time UI apply.

Native HTTP, RFL, layout, rendering and audio APIs remain controlled. The actual
UI methods and internal helpers execute; this is not real rendered gameplay.
Friend highlighting and controller navigation are not exercised. Canonical RFL
BOOL values 0/1 are tested. Allocator internals, own-Mii override internals,
asynchronous scheduling and the rest of the released core remain separate work.
This does not establish complete current/older client Corresponding Source.
