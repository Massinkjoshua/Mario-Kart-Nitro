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
