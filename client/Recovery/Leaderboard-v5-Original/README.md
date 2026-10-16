# Original v5 leaderboard source snapshot

These four C++/header files and LICENSE are copied byte-for-byte from the
operator-supplied MKNitro_Menu_Character_Fix_v5/Source. Hashes are in MANIFEST.json.
They retain the original source text and notices. This is a module snapshot,
not a complete standalone v5 project or proof that all of v5 matches its binary.
The broader v5 audit is in ../CoreAudit-2026-10-16/.

The active client/PulsarEngine source is the repaired candidate. This snapshot
is excluded from its build. Do not compile both copies or replace the candidate
with these older files without reviewing their request-lifetime behavior.

The ParseResponse source body is identical in this snapshot and the candidate.
Its compiled released/source-built behavior was separately tested; see
../../docs/leaderboard-parser-followup-2026-10-16.md. Other methods differ.
