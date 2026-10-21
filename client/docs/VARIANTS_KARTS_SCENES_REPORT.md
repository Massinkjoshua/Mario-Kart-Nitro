# Mario Kart Nitro — variants, race karts and scenes

Comparison checkpoint, 16 October 2026. Continues the first binary/core-asset
report. The received mod files remain unchanged.

## Uploads checked

| Upload | Files | Uncompressed bytes | Contents |
| --- | ---: | ---: | --- |
| `VariantSound.zip` | 1,171 | 225,788,149 | Variant sounds plus three additional model/icon folders. |
| `RaceKart.zip` | 1,606 | 326,737,744 | 1,601 RaceKart files and five BaseAllKart files. |
| `Scene(5).zip` | 43 | 65,997,181 | Scenes, MenuRace, an alternative Earth, My Stuff and Race resources. |

Together with `Binaries(2).zip`, the working audit now has **2,879 pack files**.
The three new uploads add 2,820 files. ZIP directory entries are not counted as
files. The uploads called `Characters(1).zip` and `Source.zip` did not arrive.
The user subsequently clarified that `Source.zip` was an AllKart/related asset
archive, not a newer C++ source project. Its retry is not a source prerequisite.

**Later checkpoint:** `MKNitroFont.zip` supplied the active XML and font archive.
See `FONT_XML_REPORT.md` for route resolutions and the current input status;
the sections below retain the findings made before that XML arrived.

## Main findings to preserve or review

1. Eight same-name variant assets differ between physical folders. The dedicated
   driver/kart folders contain newer or alternative versions; the XML is needed
   to establish which copy wins.
2. One voice file does not contain the required RWSD header. Under the supplied
   source's loader, that file would be rejected as a loose voice replacement.
3. A `.silent` marker coexists with a full custom voice set. The source's rule
   makes the voice files take precedence; deleting either would change behavior.
4. Six received driver variants have no nonblank custom-name entry in the BMGs
   inspected so far and have fewer ordinary race vehicle files than most skins.
5. Three different `Race.szs` files and alternative menu/background resources
   must be kept distinct until Riivolution mapping is available.
6. The small license Mii/layout edits were identified at pane level, along with
   hundreds of other transform, size, flag and color differences.

These are review findings, not a list of confirmed in-game crashes. Some may be
intentional overrides, restricted vehicle variants or resources superseded by
other files not yet supplied.

## 1. What is actually inside VariantSound.zip

| Physical folder | Files |
| --- | ---: |
| `VariantSound` | 906 |
| `VariantDriver` | 105 |
| `VariantMap` | 50 |
| `VariantAllKart` | 110 |

The folder name therefore understates this upload. It includes 99 numbered
driver-skin stems and six Mii model files in the dedicated driver folder, plus
minimap icons and menu kart archives. The failed Characters upload is not
needed to establish that these particular character files arrived, but may
contain additional material.

The full upload contains:

- 457 BRWSD files and 72 BRBNK files, including character-alias suffixes.
- 196 BRRES files, including copies in different folders.
- 92 TPL files, also including duplicates.
- 340 SZS archives, representing 256 distinct compressed payloads.
- 14 zero-byte `.silent` marker files.

All 340 SZS archives decompressed and had valid U8 member bounds; they contain
2,874 internal file entries counting copies. All 196 BRRES files had the expected
`bres` header and a declared length matching their supplied bytes. TPL dimensions
and formats are recorded in `variant_results/model_texture_headers.json`.
These checks do not validate every model bone, animation or rendered appearance.

## 2. Sound checks

### Invalid RWSD header

`VariantSound/GRP_VO_DS-3_CAN_PC.brwsd` is **89,248 bytes**, but its first 576
bytes are zero and it contains no RWSD header. It is not a valid header-bearing
RWSD replacement as expected by the supplied loader.

The source function `ReadLooseVoiceLayout` in
`PulsarEngine/Sound/LooseBRSAROverrides.cpp` first checks the four-byte magic and
returns false when it does not match. Merely finding a nonempty file is therefore
not enough to establish that this cannon voice will load.

The remaining 528 sound files passed the implemented header byte-order,
declared-size and block/embedded-wave bounds checks. This is not an audio
playback, loudness, sample-quality or BRSTM-loop assessment. The bad file was
preserved, not repaired with invented sound data.

### Silent markers are meaningful files

`wr-3.silent` is present alongside 15 `wr-3` voice/bank files, with a `mario`
voice alias and all 13 expected voice-group suffixes represented. The supplied
Common BMG calls this skin **King Bob-omb**.

The source only applies a silent marker when no loose voice files were found.
Consequently, the marker alone does not silence this skin under that source
logic. This may be intentional; do not delete or rename it during cleanup
without deciding the intended behavior.

Other marker stems are `pc-1`, `bk-1`, `bmr-3`, `bmr-6`, `bmr-5`, `ko-3`,
`ds-5`, `rs-1`, `ka-4`, `blg-4`, `dk-3`, `mr-1` and `ko-1`.

### Aliases and numerical overrides must survive

Files ending in `.brwsd.mario`, `.brbnk.wario`, `.baby_peach`, `.toad`, `.luigi`,
`.waluigi`, `.bowser_jr`, `.donkey_kong` and `.baby_mario` are not generic junk
extensions. The source constructs alias-bearing paths to borrow a base voice
character's groups. Their exact filenames and suffixes are retained in the
inventory; runtime lookup and case handling still require the actual mapping.

`688.jr-3.brbnk` and `688.mr-5.brbnk` are numbered sound-effect overrides and
must not be flattened into the ordinary `GRP_VO_...` naming scheme. The provided
source routes character-tagged numerical overrides through its custom sound
effect logic rather than ordinary global overrides.

### Tails and Knuckles

- `ca-5` has the Tails name in the received default/locale BMGs and 15 per-variant
  sound/bank files in this upload.
- `lg-6` has the Knuckles name in the received default/locale BMGs. No `lg-6`
  loose voice group was found in this upload. That alone does not identify what
  it sounds like in-game: the main BRSAR or later material can affect base audio.

The source's custom-name IDs and exact registry are included for later matching.

## 3. Conflicting copies of character assets

There are 218 same-name overlap groups within the four variant folders. Of
these, 210 have identical file bytes and **eight differ**:

| Filename | Dedicated folder bytes | VariantSound copy bytes |
| --- | ---: | ---: |
| `bk-1.brres` | 211,200 | 76,800 |
| `bk-1-allkart.szs` | 518,496 | 504,224 |
| `fk-1-allkart.szs` | 517,251 | 662,087 |
| `fk-2-allkart.szs` | 520,647 | 666,456 |
| `fk-3-allkart.szs` | 529,185 | 526,608 |
| `fk-4-allkart.szs` | 521,123 | 664,752 |
| `fk-5-allkart.szs` | 510,979 | 580,840 |
| `fk-6-allkart.szs` | 524,367 | 668,089 |

These SZS differences are substantive contents, not only compression changes.
The two `bk-1-allkart` archives share their 13 member names but all 13 member
hashes differ. For each of the six Funky skin allkart pairs, 12 members differ
and one is unchanged. The complete member lists and hashes are saved.

The `bk-1` Common BMG name is **King Boo (Dark Moon)**. Keeping the wrong copy
could discard newer model work even though the archive name looks correct.
Which physical path is active is not known until the XML arrives.

## 4. Race kart coverage and variant names

All 1,606 files in `RaceKart.zip` are SZS files. All were included in the
decompression/U8 checks. The five BaseAllKart files were kept separate from
RaceKart rather than moved into it.

Every one of the 99 numbered dedicated driver-skin stems has at least one
matching race-variant filename. Six additional race stems are the small/medium/
large male/female Mii combinations. No inference of a missing driver is made
for those six, because the dedicated folder contains their non-numbered models.

Most numbered skins have the usual 12 ordinary vehicle prefixes represented.
Some have additional red/blue team forms. Six deserve review:

| Stem | Ordinary vehicle prefixes present in RaceKart | Name in received ConfigRT/Common/Menu BMGs |
| --- | ---: | --- |
| `ds-6` | 1 (`mb_kart`) | No nonblank custom name found |
| `fk-7` | 1 (`la_bike`) | No nonblank custom name found |
| `fk-8` | 1 (`la_bike`) | No nonblank custom name found |
| `ka-5` | 1 (`sa_bike`) | No nonblank custom name found |
| `kt-5` | 10 | No nonblank custom name found |
| `wl-6` | 10 | No nonblank custom name found |

The newly received scene/menu BMGs were also searched for these six IDs and did
not supply a nonblank name. The archived source normally falls back to a base
character name for missing custom text. Whether the current engine restricts
these variants or has additional fallback behavior is not yet established.

`kt-5` lacks `lb_kart` and `le_kart` variant-named files in RaceKart; `wl-6`
lacks `lb_bike` and `ldf_bike`. This records the received filenames, not proof
that those combinations are intended to be selectable.

Tails (`ca-5`) has 48 race files: 16 ordinary/team vehicle forms plus 32 `_2`/
`_4` forms. Knuckles (`lg-6`) has 16 ordinary/team forms and no `_2`/`_4` files
in this upload. Multiplayer support/fallback must be checked against current
code and mapping before changing either set.

### My Stuff overlaps

Scene(5).zip includes a `My Stuff` set for the base `kt` character. Ten of its
12 vehicle archives are byte-identical to the corresponding received `kt-5`
race variants. The other two match-name variant files are absent from RaceKart,
and `My Stuff/kt.brres` differs from `VariantDriver/kt-5.brres`.

This is another reason to preserve physical folder identity and wait for XML
and override precedence. Base-character names and selected-variant names are
not interchangeable.

## 5. Scene and menu differences

| Comparison | Added members | Removed members | Changed members | Unchanged |
| --- | ---: | ---: | ---: | ---: |
| Old source Menusingle → current MenuRace/Menusingle | 18 | 0 | 313 | 1,202 |
| Old source Race → current MenuRace/Race | 0 | 0 | 46 | 655 |
| Old source Race_E → current MenuRace/Race_E | 6 | 9 | 55 | 14 |
| Assets BackModel → Scene BackModel | 0 | 0 | 2 | 2 |
| Assets Earth → Scene Earth | 0 | 0 | 0 | 3 |
| Assets Globe → Scene Globe | 0 | 0 | 0 | 989 |
| Assets MenuOther → MenuRace MenuOther | 1 | 0 | 5 | 469 |

Redundant `./` U8 directory components were normalized for comparison; the
original stored names and hashes are preserved. This avoids falsely treating
the same member as removed and re-added just because an archive tool wrote a
different root-directory representation.

The two BackModel archives differ in `baloon.brres` and `trophy_kinoko.brres`.
The two Earth copies at `Assets/Scene/Model/Earth.szs` and
`Scene/Model/Earth.szs` are identical, but `Model/Earth.szs` is a different file.

### Three Race.szs choices

| Physical path | Bytes |
| --- | ---: |
| `MenuRace/Race.szs` | 1,882,603 |
| `Race/Race.szs` | 2,027,424 |
| `Scene/UI/Race.szs` | 6,005,464 |

These files are not equivalent. Across all received folders there are 12
same-name groups with differing bytes, including these race/menu/background
groups and the eight character groups above. Identical basenames alone are
not proof they map to the same virtual path; the XML resolves that question.

## 6. Small layout details captured

Using the NW4R pane structures in the supplied source, 84 changed BRLYT layouts
were inspected at pane level, producing **640 pane-record differences** with
no parser errors. Position, rotation, scale, dimensions, alpha, flags, picture
vertex colors and text color/font sizes are recorded where applicable.

Examples from the MenuOther alternative:

- The license `mii` pane changes from 120×120 to 90×90, with scale 0.65 to 0.5
  and Y position approximately -42.0072 to -28.7572.
- `nitro_mii_frame` moves from Y=55 to Y=45.
- The license menu adds a `nitro_button_pan` picture pane sized 274×80.

These are comparisons of `Assets/Scene/UI/MenuOther.szs` against
`MenuRace/MenuOther.szs`; which alternative is displayed still depends on XML.

Other recorded details:

- The current MenuRace item-window layout removes the old off-screen
  `xMeap826` picture pane at (9999,9999).
- The speedometer layout's bytes differ from the old archive, although the
  decoded pane transform/color fields in that layout are unchanged. This points
  to other layout data rather than proving a position change.
- The default and locale Nitro rankings layouts differ in capsule dimensions,
  scale, colors and icon dimensions.

This inspection does not fully decode material programs, animation tracks,
texture pixels or rendered 3D meshes. Their exact file hashes remain available
so those details will not be silently discarded during source/asset updates.

## Next inputs and source status

The active **Riivolution XML** was subsequently received in `MKNitroFont.zip`.
The resulting routes, My Stuff setting and save redirection are now recorded in
`FONT_XML_REPORT.md`. The user clarified that the failed `Source.zip` contained
assets, so it is not treated as a missing source project. The current executable
still has implementation differences from the three older source archives;
that separate finding does not depend on the failed upload's filename.

Tracks, BRSTM music, any remaining character/assets folders and the server
source remain pending. This report does not claim a source/binary match,
successful compilation, rendered visual QA, Wii/Dolphin boot, online play or
licence compliance. No uploaded asset was replaced with an older copy.

## Included evidence

- `variant_results/inventory.csv`: all 1,171 files from VariantSound.zip.
- `variant_results/variant_registry.csv`: driver/map/kart/voice/marker/name joins.
- `variant_results/sound_headers.json`: exact sound header checks.
- `variant_results/overlapping_filenames.json`: all variant duplicate groups.
- `variant_results/overlapping_szs_differences.json`: internal differences.
- `model_scene_results/inventory.csv`: the 1,649 kart/scene files.
- `model_scene_results/race_variant_registry.json`: exact vehicle filenames.
- `model_scene_results/scene_internal_differences.json`: canonical member diffs.
- `model_scene_results/pane_layout_differences.json`: pane values before/after.
- `model_scene_results/all_upload_filename_overlaps.json`: cross-folder groups.
- `model_scene_results/upload_provenance.csv`: which upload supplied each file.
- Header/resource manifests and the read-only inspection scripts.

The first binary/core-asset report is included for continuity. Its detailed
evidence remains in the first comparison ZIP.
