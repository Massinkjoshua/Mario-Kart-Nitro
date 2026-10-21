#include <kamek.hpp>
#include <MarioKartWii/UI/Ctrl/CtrlRace/CtrlRaceItemWindow.hpp>

namespace Pulsar { namespace Race {
#ifdef MKNITRO_SERVER
static bool IsNitroItemWindowEmpty(CtrlRaceItemWindow *window) {
    Item::Manager *mgr = Item::Manager::sInstance;
    if (window->hudSlotId >= 4 || !mgr || !mgr->players) return false;
    const u8 playerId = window->GetPlayerId();
    if (playerId >= mgr->playerCount) return false;
    const Item::Player &player = mgr->players[playerId];
    const bool activeGolden = player.inventory.currentItemId == GOLDEN_MUSHROOM
        && player.inventory.hasGolden && player.inventory.goldenTimer != 0;
    return (player.inventory.currentItemId == ITEM_NONE
            || (player.inventory.currentItemCount == 0 && !activeGolden))
        && player.roulette.isTheRouletteSpinning == 0;
}
static void DrawNitroItemWindow(CtrlRaceItemWindow *window, u32 hud) {
    if (!IsNitroItemWindowEmpty(window)) window->LayoutUIControl::Draw(hud);
}
static void UpdateNitroItemWindow(CtrlRaceItemWindow *window) {
    window->CtrlRaceItemWindow::OnUpdate();
    // Native roulette animations can re-enable the additive white pictures.
    if (window->hilight_curr) window->hilight_curr->flag &= ~1;
    if (window->hilight_next) window->hilight_next->flag &= ~1;
    if (window->layout.GetPaneByName("nitro_item_frame"))
        window->HudSlotColorEnable("nitro_item_frame", true);
}
static void ColorNitroItemFrame(CtrlRaceBase *window, const char *pane, bool enable) {
    window->HudSlotColorEnable(pane, enable);
    if (window->layout.GetPaneByName("nitro_item_frame"))
        window->HudSlotColorEnable("nitro_item_frame", true);
}
kmWritePointer(0x808d3cdc, DrawNitroItemWindow);
kmWritePointer(0x808d3ce4, UpdateNitroItemWindow);
kmCall(0x807eede0, ColorNitroItemFrame);
#endif
} }
