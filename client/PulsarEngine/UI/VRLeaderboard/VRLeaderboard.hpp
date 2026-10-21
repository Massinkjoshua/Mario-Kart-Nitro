// Integrated recovered October checkpoint on 2026-10-16; see docs/recovery-provenance.json.
#ifndef _PUL_VRLEADERBOARD_
#define _PUL_VRLEADERBOARD_

#include <kamek.hpp>
#include <MarioKartWii/UI/Page/Page.hpp>
#include <MarioKartWii/UI/Ctrl/Menu/CtrlMenuText.hpp>
#include <MarioKartWii/UI/Ctrl/UIControl.hpp>
#include <MarioKartWii/Mii/MiiGroup.hpp>
#include <core/rvl/RFL/RFLTypes.hpp>
#include <UI/UI.hpp>

namespace Pulsar {
namespace UI {

class VRLeaderboardPage : public Page {
public:
    static const PulPageId id = PULPAGE_VRLEADERBOARD;

    static const int kRowsPerPage = 10;
    static const int kPagesPerAPIFetch = 5;
    // Match the exported API bound; discover pages using each 50-row response.
    static const u32 kMaxAPIPage = 1000000;
    static const int kMaxEntries = kRowsPerPage * kPagesPerAPIFetch;

    VRLeaderboardPage();
    ~VRLeaderboardPage() override;

    PageId GetNextPage() const override;
    void OnInit() override;
    void OnActivate() override;
    void OnDeactivate() override;
    void BeforeEntranceAnimations() override;
    void OnUpdate() override;

private:
    void OnBackPress(u32 hudSlotId);
    void OnBackButtonClick(PushButton &button, u32 hudSlotId);
    void ResetRowsToLoading();
    void ApplyResults();
    void ApplyError();

    enum FetchState {
        FETCH_IDLE = 0,
        FETCH_REQUESTING = 1,
        FETCH_READY = 2,
        FETCH_ERROR = 3,
        FETCH_WAITING = 4,
    };

    struct Entry {
        wchar_t name[24];
        u32 vr;
        u32 rank;
        RFL::StoreData miiData;
        u64 friendCode;
    };

    static void OnLeaderboardReceived(s32 result, void *response, void *userdata);
    static void StartFetch(VRLeaderboardPage *page);
    static int ParseResponse(const char *json, Entry *outEntries, int maxEntries);
    static void OverrideOwnMiiData(Entry *entries, int entryCount, u64 ownFriendCode);

    static FetchState s_fetchState;
    static bool s_hasApplied;
    static Entry *s_entries;

    CtrlMenuPageTitleText *titleText;
    CtrlMenuInstructionText *bottomText;
    CtrlMenuBackButton *backButton;
    LayoutUIControl *rows[kRowsPerPage];

    MiiGroup *miiGroup;

    ControlsManipulatorManager *controlsManipulatorManager;
    PtmfHolder_2A<VRLeaderboardPage, void, PushButton &, u32> onBackButtonClickHandler;
    PtmfHolder_1A<VRLeaderboardPage, void, u32> onBackPressHandler;

    PageId nextPageId;

    u32 curPage;
};

}  // namespace UI
}  // namespace Pulsar

#endif
