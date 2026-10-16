> Historical comparison against the initially supplied sources. Later October
> sources and original recipes were recovered during this session; see root
> SOURCE_STATUS.md and docs/recovery-provenance.json for the current result.
> Two incorrectly inferred hook labels below have been corrected.

# Mario Kart Nitro — first upload comparison

Prepared 16 October 2026 from the supplied files. This is a read-only technical
comparison of the current binaries and core assets, with evidence saved for the
remaining uploads. No release binary, configuration, asset or source was changed.

## Main finding

The current release is substantially newer than the compiled build in
`MKNITRO-Pulsar-Source (2).zip`. That source archive is useful, but it cannot yet
be presented as verified matching source for the current release. The newer
loader, PAL-specific patches, character preview changes and several appended
runtime patches must be accounted for before rebuilding.

The three supplied projects are preserved as separate baselines. None was
silently selected as the authoritative latest source.

## Material received and inspected

| Material | What was established |
| --- | --- |
| `MKNitro_RR_Build_Kit(1).zip` | Older build/integration kit; bundled 22-cup config; defaults to one catalogue. |
| `MKNITRO-Pulsar-Source-play.mknitro.com (1) (1)(2).zip` | Nitro domain/public-key configuration and a loader link-order fix; older runtime files in `CurrentPack`. |
| `MKNITRO-Pulsar-Source (2).zip` | Later Nitro UI and branding changes, diagnostics, object files, map and compiled engine/loader. |
| `Binaries(2).zip` | 59 actual files: seven `.pul` files and 52 core asset files. The ZIP also contains directory entries. |
| `Characters(1).zip` | Upload failed; no character archive bytes were available or used. |
| `Source.zip` | Upload failed. The user subsequently clarified that this was an AllKart/related asset archive, not a newer C++ source project. It is not a pending source-project upload. |

The latest upload includes 48 SZS/ARC archives with **11,739 internal file
entries**, counting language copies and the backup archive. Every one was
decompressed/listed without a parser error. BRSAR, THP and the nested backup ZIP
were inventoried, but their audio/video content was not play-tested.

## 1. Executable identity and structure

| Binary | Bytes | SHA-256 |
| --- | ---: | --- |
| Current `Code.pul` | 2,688,428 | `58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364` |
| Current `Code working.pul` | 2,688,428 | `2001277443489e01c45673430f50ccf4afbd17855fc62232f60cc93d612c9f52` |
| Current `Loader.pul` | 4,192 | `ffa108e11f4c0b925f736bdb28681bf83e997b81de9fca9b2e2d6dd7ea6c9dbb` |
| Source (2) `build/Code.pul` | 1,636,876 | `e159683d3562d5659fa3fedf371a22524747511f57ab6b85724dc65c2a23edde` |
| Source (2) `build/Loader.pul` | 2,988 | `81f6e886d0aa328bc9839ae16f5a72ae65f08249a725031a8e96db503a4a7634` |

All three projects' old `CurrentPack` engine binaries share the older
`19a108b8…` hash. They are not the current release engine.

### Active engine sections

The current combined file has PAL, NTSC-U and NTSC-J sections, all Kamek v2.
Its Korean section length is zero. This records the supplied binary's contents;
it is not a claim of tested support for any region.

| Region | Section bytes | Code/data bytes | Declared BSS | Patch/relocation records |
| --- | ---: | ---: | ---: | ---: |
| PAL | 915,092 | 821,652 | 0 | 11,078 |
| NTSC-U | 886,660 | 794,076 | 0 | 10,975 |
| NTSC-J | 886,660 | 794,076 | 0 | 10,975 |

Checks passed: container lengths, Kamek headers, constructor ranges, exact
command-stream consumption and relative patch/target allocation bounds. There
are 42 constructor-table entries per region. These are static structural checks,
not a boot or online compatibility test.

The source archive's compiled engine instead declares a 333,128-byte BSS and a
455,192-byte code/data span per region. File-size growth alone must therefore
not be interpreted as an equivalent increase in gameplay functionality.

### The 11-byte `Code working` difference

The active `Code.pul` and `Code working.pul` differ in exactly 11 bytes, in three
contiguous runs. Every difference is in PAL.

1. At file offset `0xC7A31`, six data bytes change from
   `FF 2D 23 9B 37 FF` to `F5 5A 41 F5 5A 41`. Interpreted as two RGB triples,
   these are `#FF2D23` / `#9B37FF` becoming `#F55A41` / `#F55A41`.
   The precise choice or UI element using these entries is not established.
2. At PAL address `0x800910B4`, the active patch stream uses a fixed `Write32`
   with instruction `0x480CCE99`; the working copy uses `BranchLink` to relative
   target `0x24338`. The fixed instruction calls `0x8015DF4C`, which the supplied
   symbols identify as `DVD::ConvertPathToEntryNum`. The archived source installs
   `ConvertPathToEntryNumWithLooseOverride` at this site instead. This is a
   functional difference in disc-path handling, not just branding.

Keep both copies as evidence. Do not assume the file called `working` is the
newest intended runtime or overwrite the active one based on its name.

## 2. Source gaps and details to preserve

| Area | Current evidence | Implication for the source update |
| --- | --- | --- |
| Loader | Contains `[NitroLoader v15]` and messages for truncated headers/commands/operands, invalid section/region bounds, missing regions and command-length mismatch. | The supplied loader source lacks this newer implementation. Recover or carefully implement it; do not replace it with the older 2,988-byte loader. |
| Save separation | Current strings use `/riivolution/save/NitroWF%s/...`; supplied `SDIO_RKSYS.cpp` uses `RetroWF%s`. | Preserve the Nitro path change and verify the matching Riivolution XML when supplied. |
| Settings file | Current engine contains `MKNitroGameSettings.pul`, while old `RRGameSettings.pul` strings also remain. | Preserve the Nitro settings handling. Presence alone does not prove which old path still executes. |
| Item frame | PAL contains `nitro_item_frame` and a new call at `0x807EEDE0`. | New item-frame behavior is absent from the supplied source. |
| Saved ratings (corrected label) | PAL branches at `0x80662D80` and `0x80662DC4` load saved VR and BR. | Original rating patch recipes and source ports were recovered during the later 16 October source repair. These are not speedometer hooks. |
| Drift patches | Six PAL fixed writes around `0x80588894–0x8058893C` differ from the old UMT source. NTSC-U/J retain the older values. | A rebuild from the old source would restore a different PAL patch set. Runtime behavior must be verified before choosing the intended implementation. |
| Character preview | New `[NitroPreview]` traces and course-model/animation traces are present. | Source for the later preview, allocation and animation changes is missing from the archives so far. |
| Character-name control | PAL/US/JP now contain a call at `0x8083D9DC`; Source (2) had disabled that hook. | Do not carry the old disabled-hook decision forward automatically. |
| Options activation / online exit (corrected label) | `0x805FD8E8` is Options activation. The separate `[NitroOnlineExit]` trace concerns player-count requests. | Options source and its original recipe are recovered; the online-exit implementation needs separate correspondence review. |
| Region handling | Current build contains `[NitroRegion v16]`. | Obtain the source for this later revision and check the intended region configuration. |
| Mii handling | All three regions write `0x3BC0001A` at the translated `0x807E2714` site instead of the supplied source's `0x3BC0001B`. | Record this small Mii-count patch difference for the rebuild. |
| Removed diagnostics | Old Lakitu diagnostic calls at `0x80722B6C` and `0x80722BDC` are absent. | Do not reintroduce old test hooks simply by copying the archived project. |
| Single-player menu | Five old menu/background hook sites are absent, including `0x8084F084`, `0x808B9BA0`, `0x808D9F30`, `0x808D9F34`, `0x808D9F4C`. | The old no-battle/background code is not an exact representation of the current hook set. Some behavior may now be implemented elsewhere or in assets. |

The PAL source-map comparison found 1,203 combined absolute patch sites:
14 current-only sites, seven archived-only sites, 378 identical raw command
sequences, 105 matching old symbol ranges by exact target bytes, and 699 other
changed/relocated sites. Relinking changes offsets, so **699 does not mean 699
feature changes**. The complete site-by-site CSV is included.

Exact raw-byte searches located 439 unique old mapped ranges of at least 24
bytes in the current PAL text. Seventy-eight were ambiguous and 727 were not
found exactly. Relocations, compilation changes and changed implementations can
all affect these results; this is supporting evidence, not proof of complete
source correspondence or semantic equivalence.

## 3. Networking

The Nitro public payload key in Source (2), a 516-byte structure, occurs exactly
in all three current region text spans. Its SHA-256 is
`4bc449731f3900297ff90a5b07c5bd9ee3727b0683df3922be00e931e49d9256`.
This verifies that one particular source data structure matches the runtime;
it does not verify the whole networking implementation.

Current strings also include these expected endpoints:

- `play.mknitro.com`
- `http://play.mknitro.com/api/badges/all`
- `http://play.mknitro.com/api/leaderboard/in-game?page=%u`
- `http://play.mknitro.com/api/game/multiplier.txt`
- `http://nas.%s/api/mkw_rr_ratings?pid=%ld`

No requests to the game server were made. Endpoint availability, rankings, VR
exchange and authentication were not tested. The NitroWFC server source is
still a separate missing input.

## 4. Configurations and track catalogue

Both main configs exactly match the newer configs supplied earlier:

| File | SHA-256 |
| --- | --- |
| `config.pul` | `46698cf9b913e9c9ebe78d95bc7357403fe15652883ac52ad28058114986f9be` |
| `ConfigRT.pul` | `b96998924356484d0e233bc1b0da4a50b42a126826457bfb98850c9ce83f4669` |

They contain 27 cups, 108 visible tracks, 112 stored track records including
padding and zero extra variants. Correction from the source-project checks: the 108 visible alphabetical indices form a permutation, but the four stored padding indices repeat 0–3 instead of 108–111. The original uploaded files are preserved; working project copies correct only those four padding entries.
They share the same visible track names and INFO settings, but **three track
records differ**. These differences must be checked against the actual track
files and intended music before synchronizing the configs.

- Main probability fields: `0 / 95`, leaving five percentage points for the
  remaining mode. This is the known 0% 100/200cc, 95% 150cc, 5% mirror setup;
  game-mode/host overrides remain a separate matter.
- Raw `has200cc`, UMT, feather and mega-thundercloud feature flags are false.
- Cup-icon count is 27; choose-next timer is 10.
- `ConfigCT.pul` and `ConfigBT.pul` are byte-identical valid 272-byte empty
  catalogues. Their stored default probability fields do not establish the
  active worldwide odds.

### Main-config differences

| Index | Track | `config.pul` | `ConfigRT.pul` |
| ---: | --- | --- | --- |
| 32 | N64 Bowser Castle | Music slot 8 | Music slot 12 |
| 59 | Wii U Thwomp Ruins | Course slot 2; CRC `50468f87` | Course slot 8; CRC `b80d59cd` |
| 90 | N64 Rainbow Road | Course slot 13; CRC `f7aea989` | Course slot 8; CRC `7b0c2394` |

Only one BMG message record differs semantically: track 59, **Wii U Thwomp
Ruins**, message `0x2003B`. `config.pul` contains a trailing color-reset control
`001a080000010000`; `ConfigRT.pul` does not. The decoded names are identical.
There are 8,965 differing file-byte positions because BMG string storage offsets
shift, in addition to the three track-record differences; this is not evidence
of thousands of separate settings changes.

### Selected latest tracks

The complete 108-track CSV is included. Important checkpoints are:

| Index | Name | Course/music slots | Config CRC |
| ---: | --- | --- | --- |
| 15 | Daisy Palace | 8 / 8 | `6129f203` |
| 19 | Windy Whirl | 18 / 8 | `d919ec64` |
| 22 | Liquid Complex | 11 / 8 | `465b3aae` |
| 30 | N64 Jungle Parkway | 8 / 8 | `5a709a58` |
| 32 | N64 Bowser Castle | 28 / 8 | `98f6d689` |
| 46 | Treetops | 8 / 8 | `35c8a1e1` |
| 51 | Kongrove Point | 8 / 8 | `9bb6aa7d` |
| 70 | Land of the Livid Dead | 8 / 8 | `171b3ef2` |
| 75 | Garnok's Fury | 8 / 8 | `39d40dde` |
| 98 | Koopa Cape | 15 / 15 | `92e96705` |
| 102 | Red Rooms | 8 / 8 | `3c16bb2a` |
| 105 | GP Monaco | 8 / 8 | `ca536b03` |

Track SZS files and BRSTMs have not arrived in this stage, so physical track
identity, computed track CRCs, slot/music overrides and audio loops are pending.

## 5. Core assets, including small differences

Compared against Source (2)'s `CurrentPack`:

| Archive | Added entries | Removed entries | Changed entries | Unchanged entries |
| --- | ---: | ---: | ---: | ---: |
| `CommonAssets.szs` | 4 | 0 | 2 | 3 |
| `RaceAssets.szs` | 13 | 1 | 41 | 82 |
| `UIAssets.szs` | 223 | 0 | 33 | 341 |

The kit has the same baseline versions of these three archives. Every changed
internal file is listed separately in the CSVs with old/new hashes and sizes.

### Changes identified

- Common assets add `ItemSlotRR.bin` and three Lakitu lap model resources;
  Pulsar effect files differ.
- Race assets change input-viewer layouts, controller textures, feather/TC
  textures, number/speed/lap textures and several controls. They add Common/Race
  messages and team/score resources. `game_image/blyt/item_vindow.brlyt` is absent
  relative to the old baseline; a missing resource in this archive alone is not
  proof of an in-game fault because archive precedence is not yet known.
- UI assets add Nitro settings/rank controls, item resources, portraits,
  messages, rank-related resources and other layouts. The first 27 cup-icon
  textures differ from the old baseline. More unused icon entries remain; the
  config count controls the current intended cup-icon count.
- Knuckles (`0x76A06`) and Tails (`0x116A05`) have the expected names and
  `01000000` message attributes in Common and Menu BMGs of the default UI
  archive and all 12 supplied language copies.
- The current Common BMG supplies the visible `NITRO VS` and `Rankings` labels.
  Absence of an old hard-coded string in the executable therefore does not by
  itself mean the label was lost.

### Language files are not identical to the default assets

All 12 language-specific UI archives are byte-identical to one another, but
they differ from the default `UIAssets.szs` in **11 resources**. All 12
language-specific Race archives are likewise identical within their family,
but differ from default `RaceAssets.szs` in **20 resources**.

Differences include the rankings layout/control, several menu controls, item
box texture, settings/rank icons, input-viewer resources and speedometer
controls. The English and other-language setups therefore must not be merged
blindly.

Two Common BMG message values differ between default UI and the language copies:

| Message ID | Default UI | Language copies |
| --- | --- | --- |
| `0x2179` | `Room Kick` | Empty |
| `0x156A01` | `Dry Bowser (Dark)` | `Pauline` |

These are verified inconsistencies to review with the character files. No
automatic correction was made because the intended character table and current
asset-loading behavior still need verification.

### Backups and other files

- `UIAssets backup.szs` contains the same 597 entry names as current UI assets,
  but 42 entry contents differ. It is not an equivalent replacement.
- `UIAssets_F.zip` is a nested archive with 31 entries, including further copies
  of core assets. Its role and whether any updater distributes it are pending.
- Twelve Strap language archives are byte-identical to each other.
- Current sound archive: `Assets/Sound/revo_kart.brsar`, 106,510,368 bytes.
- Current title movie: `Assets/Thp/Title/top_menu.thp`, 30,759,856 bytes.
- Current transmission movie: `Assets/Thp/Button/transmissionType.thp`,
  4,879,184 bytes.

Those files have individual hashes in the inventory. Audio/video behavior and
full scene appearance have not been inferred from their hashes.

## 6. What remains to finish the full-pack comparison

1. Any remaining character assets not already supplied in the later variant/kart uploads. The user clarified that the failed `Source.zip` was an asset archive; a retry is not a source-project prerequisite.
2. Remaining track files and BRSTMs, including any override folders.
3. Riivolution XML received subsequently in `MKNitroFont.zip`; see `FONT_XML_REPORT.md` for the resulting path and option audit.
4. Remaining menu/race/common assets, settings, ghosts and other pack folders.
5. Any source patches or scripts used after the September source build,
   especially loader v15, region v16, preview fixes and PAL HUD patches.
6. NitroWFC source and release history for the separate server/source review.

Preserve all incoming files and current runtime hashes while this continues.
Do not replace the user's working engine with an older rebuild just to align
its file name with a source archive. The intended result is a verified source
update that retains the small current fixes.

## Evidence and reproduction

- `results/inventory.csv`: every received runtime file, byte size and hash.
- `results/configs/`: decoded configuration/BMG data and track tables.
- `results/binaries/`: every decoded active Kamek command and region header.
- `results/pal_absolute_patch_comparison.csv`: old/current patch-site comparison.
- `results/source_hook_registry.json`: old source paths and hook statements.
- `results/regional_patch_checks.json`: PAL versus translated US/JP patch checks.
- `results/code_working_byte_differences.json`: all 11 exact byte changes.
- `results/asset_differences/`: internal-file comparisons.
- `results/locale_and_backup_differences.json`: default/locale/backup differences.
- `results/network_public_key_comparison.json`: public-key match evidence.
- `results/*_source_manifest.csv`: source baseline fingerprints.
- `inspect_release.py` and `compare_release.py`: read-only parsing tools.

The package contains inspection results and tools, not a replacement mod or a
new source release. Source correspondence, full build reproducibility, gameplay,
online behavior and licence compliance are not certified by this first stage.
