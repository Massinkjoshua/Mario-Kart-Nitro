# MKNitro Pulsar + NitroIntegrity — 9 October 2026 checkpoint

A clean PowerPC build now succeeds. `Candidate/Code_AUDIT_CANDIDATE.pul` is a
source reconstruction candidate, **not a verified replacement for the working
pack**. The working Code(10) and XML in `Reference/` remain byte-for-byte unchanged.
No working installation, server or account was modified.

## Changes completed

- Reserved a 256 KB native MEM2 pool early at boot for failed online-request
  allocations, with bounded ownership tracking and frees to the owning heap.
- Restored preview allocation, update ordering, animation reuse, voting vehicle
  state and asynchronous kart archive selection from recovered repair evidence.
- Restored outbound VR/BR conversion, item-window handling, Options channel
  behavior, stopwatch BackModel and the Nitro roster constant.
- Retained the recovered profile-ID, rating persistence, Mii validation, settings
  fallback, separate save paths and online TT source fixes.
- Added persistent local denial after a reviewed PAL instruction mismatch.
  Restoring the instruction does not clear that process's denial; reboot resets it.
- Added audit baseline snapshots of readable instruction words for runtime review.

The reserved pool adds 256 KB of MEM2 use. The preview allocation change adds
256 KB to each native local all-kart heap. These need real game memory testing.
Existing pack assets and configuration remain required; this archive contains
no tracks, music or complete runtime UI archives.

## Anti-cheat status

**The candidate remains in audit mode.** `.env` defaults `MKNITRO_AC_MODE` to 0
and `ManifestRuntimeReviewed` remains false. It logs observations and allows
online entry. No accounts are banned and no telemetry is sent to a server.

There are 23 selected PAL instruction checks: two DOL checks and 21 deferred
REL checks. Race rechecks run every 60 callbacks; local item/physics diagnostics
run every 300 callbacks. Non-PAL games skip these PAL integrity checks.
With enforcement enabled after review, the existing local guard rejects online
entry and stops local online play on a validated mismatch. It cannot reliably
identify or ban a remote player. Permanent bans need trusted server-side
validation, account identification and a sanction path in the NitroWFC backend.
Local item/physics observations are diagnostics, not proof of cheating.

The selected addresses overlap neither the working Code(10) nor candidate
absolute patch writes. This alone does not approve the manifest: clean runtime
and downloaded payload behavior still need review. Do not accept unexplained
memory changes as a new legitimate baseline.

## Build and verification

On Linux x86_64 with Python 3.12+ and make:

```sh
python3 scripts/build_linux.py
```

The script downloads checksum-pinned official wibo 1.2.0 and Kamek
2026-02-24 Linux tools, then performs a clean audit build using the supplied
PowerPC compiler. Windows/MSYS2 tool paths remain in `.env` for `make`.
The script refuses `--enforce` while the manifest is unreviewed. Compiler mode
and project header changes trigger object rebuilds. Loader was not replaced.

```sh
bash NitroIntegrity/tests/run.sh
python3 Verification/check_integration.py
python3 Verification/test_http_reserve.py
python3 Verification/verify_candidate.py
```

Passed: parser and sanitized C++ policy/adapter tests; reviewed-enforcement
clean login, tamper stop and persistent denial; actual HTTP source with mocked
native APIs; Mii-row/settings integration checks; Kamek v2 structural and hook
checks; 124 rating and 72 item-window executions of the compiled PowerPC code
at two relocation bases with native calls stubbed.

`Verification/candidate-validation.json` records the candidate checksum and
limits. The candidate retains all working PAL absolute hook addresses except
an old allocation diagnostic wrapper at 0x8081ee34, and adds the preview heap
size write at 0x80542310. Address coverage does not prove equivalent hook
bodies, full asset parity or correct rendered behavior. USA/Japan were also
rebuilt but have not been runtime tested; Korea is not included.

**Not performed:** Dolphin/Wii play, real RFL rendering, online payload review,
settings migration on a console, complete pack parity, server integration,
server hash approval or deployment. Keep the working pack until these pass.

## What is needed next

1. Original matching PAL `main.dol` and `StaticR.rel`, to regenerate and review
   the final candidate's instruction baseline.
2. NitroWFC server source/export, with credentials and private keys removed,
   to implement trusted validation and account blocking/bans.
3. Clean Dolphin/Wii candidate test logs for previews, leaderboards, voting,
   menus, item HUD, settings and online entry using the current pack assets.

Recovery recipes and prior reports are evidence, not current deployment
instructions. `Recovery/REMAINING_WORK.md` describes the remaining release work.
