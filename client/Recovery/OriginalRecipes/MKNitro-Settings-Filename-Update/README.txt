MARIO KART NITRO - SETTINGS FILENAME UPDATE

INSTALL
Fully close Dolphin. Back up and replace MarioKartNitro_Test/Binaries/Code.pul using this file. No XML or asset changes are required. Start without a save state. For the release ZIP include this new Code.pul.

BEHAVIOUR
New saves use MKNitroGameSettings.pul. If it cannot be opened, the initial settings load tries RRGameSettings.pul in the same directory. Existing settings/progress load through the original validation and are written to the new file by normal initialization. The old file is retained as a backup. If neither exists, original defaults are created. The new settings file takes priority whenever it can be opened. Invalid/version-incompatible files follow the original validation/reset rules. Legacy RRSettings.pul trophy migration is unchanged.

DOLPHIN LOCATION
Open Dolphin File > Open User Folder, then Wii/shared2/Pulsar. Search its distribution subfolders for RRGameSettings.pul or MKNitroGameSettings.pul. This is separate from Load/riivolution. The exact distribution subfolder comes from ConfigRT.pul. SD-based installations use their existing mod save location.

PRESERVED
Built from the uploaded Code(4).pul, including the corrected item-box hook. Original commands and all unrelated code/data are preserved. Filename/fallback edits apply to the existing PAL, USA, and Japanese blocks; no Korean block is added. This does not complete other regional compatibility fixes.

RELEASE CLEANUP
Do not bundle your personal settings or progress files. Keep Config.pul, ConfigRT.pul, Code.pul, Loader.pul, and required mod assets. If your ZIP contains only Load/riivolution assets, NAND settings are outside it. Review any Ghosts/Trophies folders for personal records before release.

VALIDATION
See Verification.json for serialized-relocation and native helper checks. No Dolphin gameplay test is claimed. Verify your existing selected HUD colour/settings persist after installation, change one setting, restart, and confirm it persists.
