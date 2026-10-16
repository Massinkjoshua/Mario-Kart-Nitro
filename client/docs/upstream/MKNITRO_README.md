# MKNitro Pulsar C++ Project

This package is the rebuildable Pulsar/Retro Rewind C++ foundation for the
PAL/Europe Mario Kart Wii build (`RMCP01`). It is based on Retro Rewind's
`rr-pulsar` revision `217f23d40345d9c4bc628f3d7c5b4845368d443e` and includes
the MKNitro runtime files supplied on 2026-08-25.

Tracks and music are intentionally not included. Keep using the existing large
`Tracks` and `sound/strm` folders; neither is required to compile `Code.pul`.

## Included requested systems

- Input display: `PulsarEngine/UI/CtrlRaceBase/InputViewer.cpp`
- Intense CPU: called `HardAI` in source; see
  `PulsarEngine/Race/BinLoader.cpp`
- Item Rain: `PulsarEngine/Gamemodes/ItemRain/`
- Custom character skins and online synchronization:
  `PulsarEngine/CustomCharacters/`
- Multiple skin tables/slots: up to 50 custom tables per character, plus the
  extra Mii Outfit C support in `PulsarEngine/Extra/MiiOutfitC.cpp`
- Selectable UI/HUD colors: 12 choices in `PulsarEngine/UI/UIColor.cpp`

`CommonAssets.szs` contains the resource used by the Intense CPU toggle
(`kartAISpdParamRR.bin`). The supplied MKNitro `CommonAssets.szs` is identical
to the current upstream resource.

## Folders

- `PulsarEngine/`: runtime C++ and PowerPC patch source.
- `GameSource/`: documented Mario Kart Wii types, symbols and region data.
- `KamekInclude/` and `Loader/`: Kamek patch/loader support.
- `PulsarPackCreator/`: Windows pack creator source and embedded resources.
- `CurrentPack/`: exact uploaded MKNitro binaries and SZS archives. This is the
  known-working baseline and does not contain tracks or music.

## Runtime layout

Keep these paths in the Riivolution pack:

```text
MKNitro/
  Assets/
    CommonAssets.szs
    RaceAssets.szs
    UIAssets.szs
  Binaries/
    Code.pul
    Config.pul
    Loader.pul
  MenuRace/
    Menusingle.szs
    Race.szs
    Race_E.szs
  Tracks/                 (existing files; not included)
  sound/strm/             (existing BRSTMs; not included)
```

Use the XML that maps `Binaries/Loader.pul`, `Assets`, `Tracks`, music, and the
player override folders in that order. Do not load a second Retro Rewind or old
MKNitro `Code.pul` at the same time.

## Building Code.pul

The upstream build uses the CodeWarrior Wii executables `mwcceppc.exe` and
`mwasmeppc.exe`, plus `Kamek.exe`. Set their locations in a root `.env` file:

```make
CC=/absolute/path/to/mwcceppc.exe
AS=/absolute/path/to/mwasmeppc.exe
KAMEK=/absolute/path/to/Kamek.exe
```

Then run `make` from the project root. The region-combined output is
`build/Code.pul`. To build the loader, run `make loader`.

The domain compile modes inherited from rr-pulsar are:

- no extra flag: local/default testing domain
- `CFLAGS=-DTEST`: Retro Rewind test server
- `CFLAGS=-DPROD`: Retro Rewind production server

Do not select a production server mode until its compatibility and permission
requirements are settled. The existing uploaded `Code.pul` is preserved in
`CurrentPack/Binaries/Code.pul` regardless of later source builds.

## Character assets

The C++ system is included, but selectable characters only appear when their
matching models, menu models, icons, names and optional voice files are placed
in the paths expected by `PulsarEngine/CustomCharacters/`. The source supports
loose custom-character assets; the full Retro Rewind character asset library is
not stored in its public source repository and is not included in this package.

## Licensing

The combined source remains GPLv3. See `LICENSE`, `LICENSE_pulsar`, and
`LICENSE_mkw-sp`. Distributing a modified binary requires distributing the
corresponding GPLv3 source and preserving the license notices.
