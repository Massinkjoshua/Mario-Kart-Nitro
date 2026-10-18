# Released leaderboard source recovery — 18 October 2026

The optional Recovery/ReleasedLeaderboard profile now supplies C++ for the
released diagnostic selector, native-creator error wrapper and Mii validation/
binding/visibility patches, and connects them to ApplyError, StartFetch and
ApplyResults. The earlier request lifecycle reconstruction is retained.

The build uses the source-built main project's objects plus two source-built
overlay objects. The added symbols.txt declares the observed native work-state
accessor at PAL 0x801d9e94, so Kamek handles regional address conversion. No
released core or instruction bytes are copied into the build output.

The profile builds for PAL/USA/Japan. Actual behavior comparisons below are PAL.
The native creator failure code is read at work-state offset 0x7d8, as observed
in the release. Allocator failure details are obtained through two read-only
getters on the same compiled recovery pool state. This preserves creation-error
selection, including the special 32 KiB allocation message and cached error text
surviving a later successful create.

| Check | Executions | Scope |
| --- | ---: | --- |
| New diagnostics/creator/Mii wrappers | 1,328 | Exact error text and state fallback; creator arguments, failure-state clearing, allocation failure classes, failure/success sequences; valid/invalid Mii row reuse and both icon panes. |
| New actual ApplyError/ApplyResults | 212 | Error text, including after actual reconstructed failed creation; ten rows; counts 0/1/9/10/11/49/50 on pages 0/4/5/49; name/VR/rank/footer, icon visibility, load/bind calls, full canonical traces. |
| New actual OnUpdate | 288 | Request timeout boundary, applying results/errors once, all numbered errors, signed invalid enum state and row-sound timing/completion. |
| Existing request-flow regression | 252 | Activation/deactivation, request start and received responses; still passes on this profile. |
| Existing parser regression | 120 | The normal source-built candidate's parser still passes; expanded profile callbacks also execute their real parser. |

Every test compares actual released PPC with actual source-built PPC, using
independently asserted expected results. Native APIs and selected surrounding
callees are intercepted. Test reports state each boundary, binary hashes and
source hashes. Their counts are executions, not claims of unique full-game
scenarios; some cases repeat checks in stateful sequences.

The new profile hash is
5ea566c7f141f923b21d80f07f14c99f8835b2dcdd1f3ac15c3e992f01539a26.
The supplied released reference remains
58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364.
No gameplay binary, current pack, default candidate, server or enforcement mode
was changed. The default source candidate continues to use the queued-callback
repair, rather than the historical direct callback parsing in this profile.

Unverified areas include real UI/RFL rendering, friend highlighting, controller
navigation, native HTTP/allocator execution, callback races, own-Mii override
internals, full game/online runtime and full released-core correspondence. The
remaining methods inherited from original v5 are not certified as a whole by
these scoped checks. This is a recovered source section, not a complete cure
for the source notice or proof of an entire matching released client.
