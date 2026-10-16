# Source status — 16 October 2026, recovery revision 3

The editable client and C++ loader build; Pack Creator also compiles. Named
post-checkpoint patches have now been reconstructed and checked against released
PowerPC functions. **Complete Corresponding Source for every existing release
has not yet been established, and nothing was deployed or published.**

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
| Core correspondence | Full correspondence of every existing compiled client function to preferred source still requires completion. Passing tests and a matching hook list are not proof of full implementation parity. |
| Public release history | GitHub 1.0 (5 October) verified by bounded ZIP reads. Its Code.pul differs from the latest upload; its loader matches the reconstructed v15 loader. No source archive is currently attached to that release. Other launcher/Discord releases are not exhaustively verified. |
| Server/payload | Recovered AGPL server and repaired candidate build; candidate race tests pass. Running server source/executable and the separately built payload remain unverified. |
| Runtime/publication | No Dolphin/Wii boot, live online test, GitHub upload or server activation performed. GitHub connection is pending. Asset redistribution permissions still need creator records. |

Normal builds write isolated candidates. CurrentPack, editor reference resources
and public release references stay byte-preserved. No new anti-cheat enforcement,
bans, online policy changes or canceled website-label edits were activated.

See NEXT_STEPS.txt, docs/recovered-source-followup.md, docs/public/ and the
separate server handoff. Preserve this status when sharing the recovery package;
do not describe it as a completed licence cure.
