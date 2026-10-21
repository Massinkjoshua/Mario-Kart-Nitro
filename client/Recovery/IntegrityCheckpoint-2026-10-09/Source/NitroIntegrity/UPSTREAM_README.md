# MKNITRO NitroIntegrity — PAL source prototype

Prepared 8 October 2026 for Code(10).pul, main(3).dol and StaticR(2).rel.

**This package contains an audit-only C++ source extension. It has not been compiled with CodeWarrior, installed in Code(10).pul, or tested in Dolphin/Wii. It does not block all codes in the linked lists.** Host tests pass; online enforcement needs a matching source build and clean-session validation first.

Your current game binaries have been preserved. The saved 7 October release-candidate source explicitly records menu, character and track incompatibilities with the active pack. Do not rebuild that entire older source to install this extension into the working game.

## What is included

- `PulsarEngine/Security/NitroIntegrity/`: new C++98-compatible policy and Pulsar adapters.
- `Manifest.hpp`: 23 selected PAL instruction words, derived from your original game files and checked against the absolute patches in Code(10).pul.
- `manifest_review.json`: exact inputs, accepted candidates and every excluded target.
- `integration/WiiLink.patch`: an admission check inside the existing auth hook, before its cached-payload path. It adds no competing hook at that address.
- `tools/build_manifest.py`: read-only generator for the supplied PAL game revision and Kamek-v2 PUL format.
- `tests/`: portable policy, mocked game-adapter and binary-parser tests.
- `ASSESSMENT.md`: coverage, existing prototype findings and work needed for broader protection.

The package contains no game executable, REL or compiled Code.pul.

## Behavior

| Part | Current behavior |
| --- | --- |
| Startup | Checks selected DOL words and observes GCT headers; never reads REL words at the boot callback. |
| Menu section / race load | Checks DOL and REL words after a REL callback establishes the correct phase. |
| Race loop | Rechecks every 60 local callbacks, independent of the reported race clock. |
| GCT header observation | Logs a double `0x00D0C0DE` marker in the specified low-memory range. This does not establish that a handler executes; it never triggers enforcement. |
| Local item/physics audit | Logs each local player's inventory, numeric validity, speed and coordinates every 300 callbacks. It supports both players on one console and skips remote players. |
| Online entry | In audit mode, logs and allows entry. With reviewed enforcement enabled, fails closed on unsupported region, unavailable REL phase, invalid/unreviewed manifest or a changed checked instruction. |
| In-race enforcement | With reviewed enforcement enabled, an integrity failure invokes the game's normal OSFatal message screen. It does not deliberately corrupt memory or force a busy loop. |

The prototype never zeroes speed, changes items, edits ratings or bans an account. An unchanged inventory, a rare item carried into first place, or speed above a mutable local limit is not treated as proof of cheating. Local state logs remain diagnostic even when instruction enforcement is enabled.

## Integrate in the matching source project

1. Obtain the complete current project/build folder corresponding to the working Code(10).pul, including any later binary-patch scripts. Keep a separate test pack. The older release-candidate source is not a verified substitute.
2. Copy the `PulsarEngine/Security/NitroIntegrity` directory into that project. The inspected Pulsar Makefile discovers `.cpp` files recursively.
3. From its root, check and merge `integration/WiiLink.patch`:

   ```bash
   git apply --check /path/to/NitroIntegrity/integration/WiiLink.patch
   git apply /path/to/NitroIntegrity/integration/WiiLink.patch
   ```

   If the current hook differs, manually add the include and `CanEnterOnline()` call at the top of the existing auth-send hook, before `s_payloadReady`. Preserve its other behavior. The patch dry-run succeeds against the archived source; compatibility with your missing current source is still unverified. The existing game-mismatch error is reused provisionally; it does not label the player a cheater.
4. Keep `MKNITRO_AC_ENFORCE_INTEGRITY=0` and `ManifestRuntimeReviewed=false` for the first test. Keep the existing server selection, public key, compiler and loader configuration. Do not enable `PROD` just to enable an inherited Gecko check; the archived project also gates private security dependencies behind that flag.
5. Use your installed Windows/MSYS2 CodeWarrior and Kamek tools. With their actual paths configured, the existing project command is:

   ```bash
   make CC='/c/path/to/mwcceppc.exe' AS='/c/path/to/mwasmeppc.exe' KAMEK='/c/path/to/Kamek.exe'
   ```

   Output should be `build/Code.pul`. These are placeholders for your installed tool paths. This environment has no PowerPC compiler, Kamek executable or Dolphin instance, so a full game build was not performed here.
6. Regenerate the baseline against the test binary and its actual `GameSource/versions.txt`:

   ```bash
   python3 tools/build_manifest.py --dol '/path/to/main(3).dol' --rel '/path/to/StaticR(2).rel' --code '/path/to/test/Code.pul' --versions '/path/to/current-project/GameSource/versions.txt' --targets tools/targets.json --out PulsarEngine/Security/NitroIntegrity
   ```

   Run this from the extracted extension package, then copy the generated header into the project. If the effective check table changes, rebuild and repeat the comparison until stable. A different game revision or Kamek format is rejected by this generator rather than guessed. The SHA in the header is provenance, not runtime attestation.
7. Verify the resulting PUL format against the active loader before installing the test build. Collect clean logs through boot, login, downloaded server payload, normal races and reconnects. Investigate each reported word against the approved runtime patch; do not auto-learn a baseline from untrusted client memory or whitelist unexplained mismatches.
8. After the matching build and approved runtime patches are understood, revise any conflicting checks, set `ManifestRuntimeReviewed=true`, and add `-DMKNITRO_AC_ENFORCE_INTEGRITY=1` to the existing CFLAGS. Do a clean rebuild with the same installed tool paths so every object sees the change. Setting only the enforcement flag intentionally refuses online play because the included manifest has not passed runtime review.

## Validation to perform before release

- Current Halloween menus, settings, characters, track list and HUD still work.
- Clean PAL Dolphin and Wii clients can log in and race with the current server payload.
- One- and two-player online, consecutive races, leaving/rejoining and host changes.
- 150cc/200cc, custom tracks, cannons, respawns, long jumps and any higher-speed modes.
- Triples, golden mushrooms, item loss, thundercloud transfer, feather, Mega TC and every enabled special item mode.
- Carry a powerful item into first place and hold an ordinary item for a long time: no sanction.
- In an isolated consenting test room, modify one selected instruction and confirm that audit reports it; only then verify admission refusal and the enforcement message.
- Restore the approved build and confirm that clean online play resumes. Do not infer account guilt from an integrity mismatch.

Run the reproducible host checks with `bash tests/run.sh` on Linux with Python 3 and GCC. They use ASan/UBSan and warnings as errors. Test mocks do not validate PowerPC ABI, real hook timing or multiplayer behavior.

## What is needed next

The current matching Pulsar project/build folder and the server/backend plus downloaded payload source are needed to complete integration, authorize item acquisition, validate results and control ratings. Credentials and player databases are not needed for the source review. The supplied DOL/REL verify game addresses; they do not recover all later Nitro modifications.
