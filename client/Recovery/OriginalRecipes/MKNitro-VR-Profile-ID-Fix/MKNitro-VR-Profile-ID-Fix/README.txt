Mario Kart Nitro — PAL VR profile ID fix

Problem
RatingSave rejects IDs >= 1,000,000,000 as reserved. NitroWFC assigns IDs
starting at that range, including HumbleKing 1000000002. A race can therefore
show a result change without saving the profile or sending wl:mkw_vrbr.
The older profile 603318948 is below the limit and remains usable.

Change
Raise the PAL reserved ID boundary to 2,000,000,000, matching the source's
existing TEST boundary. IDs 1 through 1,999,999,999 can save ratings.
Only three bytes in two PPC instructions change. All other uploaded Code(9)
bytes, relocations, other region blocks, and prior fixes are preserved.
US/Japan retain their existing profile-ID limit; this repair is PAL only.
This does not repair or confirm the separate Mii data issue.

Install game
Stop Dolphin completely. Back up your current Binaries/Code.pul.
Copy Game/Code.pul to MarioKartNitro_Test/Binaries/Code.pul.
Start fresh without a save state. Use the new file on both PAL test clients.

Approve game on server
The file has a new PAL code hash. Upload this ZIP to /root on your VPS,
extract it, then run:
python3 /root/MKNitro-VR-Profile-ID-Fix/Server/register-build.py --config /opt/mknitro/config.xml
The script backs up current approvals and registers the manifest through the
local admin API. It preserves enforcement. No server executable update or
service restart is required.

Test
Reconnect to Nitro VS. Complete a race with another player.
Confirm VR remains in the next lobby and after disconnect/reconnect.
Inspect journal for "Nitro ratings saved:" and check website leaderboard.
Native predicate, license ID resolution and profile allocation are emulated
in test.py. Filesystem/network execution and a live race remain untested.

Rollback
Restore Game/Code-previous.pul as your client Code.pul and run the registration
script with --manifest /root/MKNitro-VR-Profile-ID-Fix/Server/restore-build.json.
The entire server/player database is unchanged by this client patch.
