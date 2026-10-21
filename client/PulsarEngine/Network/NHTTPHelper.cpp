// Integrated recovered October checkpoint on 2026-10-16; see docs/recovery-provenance.json.
#include <PulsarSystem.hpp>
#include <Network/NHTTPHelper.hpp>
#include <Network/NHTTPPool.hpp>
#include <core/RK/RKSystem.hpp>
#include <core/egg/mem/Heap.hpp>
#include <core/rvl/DWC/NHTTP.hpp>

namespace Pulsar {
namespace Network {

static u32 s_activeRequestCount = 0;

void *NHTTPAlloc(u32 size, s32 align) {
    EGG::Heap *heap = RKSystem::mInstance.EGGSystem;
    if (align < 4) align = 4;
    void *ptr = heap == nullptr ? nullptr : EGG::Heap::alloc(size, align, heap);
    return ptr != nullptr ? ptr : AllocNHTTPFallback(size, align);
}

void NHTTPFree(void *ptr) {
    if (FreeNHTTPFallback(ptr)) return;
    EGG::Heap *heap = RKSystem::mInstance.EGGSystem;
    if (heap != nullptr) EGG::Heap::free(ptr, heap);
}
kmBranch(0x800ed69c, NHTTPAlloc);
kmBranch(0x800ed6b4, NHTTPFree);

bool PrepareNHTTPRequest() {
    if (s_activeRequestCount != 0) return true;

    const s32 startupRet = NHTTPStartup(reinterpret_cast<void *>(&NHTTPAlloc),
                                        reinterpret_cast<void *>(&NHTTPFree),
                                        0x11);
    if (startupRet < 0) return false;

    return true;
}

bool PreparePersistentNHTTPRequest(bool &started) {
    if (started) return true;
    if (!PrepareNHTTPRequest()) return false;
    started = true;
    return true;
}

void MarkNHTTPRequestActive() {
    ++s_activeRequestCount;
}

void FinishNHTTPRequest() {
    if (s_activeRequestCount != 0) --s_activeRequestCount;
}

}  // namespace Network
}  // namespace Pulsar
