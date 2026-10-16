# Mario Kart Nitro — font and Riivolution routes

Comparison checkpoint, 16 October 2026. Continues the binary/core-asset and
variant/kart/scene reports. This is a static audit of the supplied files; the
mod and source projects were not edited or rebuilt.

## Upload clarification

The user clarified that the failed upload called `Source.zip` contained
AllKart and related assets. It was **not** a newer C++ source project. The audit
no longer lists a retry of that file as a source prerequisite. The three source
projects supplied earlier remain the actual source baselines.

## What MKNitroFont.zip contains

| Content | Files | Action |
| --- | ---: | --- |
| `MKNitroFont/Font.szs` | 1 | Decompressed; all six internal fonts inspected. |
| `riivolution/MarioKartNitro.xml` | 1 | Every patch declaration and available file route inspected. |
| `riivolution/config/RMC*.xml` | 4 | Saved option values inspected. |
| Save data | 8 | Content not parsed, extracted, or included in this checkpoint. |

The archive has 14 files and 6,775,190 uncompressed bytes. Its SHA-256 is
`7fab3a614f1137aa799ea2c47a4d23096d7eb810ec384374efdb0ca2b23dc0e0`.

The audit now has **2,885 non-save pack files** locally available. Counting the
eight save entries in the uploaded ZIP gives 2,893 received files; their contents
are excluded from the comparison and shareable evidence.

## 1. Routes that resolve the earlier ambiguities

Uploaded character folders were provided without their enclosing `Characters`
directory. The audit explicitly translates the XML's
`/MarioKartNitro_Test/Characters/<folder>` into the corresponding uploaded
`<folder>`; it does not assume that these are root-level installation paths.

| Disc or loader destination | Physical source specified by this XML |
| --- | --- |
| Loader memory at `0x80004000` | `/MarioKartNitro_Test/Binaries/Loader.pul` |
| `/Binaries` | `/MarioKartNitro_Test/Binaries` |
| `/Race/Course` | `/MarioKartNitro_Test/Tracks` |
| `/Scene/Model/Driver` | `/MarioKartNitro_Test/Characters/VariantDriver` |
| `/Scene/Model/Kart` | `/MarioKartNitro_Test/Characters/VariantAllKart` |
| `/Race/Map` | `/MarioKartNitro_Test/Characters/VariantMap` |
| `/Race/Kart` | `/MarioKartNitro_Test/Characters/RaceKart` |
| `/sound` | `/MarioKartNitro_Test/Characters/VariantSound` |
| `/Scene/UI/Race.szs` | `/MarioKartNitro_Test/MenuRace/Race.szs` |
| `/Scene/UI/MenuOther.szs` | Explicit override from `/MarioKartNitro_Test/MenuRace/MenuOther.szs` |
| `/Scene/Model/BackModel.szs` | Explicit override from `/MarioKartNitro_Test/Scene/Model/BackModel.szs` |
| `/Scene/Model/Earth.szs` | `/MarioKartNitro_Test/Assets/Scene/Model/Earth.szs` |
| `/Scene/UI/Globe.szs` | `/MarioKartNitro_Test/Assets/Scene/UI/Globe.szs` |
| `/Scene/UI/Font.szs` | **`/MKNitroFont/Font.szs`**, outside the main pack directory |
| `/Sound/strm` | `/MarioKartNitro_Test/CTBRSTM` |

### Eight character-asset copies are not same-target XML conflicts

The differing `bk-1.brres`, `bk-1-allkart.szs` and six `fk-*-allkart.szs`
copies in VariantSound are routed under `/sound`. Their dedicated driver/kart
counterparts are routed under `/Scene/Model/Driver` or `/Scene/Model/Kart`.
The supplied character code requests the latter model paths. Preserve the
dedicated copies for those paths; the duplicate filenames alone do not establish
an override conflict. Direct SD reads by other code are not ruled out.

### Three Race.szs files

The main XML explicitly maps `MenuRace/Race.szs` to `/Scene/UI/Race.szs`.
Neither `Race/Race.szs` nor `Scene/UI/Race.szs` has a main file/folder route in
this XML. That resolves which supplied archive this XML selects for the race
UI, without deleting the alternatives or assuming that another launcher/XML
could never load them.

### The two real differing-payload target overlaps

The broad `Assets` folder route introduces the Assets copies of BackModel and
MenuOther. Later explicit file declarations target the same disc paths using
`Scene/Model/BackModel.szs` and `MenuRace/MenuOther.szs`. These are the two
different-payload overlap groups in the available main routes. The declaration
order and exact hashes are recorded; effective launch precedence has not been
tested in Dolphin or on Wii.

The smaller license Mii and `nitro_mii_frame` layout changes from the previous
report are in the explicitly specified MenuRace MenuOther archive. They must
remain part of the reconstruction rather than be lost by copying only Assets.

### Files with no main XML route

The five BaseAllKart files, eight additional Race language archives, eight
additional Title language archives, the alternative Earth/Globe/Race copies,
and the My Stuff files are not selected by a main file/folder route. Their exact
list is saved in the evidence. This does not prove that they are disposable:
optional patches, direct SD reads, or another launcher definition may use them.

Two explicit external paths differ only in case from the supplied physical
paths: `Assets/Boot/Strap/eu` versus `Assets/Boot/Strap/Eu`, and
`Assets/thp/title` versus `Assets/Thp/Title`. Record the distinction when
packaging for a host with a case-sensitive filesystem; do not silently rename
the uploaded files or claim that a current launcher fails because of it.

## 2. Options and save routing

The XML's Game option defaults to its Enabled choice. My Stuff defaults to its
first choice, Disabled. The four saved RMC region configurations also set My
Stuff to index 1, which selects Disabled. These are the supplied settings;
another user's saved selection can differ.

If My Stuff All is enabled, its patch writes byte `01` to `0x80001200` and
declares both a filename-search folder and a recursive root folder, plus a
Music subfolder route. Music Only writes byte `02` and declares music routes.
These optional declarations are recorded separately from main routes.

The main save redirection is
`/riivolution/save/NitroWFC/RMC{$__region}`, with cloning enabled. This is
consistent with the current binary's `NitroWF%s` format when its suffix is `C`.
The source's separate-save `C2` option is a different path and is not established
as active merely by the main save declaration. Save contents were not inspected.

The game ID filter is `RMC` without a region restriction. This is broader than
the actual current engine container, whose Korean section length is zero.
The XML filter does not prove Korean engine support.

The eight guarded DOL/REL branch memory writes have the same addresses and
values as the old source project's Base.xml template. The injected Loader.pul
is the current 4,192-byte loader identified in the first report, not the old
source build's 2,988-byte loader.

## 3. Stale or not-yet-supplied XML references

There are 348 explicit RaceKart references, grouped into **29 variant stems**,
that have no matching file in the received RaceKart folder. None of those 29
stems has a driver BRRES or any race archive in the received dedicated folders.
Each has 12 old XML vehicle references. These may be stale declarations for
removed variants, or material not supplied; they do not establish 348 broken
selectable combinations in the current game.

The stems are `bds-3`, `bk-3`, `bk-4`, `blg-5`, `bpc-2`, `bpc-4`, `ca-1`,
`ca-2`, `dd-3`, `dk-1`, `dk-4`, `dk-6`, `ds-1`, `jr-5`, `jr-6`, `kp-3`,
`kp-4`, `kp-6`, `kt-2`, `kt-3`, `lg-1`, `lg-2`, `mr-3`, `mr-4`, `pc-4`,
`pc-5`, `wl-5`, `wr-4` and `wr-5`.

The main folder rules for Tracks, CTBRSTM, Ghosts/Experts and Ghosts/ExpertsRT
also await those uploads. An optional My Stuff/Sound/strm directory was not
received. None of these absent upload inputs was inferred from filenames alone.

## 4. Six fonts inspected

The Font.szs U8 archive contains these six RFNT files. No older Font.szs was
found in the supplied source resources for a pixel-by-pixel baseline comparison.

| Font | Mapped codepoints | Distinct mapped glyphs | Texture sheets |
| --- | ---: | ---: | ---: |
| `indicator_font.brfnt` | 43 | 43 | 4 |
| `kart_kanji_font.brfnt` | 850 | 850 | 2 |
| `mario_font_number_blue.brfnt` | 13 | 13 | 3 |
| `mario_font_number_red.brfnt` | 13 | 13 | 3 |
| `tt_kart_extension_font.brfnt` | 49 | 49 | 10 |
| `tt_kart_font_rodan_ntlg_pro_b.brfnt` | 30 | 30 | 2 |

All six passed the implemented declared-length, block-boundary, linked pointer,
texture-data bounds, CWDH width-table and CMAP character-map checks. No mapped
glyph lies outside its sheet capacity; every mapped glyph has a width entry;
every alternate glyph lies within capacity. Exact signed bearings, advances,
font sizes and glyph mappings are retained in `font_structures.json`.

The union contains 942 distinct codepoints. All visible text characters in both
main track config BMGs are covered by at least one supplied font. That does not
simulate each control's font selection, dynamic text substitutions, line breaks
or actual rendering, and does not prove the earlier garbled-text issue had any
particular cause.

### Language-name coverage limitation

The UI Common BMG language names include 12 distinct codepoints absent from
all six supplied fonts:

| Common BMG ID | Label | Unmapped characters |
| --- | --- | --- |
| `0x6EA11` | 日本語 | 語 |
| `0x6EA19` | 한국어 | 한, 국, 어 |
| `0x6EA1A` | Русский | Р, у, с, к, и, й |
| `0x6EA1C` | Čeština | Č, š |

This is a font coverage finding for those labels, not a confirmed screenshot of
their in-game appearance. Region-specific fallback and runtime font selection
were not simulated. Do not modify the language strings or generate replacement
glyphs without choosing the intended localization behavior.

## Evidence and limits

`font_xml_results/` records all 1,733 declarations, 4,187 expanded main routes
for received files, 1,302 repeated target groups (mostly identical redundant
declarations), source paths, saved option values, font structures and text
coverage. `inspect_font_and_xml.py` reproduces the static audit. Font structs
were read from the supplied `GameSource/core/nw4r/ut/RawFont.hpp`.

Folder, option-index, default parameter and save-cloning interpretation follows
the primary Riivolution [Patch Format documentation](https://riivolution.github.io/wiki/Patch_Format/).
The report uses that documentation to interpret this XML; it does not claim to
have executed Riivolution's or Dolphin's patcher implementation.

Tracks, BRSTM music and ghosts remain to be compared when supplied. Existing
binary/source differences, three config-record differences, one malformed loose
voice file and six partial/unnamed variants remain recorded in the earlier
reports. No uploaded mod file was repaired or replaced in this checkpoint.
