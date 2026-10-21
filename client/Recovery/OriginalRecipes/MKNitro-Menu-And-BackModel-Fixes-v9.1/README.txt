MKNitro menu and BackModel fixes v9.1 (PAL)

Back up the three destination files, then merge MarioKartNitro_Test into your active mod folder and replace the matching files:
Binaries/Code.pul
MenuRace/MenuOther.szs
MenuRace/Title.szs

Fully stop Dolphin and boot normally, without restoring a save state. No XML or BackModel.szs replacement is needed.

BackModel change: VS initialization and VS menu requests now select the same stopwatch/logo slot as the working custom Single Player menu, instead of the native flag slot. Includes multiplayer VS requests for consistency. Other modes and the hide request are unchanged. Native execution checks confirm slot selection and transition flags; Dolphin rendering has not been tested here. Test a VS race, return to course selection, then back out and repeat.

Includes the preceding license-menu fixes (title-sized Mii, Records disabled/hidden, button panels, readable heading/help backing, smaller title settings emblem) and removal of additive item-roulette whitening.

MARIO KART NITRO - LICENSE AND ITEM FIXES v9 (PAL)

INSTALL
Close Dolphin fully. Back up and replace these files in your active
Dolphin Emulator/Load/riivolution/MarioKartNitro_Test folder:
  Binaries/Code.pul
  MenuRace/MenuOther.szs
  MenuRace/Title.szs
Merge the included MarioKartNitro_Test folder into the existing folder.
Start the game normally, without a save state.

CHANGES
- License Settings uses the same Mii portrait and ring transforms as the title
  license card. The title screen's Mii size itself is preserved.
- Check Records is hidden and disabled for navigation. Initial selection and
  help text now point to Change Mii. Saved records are not deleted.
- Change Mii and Erase License are centered into two rows with visible framed
  dark panels, using the existing purple/orange artwork.
- MenuOther headings and help text receive dark backing panels for readability.
- Title-screen settings emblem is 35 percent smaller; its label is preserved.
- Removes the additive whitening of the incoming item layer during roulette
  and item acquisition, targeting the rectangular white flash.

KEEP
Keep the current Font.szs, UIAssets.szs and Assets/RaceAssets.szs (including
v8.2 pumpkin joystick), MenuRace/Race.szs from v8.1, Race_E.szs and XML.
This Code.pul includes the v6 preview-memory repair and existing v5 settings
and course-preview code. Only five PAL instruction writes are appended.
No main.dol or StaticR.rel replacement is needed.

VALIDATION
Archive round-trips, layout section counts and hierarchy checked. No native
patch address conflicts with existing v6 commands. Existing code and commands
and non-PAL blocks are preserved. Native OnActivate execution checks confirm
Change Mii is initially selected with its matching help message (rendering and
button-selection implementation intercepted). Additive-flash instructions
verified in a PowerPC execution harness. Full Dolphin rendering is untested.

CHECK IN GAME
Open License Settings: only Change Mii and Erase License should be selectable.
Check the portrait against the title card and inspect the smaller settings icon.
Collect an item and watch a complete roulette roll for the white bar.

ROLLBACK
Restore the three backed-up files together.
