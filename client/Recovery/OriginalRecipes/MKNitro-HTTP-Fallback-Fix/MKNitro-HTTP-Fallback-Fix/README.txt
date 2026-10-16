MKNitro PAL HTTP fallback test

INSTALL
1. Close Dolphin completely.
2. Restore the original XML using Install/MarioKartNitro.xml. Replace your
   active Nitro XML using the same filename as your existing launch preset.
   This is the original XML you uploaded, WITHOUT the heap-size increase.
3. Replace the pack's Binaries/Code.pul with Game/Code.pul from this ZIP.
   Keep the existing Loader.pul.
4. Run these commands separately in Windows PowerShell:

scp "$env:USERPROFILE\Downloads\MKNitro-HTTP-Fallback-Fix.zip" root@2.28.230.188:/root/
ssh root@2.28.230.188 "unzip /root/MKNitro-HTTP-Fallback-Fix.zip -d /root"
ssh root@2.28.230.188 "python3 /root/MKNitro-HTTP-Fallback-Fix/Server/register-build.py --config /opt/mknitro/config.xml"

5. Launch Dolphin, connect online and open the leaderboard. If it loads,
   leave and reopen it, check another page and then test a short race.
   Report the exact result or error screenshot.

The hash registration changes PAL pack 10/version 6124 to this Code.pul.
Other PAL clients need the same approved Code.pul while this is registered.
It does not reset ratings or change the database. No server restart needed.

WHAT THE NEW LOG REVEALED
With the working original XML, the StaticR section table was at 0x8051032c.
With the heap-increase XML, it moved to 0x8059032c, exactly 0x80000 later.
Nitro's absolute game patches expect the original module address range.
That invalidates the heap-increase approach for this pack. This package
restores the original XML and therefore its original memory layout.

HTTP CHANGE
The normal HTTP allocation path is tried first, exactly as in Static-Fix.
Only if that allocation fails, a bounded fallback allocates directly from
EGGRootMEM2. The heap's virtual allocator is used, avoiding the generic
EGG::Heap::alloc path that may substitute the current thread's heap.
Each fallback allocation records its pointer and owning heap. Freeing it
uses that heap's virtual free function; normal allocations keep their
original free path. This is not the earlier unconditional MEM2 switch.

Tracking supports 16 simultaneous fallback allocations, each up to 128 KiB,
with alignment up to 32. Slot reservation and release preserve interrupt
state. Full tracking, unavailable heap, or failed allocation returns null.
The native library's memory and URL creation errors have distinct labels.

The PAL module grows by 960 bytes, not a large embedded reserve. HTTP
startup logic is unchanged. The leaderboard's existing static 16 KiB
response buffer is retained. Non-PAL payloads are byte-for-byte unchanged.

VALIDATION AND LIMITS
724 checks ran the user-supplied PAL game's native MEM2 heap creation,
allocation/free, NHTTP context/request creation, URL parsing and snprintf.
They include the actual logged mod load address, normal-heap failure,
heap/tracking exhaustion, failed-request cleanup, random memory lifetimes,
register preservation and interrupt-state restoration.
The native request path reaches SendAsync when the normal heap refuses
allocations. OS scheduling/locks and actual network sending are simulated;
a live Dolphin/network test is still required. This is not a verified
production release. The prior shared-heap ownership problem is a risk
identified in the native allocator, not a proven cause of error 20100.

Verification/test.py can reproduce the checks with the provided original
Code-previous.pul and your main.dol (not distributed here). See results.txt.

ROLLBACK
Close Dolphin. Keep the original XML installed. Replace the pack Code.pul
with Game/Code-previous.pul, renaming it to Code.pul. In PowerShell run:

ssh root@2.28.230.188 "python3 /root/MKNitro-HTTP-Fallback-Fix/Server/register-build.py --config /opt/mknitro/config.xml --manifest /root/MKNitro-HTTP-Fallback-Fix/Server/restore-build.json"

This returns to the working Static-Fix build and its approval. That build
connects online but still displays Failed: create on the leaderboard.
