Mario Kart Nitro — leaderboard Mii fix (PAL), corrected installer/server

The leaderboard now loads, but its API did not include the miiData records
expected by the game. Missing/invalid records could display the local Mii.
This package adds each profile's Mii to the API and hides missing/invalid icons.
It keeps the working MEM2-Pool-Fix intact.

INSTALL
This requires BOTH the server and game changes. The server restart briefly
disconnects online players. The installer backs up the current executable,
config and PostgreSQL database before stopping mknitro.service. It preserves
ratings/accounts and restores the previous executable if its health check fails.

1. Close Dolphin. Download this ZIP to Windows Downloads and extract it.
2. Copy Game/Code.pul over MarioKartNitro_Test/Binaries/Code.pul in your pack.
   Keep your current XML and Loader.pul.
3. In Windows PowerShell, run these commands separately:

scp "$env:USERPROFILE\Downloads\MKNitro-Leaderboard-Mii-Fix.zip" root@2.28.230.188:/root/
ssh root@2.28.230.188 "unzip -o /root/MKNitro-Leaderboard-Mii-Fix.zip -d /root"
ssh root@2.28.230.188 "python3 /root/MKNitro-Leaderboard-Mii-Fix/Server/install.py"

The final command installs the server, checks the leaderboard and registers
this matching PAL build for pack 10/version 6124. All PAL clients on that
pack/version need the approved code. It prints how many rows on the first
leaderboard page have stored Mii data. Do not launch until installation succeeds.

4. Start Dolphin fresh without loading a save state. Open the leaderboard.
   Check different portraits, then change page and return. Send a screenshot.
5. Players whose Mii is not stored yet need to reconnect and join a room.
   Wait about 15 seconds, then close/reopen the leaderboard. Their client must
   send Mii data before the server can show it; a friend code alone is not enough.

WHAT CHANGES
Server: each profile uses its persisted room Mii, falling back to its existing
stored license/FriendInfo Mii. Authenticated room snapshots save fresh Miis.
A new mii_data column is additive; empty room data preserves the last good value.
The response converts padded or raw base64 into a complete 76-byte RFL record,
removes birthday/creator/console metadata, assigns a stable profile-specific
rendering ID and recomputes the checksum. Face appearance and Mii name remain.
This does not substitute another player's Mii or invent missing license data.

The in-game response omits unused per-row profile IDs/timestamps and limits
fallback names to 10 Unicode characters so 50 portraits fit the existing
16 KiB buffer. The website endpoint retains its existing fields, plus miiData.

Game: native RFL validation gates Mii loading, pane binding and visibility.
Missing/corrupt Miis remain blank. The next valid row restores visibility.
Only PAL changes. Existing memory allocation/HTTP fixes are preserved byte
for byte; the small UI patch grows the PAL module by 172 bytes.

VALIDATION/LIMITS
See Verification/results.txt. Tests use two distinct synthetic names with
valid Wii Mii data through the actual PAL parser and native RFL validation.
Actual portrait rendering and live server behavior still need your test.
This package does not alter ratings, save paths, game assets or live-room web UI.

ROLLBACK
Close Dolphin. Copy Game/Code-previous.pul over Binaries/Code.pul, renaming it
Code.pul. In Windows PowerShell:

ssh root@2.28.230.188 "python3 /root/MKNitro-Leaderboard-Mii-Fix/Server/install.py --rollback"

This restores the executable saved by this installer and the working MEM2-Pool
client approval. The harmless added Mii column stays; ratings are not restored
from an old backup. The database dump is retained privately on the VPS for
recovery if needed. If installation failed before stopping the service, the
old server remains active; the installer prints the failure.

REPRODUCE
Server source: Source/server. Build with Go 1.25.5 or compatible:
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -buildvcs=false -trimpath -ldflags '-s -w' -o wwfc .
Game patch (Python + capstone):
python3 Verification/build.py Game/Code-previous.pul Game/Code.pul
Game tests (also require unicorn and your own main.dol):
python3 Verification/test.py Game/Code-previous.pul Game/Code.pul PATH_TO_MAIN_DOL
PostgreSQL tests: Source/server/verification/ratings-sql.mjs (requires PGlite).
Installer tests: python3 Verification/test_installer.py (no live service changes).

CORRECTION AFTER THE FIRST INSTALLATION ATTEMPT
The first installer checked the RPC port instead of the configured NAS HTTP
port. Its health check now reads nasPort from config.xml and bypasses proxies.
The in-game response type is now registered consistently with the HTTP router,
including its error field and conversion on both success/error paths.
Tests run through the real HTTP dispatcher and an actual local HTTP listener
on a randomly selected configured port. Both passed. These corrections affect
only the installer/server. Game/Code.pul is unchanged from the Mii-fix package.
Let an earlier installer command finish before rerunning the corrected one.
If your game already has this Mii-fix Code.pul, keep it. Download this updated
ZIP again, replace the old download, upload it and use unzip -o as shown above.
