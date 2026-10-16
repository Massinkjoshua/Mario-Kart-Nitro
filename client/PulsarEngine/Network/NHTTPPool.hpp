// Integrated recovered October checkpoint on 2026-10-16; see docs/recovery-provenance.json.
#ifndef _PUL_NHTTP_POOL_
#define _PUL_NHTTP_POOL_
#include <types.hpp>
namespace EGG { class Heap; }
namespace Pulsar { namespace Network {
// Called with RootScene's persistent MEM2 heap, before the first BootHook.
void InitNHTTPPool(EGG::Heap *rootMEM2);
void *AllocNHTTPFallback(u32 size, s32 align);
bool FreeNHTTPFallback(void *ptr);
const wchar_t *GetNHTTPAllocationError();
void ClearNHTTPAllocationError();
} }
#endif
