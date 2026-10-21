MKNitro PAL MEM2 Pool Fix — live test required

Your Memory Trace build reported Mem: MEM2 full (32K). The ordinary heap and
root MEM2 fallback could not supply the 32,864-byte native HTTP request.
Native scene creation allocates the parent's remaining capacity into child
heaps, which explains why trying the top-level parent during gameplay fails.

This build reserves 256 KiB inside the persistent RootScene MEM2 heap during
RootScene entry, before the original mod boot hooks and before menu scenes.
A native expanded heap with the thread-safe flag manages this buffer.
Normal HTTP allocation is tried first; failures use this reserved pool.
Fallback allocations retain their owner and are freed into that same pool.
The pool stays allocated across menu/race child scene replacement.

INSTALL
1. Close Dolphin completely. Extract this ZIP.
2. Copy Game/Code.pul over your pack's MarioKartNitro_Test/Binaries/Code.pul.
   Keep your current working XML and Loader.pul.
3. Save the ZIP in your Windows Downloads folder. Run each command separately
   in Windows PowerShell:

scp "$env:USERPROFILE\Downloads\MKNitro-MEM2-Pool-Fix.zip" root@2.28.230.188:/root/
ssh root@2.28.230.188 "unzip /root/MKNitro-MEM2-Pool-Fix.zip -d /root"
ssh root@2.28.230.188 "python3 /root/MKNitro-MEM2-Pool-Fix/Server/register-build.py --config /opt/mknitro/config.xml"

4. After registration succeeds, launch normally (do not load a save state).
   Connect online and open the leaderboard. Send the result or exact error.
   If the page loads, close/reopen it and try the next page. Then test a race,
   return to the lobby and check whether VR remains updated.

Registration approves this PAL Code.pul for pack 10/version 6124. Other PAL
clients on that pack/version need the matching code while it is approved.
No database reset, server restart, XML edit, or Loader replacement is required.

VALIDATION
961 checks execute native PAL MEM heap creation, allocation/free, request
creation and parsing in PowerPC emulation. Crucially, the pool is initialized,
then the parent heap is exhausted: the new request still reaches SendAsync.
Tests cover the boot wrapper and original hook chain, callee-saved registers,
repeated initialization, parent OOM, heap creation failure cleanup, tracking
limits, mixed lifetimes, and repeated request cleanup/child replacement.
Non-PAL blocks are byte-identical. HTTP startup behavior is unchanged.

The module adds 296 bytes over Memory Trace. The 256 KiB buffer comes from
MEM2 at runtime, not from a large embedded code buffer. The system heap size
and XML remain unchanged. Existing tracking supports 16 live fallback
allocations. OS scheduling/locks and actual network send are simulated in
tests; full live game behavior is not verified. The pool reduces memory
available to scene content by 256 KiB. Other failures may remain after HTTP
request creation, including responses, parsing or VR persistence.

FAILURE LABELS
Mem: pool missing — the startup pool was not created.
Mem: pool full 32K — the reserved pool could not supply the native request.
Mem: pool full — another request allocation exhausted the pool.
Mem: tracking full — all 16 fallback tracking slots were occupied.
Mem: other allocator — native memory error without our allocator recording
  a failure during that request; callback ownership needs inspection.
Other existing diagnostics remain available. Send a screenshot of any error.

ROLLBACK TO MEMORY TRACE
Close Dolphin. Copy Game/Code-previous.pul to the pack's Binaries folder,
renaming it Code.pul. Restore the matching server approval:

ssh root@2.28.230.188 "python3 /root/MKNitro-MEM2-Pool-Fix/Server/register-build.py --config /opt/mknitro/config.xml --manifest /root/MKNitro-MEM2-Pool-Fix/Server/restore-build.json"

This restores the build that boots/connects but reports MEM2 full (32K).

REPRODUCE
From this package folder, with Python, capstone and unicorn installed:
python3 Verification/build.py Verification/Code-static-base.pul Game/Code.pul
python3 Verification/test.py Verification/Code-static-base.pul Game/Code.pul PATH_TO_YOUR_MAIN_DOL
The user's main.dol is required but not redistributed. Results are included.
