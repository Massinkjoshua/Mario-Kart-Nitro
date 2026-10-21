#include <UI/UI.hpp>
#include <Settings/UI/ExpOptionsPage.hpp>
#include <Settings/UI/SettingsPanel.hpp>
#include <Settings/UI/SettingsPageSelect.hpp>

namespace Pulsar {
namespace UI {

kmWrite32(0x805fd754, 0x60000000);  // nop the InitControl call in the init func

#ifdef MKNITRO_SERVER
// Recovered v10 native Options behavior; assets supply the final button positions.
kmWrite32(0x805fd854, 0x39200001);
static void ActivateNitroOptions(Pages::Options *page) {
    page->AddMarioKartChannel.isHidden = true;
    page->nextPageId = PAGE_NONE;
    if (page->currentState == 0) page->gcnRumble.SelectInitial(0);
}
kmBranch(0x805fd8e8, ActivateNitroOptions);
#endif

ExpOptions::ExpOptions() { this->onButtonClickHandler.ptmf = &ExpOptions::ExpandedOnButtonClick; }

void ExpOptions::OnInit() {
    this->InitControlGroup(5 + 1);
    Options::OnInit();
    this->AddControl(this->controlGroup.controlCount - 1, settingsButton, 0);

    this->settingsButton.Load(UI::buttonFolder, "SettingsButton", "Settings", 1, 0, false);

    this->settingsButton.buttonId = 5;
    this->settingsButton.SetOnClickHandler(this->onButtonClickHandler, 0);
    this->settingsButton.SelectInitial(0);
}

void ExpOptions::ExpandedOnButtonClick(PushButton &pushButton, u32 hudSlotId) {
    if (pushButton.buttonId == 5) {
        ExpSection::GetSection()->GetPulPage<SettingsPageSelect>()->SetContext(
            Settings::SETTINGS_CONTEXT_OFFLINE, PAGE_OPTIONS);
        ExpSection::GetSection()->GetPulPage<SettingsPanel>()->prevPageId = PAGE_OPTIONS;
        this->nextPageId = static_cast<PageId>(SettingsPageSelect::id);
        this->EndStateAnimated(0, pushButton.GetAnimationFrameSize());
    } else {
        this->OnButtonClick(pushButton, hudSlotId);
    }
}

static void PatchOptionsBRCTR(PushButton *button, const char *folderName, const char *ctrName, const char *variant, u32 playerCount, u32 r8, bool inaccessible) {
    button->Load(folderName, "SettingsButton", variant, playerCount, r8, inaccessible);
}
kmCall(0x805fd7bc, PatchOptionsBRCTR);  // so that the positions are correct
kmCall(0x805fd80c, PatchOptionsBRCTR);
kmCall(0x805fd858, PatchOptionsBRCTR);
}  // namespace UI
}  // namespace Pulsar
