// Reconstructed from the supplied Code.pul on 16 October 2026.
// Editable source for three installations missing from the October checkpoint.
// See docs/recovered-runtime-repairs.md for addresses, evidence and limits.
#include <kamek.hpp>
#include <MarioKartWii/3D/Model/Menu/MenuModelMgr.hpp>
#include <MarioKartWii/3D/Model/Menu/BackModel.hpp>
#include <MarioKartWii/3D/Model/ModelDirector.hpp>
#include <MarioKartWii/3D/Scn/ScnMgr.hpp>
#include <MarioKartWii/UI/Ctrl/CtrlRace/CtrlRaceItemWindow.hpp>
#include <MarioKartWii/Item/ItemManager.hpp>
#include <MarioKartWii/Item/ItemPlayer.hpp>
#include <core/rvl/OS/OS.hpp>

extern "C" bool NitroNativeModelExists(const char *, const nw4r::g3d::ResFile &);
extern "C" void NitroNativeLoadModel(ModelDirector *, const char *, nw4r::g3d::ResFile &, Light *);
extern "C" void NitroNativeSetBackModel(BackModelMgr *, BackModelType, bool);

namespace Pulsar { namespace UI {

// The released branch replaces RequestBackModel itself: even callers requesting
// another model go through model zero with reAnimate enabled. Null owners return.
void RequestReleasedBackModel(MenuModelMgr *manager, BackModelType) {
    if (manager != nullptr && manager->backModelMgr != nullptr)
        NitroNativeSetBackModel(manager->backModelMgr, static_cast<BackModelType>(0), true);
}
kmBranch(0x8059e598, RequestReleasedBackModel);

bool SuppressEmptyItemDraw(CtrlRaceItemWindow *window) {
    Item::Manager *manager = Item::Manager::sInstance;
    if (window->hudSlotId >= 4 || manager == nullptr || manager->players == nullptr) return false;
    const u8 playerId = window->GetPlayerId();
    if (playerId >= manager->playerCount) return false;
    const Item::Player &player = manager->players[playerId];
    const Item::PlayerInventory &inventory = player.inventory;
    const bool activeGolden = inventory.currentItemId == GOLDEN_MUSHROOM &&
                              inventory.hasGolden && inventory.goldenTimer != 0;
    return (inventory.currentItemId == ITEM_NONE ||
            (inventory.currentItemCount == 0 && !activeGolden)) &&
           !player.roulette.isTheRouletteSpinning;
}

void DrawReleasedItemWindow(CtrlRaceItemWindow *window, u32 screen) {
    if (!SuppressEmptyItemDraw(window)) window->LayoutUIControl::Draw(screen);
}
// The released vtable overrides Draw as well as the recovered OnUpdate hook.
kmWritePointer(0x808d3cdc, DrawReleasedItemWindow);

static void ReportPreviewHeap(const char *name, EGG::Heap *heap) {
    const u32 available = heap != nullptr ? heap->getAllocatableSize(32) : 0;
    const u32 blocked = heap != nullptr ? heap->dameFlag & 1 : 0;
    OS::Report("[NitroPreview] %s heap=%p available=%u blocked=%u\n", name, heap, available, blocked);
}

void LoadReleasedPreviewModel(ModelDirector *model, const char *name,
                             nw4r::g3d::ResFile &file, Light *light) {
    const bool exists = name != nullptr && file.data != nullptr && NitroNativeModelExists(name, file);
    ScnMgr *scene = ScnMgr::sInstance[0];
    OS::Report("[NitroPreview] begin model=%p name=%s brres=%p mdlExists=%u allocator=%p menuAllocator=%p\n",
               model, name != nullptr ? name : "(null)", file.data, exists,
               scene != nullptr ? scene->curAllocator : nullptr, menuAllocator);
    ReportPreviewHeap("scene", scene != nullptr ? scene->curHeap : static_cast<EGG::Heap *>(nullptr));
    MenuModelMgr *manager = MenuModelMgr::sInstance;
    if (manager != nullptr) {
        ReportPreviewHeap("menu", manager->heap);
        ReportPreviewHeap("menu-other", manager->otherHeap);
    }
    NitroNativeLoadModel(model, name, file, light);
    OS::Report("[NitroPreview] complete model=%p\n", model);
}
kmCall(0x8081ee34, LoadReleasedPreviewModel);
} }
