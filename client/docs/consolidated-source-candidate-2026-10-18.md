# Consolidated source-built review candidate — 18 October 2026

This candidate brings the currently published client source into one isolated build, paired with the exact reconstructed released v15 loader. It does not use a precompiled engine or loader as a build input. Three clean builds produced identical binaries. This is a new review candidate, not proof that the source matches older distributed engines.

Build ID: `nitro-source-candidate-20261018`. Binary hashes, tool hashes and manifest binding are in `BUILD_RESULT.json`; the manifest lists all 1,124 build-source inputs. Source scripts permit a fixed version string so archive/check-out differences cannot silently change this candidate's label. The checked-in generated Version.cpp intentionally uses this label.

11,176 isolated PowerPC executions passed (460 + 10,244 + 352 + 120), using the candidate binary. MEM2 pool, portable loader parser and cup-order host checks also passed with ASan/UBSan. Fixed/native installation sites match the recorded release for PAL (1,196), USA (1,188) and Japan (1,188). These checks cover isolated logic and installation records, not native game rendering/network/runtime behavior. Comparison references were introduced only after the source builds completed.

The full runtime manifest suite is BLOCKED: 2,777 of 2,885 files are absent from the supplied source handoff. See runtime-input-gap.json and host-integration.log. This pass did not build the WPF editor or run Dolphin/Wii. The optional historical leaderboard profile is separate; its older 1,828 checks are not counted here.

## Rebuild

From client/, with Python 3, make, Keystone 0.9.2, and separately obtained compiler/assembler/Kamek (see source/toolchain notices):

```sh
python3 scripts/build_review_candidate.py --compiler /absolute/path/mwcceppc.exe --assembler /absolute/path/mwasmeppc.exe --linker /absolute/path/Kamek --runner /absolute/path/wibo --output /absolute/path/new-output-directory
```

On a platform running the compiler directly, omit --runner. The output directory must not exist. The script copies editable sources into an isolated work area, builds P/E/J, assembles the loader, validates container/policy structure and writes CandidateOverlay plus reports. Proprietary tool binaries are not included. See BUILD_RESULT.json for the exact tested tool hashes.

## Team testing and remaining gates

1. Make a separate COPY of the complete latest runtime pack. Keep its config/configRT, track, music, UI and other assets. Back up the original Code.pul and Loader.pul in that copy.
2. Apply only CandidateOverlay/MarioKartNitro_Test/Binaries to the matching test-pack folder. Do not treat this ZIP as a complete runtime pack.
3. Test offline: boot, licence, characters/vehicle previews, cup/track selection, race start/finish, items, HUD, music and Time Trials. Record platform, build ID, result and crash logs.
4. Check leaderboard loading, pagination, back/reopen behavior. A controlled online test needs the team's normal server review/approval. This work has not approved hashes or changed the server.
5. Review results before any launcher/public release update. Neither the live launcher nor the current public runtime download was replaced here.

Matching source for all older released cores remains unresolved. Asset permissions/preferred editable inputs and the historical GPL/AGPL notice require separate review. This candidate does not establish that the notice has been cured. Existing published server/patcher sources and notices remain in the complete source snapshot.
