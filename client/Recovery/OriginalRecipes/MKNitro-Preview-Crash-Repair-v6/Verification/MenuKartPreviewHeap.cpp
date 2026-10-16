// Source equivalent of the v6 crash-repair delta. Add to the existing project
// when rebuilding it. This is not a complete replacement for the v5 UI hooks.
// Addresses below are PAL. The distributed Code.pul changes PAL only.
#include <kamek.hpp>

// ArchiveMgr::InitAllkartArchivesLoaders reserves one heap per local player.
// These heaps hold both the decompressed allkart archive and runtime models.
// fk-7's 897952-byte archive starves the original 0xE1000-byte heap: the native
// 800-byte ScnMdl allocation fails, then SetPriorityDrawOpa writes through null.
// 0x121000 adds 256 KiB per local player while retaining native heap ownership
// and cleanup. The following addi r3,r26,0x1000 instruction remains unchanged.
kmWrite32(0x80542310, 0x3F400012); // lis r26,0x12 (was lis r26,0x0e)
