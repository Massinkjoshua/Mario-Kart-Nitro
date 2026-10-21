#include <Network/NHTTPReserve.hpp>
#include <core/egg/mem/Heap.hpp>
#include <core/rvl/OS/OS.hpp>

// Native PAL entry points, relocated by Kamek. No fabricated EGG heap object.
extern "C" {
void *NitroCreateExpHeap(void *, u32, unsigned short);
void *NitroAllocExpHeap(void *, u32, s32);
void NitroFreeExpHeap(void *, void *);
}
namespace Pulsar { namespace Network {
static void *sHTTPPool;
struct ReserveSlot { void *pointer; bool busy; };
static ReserveSlot sHTTPSlots[16];
static const u32 HTTPReserveBytes = 256 * 1024;

static bool UseHTTPReserve() {
#ifdef MKNITRO_SERVER
#ifdef NITRO_HTTP_HOST_TEST
    extern bool TestHTTPPAL();
    return TestHTTPPAL();
#else
    return *reinterpret_cast<const volatile u32 *>(0x80000000u) == 0x524d4350u;
#endif
#else
    return false;
#endif
}
void InitializeHTTPReserve(EGG::Heap *rootMEM2) {
    // Called once before BootHook::Exec / child scenes, on the main thread.
    if (!UseHTTPReserve() || sHTTPPool || !rootMEM2) return;
    // Disambiguate the virtual overload: static EGG::alloc may substitute
    // the current thread's heap, defeating an early persistent MEM2 reserve.
    typedef void *(EGG::Heap::*RootAlloc)(u32, s32);
    const RootAlloc rootAlloc = static_cast<RootAlloc>(&EGG::Heap::alloc);
    void *buffer = (rootMEM2->*rootAlloc)(HTTPReserveBytes, 32);
    if (!buffer) {
        OS::Report("[Nitro HTTP] could not reserve 256 KiB MEM2\n");
        return;
    }
    sHTTPPool = NitroCreateExpHeap(buffer, HTTPReserveBytes, 4);
    if (!sHTTPPool) {
        typedef void (EGG::Heap::*RootFree)(void *);
        const RootFree rootFree = static_cast<RootFree>(&EGG::Heap::free);
        (rootMEM2->*rootFree)(buffer);
        OS::Report("[Nitro HTTP] reserved heap creation failed\n");
    }
}
void *AllocateHTTPReserve(u32 size, s32 alignment) {
    if (!UseHTTPReserve() || !sHTTPPool || !size || size > 128 * 1024 || alignment > 32)
        return nullptr;
    if (alignment < 4) alignment = 4;
    if ((alignment & (alignment - 1)) != 0) return nullptr;
    int slot = -1;
    int irq = OS::DisableInterrupts();
    for (int i = 0; i < 16; ++i) {
        if (!sHTTPSlots[i].busy && !sHTTPSlots[i].pointer) {
            sHTTPSlots[i].busy = true;
            slot = i;
            break;
        }
    }
    OS::RestoreInterrupts(irq);
    if (slot < 0) return nullptr;
    // Native heap uses its thread-safe flag; do not hold interrupts across it.
    void *result = NitroAllocExpHeap(sHTTPPool, size, alignment);
    irq = OS::DisableInterrupts();
    sHTTPSlots[slot].pointer = result;
    sHTTPSlots[slot].busy = false;
    OS::RestoreInterrupts(irq);
    return result;
}
bool FreeHTTPReserve(void *ptr) {
    if (!ptr) return true;
    int slot = -1;
    int irq = OS::DisableInterrupts();
    for (int i = 0; i < 16; ++i) {
        if (sHTTPSlots[i].pointer == ptr) {
            if (sHTTPSlots[i].busy) {
                OS::RestoreInterrupts(irq);
                return true;
            }
            sHTTPSlots[i].busy = true;
            slot = i;
            break;
        }
    }
    OS::RestoreInterrupts(irq);
    if (slot < 0) return false;
    NitroFreeExpHeap(sHTTPPool, ptr);
    irq = OS::DisableInterrupts();
    sHTTPSlots[slot].pointer = nullptr;
    sHTTPSlots[slot].busy = false;
    OS::RestoreInterrupts(irq);
    return true;
}
} }
