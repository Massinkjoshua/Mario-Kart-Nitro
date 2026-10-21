# Three recovered runtime installations

Reconstructed 16 October 2026 from the uploaded current PAL `Code.pul` and the
supplied native class layouts. Implemented in
`PulsarEngine/UI/RecoveredRuntimeRepairs.cpp` under GPLv3.

| PAL installation | Current function offset | Recovered behavior |
| --- | --- | --- |
| `0x8059E598` | `0x445E4` | Null-check menu/background managers and request background model zero with reanimation. |
| `0x808D3CDC` | `0x505E4` | Suppress item-window drawing for an empty inventory while preserving spinning roulette and an active Golden Mushroom. |
| `0x8081EE34` | `0x55DC` | Report preview model/BRRES and allocation state, call native model loading, then report completion. |

Kamek maps the native installations to USA/Japan. The implementation is newly
reconstructed source, not recovered original C++. Compilation and native-site
comparison do not prove full game behavior or byte equality.

The actual reconstructed PowerPC functions were also compared with the released
PowerPC functions in 460 isolated executions at two allocation bases. Empty,
Golden Mushroom and roulette cases, invalid HUD/player/owner cases, background
null checks and reanimation, preview diagnostics, heap checks and exact native
load arguments matched. Native game APIs were intercepted; real rendering and
allocation were not tested. See `docs/recovered-runtime-emulation.json`.

To repeat after a fresh build, install `tests/requirements-ppc.txt` and run
`python3 tests/recovered_runtime_ppc.py`.

Corrections to the previous audit: `0x80662D80`/`0x80662DC4` load saved VR/BR;
they are not speedometer hooks. `0x805FD8E8` activates the Options page; it is
not an online-exit hook. The recovered original patch recipes and native class
interfaces establish these names.
