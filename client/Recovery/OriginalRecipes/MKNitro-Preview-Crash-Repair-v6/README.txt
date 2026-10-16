Mario Kart Nitro - Preview Crash Repair v6 (PAL)

INSTALL
1. Fully stop Dolphin.
2. Back up your current MarioKartNitro_Test/Binaries/Code.pul and
   MarioKartNitro_Test/Assets/UIAssets.szs.
3. Merge this package's MarioKartNitro_Test folder into your existing folder
   under Dolphin Emulator/Load/riivolution. Replace the two matching files.
   Do not create a second MarioKartNitro_Test folder inside the existing one.
4. Start the game normally, without restoring a save state.

The correct installed files are:
  MarioKartNitro_Test/Binaries/Code.pul
  MarioKartNitro_Test/Assets/UIAssets.szs

This package includes the v5 settings and course-preview changes. UIAssets.szs
is byte-identical to v5. The current font, ranks, online icons, sea, sky, title,
character assets, XML, Loader.pul and Config.pul are retained.
You do not install main.dol or StaticR.rel; they were used for diagnosis only.

REPAIR
The log shows Funky's seventh skin loading fk-7-allkart.szs before the crash.
Its decompressed archive uses 897952 bytes of the original 921600-byte heap.
That same heap must also hold runtime vehicle models and animation objects.
Native-code execution reproduced the screenshot's exact fault: an 800-byte
ScnMdl allocation returns null and SetPriorityDrawOpa writes to address 0xD0
at PC 0x8006DD0C.

The PAL patch raises this preview heap to 1183744 bytes. This adds 256 KiB per
local player, at most 1 MiB for four local players. It preserves native cleanup.
Relative to v5, the binary adds exactly one instruction-write patch; existing
settings/preview hooks and all other region blocks are unchanged.

VALIDATION AND FIRST GAME CHECK
The same native loading test completes with all twelve primary vehicle models.
The supplied fk-7, fk-8 and kt-5 archives pass normal/battle allocation tests
with one/four screen settings. Repeated native heap initialization and reset
recover all memory in the test fixture. Detailed coverage and limits are in
Verification/Verification.json.

A full Dolphin boot was not available here. First, cycle through Funky's skins
past slot 7, enter vehicle selection, press Back, and repeat once. Then check
King Boo's new skin and the return from a race to course selection. If another
crash occurs, keep its screenshot and the new Dolphin log.

The earlier recovery ZIP removes recent UI/code changes but retains the same
old small preview heap, so it is not a fix for this particular allocation crash.

Verification scripts are development records using the build workspace and
uploaded binaries; they are not installation tools. No original game executable
or StaticR.rel is redistributed in this package.
