#include <kamek.hpp>
#include <MarioKartWii/UI/Page/Menu/SinglePlayer.hpp>
#include <MarioKartWii/UI/Page/Other/BackModel.hpp>
#include <PulsarSystem.hpp>
#include <UI/UI.hpp>
#include <Settings/UI/SettingsPanel.hpp>
#include <Settings/UI/SettingsPageSelect.hpp>

namespace Pulsar {
static void SetCC();
namespace UI {

void CorrectButtonCount(Pages::SinglePlayer *page) {
    // Three race modes and a separate Settings button.
    page->externControlCount = 4;
    new (page) Page;
}
kmCall(0x806266b8, CorrectButtonCount);
kmWrite32(0x806266d4, 0x60000000);

UIControl *CreateExternalControls(Pages::SinglePlayer *page, u32 id) {
    if (id >= 4) return nullptr;
    PushButton *button = new (PushButton);
    page->AddControl(page->controlCount++, *button, 0);
    button->buttonId = id;
    if (id == 3) {
        button->Load(UI::buttonFolder, "NitroSettings1P", "Settings1P", page->activePlayerBitfield, 0, false);
    } else {
        const char *variants[] = {"ButtonGP", "ButtonTA", "ButtonVS"};
        button->Load("button", "SingleTop", variants[id], page->activePlayerBitfield, 0, false);
    }
    // The native factory constructs movie buttons and crops missing movie panes.
    // These ordinary PushButtons use the existing layouts without movie previews.
    page->curMovieCount = 0;
    return button;
}
kmWritePointer(0x808D9F84, CreateExternalControls);

static int FixCalcDistance(const ControlManipulator &subject, const ControlManipulator &other, Directions direction) {
    return subject.CalcDistanceBothWrapping(other, direction);
}

static void SetDistanceFunc(ControlsManipulatorManager &mgr) {
    mgr.distanceFunc = &FixCalcDistance;
}
kmCall(0x8084ef68, SetDistanceFunc);

static void RequestCommonBackModel() {
    SectionMgr *mgr = SectionMgr::sInstance;
    if (mgr == nullptr || mgr->curSection == nullptr) return;
    Pages::BackModel *page = mgr->curSection->Get<Pages::BackModel>();
    if (page != nullptr) page->backgroundModel.RequestModel(BACKMODEL_STOPWATCH);
}

void OnButtonSelect(Pages::SinglePlayer *page, PushButton &button, u32 hudSlotId) {
    if (button.buttonId == 3) page->bottomText->SetMessage(BMG_SETTINGSBUTTON_BOTTOM);
    else page->Pages::SinglePlayer::OnExternalButtonSelect(button, hudSlotId);
    // Scope the common background slot to SinglePlayer; keep driver/kart APIs native.
    RequestCommonBackModel();
}
kmWritePointer(0x808D9F64, &OnButtonSelect);

void OnButtonClick(Pages::SinglePlayer *page, PushButton &button, u32 hudSlotId) {
    if (button.buttonId == 3) {
        ExpSection::GetSection()->GetPulPage<SettingsPageSelect>()->SetContext(
            Settings::SETTINGS_CONTEXT_OFFLINE, PAGE_SINGLE_PLAYER_MENU);
        ExpSection::GetSection()->GetPulPage<SettingsPanel>()->prevPageId = PAGE_SINGLE_PLAYER_MENU;
        page->nextPageId = static_cast<PageId>(SettingsPageSelect::id);
        page->EndStateAnimated(0, button.GetAnimationFrameSize());
        return;
    }
    if (button.buttonId > 2) return;
    page->Pages::SinglePlayer::OnButtonClick(button, hudSlotId);
    if (button.buttonId == 1) {
        System::sInstance->ttMode = TTMODE_150;
        SetCC();
    }
}
kmWritePointer(0x808BBED0, OnButtonClick);
}  // namespace UI

static void SetCC() {
    const System *system = System::sInstance;
    EngineClass cc = CC_150;
    if (system->ttMode == TTMODE_200 || system->ttMode == TTMODE_200_FEATHER) cc = CC_100;
    Racedata::sInstance->menusScenario.settings.engineClass = cc;
}
kmBranch(0x805e1ef4, SetCC);
kmBranch(0x805e1d58, SetCC);
}  // namespace Pulsar
