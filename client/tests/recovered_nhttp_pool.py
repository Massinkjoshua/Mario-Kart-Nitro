#!/usr/bin/env python3
"""Compile the real pool implementation against a controlled native-heap adapter."""
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[1]
source=(root/'PulsarEngine/Network/NHTTPPool.cpp').read_text()
source='\n'.join(x for x in source.splitlines() if not x.startswith('#include'))
stubs=r'''
#include <cassert>
#include <cstdlib>
#include <cwchar>
typedef unsigned int u32; typedef int s32;
static bool interruptsEnabled=true;
static bool failCreate=false,failAlloc=false;
static int rootAllocs=0,rootFrees=0,expAllocs=0,expFrees=0;
namespace EGG { class Heap { public:
 virtual void *alloc(u32 n,s32 a) { ++rootAllocs; assert(n==0x40000 && a==32); return malloc(n); }
 virtual void free(void *p) { ++rootFrees; ::free(p); }
}; }
namespace OS {
s32 DisableInterrupts() { int previous=interruptsEnabled;interruptsEnabled=false;return previous; }
void RestoreInterrupts(s32 p) {interruptsEnabled=p;}
}
namespace MEM {
struct iHeapHead {}; typedef iHeapHead *HeapHandle;
HeapHandle CreateExpHeapEx(void *p,u32 n,unsigned short flags) {
 assert(n==0x40000 && flags==4);return failCreate?nullptr:static_cast<HeapHandle>(p);
}
void *AllocFromExpHeapEx(HeapHandle h,u32 n,s32 a) {
 assert(interruptsEnabled && h && a>=4 && a<=32);++expAllocs;
 return failAlloc?nullptr:malloc(n);
}
void FreeToExpHeap(HeapHandle h,void *p) {
 assert(interruptsEnabled && h && p);++expFrees;free(p);
}
}
'''
tests=r'''
int main() {
 using namespace Pulsar::Network;
 assert(!AllocNHTTPFallback(32,4));
 assert(wcscmp(GetNHTTPAllocationError(),L"Mem: pool missing")==0);
 EGG::Heap root; failCreate=true; InitNHTTPPool(&root);
 assert(rootAllocs==1 && rootFrees==1 && !s_pool);
 failCreate=false; InitNHTTPPool(&root); InitNHTTPPool(&root);
 assert(rootAllocs==2 && s_pool);
 assert(!AllocNHTTPFallback(0,4));
 assert(!AllocNHTTPFallback(0x20001,4));
 assert(!AllocNHTTPFallback(32,64));
 assert(expAllocs==0);
 void *slots[16];for(int i=0;i<16;i++){slots[i]=AllocNHTTPFallback(32,1);assert(slots[i]);}
 assert(!AllocNHTTPFallback(32,4));
 assert(wcscmp(GetNHTTPAllocationError(),L"Mem: tracking full")==0);
 for(int i=0;i<16;i++)assert(FreeNHTTPFallback(slots[i]));
 assert(expFrees==16);
 int foreign=0;assert(!FreeNHTTPFallback(&foreign));assert(FreeNHTTPFallback(nullptr));
 failAlloc=true;assert(!AllocNHTTPFallback(0x20000,32));
 failAlloc=false;void *last=AllocNHTTPFallback(0x20000,32);assert(last);
 assert(FreeNHTTPFallback(last));assert(interruptsEnabled);
 ClearNHTTPAllocationError();assert(s_failure==0);
 free(s_pool); s_pool=nullptr;
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(stubs+'\n'+source+'\n'+tests)
 subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=0"))
print('PASS: actual MEM2 pool source; failed initialization cleanup, one-time reserve, size/alignment limits, 16-slot exhaustion/reuse, failure recovery and correct free ownership (native APIs mocked).')
