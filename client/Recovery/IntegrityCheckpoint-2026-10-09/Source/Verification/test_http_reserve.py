"""Compile actual HTTP helper/reserve sources with mocked platform heaps/locks.
Does not emulate PowerPC or certify RootScene's ABI/native allocator behavior.
"""
from pathlib import Path
import subprocess
import tempfile
import os
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    stub = r'''
#ifndef HTTP_TEST_PLATFORM
#define HTTP_TEST_PLATFORM
#include <cassert>
#include <cstdlib>
#include <map>
#include <cstdio>
typedef unsigned int u32; typedef int s32;
static bool pal=true, parentFail=false, createFail=false, nativeFail=false, normalFail=true;
static int irqState=1, locks=0, parentAllocs=0, parentFrees=0, nativeFrees=0, normalFrees=0, startups=0;
static unsigned int poolUsed=0;
static std::map<void *, unsigned int> poolBlocks;
namespace OS {
inline int DisableInterrupts() { int prev=irqState; irqState=0; ++locks; return prev; }
inline void RestoreInterrupts(int value) { assert(locks>0); --locks; irqState=value; }
inline void Report(const char *, ...) {}
}
namespace EGG {
class Heap {
public:
    void *alloc(u32 n, s32) { ++parentAllocs; return parentFail ? nullptr : std::malloc(n); }
    void free(void *p) { ++parentFrees; std::free(p); }
    static void *alloc(u32 n, s32 a, Heap *h) { if(n==256*1024) return h->alloc(n,a); return normalFail ? nullptr : std::malloc(n); }
    static void free(void *p, Heap *h) { if(createFail) { h->free(p); return; } ++normalFrees; std::free(p); }
};
}
struct RKSystem { struct System { EGG::Heap *EGGSystem; }; static System mInstance; };
RKSystem::System RKSystem::mInstance={nullptr};
inline int NHTTPStartup(void *, void *, u32) { ++startups; return 0; }
#define kmBranch(address, function)
#endif
'''
    (root/'platform.hpp').write_text(stub)
    for name in ['types.hpp', 'PulsarSystem.hpp', 'core/egg/mem/Heap.hpp',
                 'core/rvl/OS/OS.hpp', 'core/RK/RKSystem.hpp', 'core/rvl/DWC/NHTTP.hpp']:
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('#include <platform.hpp>\n')
    test = r'''
#include <platform.hpp>
namespace Pulsar { namespace Network { bool TestHTTPPAL() { return pal; } } }
extern "C" void *NitroCreateExpHeap(void *buffer, u32 n, unsigned short flags) {
    assert(!locks && irqState && n==256*1024 && flags==4);
    return createFail ? nullptr : buffer;
}
extern "C" void *NitroAllocExpHeap(void *, u32 n, s32 align) {
    assert(!locks && irqState && align>=4 && align<=32);
    if (nativeFail || poolUsed+n>256*1024) return nullptr;
    void *p=std::malloc(n); poolBlocks[p]=n; poolUsed+=n; return p;
}
extern "C" void NitroFreeExpHeap(void *, void *p) {
    assert(!locks && irqState && poolBlocks.count(p));
    poolUsed-=poolBlocks[p]; poolBlocks.erase(p); ++nativeFrees; std::free(p);
}
#include <Network/NHTTPReserve.cpp>
#include <Network/NHTTPHelper.cpp>
using namespace Pulsar::Network;
int main() {
    EGG::Heap parent, normal, replacement;
    RKSystem::mInstance.EGGSystem=&normal;
    pal=false; InitializeHTTPReserve(&parent); assert(parentAllocs==0);
    pal=true; InitializeHTTPReserve(nullptr); assert(parentAllocs==0);
    assert(!AllocateHTTPReserve(64,32));
    parentFail=true; InitializeHTTPReserve(&parent); assert(!sHTTPPool);
    parentFail=false; createFail=true; InitializeHTTPReserve(&parent);
    assert(!sHTTPPool && parentFrees==1);
    createFail=false; InitializeHTTPReserve(&parent); assert(sHTTPPool);
    int initialized=parentAllocs; InitializeHTTPReserve(&parent); assert(parentAllocs==initialized);
    assert(!AllocateHTTPReserve(0,32)); assert(!AllocateHTTPReserve(131073,32));
    assert(!AllocateHTTPReserve(64,64)); assert(!AllocateHTTPReserve(64,7));
    nativeFail=true; assert(!AllocateHTTPReserve(64,32)); nativeFail=false;
    for(int i=0;i<16;++i) assert(!sHTTPSlots[i].busy && !sHTTPSlots[i].pointer);
    void *ptrs[16]; for(int i=0;i<16;++i) { ptrs[i]=NHTTPAlloc(100,32); assert(ptrs[i]); }
    assert(!NHTTPAlloc(100,32));
    RKSystem::mInstance.EGGSystem=&replacement;
    for(int i=15;i>=0;--i) NHTTPFree(ptrs[i]);
    assert(nativeFrees==16 && normalFrees==0 && poolUsed==0);
    // Reserve survives child/normal heap exhaustion/replacement and slot reuse.
    for(int j=0;j<100;++j) { void *p=NHTTPAlloc(32864,32); assert(p); NHTTPFree(p); }
    void *a=NHTTPAlloc(131072,32), *b=NHTTPAlloc(131072,32);
    assert(a && b && !NHTTPAlloc(1,4)); NHTTPFree(a); NHTTPFree(b);
    normalFail=false; void *regular=NHTTPAlloc(100,32); assert(regular && poolUsed==0);
    NHTTPFree(regular); assert(normalFrees==1);
    normalFail=true; RKSystem::mInstance.EGGSystem=nullptr;
    void *p=NHTTPAlloc(64,4); assert(p); NHTTPFree(p);
    pal=false; assert(!NHTTPAlloc(64,32)); pal=true;
    NHTTPFree(nullptr); assert(!FreeHTTPReserve(&parent));
    assert(!locks && irqState && poolBlocks.empty());
    std::free(sHTTPPool); sHTTPPool=nullptr;
    std::puts("PASS: actual HTTP source: reserve failure/cleanup, 16-slot limit, size/alignment, exhaustion, ownership, reuse, PAL gating and unlocked native calls (mocked APIs)");
}
'''
    (root/'test.cpp').write_text(test)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror',
                    '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                    '-DMKNITRO_SERVER','-DNITRO_HTTP_HOST_TEST', '-I'+str(root),
                    '-I'+str(ROOT/'PulsarEngine'),str(root/'test.cpp'),'-o',str(root/'test')],check=True)
    subprocess.run([str(root/'test')],check=True, env={**os.environ, 'ASAN_OPTIONS':'detect_leaks=0'})
