# Mario Kart Nitro patcher source — altered upstream version

Online communications credit to WiiLink WFC - https://wfc.wiilink24.com

Derived from Retro Rewind Team's wfc-patcher-wii, itself derived from WiiLink WFC.
Upstream: https://github.com/Retro-Rewind-Team/wfc-patcher-wii
Base commit: 9ee5c2dfdcbe97408786184566ab50c9bee0d1eb

This is an altered Mario Kart Nitro version, not an original or endorsed
Retro Rewind/WiiLink release. Original LICENSE and per-file notices remain intact.
Compared with that upstream commit, only the public verification key header,
payload/mkwFeature.cpp (Welcome to Nitrowfc), and include/wwfcTypes.h
(default domain play.mknitro.com) differ. All other exported tracked files
match upstream Git blob hashes. The upstream test private-key-DEFAULT.pem is
intentionally omitted. Production signing keys are not included.

The custom attribution licence is retained verbatim in Live-2026-10-16/LICENSE.
The upstream README also describes its alternative GPL-2.0-or-later option.
SHA-256 and RSA implementation notices remain in stage1/wwfcStage1.cpp.
