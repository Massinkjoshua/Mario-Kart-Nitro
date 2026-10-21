// Integrated recovered October checkpoint on 2026-10-16; see docs/recovery-provenance.json.
// Source ports of the verified v5 / v9.1 / v9.2 / v10 runtime recipes.
// Native addresses are PAL inputs; Kamek's versions.txt maps all hook targets.
#include <kamek.hpp>
#include <MarioKartWii/UI/Page/Other/Options.hpp>
#include <MarioKartWii/UI/Ctrl/CtrlRace/CtrlRaceBase.hpp>
#include <MarioKartWii/RKSYS/RKSYSMgr.hpp>
#include <Network/Rating/PlayerRating.hpp>

extern "C" void NitroNativePreviewVisibility();
extern "C" void NitroNativePreviewSwitchState();

namespace Pulsar { namespace UI {
// Records and obsolete channel-install controls remain inaccessible when hidden.
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x805eda74, 0x39200001);
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x805edc24, 0x3863081c);
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x805edc30, 0x3880084a);
kmWrite32(0x805fd854, 0x39200001);
// Leave the stopwatch BackModel slots in the native hidden state.
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x805fb7d4, 0x38800000);
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x8084db24, 0x38800000);
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x8084fad4, 0x38800000);
// The metallic item frames use a white additive layer during roulette/acquisition.
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x807ef204, 0x38c00000);
// Historical recipe: absent from Code(10); retained for review only.
// kmWrite32(0x807ef0a4, 0x38000000);

static void ActivateOptions(Pages::Options *page) {
    page->AddMarioKartChannel.isHidden = true;
    page->nextPageId = PAGE_NONE;
    if (page->animationDirection == 0) page->gcnRumble.SelectInitial(0);
}
kmBranch(0x805fd8e8, ActivateOptions);

static void ItemFramePlayerColour(CtrlRaceBase *control, const char *pane, bool enabled) {
    control->HudSlotColorEnable(pane, enabled);
    if (control->layout.GetPaneByName("nitro_item_frame") != nullptr)
        control->HudSlotColorEnable("nitro_item_frame", true);
}
kmCall(0x807eede0, ItemFramePlayerColour);

static void RepairLicensePanes(void *page) {
    u8 *raw = reinterpret_cast<u8 *>(page);
    raw[1608] = 1; // LicenseSettings::recordsButton.isHidden
    if (*reinterpret_cast<void **>(raw + 1296) == nullptr) return;
    BaseLayout *layout = reinterpret_cast<BaseLayout *>(raw + 1276);
    const char *names[2] = {"mii", "nitro_mii_frame"};
    // The ten runtime transform floats from the current Title layout.
    static const u32 transform[2][10] = {
        {0xc2860000, 0xc1e60ec8, 0, 0, 0, 0, 0x3f000000, 0x3f000000, 0x42b40000, 0x42b40000},
        {0, 0x42340000, 0, 0, 0, 0, 0x3f800000, 0x3f800000, 0x43000000, 0x43040000}
    };
    for (u32 i = 0; i < 2; ++i) {
        nw4r::lyt::Pane *pane = layout->GetPaneByName(names[i]);
        if (pane != nullptr) memcpy(reinterpret_cast<u8 *>(pane) + 44, transform[i], sizeof(transform[i]));
    }
}
static asmFunc LicenseActivationEpilogue() {
    ASM(nofralloc;
        stwu r1, -0x20(r1);
        mflr r0;
        stw r0, 0x24(r1);
        mr r3, r31;
        bl RepairLicensePanes;
        lwz r0, 0x24(r1);
        mtlr r0;
        addi r1, r1, 0x20;
        lwz r0, 0x14(r1);
        blr;)
}
// Historical recipe: absent from Code(10); retained for review only.
// kmCall(0x805edc3c, LicenseActivationEpilogue);

// NoteModelControl's r27 is the control. Only the two course-selection pages
// use the standing preview state; other pages retain the native state machine.
static asmFunc CoursePreviewVisibility() {
    ASM(nofralloc;
        lwz r12, 100(r27); cmpwi r12, 0; beq original;
        lwz r12, 12(r12); cmpwi r12, 0; beq original;
        lwz r12, 4(r12); cmpwi r12, 110; beq course;
        cmpwi r12, 111; bne original;
    course: li r6, 0;
    original: b NitroNativePreviewVisibility;)
}
static asmFunc CoursePreviewStateCheck() {
    ASM(nofralloc;
        lwz r12, 100(r27); cmpwi r12, 0; beq original;
        lwz r12, 12(r12); cmpwi r12, 0; beq original;
        lwz r12, 4(r12); cmpwi r12, 110; beq course;
        cmpwi r12, 111; bne original;
    course: li r12, 0; cmpw r0, r12; blr;
    original: cmpwi r0, 3; blr;)
}
static asmFunc CoursePreviewSwitchState() {
    ASM(nofralloc;
        lwz r12, 100(r27); cmpwi r12, 0; beq original;
        lwz r12, 12(r12); cmpwi r12, 0; beq original;
        lwz r12, 4(r12); cmpwi r12, 110; beq course;
        cmpwi r12, 111; bne original;
    course: li r5, 0;
    original: b NitroNativePreviewSwitchState;)
}
// Historical recipe: absent from Code(10); retained for review only.
// kmCall(0x805f4718, CoursePreviewVisibility);
// Historical recipe: absent from Code(10); retained for review only.
// kmCall(0x805f475c, CoursePreviewStateCheck);
// Historical recipe: absent from Code(10); retained for review only.
// kmCall(0x805f47c8, CoursePreviewSwitchState);

static void LoadSavedVR(void *target) {
    const RKSYS::Mgr *mgr = RKSYS::Mgr::sInstance;
    if (mgr == nullptr || mgr->curLicenseId < 0 || mgr->curLicenseId >= 4) return;
    *reinterpret_cast<u16 *>(reinterpret_cast<u8 *>(target) + 0xc0) =
        static_cast<u16>(PointRating::GetUserVR(mgr->curLicenseId));
}
static void LoadSavedBR(void *target) {
    const RKSYS::Mgr *mgr = RKSYS::Mgr::sInstance;
    if (mgr == nullptr || mgr->curLicenseId < 0 || mgr->curLicenseId >= 4) return;
    *reinterpret_cast<u16 *>(reinterpret_cast<u8 *>(target) + 0xc2) =
        static_cast<u16>(PointRating::GetUserBR(mgr->curLicenseId));
}
kmBranch(0x80662d80, LoadSavedVR);
kmBranch(0x80662dc4, LoadSavedBR);
} }
