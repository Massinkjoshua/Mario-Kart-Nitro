# Leaderboard and matchmaking test update — 18 October 2026

Build `nitro-paging-20261018` includes the prior packet/rating safeguards and fixes:

- Removes the game's fixed 500-player ceiling. Page index is now 32-bit. Each request still fetches only 50 players; the next batch is discovered when the current one is full. A partial batch disables forward paging at its final player. The API's existing maximum of 1,000,000 batches (50 million entries) remains enforced; this is not an unbounded request or allocation.
- Allows left/back paging and right/retry from failed requests, recognizes a complete successful empty-results envelope, and invalidates cleared cache metadata before a fresh fetch. Error retries stay on the same page. Exact full batches may require one empty next-page probe to discover the end; the player can page back normally.
- Gives FETCH_WAITING the same 45-second local timeout as REQUESTING. An outstanding native request retains ownership of its buffers. If it never completes, further fetches still wait safely; no unsafe cancellation/reuse is introduced. The screen can show an error and the user can leave.
- Uses a 40,000 displayed-VR margin instead of 4,000,000 for worldwide race room filtering. Boundary equality is accepted. High-rated rooms remain available when no otherwise eligible nearby room exists. Full-room, infinite-matchmaking and battle behavior retain their existing policies.

The page footer now displays the current page and a right arrow only when more results may be available. It does not invent a total that the API does not provide.

## Candidate identity and checks

Code SHA-256: `25071c02e4a24e99432627165c87d5be212491f931c0d68e36b9e71d11b54dba`

Loader SHA-256: `ffa108e11f4c0b925f736bdb28681bf83e997b81de9fca9b2e2d6dd7ea6c9dbb` (unchanged).

Clean source build passed for PAL, USA and Japan. The 1,124-input source manifest and tool hashes are included. 142 new controlled PAL PowerPC scenario executions passed at two bases, covering error/back/retry, empty/invalid results, partial/full batches, page 50 and the old 8-bit boundary, API-bound URLs, waiting timeouts, cache invalidation, VR cutoff equality, high-room fallback, battle and infinite-matchmaking controls. All 284 prior safeguard scenarios and 11,176 existing regression executions passed on this new binary. Portable container checks also passed under ASan/UBSan for all three regions and malformed inputs.

These checks execute compiled functions with controlled native APIs. They do not replace Dolphin/Wii gameplay, rendering, native-thread, database or live server tests. The user reported that the preceding 3fb4 safeguards build worked; their exact test coverage was not specified. This new 2507 build has not yet been runtime-tested or deployed. No launcher, website, live server, or server hash approval was changed.

## Reproduce

From client/, run scripts/build_review_candidate.py with the tool paths in the existing build documentation, explicitly passing `--version nitro-paging-20261018 --output /absolute/output`. See BUILD_RESULT.json for tool versions/hashes. With the tests/requirements-ppc.txt dependencies installed:

```sh
python3 tests/paging_regression_20261018.py --source-root . --candidate /absolute/output/CandidateOverlay/MarioKartNitro_Test/Binaries/Code.pul --map /absolute/output/Reports/Code.map --report /absolute/paging-regression.json
python3 tests/safeguards_regression_20261018.py --source-root . --candidate /absolute/output/CandidateOverlay/MarioKartNitro_Test/Binaries/Code.pul --map /absolute/output/Reports/Code.map --report /absolute/safeguards-regression.json
```

The new paging test is pinned to this candidate hash and verified private-data offsets. Historical comparison suites need the separately held reference core; it is not included and is not a build input.

## Install and test

Back up the working pack and player saves. Copy only CandidateOverlay's Code.pul and Loader.pul into the matching Binaries directory of a separate test copy. Keep Config/ConfigRT, tracks, music, UI and other runtime assets. SourceSnapshot is the complete published project; BuildSource contains exactly the manifest-listed build inputs. Neither is an install overlay.

Test boot, ordinary offline racing, leaderboard next/previous pages, the final available page, leaving/reopening the leaderboard, and a failed-request retry. Test ranks above 500 when the server has enough records. Test controlled online matchmaking only with the appropriate candidate approval. Do not publish the new build through the launcher before runtime testing.

## Remaining scope

This is the in-game leaderboard fix; the website's separate 100-row paging issue is not changed here. The exported server's missing rating-download endpoint/report handler remains unresolved. Full runtime-pack validation, historical source correspondence and asset licensing questions remain open. This update does not establish the cause of any hacker-related crash or guarantee immunity from malicious traffic.
