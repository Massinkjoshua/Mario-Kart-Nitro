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
- Complete safe runtime inputs and a prominent public source offer for online
  users. Actual HTTP-served payload bytes/configuration were not independently
  fetched. No credentials, signing keys or live player/database data belong here.
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
