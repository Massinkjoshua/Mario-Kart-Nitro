MKNitro native settings and character-preview repair v5 (PAL)

INSTALL
Fully stop Dolphin, then merge MarioKartNitro_Test from this ZIP into your
existing MarioKartNitro_Test folder. Replace BOTH files:
  Binaries/Code.pul
  Assets/UIAssets.szs
Start normally, without loading a save state.

This replaces v4 whether or not you already applied the recovery ZIP.
Keep your current XML. Do not install StaticR.rel into your mod; the supplied
clean module was used for analysis and native execution checks only.
Your sea, sky, fonts, badges and earlier online-menu positions are retained.

SETTINGS
The v4 mistake was writing the same values into four different transform
records. They are local, inherited, animation-offset and final transforms.
Writing absolute positions into the animation record applied the offset twice;
children also retained their old inherited positions.

v5 changes only each active row's local position and uniform scale, then calls
the native ControlGroup::ResetControlsPosition routine. That function rebuilds
the label, radio choices, arrows and nested value-control transforms together.
The original animation offsets and opacity remain intact. Each page uses its
actual radio/scroller count. Radio rows 6 and 7 and their option variants are
added because the code requests them but the supplied UI archive lacks them.
No settings values, options, messages or save data are removed or reassigned.

CHARACTERS
The v4 global vehicle-vtable visibility guard is removed.
On Cup Select and Course Select, the existing NoteModelControl preview path now
requests a standing idle driver and a hidden vehicle together. Its native state
comparison also recognizes the idle state, so it does not reload the character
and restart the animation every frame. Vehicle selection keeps its native
riding state and vehicle visibility. Other page owners keep their original path.
This intentionally provides a standing character preview on the course pedestal.

VERIFICATION AND LIMITS
Based on the exact uploaded pre-v4 Code(2).pul, SHA256:
5fe4083a44008ac5536e727b87999c03cea8597fb5d8da4120b45a66b60b2342
Only the PAL code block is modified. NTSC-U/J blocks remain byte-identical.
The original code/relocations are preserved except the SettingsPanel entry
branch and three additional hooks at verified native NoteModelControl sites.
Old BSS addresses are preserved as explicit zero-filled code data. Runtime
allocation grows by roughly 1.3 KiB; the larger file is mostly zero padding.

164 native integration cases passed at two dynamic code addresses. They execute
the real recursive UI transform routines, the native course-preview state path,
native driver state switching and native visibility management. Tests cover all
17 settings definitions with nested controls, four player slots, repeated frames,
course-to-vehicle transitions and return to course selection. Resource loading,
graphics/animation service boundaries and existing settings message setup are
stubbed; actual game/model rendering and full Dolphin boot are NOT tested here.
Archive repacking and decompression checks passed. This is a targeted repair
verified against the supplied native code, not a claim of in-game validation.

FIRST IN-GAME CHECK
Open Sound/Menu settings, then Knockout and both Race settings pages. Confirm
labels, choices, arrows and values align and controller/pointer navigation works.
Select a character and bike, enter course selection and check the standing pose.
Go back to vehicle selection, then return to courses. Complete a race with the
character/bike that previously showed the wheel and return to course selection.

DEVELOPMENT FILES
Verification contains the build/analysis scripts and selected native traces.
They require the referenced source, original uploads, extraction workspace and
Python dependencies; they are not an end-user installer. The original REL is
not bundled and has not been modified.
