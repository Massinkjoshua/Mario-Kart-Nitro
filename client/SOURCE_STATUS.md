# Source status — 18 October 2026, recovery revision 4

The editable client and C++ loader build; Pack Creator also compiles. Named
post-checkpoint patches have now been reconstructed and checked against released
PowerPC functions. **Complete Corresponding Source for every existing release
has not yet been established. Recovered source is public on the draft recovery
branch; no gameplay candidate or server change was deployed by that draft.**

| Area | Verified result |
| --- | --- |
| Latest named client repairs | Editable C++ for drift colours, PAL capability flags and vehicle fallback, kart-only custom effects, region v16 initialization, online-exit worker, course-preview matrix/scale/animation and selected-kart visibility. |
| Isolated behavior comparisons | 10,244 executions of released/rebuilt PowerPC functions at two bases matched. All 2,448 palette entries covered at both bases. Native APIs were intercepted. Three earlier reconstructed hooks also pass 460 executions. |
| Native installation comparison | PAL: 1,196 sites; USA/Japan: 1,188 each. No missing/extra sites or fixed-value/opcode differences. This checks installation structure, not all function bodies. |
| Released loader v15 | 678 editable assembly instructions and typed data independently rebuild all 4,192 bytes, SHA-256 ffa108e11f4c0b925f736bdb28681bf83e997b81de9fca9b2e2d6dd7ea6c9dbb. No precompiled loader input. Original C++ was not recovered. |
| C++ loader candidate | Shared parser/guard implementation, command consumption and owning-heap free checks pass. It is intentionally distinct from the exact historical assembly implementation. |
| Clean engine/loader build | CodeWarrior 4.3 via wibo 1.2.0, Kamek 2.0, PAL/USA/Japan. C++ flags aligned with the recovered October Makefile. |
| Pack Creator | Release WPF build passed using .NET SDK 10.0.402 with Windows targeting; zero errors and nine warnings. Target framework remains net7.0-windows. GUI was not run. Embedded runtime references are preserved. |
| Current assets/configs | All 2,885 received non-save files preserved. Working odd-cup padding fixed separately; three original config/RT differences retained. Missing Tracks/CTBRSTM/ghosts were not invented. |
| Exact final-PAL recipe | Latest Code.pul is reproduced exactly by editable final patch source plus a precompiled October core. This is useful patch evidence, not a clean source rebuild of that core. |
| Original supplied v5 source | Recovery/V5SourceSnapshot restores all 1,097 supplied original files with exact hash/path checks. The v5 binary correspondence audit remains separate. |
| Expanded released leaderboard source | Editable diagnostics/creator/Mii guards are connected to ApplyError/ApplyResults/OnUpdate in the optional recovery profile. 1,828 additional isolated PPC executions pass (1,328 wrappers, 212 UI methods, 288 update state machine), plus the existing 252 request-flow regression executions. Native APIs remain controlled; see docs/leaderboard-source-progress-2026-10-18.md. |
| Additional PAL checks | 352 isolated ghost/local-player/Dolphin executions, 120 leaderboard parser executions and 252 recovered request-flow executions passed. Each report states intercepted/native boundaries; none is a game boot. |
| Uploaded 9 October candidate | Recovery/IntegrityCheckpoint-2026-10-09 reproduces the uploaded experimental audit candidate and its linker map exactly from 1,136 original source/test files with a fixed 187-object order. This is a different binary from Code(10) and the latest release. |
| Core correspondence | Full correspondence of every existing compiled client function to preferred source still requires completion. Passing tests and a matching hook list are not proof of full implementation parity. |
| Public release history | GitHub 1.0 (5 October) verified by bounded ZIP reads. Its Code.pul differs from the latest upload; its loader matches the reconstructed v15 loader. No source archive is currently attached to that release. Other launcher/Discord releases are not exhaustively verified. |
| Server/payload | The 134-file live NitroWFC export is published. An operator rebuild on the original host exactly matched the running executable hash. Matching patcher source and pinned devkitPPC instructions reproduced stage1 and all four RMC on-disk payloads. Actual HTTP-served response bytes were not independently fetched. See ../server/docs/live-export-2026-10-16.md and ../patcher/VERIFICATION.json. |
| Runtime/publication | Source is public for review in draft PR #3 on Massinkjoshua/Mario-Kart-Nitro-Releases. The website Source & credits links are live. No Wii/Dolphin boot or live online candidate test was performed. The draft was not merged or deployed. Asset permission/editable-source records remain open. |

Normal builds write isolated candidates. The source-only publication omits the
CurrentPack/runtime assets, editor binary resources and precompiled references;
historical local handoff records describe those separately preserved inputs. No new anti-cheat enforcement,
bans, online policy changes or canceled website-label edits were activated.

See NEXT_STEPS.txt, docs/recovered-source-followup.md, docs/public/ and the
separate server handoff. Preserve this status when sharing the recovery package;
do not describe it as a completed licence cure.


