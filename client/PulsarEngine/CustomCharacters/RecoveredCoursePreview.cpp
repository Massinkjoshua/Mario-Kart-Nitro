// Reconstructed from the released PAL course-animation v2 and visibility hooks.
// Mario Kart Nitro, 16 October 2026; GPLv3. Native PAL addresses are intentional.
#include <CustomCharacters/CustomCharacters.hpp>
#include <MarioKartWii/3D/Model/Menu/MenuKartModel.hpp>

namespace Pulsar { namespace CustomCharacters {
static bool CourseMemory(const void *pointer, u32 size) {
    const u32 address = reinterpret_cast<u32>(pointer);
    return (address & 3) == 0 &&
        ((address >= 0x80004000 && address <= 0x81800000 - size) ||
         (address >= 0x90000000 && address <= 0x94000000 - size));
}

static PageId ActiveCoursePage() {
    const SectionMgr *manager = SectionMgr::sInstance;
    if (manager == nullptr || manager->curSection == nullptr) return PAGE_NONE;
    const Section *section = manager->curSection;
    const s32 count = static_cast<s32>(section->layerCount);
    if (count < 0 || count > 10) return PAGE_NONE;
    for (s32 index = 0; index <= count; ++index) {
        const Page *page = section->activePages[index];
        if (page != nullptr && (page->pageId == PAGE_CUP_SELECT || page->pageId == PAGE_COURSE_SELECT)) return page->pageId;
    }
    return PAGE_NONE;
}

struct CourseObservation {
    ModelDirector *kart;
    ModelDirector *driver;
    PageId page;
    u32 frames;
};
static CourseObservation courseObservations[LOCAL_PLAYER_COUNT];

static bool CourseDirector(const ModelDirector *director) {
    return CourseMemory(director, 0x4c) && (director->bitfield & 0x100000) != 0 &&
        CourseMemory(director->curScnMdlEx, 0x14) && CourseMemory(director->curScnMdlEx->scnObj, 0xe8);
}

void UpdateReleasedCourseKart(MenuKartModel *kart) {
    typedef void (*Update)(MenuKartModel *);
    reinterpret_cast<Update>(0x8083275c)(kart);
    const PageId page = ActiveCoursePage();
    if (page == PAGE_NONE) return;
    MenuModelMgr *manager = MenuModelMgr::sInstance;
    if (manager == nullptr || !manager->isActive || manager->driverModels == nullptr || manager->kartModels == nullptr) return;
    MenuDriverModelMgr *drivers = manager->driverModels;
    MenuKartModelMgr *karts = manager->kartModels;
    if (karts->playerCount < 1 || karts->playerCount > 4 || karts->modelCount < 1 || karts->modelCount > 12) return;
    for (u32 hud = 0; hud < karts->playerCount; ++hud) {
        if (karts->players[hud].idx >= karts->modelCount) continue;
        if (karts->GetMenuKartModel(hud, karts->players[hud].idx) != kart) continue;
        ModelDirector *kartDirector = kart->model;
        if (kartDirector == nullptr || hud >= drivers->playerCount || drivers->players[hud].playerModel == nullptr) return;
        MenuDriverModel *driver = drivers->players[hud].playerModel;
        ModelDirector *driverDirector = driver->model;
        if (!CourseDirector(driverDirector) || !CourseDirector(kartDirector)) return;
        CourseObservation &observation = courseObservations[hud];
        if (observation.kart == kartDirector && observation.driver == driverDirector && observation.page == page) ++observation.frames;
        if (observation.kart != kartDirector || observation.driver != driverDirector || observation.page != page || observation.frames >= 60) {
            observation.kart = kartDirector; observation.driver = driverDirector; observation.page = page; observation.frames = 0;
        }
        // Native driver-state offset 8 and kart stride 0x2c are used below because
        // the inherited header padding does not describe those two layouts correctly.
        // The released v2 diagnostic block is bypassed. It does not log here.
        for (u32 buffer = 0; buffer < 2; ++buffer) {
            EGG::ScnMdlEx *kartBuffer = kartDirector->scnMdlEx[buffer];
            EGG::ScnMdlEx *driverBuffer = driverDirector->scnMdlEx[buffer];
            if (!CourseMemory(kartBuffer, 0x14) || !CourseMemory(driverBuffer, 0x14)) continue;
            nw4r::g3d::ScnObj *kartObject = kartBuffer->scnObj;
            nw4r::g3d::ScnObj *driverObject = driverBuffer->scnObj;
            if (!CourseMemory(kartObject, 0xe8) || !CourseMemory(driverObject, 0xe8)) continue;
            if (buffer == 1 && *reinterpret_cast<const u32 *>(reinterpret_cast<const u8 *>(driver) + 8) == 1) {
                drivers->PrepareDriverOnKartAnms(hud);
                driver->SwitchState(hud, static_cast<MenuDriverModel::State>(3));
            }
            kartObject->SetMtx(nw4r::g3d::ScnObj::MTX_LOCAL, driverObject->matrixArray[0]);
        }
        Vec3 scale;
        typedef void (*GetScale)(const ModelDirector *, Vec3 &);
        typedef void (*SetScale)(ModelDirector *, const Vec3 &);
        reinterpret_cast<GetScale>(0x8055f848)(driverDirector, scale);
        reinterpret_cast<SetScale>(0x8055b05c)(kartDirector, scale);
        return;
    }
}

void ToggleReleasedCourseKart(MenuKartModel *kart, bool visible) {
    if (ActiveCoursePage() != PAGE_NONE) {
        MenuModelMgr *manager = MenuModelMgr::sInstance;
        MenuKartModelMgr *karts = manager == nullptr ? static_cast<MenuKartModelMgr *>(nullptr) : manager->kartModels;
        if (karts != nullptr && karts->playerCount >= 1 && karts->playerCount <= 4 && karts->modelCount >= 1 && karts->modelCount <= 12) {
            bool selected = false;
            for (u32 hud = 0; hud < karts->playerCount; ++hud) {
                if (karts->players[hud].modelsArray != nullptr && karts->players[hud].idx < karts->modelCount &&
                    reinterpret_cast<u32>(karts->players[hud].modelsArray) + 0x2c * karts->players[hud].idx == reinterpret_cast<u32>(kart)) selected = true;
            }
            if (!selected) visible = false;
        }
    }
    typedef void (*Toggle)(MenuKartModel *, bool);
    reinterpret_cast<Toggle>(0x80830a5c)(kart, visible);
}

// REL vtables are located by their original method signatures, as in the release.
void InstallReleasedCoursePreview() {
    if (*reinterpret_cast<const volatile u32 *>(0x80000000) != 0x524d4350u) return;
    static u32 *updateSlot = nullptr;
    static u32 *visibilitySlot = nullptr;
    if (CourseMemory(updateSlot, 4) && CourseMemory(visibilitySlot, 4)) {
        if (*updateSlot == 0x8083275c) *updateSlot = reinterpret_cast<u32>(UpdateReleasedCourseKart);
        if (*visibilitySlot == 0x80830a5c) *visibilitySlot = reinterpret_cast<u32>(ToggleReleasedCourseKart);
        if (*updateSlot == reinterpret_cast<u32>(UpdateReleasedCourseKart) &&
            *visibilitySlot == reinterpret_cast<u32>(ToggleReleasedCourseKart)) return;
    }
    const GameScene *scene = GameScene::GetCurrent();
    if (scene == nullptr || *reinterpret_cast<const u32 *>(reinterpret_cast<const u8 *>(scene) + 0x28) != 1) return;
    for (u32 address = 0x80880000; address < 0x808e4000; address += 4) {
        u32 *entry = reinterpret_cast<u32 *>(address);
        if (entry[-1] != 0x80831f84 || entry[0] != 0x80832240) continue;
        if (entry[1] == 0x8083275c) entry[1] = reinterpret_cast<u32>(UpdateReleasedCourseKart);
        if (entry[1] == reinterpret_cast<u32>(UpdateReleasedCourseKart) && entry[2] == 0x80830a5c && entry[3] == 0x8059f4f0)
            entry[2] = reinterpret_cast<u32>(ToggleReleasedCourseKart);
        updateSlot = entry + 1;
        visibilitySlot = entry + 2;
        break;
    }
}
} }
