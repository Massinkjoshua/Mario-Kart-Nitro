MKNitro PAL leaderboard HTTP reserve fix - test build

INSTALL
1. Fully close Dolphin. Replace the Code.pul in your Nitro pack with
   Game/Code.pul from this ZIP. Keep the filename Code.pul.
   Do not replace main.dol or StaticR.rel.
2. In Windows PowerShell, run these lines separately:

scp "$env:USERPROFILE\Downloads\MKNitro-Leaderboard-Reserve-Fix.zip" root@2.28.230.188:/root/
ssh root@2.28.230.188 "unzip /root/MKNitro-Leaderboard-Reserve-Fix.zip -d /root"
ssh root@2.28.230.188 "python3 /root/MKNitro-Leaderboard-Reserve-Fix/Server/register-build.py --config /opt/mknitro/config.xml"

3. Launch Dolphin again, connect online, open the leaderboard, leave it,
   reopen it, and check another page. Send a screenshot if an error remains.

The server command registers this Code.pul's PAL hash. It does not restart
services, change ratings, or reset the database. Other PAL players will
need this approved Code.pul while it is registered. Do not distribute as
confirmed working until the live test succeeds.

WHAT CHANGED
The uploaded PAL main.dol shows that native NHTTPCreateRequest first needs
an internal 32,864-byte allocation, separate from the response buffer.
Emulating the original game instructions reproduces Failed: create when
that allocation is refused, with native error 1 (allocation failure).
The generated leaderboard URL is valid and native creation succeeds with
adequate memory. This supports memory exhaustion as the cause, but the
previous game screen alone did not expose the native error code.

This build keeps the normal EGGSystem HTTP allocation path first. If it
fails, an interrupt-protected 512 KiB reserve in the mod supplies memory.
Reserve allocations are freed back to that reserve. Normal allocations
still use the original free path. It does not switch the HTTP heap to MEM2.
The leaderboard keeps its static 16 KiB response buffer.

The mod's HTTP startup helper now checks the native initialization flag,
which main.dol sets during startup and clears during cleanup. An already
initialized library is reused instead of allocating another worker stack
and resetting its request lists. A fresh startup's return value is retained.

Creation errors now distinguish Create: memory and Create: URL when the
native library supplies those errors. Other existing stage messages remain.
Only the PAL region was changed; the other regional payloads are identical.

VALIDATION
See Verification/results.txt and Source/findings.txt. The test runs the
uploaded game's native context initialization, request creation and URL
parser, plus native snprintf and the patched PowerPC functions. OS locks,
EGG heap availability, fresh startup, and network sending are simulated.
This verifies the local creation path, not a live HTTP transaction or
Dolphin compatibility. main.dol is not included in this ZIP.

ROLL BACK TO THE PREVIOUS STATIC-FIX BUILD
Close Dolphin. Copy Game/Code-previous.pul into your pack as Code.pul.
Then run in Windows PowerShell:

ssh root@2.28.230.188 "python3 /root/MKNitro-Leaderboard-Reserve-Fix/Server/register-build.py --config /opt/mknitro/config.xml --manifest /root/MKNitro-Leaderboard-Reserve-Fix/Server/restore-build.json"

This rollback restores the exact previous Static-Fix approval, which could
connect online but still displayed Failed: create. No server restart needed.
