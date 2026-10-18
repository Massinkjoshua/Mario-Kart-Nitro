// Integrated recovered October checkpoint on 2026-10-16; see docs/recovery-provenance.json.
#include <Network/NHTTPPool.hpp>
#include <core/egg/mem/Heap.hpp>
#include <core/rvl/MEM/MEMexpHeap.hpp>
#include <core/rvl/OS/OS.hpp>

namespace Pulsar { namespace Network {
static const u32 kPoolBytes = 0x40000;
static const u32 kMaxFallbackBytes = 0x20000;
static const u32 kTrackingSlots = 16;
struct FallbackSlot { void *ptr; MEM::HeapHandle heap; };
static FallbackSlot s_slots[kTrackingSlots];
static MEM::HeapHandle s_pool = nullptr;
static u32 s_failure = 0;
static u32 s_failureBytes = 0;

void InitNHTTPPool(EGG::Heap *rootMEM2) {
    if (s_pool != nullptr || rootMEM2 == nullptr) return;
    // Call the supplied heap directly: EGG's static allocator can substitute
    // the current thread's heap, which is too late/small on leaderboard entry.
    void *(EGG::Heap::*allocate)(u32, s32) = &EGG::Heap::alloc;
    void *storage = (rootMEM2->*allocate)(kPoolBytes, 32);
    if (storage == nullptr) return;
    s_pool = MEM::CreateExpHeapEx(storage, kPoolBytes, 4); // native mutex support
    if (s_pool == nullptr) {
        void (EGG::Heap::*release)(void *) = &EGG::Heap::free;
        (rootMEM2->*release)(storage);
    }
}

u32 GetReleasedNHTTPFailureKind() { return s_failure; }
u32 GetReleasedNHTTPFailureBytes() { return s_failureBytes; }

void ClearNHTTPAllocationError() { s_failure = 0; s_failureBytes = 0; }
const wchar_t *GetNHTTPAllocationError() {
    switch (s_failure) {
    case 1: return L"Mem: size or align";
    case 2: return L"Mem: tracking full";
    case 3: return L"Mem: pool missing";
    case 4: return s_failureBytes == 32864 ? L"Mem: pool full 32K" : L"Mem: pool full";
    default: return L"Mem: other allocator";
    }
}

void *AllocNHTTPFallback(u32 size, s32 align) {
    u32 failure = 1;
    void *ptr = nullptr;
    FallbackSlot *slot = nullptr;
    if (size != 0 && size <= kMaxFallbackBytes && align <= 32) {
        if (align < 4) align = 4;
        failure = 2;
        s32 interrupts = OS::DisableInterrupts();
        for (u32 i = 0; i < kTrackingSlots; ++i) {
            if (s_slots[i].ptr == nullptr) {
                slot = &s_slots[i];
                slot->ptr = reinterpret_cast<void *>(-1);
                break;
            }
        }
        OS::RestoreInterrupts(interrupts);
        if (slot != nullptr) {
            failure = s_pool == nullptr ? 3 : 4;
            if (s_pool != nullptr) ptr = MEM::AllocFromExpHeapEx(s_pool, size, align);
            interrupts = OS::DisableInterrupts();
            slot->heap = s_pool;
            if (ptr == nullptr) slot->heap = nullptr;
            slot->ptr = ptr;
            OS::RestoreInterrupts(interrupts);
        }
    }
    if (ptr == nullptr) { s_failure = failure; s_failureBytes = size; }
    return ptr;
}

bool FreeNHTTPFallback(void *ptr) {
    if (ptr == nullptr) return true;
    FallbackSlot *slot = nullptr;
    MEM::HeapHandle heap = nullptr;
    s32 interrupts = OS::DisableInterrupts();
    for (u32 i = 0; i < kTrackingSlots; ++i) {
        if (s_slots[i].ptr == ptr) {
            slot = &s_slots[i];
            heap = slot->heap;
            slot->ptr = reinterpret_cast<void *>(-1);
            break;
        }
    }
    OS::RestoreInterrupts(interrupts);
    if (slot == nullptr) return false;
    MEM::FreeToExpHeap(heap, ptr);
    interrupts = OS::DisableInterrupts();
    slot->heap = nullptr;
    slot->ptr = nullptr;
    OS::RestoreInterrupts(interrupts);
    return true;
}
} }
