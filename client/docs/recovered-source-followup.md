# Remaining-source repair evidence

New reconstruction work is dated 16 October 2026 and licensed under GPLv3.
All original project and third-party notices remain in place.

## Client implementations

- CustomCharacters/DriftColours.cpp and Project/DriftColours.json: all 48 x 51
  skin RGB triples; effect-name matching and whitening; PAL create/update slots.
- CustomCharacterAssets.cpp: PAL missing-race-archive fallback now applies beyond
  the old Halloween whitelist. Original E/J restriction retained.
- Info.hpp: PAL INFO copy enables UMT and Feather capability bytes. It does not
  change the configured 200cc flag.
- Race/UltraMiniTurbos.cpp: PAL skips the extra RR effects resource, bike custom
  effects and orange SMT allocations, matching the final released branches.
- Network/Region.cpp: wrapper calls System::CreateSystem before PAL region/login
  refresh and the v16 diagnostic. Existing priority-two login hook retained.
- UI/PlayerCount.cpp: PAL asynchronous browser request validates scene/match
  pointers, checks disconnect pages, stops at 100 polls with 50 ms sleeps,
  frees browser state on failure/completion/exit, and preserves E/J behavior.
- CustomCharacters/RecoveredCoursePreview.cpp: native update first; cup/course
  page filtering; selected local kart; validated double-buffered scene pointers;
  native driver animation transition; local matrix and scale forwarding; selected
  kart visibility. Installer locates the released REL virtual-table signature.
  Native driver state offset 8 and kart stride 0x2c avoid incorrect padding in
  inherited headers. The bypassed historical diagnostic block does not execute.

The course installer is integrated into the existing pre-CalcMain source path;
its scheduling is source-based and has not been checked in a full game boot.
Function tests exercise the update/visibility behavior, not a live scene load.

## Build and checks

The inherited October C++ Makefile does not request -proc gekko. Removing the
later-added compiler override substantially improves normalized function matches;
assembly retains its Gekko setting. This does not establish complete parity.
Generated palette includes participate in the header content stamp.

See recovered-remaining-emulation.json for 10,244 real PowerPC executions at
0x81000000 and 0x81200000. Native APIs are controlled adapters. Cases cover every
palette entry, whitening, bounds, MEM1/MEM2 scene checks, disconnects, browser
failure, completion, timeout, region creation, and course matrix/scale/state.
See recovered-runtime-emulation.json for 460 earlier hook executions.

Native hook comparison is exact for addresses/types/fixed values in PAL/USA/
Japan after translated PAL-only effect writes are omitted from E/J. Internal
relocated target addresses are intentionally excluded from that comparison.

## Loader

Recovery/LoaderV15 builds the released loader from editable mnemonic assembly,
C strings, four typed native-API parameter sets, a command jump table and zero
initial state. It needs no old binary. Its output matches the received v15
SHA-256. This is a disassembly reconstruction; original C++ was not recovered.
The default C++ loader remains a separately labelled stricter candidate.

## What remains unproven

The entire client core and older public clients still need source correspondence
review; the exact final-PAL patch recipe still needs a precompiled core. No full
Wii/Dolphin runtime or live NitroWFC verification occurred. Complete deployed
server/payload source and asset permissions are not established by these tests.
