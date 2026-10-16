Mario Kart Nitro — PAL preview and online rating TEST FIX

Install
Stop Dolphin fully. Back up your current Code.pul, then replace the active
MarioKartNitro_Test/Binaries/Code.pul with Binaries/Code.pul from this ZIP.
Start without a save state. No character archives or StaticR.rel are included.

This replaces the earlier PAL VR test fix and includes that same VR/BR correction.
US/Japan blocks remain unchanged; this is a PAL fix.

Preview corrections
1. The shared vehicle-field accessor now writes MenuDriverModel +0x14, which
   the original PAL SwitchState function actually reads to select the riding
   animation. Previously it wrote +0x1c.
2. Deferred driver reloads preserve riding states 2 and 3, instead of recognizing
   only state 2 and always restoring state 2. Character-select behavior remains
   on its existing path.

Testing performed
80 PowerPC reload-control-flow cases passed at two load addresses, covering
states 0–4, character select, kart/bike IDs, target-field writes and preserved
registers. Native loading and rendering dependencies were mocked. Earlier VR
wrapper bytes remain unchanged; their 120 execution checks passed previously.
There has been NO rendered Dolphin or live online verification here.

Please test
- Fresh boot: character idle and selection animations.
- Vehicle selection: Bowser sits on the bike rather than standing through it.
- Online course selection: same check as your supplied screenshot.
- After a race: return to course selection and check the preview again.
- With another updated PAL client: each player's 5,000 VR displays correctly.

These fix two verified code errors, but are not a guarantee that every preview
symptom is resolved. If the standing pose remains, send the new screenshot and
which step first shows it. Restore your backed-up Code.pul if this introduces
any regression. Keep the public release draft until in-game checks pass.
