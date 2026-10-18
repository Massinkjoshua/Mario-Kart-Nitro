#ifndef _PUL_NHTTP_RESERVE_
#define _PUL_NHTTP_RESERVE_
#include <types.hpp>
namespace EGG { class Heap; }
namespace Pulsar { namespace Network {
void InitializeHTTPReserve(EGG::Heap *rootMEM2);
void *AllocateHTTPReserve(u32 size, s32 alignment);
// True means owned/handled by this reserve; never pass that pointer to EGG.
bool FreeHTTPReserve(void *ptr);
} }
#endif
