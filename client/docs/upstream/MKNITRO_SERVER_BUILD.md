# MKNITRO server client build

This source is configured for `play.mknitro.com` with the public key provided by the server owner. The private signing key is not included.

Use the Wii CodeWarrior tools `mwcceppc.exe`, `mwasmeppc.exe`, and `Kamek.exe` as documented in MKNITRO_README.md. The included `.env` selects the MKNITRO_SERVER branch. Set compiler paths in the Makefile or prepend `CC=...`, `AS=...`, `KAMEK=...` assignments to `.env` as necessary; then run `make`. Its output is `build/Code.pul`. Copy that file into your pack's `Binaries/Code.pul` after backing up the existing one.

The included `CurrentPack/Binaries/Code.pul` is the original uploaded binary and is not rebuilt. Do not install it expecting it to use the new key or domain.

The loader requests `http://nas.play.mknitro.com/payload`, so configure an A record for `nas.play.mknitro.com` pointing to the same VPS and allow TCP port 80. The server payloads and its private key were prepared separately on the VPS.
