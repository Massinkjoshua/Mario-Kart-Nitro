# Leaderboard parser follow-up — 16 October 2026

All 120 isolated PowerPC executions passed: 30 synthetic fixtures, each run
against the latest released PAL code and the existing source-built candidate at
two allocation bases. The function runs at released offset 0x4a2e0; the candidate
offset is taken from its build map. Exact hashes are recorded in
leaderboard-parser-emulation.json. No engine source or gameplay binary changed.

Checks assert expected results as well as released/candidate equality: names,
VR/rank, numeric and formatted friend codes, alternate friend_code spelling,
entry limits including 51 entries with capacity 50, skipped nameless objects,
escaped strings/braces, incomplete objects, long-name truncation, synthetic Mii
name preference and JSON fallback. Full sentinel-initialized output buffers are
compared; surrounding capacity canaries stay intact. Synthetic Mii bytes test
name extraction only; no RFL validity, private player data or network is used.

The compiled internal JSON, base64 and Mii-name helpers execute directly. Only
memcpy, memset, strchr, strlen and strncmp are intercepted with controlled libc
semantics. Any unexpected native call fails. The historical JSON-name behavior
replaces non-ASCII bytes and Unicode escapes with question marks; these tests
record that behavior rather than claiming full Unicode support.

The original v5 module is now preserved under Recovery/Leaderboard-v5-Original/,
with its supplied licence and byte hashes. ParseResponse's source body is
identical to the repaired candidate. The surrounding network implementation is
not: the candidate uses the shared NHTTP pool, a static 0x4000-byte work buffer,
a copied response, generation/in-flight state and menu-thread parsing/Mii work;
the original callback parses directly with an allocated 0x20000-byte work buffer.
Request lifetime and UI application therefore remain separate verification work.
This passing parser test does not establish their equivalence or justify replacing
the released binary. The module snapshot is not a complete source project.

To run from client/ with Unicorn 2.1.4 and the authorised binary references in the
locations used by the existing test harness:

```sh
python3 tests/leaderboard_parser_ppc.py
```

The test requires build/Code.pul, build/Code.map and the exact supplied latest
CurrentPack/MarioKartNitro_Test/Binaries/Code.pul. These precompiled inputs are
not bundled with the public source-only tree. Full client Corresponding Source,
historical version coverage, actual game runtime and asset questions remain open.
