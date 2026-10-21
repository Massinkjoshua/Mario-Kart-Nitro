MARIO KART NITRO - MAIN SETTINGS v10 (PAL)

INSTALL
1. Back up the destination files listed below.
2. Merge MarioKartNitro_Test into your existing mod folder, replacing matching files:
   Binaries/Code.pul
   MenuRace/Channel.szs
   Assets/UIAssets.szs and the included UIAssets language copies.
3. Replace your active Riivolution XML with the included MarioKartNitro.xml (use your existing XML filename if needed). The only XML change is an explicit route from /MarioKartNitro_Test/MenuRace/Channel.szs to /Scene/UI/Channel.szs.
4. Fully stop Dolphin and boot normally without restoring a save state.

CHANGES
The title Settings button opens the native Options page. Its background and white decorations are supplied by Channel.szs. Your current MenuOther already has Halloween artwork; this update copies that matching artwork and background layout into Channel's OptionBG.
Mario Kart Channel is hidden on every Options activation and loaded as inaccessible. The remaining GameCube Controller, Custom Wi-Fi Connection, and Settings buttons are centered at y=70, 0, -70 for both aspect-ratio variants.
Channel's top and bottom decorative picture strips have zero dimensions. The Settings title, controls, and Back button stay present. Those shared Channel decorations are also removed on related screens that use the same Channel layouts.

No MenuOther_E file is required. Your uploaded XML has no route for it.
MenuOther, Title, Title_E, Font, race HUD, globe and character assets are not replaced.
The current uploaded Code.pul is the baseline: old code, old commands and other regions are preserved. The two added code patches target PAL only.
All 13 supplied UIAssets language copies were identical; each receives the same one-file button-position edit.

VERIFICATION
Yaz0/U8 round-trip contents checked for both modified archives; all files outside the recorded changes remain exact.
Native Options activation tested with states 0, 1, 2: hidden flag, next-page reset, initial selection, stack and preserved r31 checked. The existing compiled button loader wrapper was executed with its relocations to confirm it forwards the inaccessible flag. Selection and layout loading were intercepted in this harness.
The imported background texture was decoded and inspected. No full Dolphin rendering/gameplay test was available.
Test Title > Settings: confirm three buttons, background and strips, move through all three with the controller, enter/exit each option, and press Back. Then check License Settings is unchanged.

ROLLBACK
Restore the current-file backups taken before installation, including your XML.
