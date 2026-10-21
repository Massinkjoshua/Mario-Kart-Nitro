# Reviewed live server inputs — 16 October 2026

These four files supplement ../Live-Export-2026-10-16; the original verified
Go snapshot is unchanged. All uploaded manifest sizes/hashes were verified.
The game list and both Lua sources exactly match the recorded upstream Git
blob hashes. Original AGPLv3 licence and attribution apply; see ../LICENSE.
The multiplier file records the operator's current 2x setting.

For a separate working copy of the server, copy the contents of this directory's
`server/` subtree into that working copy. Do not copy these into production as
part of source review. The existing live code reads multiplier.txt from the
absolute path /opt/mknitro-rwfc/multiplier.txt, not its working directory; the
`multiplier/` copy documents that external input. No installation is performed.

The collector did not find motd.txt, profanity.txt or multiplierBeta.txt.
The beta multiplier falls back to 1x; the Go code handles other missing files
through its existing error paths. We have not invented production replacements.

The Lua generator fetches a live Google spreadsheet and overwrites
`gpcm/error_messages.go`. Do not run it to reproduce the verified binary: use
the generated Go file already preserved in the live export. Historical sheet
input and whether any local preferred translation source exists remain open.

See VERIFICATION.json, PUBLIC_INPUT_MANIFEST.json and ../docs/runtime-inputs.md.
Private configuration, signing keys and player/database state are excluded.
