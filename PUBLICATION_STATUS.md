## Server candidate and uploaded core review — 21 October 2026

`server/Server-Fixes-2026-10-21` adds website API paging and client rating-sync handlers. Go tests, focused race checks and Linux amd64 build passed. PostgreSQL/live integration and current website edits remain pending; nothing was deployed. See `server/Server-Fixes-2026-10-21/SERVER-UPDATE.md`.

The newly uploaded Code.pul matches the historical 58de core, not the latest 2507 candidate. See `client/docs/uploaded-code-review-2026-10-21.md`; the active game file should be verified before assigning runtime test results.

## New paging and matchmaking candidate (18 October 2026)

The new 2507 candidate fixes the in-game leaderboard ceiling/navigation, adds a safe waiting-screen timeout, and corrects the VR room-filter scale. 142 new scenarios, 284 safeguard scenarios and 11,176 existing regression executions passed. Runtime testing remains pending. [Details](client/docs/paging-update-2026-10-18.md). Earlier records below describe previous candidates.

## New safeguards candidate (18 October 2026)

Packet envelope checks, serialized frame-applied rating downloads, and invalid-save rejection are implemented in the new 3fb4 candidate. 284 focused checks and 11,176 existing regression executions passed. Runtime testing and deployment remain pending. [Details and remaining work](client/docs/safeguards-update-2026-10-18.md). Earlier candidate records below remain historical.

# Source publication status — 16 October 2026

This branch publishes the recovered editable source for team review. It does
not establish that the GPL/AGPL notice is resolved. Existing release assets and
the running NitroWFC service are not changed by this pull request.

## Included and verified locally

- Editable client/loader source and PAL/USA/Japan build scripts; C#/XAML editor
  source; original licences and acknowledgements; source reconstruction history.
- Named PAL region, online-exit, course-preview and skin-effect source ports.
- Clean engine and C++ loader builds, and a WPF Release compile using the full
  private resource inputs. WPF GUI and full game runtime were not tested.
- 10,704 isolated PowerPC comparisons with controlled native game APIs; shared
  parser/cup checks and MEM2 pool checks; all-region native installation checks.
- Released Loader v15 independently reconstructs all 4,192 bytes from assembly
  and typed data, without a precompiled loader input. Original C++ was not found.
- Two recovered NitroWFC source snapshots; repaired candidate builds and passes
  race tests. Its public /api/source route needs the actual deployed source URL.

- Operator-exported live NitroWFC source (134 files) and running executable hash;
  manifest verified, source compiles and race tests pass with inherited vet
  warnings disabled. An operator rebuild on the original host exactly matched
  the running executable. See server/docs/live-export-2026-10-16.md for evidence
  and the distinction between the export and the on-host rebuild.
- Matching patcher source, public verification key, upstream notices and pinned
  Docker build instructions. Operator rebuilds from the exported archive exactly
  matched stage1 and all four RMC payloads; see patcher/VERIFICATION.json.

- Supplemental live inputs: game_list.tsv and both Lua translation scripts
  exactly match upstream; the separately stored multiplier is 2x. Absent optional
  inputs and the generator's unrecovered historical sheet are documented.

## Still unverified

- Full preferred-source correspondence for the latest client core and the older
  public 1.0 Code.pul. The final-PAL engine recipe still needs a precompiled core.
- Completeness of safe runtime inputs. Actual HTTP-served payload bytes and
  configuration were not independently fetched. No credentials, signing keys
  or live player/database data belong here.
- Full Wii/Dolphin and online runtime testing; complete historical release mapping;
  asset redistribution permission and preferred editable asset sources.

## Scope of this source-only tree

Runtime pack assets, editor binary resources, precompiled client references and
proprietary compiler tools are omitted. Names/hashes of omitted client build
resources are in publication/omitted-client-inputs.json. This tree's engine build
requires an authorised CodeWarrior toolchain; editor/integration/reproduction
checks that need omitted inputs cannot run from this tree alone. This omission
is explicit and is not being represented as a complete source offer.

Existing handoff build/test records describe the full local recovery snapshot
and its supplied inputs. Those records retain their original scope. Current
publication and GitHub access status are recorded here instead of rewriting
historic evidence. The branch is intended to remain a draft while the remaining
source, deployment, runtime and asset checks are completed.

## Additional client audit and checks

The v5 source audit and compiler probes are recorded in
client/Recovery/CoreAudit-2026-10-16/. None reproduces that historical binary
in full; this comparison is separate from the latest-release function checks.

A further 352 isolated latest-release/source-built PowerPC executions passed
across ghost challenge/replay selection, the ghost-viewer local-player check
and cached Dolphin detection. Exact hashes and scope are in
client/docs/core-codegen-emulation.json and core-source-followup-2026-10-16.md.
No engine code or gameplay binaries were changed for these checks.

The active publication destination remains Massinkjoshua/Mario-Kart-Nitro-Releases
by the operator's instruction. A nitroforge/Nitropack upload was attempted but
rejected by the GitHub integration (403); nothing was published there.
The Source & credits section is now visible on https://mknitro.com/ with
WiiLink attribution and links to this branch's server, patcher, client and status.
A fresh public HTTP fetch confirmed those links after the operator deployed it.
This verifies visibility, not completeness of the linked source offer.

## Leaderboard parser verification

A further 120 isolated released/source-built PowerPC parser executions passed
across 30 synthetic fixtures at two bases. Original v5 leaderboard/JSON source
files are preserved separately from the repaired candidate. See
client/docs/leaderboard-parser-followup-2026-10-16.md for exact scope and the
network-lifecycle differences that remain unverified. No game binary changed.

## Original project restoration and released request-flow recovery

Recovery/V5SourceSnapshot now restores the complete supplied v5 Source directory:
1,097 files, all paths and bytes verified against the original. 42 differing or
missing files are stored alongside a manifest referencing 1,055 identical files
already published here. This fixes the original-source omission; it does not
certify a whole binary match (see the existing v5 audit).

Recovery/ReleasedLeaderboard contains readable source for the observed latest
PAL request-flow changes and an isolated build script using source-built objects.
252 PowerPC executions across 63 distinct cases passed for OnActivate,
OnDeactivate, StartFetch and OnLeaderboardReceived. See
client/docs/leaderboard-network-emulation.json and the recovery README for
controlled-call boundaries, historical behavior and remaining integration gaps.
The full latest core source correspondence and older release coverage remain open.

## Verified 9 October source checkpoint — 18 October follow-up

The newly supplied Updated checkpoint is now preserved under
client/Recovery/IntegrityCheckpoint-2026-10-09/. Its 1,136 selected original
source/test files restore a complete source build of the included experimental
AUDIT CANDIDATE. An explicit 187-object order reproduces all three regional
modules and the linker map byte-for-byte without a precompiled core input.
The verified code hash is 8155c33e2798ed75c45c35161c93e98156869f873d84cda7aab351ea6f76a9d4.
Compiler/toolchain binaries, compiled references and unrelated historical audit
records are omitted and listed. Original licences and notices are retained.

This candidate differs from Code(10), which the upload stores as a reference,
and from the latest released Code.pul. It predates the 11 October changes in the
active candidate, so its reproducibility does not close the released-core gap.
No default engine code, enforcement mode, server or released game pack changed.


## Released leaderboard diagnostics and display source — 18 October

The optional client/Recovery/ReleasedLeaderboard C++ profile now implements the
released creator/allocation diagnostics and Mii guard patches and connects them
to the real UI methods. A further 1,828 isolated PPC executions passed for the
new wrapper, UI and update checks; the earlier 252 request-flow executions also
pass. Details and boundaries are in client/docs/leaderboard-source-progress-2026-10-18.md.
This recovers another released-core source section. It does not establish the
whole released core, actual Wii/Dolphin/online behavior or asset-source completeness.
The default queued-callback candidate and existing game/server releases are unchanged.



## Consolidated review candidate — 18 October 2026

A new source-built candidate (`nitro-source-candidate-20261018`) now has an isolated build recipe and matching 1,124-file source manifest. Three builds are byte-identical; 11,176 isolated PowerPC executions and the documented host checks passed. See client/Validation/ReviewCandidate-2026-10-18/README.md for hashes, scope, rebuilding and team testing.

This candidate is not deployed or server-approved. Dolphin/Wii and controlled online testing remain pending; the complete runtime manifest test is blocked by 2,777 omitted pack assets. Complete matching source for older distributed engines and asset-rights review remain unresolved. This publication does not establish that the licence notice is cured.
