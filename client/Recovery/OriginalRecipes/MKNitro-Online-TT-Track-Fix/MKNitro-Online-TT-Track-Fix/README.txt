MARIO KART NITRO — ONLINE TIME TRIALS TRACK FIX (PAL)

What changed
Online Time Trials region 0x0B was explicitly restricted to vanilla courses.
This build clears that track restriction, restores the custom cup list, and
uses the existing Nitro VS cup navigation/random-selection helper for OTT.
OTT physics/rules retain their existing behavior.

Based on the working Leaderboard-Mii-Fix Code.pul. The leaderboard, Mii guards,
MEM2 HTTP pool, server addresses, and all existing relocation commands are
preserved. Only three PAL instructions are redirected, with 120 bytes appended.
NTSC-U/J blocks are unchanged; this fix is PAL only.

INSTALL — one player test before launcher distribution
1. Fully close Dolphin.
2. Back up MarioKartNitro_Test/Binaries/Code.pul, then replace it with
   Game/Code.pul from this ZIP. Keep your Loader.pul, XML, configs, tracks,
   and save data. Start normally, not from a savestate.
3. Upload and extract this ZIP to /root on the Hetzner server.
4. Register the new code hash:
   python3 /root/MKNitro-Online-TT-Track-Fix/Server/register-build.py --config /opt/mknitro/config.xml
   No game-server restart or database reset is needed.
5. Reopen Online Time Trials. Confirm Nitro cups/names appear, cycle all
   24 cups, then select and load a custom course. Also reopen the leaderboard.

The approval replaces PAL's accepted hash for pack 10/version 6124. Clients
still using the previous Code.pul may get Invalid pack version after step 4.
Update every player to the same tested code. Do not mix old/new clients.
This code supersedes the Code.pul in the earlier launcher handoff; update the
launcher payload/checksum after the in-game test succeeds.

ROLLBACK
Close Dolphin; restore Game/Code-previous.pul as your installed Code.pul.
Run on the server:
   python3 /root/MKNitro-Online-TT-Track-Fix/Server/register-build.py --config /opt/mknitro/config.xml --manifest /root/MKNitro-Online-TT-Track-Fix/Server/restore-build.json

VERIFICATION
1052 checks executed actual PowerPC instructions with Unicorn at two load
addresses: vanilla-before/custom-after OTT cup selection, all 24 Nitro cups
and wraparound matching Nitro VS, unchanged other modes and physics predicate,
restriction bit behavior, and exact preservation of non-PAL/leaderboard bytes.
No live Dolphin/console race has been tested with this new build yet.
Verification/build.py reproduces the binary using the included previous code.
Verification/test.py requires Python packages capstone and unicorn.

SOURCE NOTE
Source/online-tt-track-selection.patch records the equivalent source changes
against the available source snapshot. The distributed Code.pul is a targeted
binary patch of the working build, not a full recompilation of that snapshot;
this preserves additional fixes already compiled into the working code.

HASHES
Full Code.pul SHA256: 0f542baa4328bb75d75f5e05fcec2348ccb0817c1ff2107cfa3f6af2eab1cd68
PAL code SHA1: 04ebc587a52dcb20a9fdab473fc39ca38b8625cd
