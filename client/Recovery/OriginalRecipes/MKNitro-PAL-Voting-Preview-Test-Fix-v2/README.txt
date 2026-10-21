Mario Kart Nitro — PAL voting-preview crash test fix v2

Install: stop Dolphin, back up Code.pul, and replace the active
MarioKartNitro_Test/Binaries/Code.pul with Binaries/Code.pul from this ZIP.
Start without a save state. Keep the latest Race.szs item-flash fix.

The supplied log ends in an EGG heap assertion while
MenuDriverModelMgr::PrepareDriverOnKartAnms creates a controller from the
custom voting-message-box pose setup during MenuUpdate. This build moves
that pose setup to the existing pre-CalcMain model-reload phase, reuses an
already prepared riding controller, and uses the existing heap-unlock routine
before creating a missing controller.

The previous selected-vehicle field/state corrections and PAL VR/BR sender
fix remain included. US/Japan blocks are unchanged. No save data is edited.

Tests: 16 helper execution scenarios cover four HUD slots, two load bases,
missing/existing controllers, repeated entry without extra allocation,
deferred-call order and stack restoration. Allocation/rendering dependencies
were mocked; this is not live Dolphin verification.

Test: character -> vehicle -> online Check Members -> courses -> race ->
return to courses. Check both the pose and whether the heap crash is gone.

VR: the screenshot shows remote Stuart at 500000 and local HumbleKing at 5000.
The room average is also inflated. The remote client's build/region is still
unconfirmed. Both PAL clients should install this sender fix and reconnect;
it does not normalize incoming values from older clients or patch US/Japan.
If it persists with both clients updated, send both installed Code.pul files.

This is a targeted test build, not a confirmed release fix. Restore the backup
if a new regression appears. The prior public release should remain a draft.
