#include <kamek.hpp>
#include <Network/NHTTPReserve.hpp>

DoFuncsHook *SectionLoadHook::sHooks = nullptr;
DoFuncsHook *RaceLoadHook::raceLoadHooks = nullptr;
DoFuncsHook *FrameLoadHook::FrameLoadHooks = nullptr;
DoFuncsHook *RaceFrameHook::raceFrameHooks = nullptr;

void DoFuncsHook::Init(void *f, Invoker inv, DoFuncsHook **prev) {
    this->funcPtr = f;
    this->invoker = inv;
    this->next = *prev;
    *prev = this;
}

void DoFuncsHook::Exec(DoFuncsHook *first, void *a1, void *a2, void *a3) {
    for (DoFuncsHook *p = first; p; p = p->next) {
        p->invoker(p->funcPtr, a1, a2, a3);
    }
}

nw4r::ut::List BootHook::list = {nullptr, nullptr, 0, offsetof(BootHook, link)};

// kmBranch(0x80001500, BootHook2::Exec);
// Preserve the one existing boot dispatch; reserve MEM2 before its callbacks.
// The recovered PAL caller supplies the persistent root MEM2 heap in r4.
static void NitroBootWithHTTPReserve(void *, EGG::Heap *mem2, void *) {
    Pulsar::Network::InitializeHTTPReserve(mem2);
    BootHook::Exec();
}
kmCall(0x80543bb4, NitroBootWithHTTPReserve);
kmBranch(0x80554728, RaceLoadHook::Exec);
kmBranch(0x8083822C, RaceLoadHook::Exec);
kmBranch(0x80601C60, FrameLoadHook::Exec);
kmBranch(0x8053369c, RaceFrameHook::Exec);  // Raceinfo::Update()
kmBranch(0x8063507c, SectionLoadHook::Exec);
