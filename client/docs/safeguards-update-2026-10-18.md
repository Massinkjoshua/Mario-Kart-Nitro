# Safeguards test update — 18 October 2026

Build `nitro-safeguards-20261018` adds three safeguards to the consolidated source candidate:

- Race packets: validate sender, total length, header size, section bounds, receive-buffer index and destination capacity before native processing. CRC is read only after the envelope is safe, and restored after checking. Bounded trailing padding remains accepted.
- Rating downloads: serialize requests with immutable in-flight context, queue the latest request, reject stale replies and changed profiles/ratings, and apply bounded responses on the frame thread. The callback does not write saves or generate reports. Invalid/missing numeric fields and oversized responses are rejected.
- Rating saves: reject non-finite or out-of-range VR/BR entries; safe clamping handles NaN. Invalid entries use the existing fallback until valid data is available. No real player save was modified during testing.

Code SHA-256: `3fb4e2e441a04eaffa9a39d7857feb289e25a75c0330e198f1819957561d3067`

Loader SHA-256: `ffa108e11f4c0b925f736bdb28681bf83e997b81de9fca9b2e2d6dd7ea6c9dbb` (unchanged).

## Validation

Clean source build completed for PAL, USA and Japan. Two engine builds produced identical Code.pul bytes; one complete engine-and-loader build was performed. The manifest records 1,124 compiled source inputs. Proprietary toolchain executables and precompiled historical cores are not included.

284 new controlled PAL PowerPC scenario executions passed at two relocation bases: malformed/valid packet envelopes, serialized and failed HTTP requests, stale replies, and invalid/valid save ratings. Existing focused regression suites passed 11,176 executions (460 + 10,244 + 352 + 120). Portable container parser checks passed for all three regions and malformed inputs under ASan/UBSan. These are controlled emulation tests with native calls mocked, not whole-game or live network tests.

The earlier 71af candidate was reported working in Dolphin. This new 3fb4 candidate has NOT been tested in Dolphin/Wii, approved by the server, deployed, or merged. Full runtime-pack testing remains incomplete because most runtime assets are unavailable here. No evidence ties these issues to the reported hacker crash; packet envelope validation cannot prevent every attack.

## Reproduce

Use `scripts/build_review_candidate.py` with the compiler, assembler, linker and runner documented in the existing build instructions, and explicitly pass `--version nitro-safeguards-20261018 --output /absolute/output`. See BUILD_RESULT.json for tool hashes and the compiled-source manifest for exact inputs.

With Unicorn and Capstone installed:

```sh
python3 tests/safeguards_regression_20261018.py --source-root . --candidate /absolute/output/CandidateOverlay/MarioKartNitro_Test/Binaries/Code.pul --map /absolute/output/Reports/Code.map --report /absolute/safeguards-regression.json
```

The existing regression scripts remain in tests/. Historical binary-comparison tests require a separately held reference core, which is not a build input or included in this handout.

## Remaining work

Leaderboard empty/error navigation, its 500-player ceiling, the 40,000-VR room filter scale, and missing callback timeout remain open. The exported server still lacks the rating-download endpoint and rating-report handler; a separate live service may implement them, but that has not been inspected. A request whose native callback never arrives safely retains ownership; no cancellation/timeout was added. Historical source correspondence and asset licensing questions are not resolved by this new candidate.

## Test-copy installation

Back up the working pack and player saves. Apply only CandidateOverlay's Code.pul and Loader.pul to a separate copy's matching Binaries directory. Keep your Config/ConfigRT, tracks, music, UI and other pack assets. Test boot, menus, license switching, offline races and ratings first. Controlled online tests require the appropriate server-side candidate approval; this task did not change that approval or the launcher. Do not roll this candidate out to everyone before runtime testing.
