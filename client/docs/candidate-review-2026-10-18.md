# Candidate edge-case review — 18 October 2026

Reviewed candidate: `nitro-source-candidate-20261018`, Code.pul SHA-256 `71af89931375f4fc46782401e54c243bee8fc657b8fb44d4fe6f52e627ac3075`.

The developer reports successful Dolphin play. This review found edge cases that a normal play session and the earlier historical-equivalence tests did not cover. No candidate binary, server setting or launcher download was changed in this review. Findings are OPEN.

## Confirmed findings

### R1 — Empty/error leaderboard page prevents paging back (P2)

`PulsarEngine/UI/VRLeaderboard/VRLeaderboard.cpp:470–483,515` treats a successful response with zero entries as `Failed: JSON`, then returns before processing left/right input for every error state. Reaching an API page beyond the last player, or a failed page request, therefore leaves the screen unable to page back. The separate Back action can still leave the leaderboard; this is not a whole-game freeze.

Reproduction: the real compiled parser receives `{"players":[],"success":true}`; OnUpdate changes to FETCH_ERROR and calls ApplyError. A left input moves page 6 to page 5 in FETCH_READY but does nothing in FETCH_ERROR. Both behaviors reproduced at two allocation bases.

Proposed repair: distinguish a valid empty response from invalid JSON; use last-page information to limit forward navigation and retain a route back/retry after a failed fetch. Do not blindly convert all parse failures into success.

### R2 — In-game leaderboard has a hard 500-player ceiling (P2)

`PulsarEngine/UI/VRLeaderboard/VRLeaderboard.hpp:20–23` fixes 50 screens of 10 rows; `VRLeaderboard.cpp:545` blocks further navigation. The exported server supports additional 50-entry API pages. The compiled candidate ignores a right input on screen 50. Thus rank 501 and later cannot be reached, even if the server has them. This is a capacity issue, not a claim that there are currently more than 500 players.

Proposed repair: derive available pages from the server (or bounded next-page discovery) and widen the current `u8 curPage` before supporting more than 256 screens. Merely increasing kPageCount would leave another overflow limit.

### R3 — Higher-VR room filter uses the wrong display scale (P2)

`PulsarEngine/Network/Matchmaking.cpp:138` adds 4,000,000 to a rating already converted to displayed/QR2 units. The comment describes a 40,000-VR margin. `PlayerRating.cpp:148–160` and `RatingQR2.cpp:53–59` show that the displayed and advertised numbers already use that conversion; normal advertised VR is at most 1,000,000. Therefore the higher-room exclusion cannot activate for valid advertised ratings.

Reproduction: a player with internal rating 50 (displayed 5,000 VR), a 5,000-VR room and a 700,000-VR room retains BOTH rooms, with a cutoff of 4,005,000. For the documented 40,000 displayed-VR margin the cutoff should be 45,000. Nearest-room sorting still correctly places the 5,000-VR room first; the bug is the exclusion/fallback policy, not reversed ordinary sorting.

Proposed repair: express the margin in the same units as `ev`, then test the exact boundary and preserve the existing fallback when no nearby eligible room exists. An initially suspected arithmetic overflow was excluded from the findings after checking the valid internal-rating range.

## Conditional recovery risk

`VRLeaderboard.cpp:467,487–495,680–686`: after an old request remains in flight, reopening can enter FETCH_WAITING. That state has no local timeout or retry while the old callback remains pending. The compiled function stays WAITING through 120 updates without consulting the clock. Native NHTTP eventual completion was not established, so this is a conditional recovery gap, not a proven permanent live hang. A repair must preserve callback buffer ownership; simply clearing the in-flight flag can reintroduce reuse races.

## Additional source observations and limits

The exported website-facing `/api/nitro/leaderboard` handler defaults to 100 rows, permits a limit up to 200, and only calculates page offsets for the separate in-game route. This may explain the previously reported website ceiling, but the current website implementation/live server was not fetched or tested in this pass.

The loader computes the engine digest and the downloaded login payload supplies pack_id, pack_ver and pack_hash. The server can check those values. This review did not inspect the live allowlist or approve the candidate; a successful offline boot alone does not prove live hash acceptance.

The reproducer executes the candidate's real PAL OnUpdate/parser/matchmaking instructions at two bases with controlled native APIs. It includes positive navigation and sorting controls. It does not run Dolphin/Wii, native threading, rendering, database queries or real network sessions. Previous 11,176 passing scoped checks remain valid; those checks did not prove absence of these edge cases. No historical source-correspondence or asset-rights conclusion is changed.

## Reproduce

From client/, install the versions in tests/requirements-ppc.txt, then use the delivered candidate/map:

```sh
python3 tests/reproduce_candidate_issues_20261018.py --source-root . --candidate /path/to/Code.pul --map /path/to/Code.map --report /path/to/review-result.json
```

The test deliberately requires the exact reviewed hash. Its passing assertions confirm the documented existing problems; it is not a test that the bugs have been fixed. See reproduced-issues.json for observations.
