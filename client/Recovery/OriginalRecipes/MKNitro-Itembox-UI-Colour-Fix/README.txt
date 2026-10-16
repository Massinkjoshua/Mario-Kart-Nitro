MARIO KART NITRO - ITEM BOX UI COLOUR FIX

Close Dolphin, back up the matching files, then merge MarioKartNitro_Test into your mod folder and replace the included Code.pul and both Race.szs copies. Keep the XML from the Menu/Scene language update. Start without a save state.

The new static item frame now receives the same native HUD colour update as the original frame panes, including the existing selected colour and multiplayer palette handling. The existing roulette highlights remain suppressed. This builds on the supplied Code(3).pul plus the title Settings v10 fix; those original commands and all US/Japanese blocks are preserved. The added item-frame hook targets PAL only. If you have installed a newer Code.pul since v10, do not overwrite it; provide it for merging.

The frame is checked for existence before applying colour. Native call/argument checks and file checks are recorded in Verification.json. No Dolphin rendering test was available. Test orange and cyan, item roulette/use, and split screen.

CORRECTED RELEASE
Fixed the incorrect absolute encoding of internal relocation addresses that caused an invalid write to 0x000c1ce6 on startup. The exact serialized patch stream is now applied using loader address rules and the patched native call is executed at two allocation bases, with and without the frame. Replace Code.pul from this corrected package; Race files are unchanged from the previous package.
