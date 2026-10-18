#include <kamek.hpp>
#include <core/egg/System.hpp>
#include <include/c_stdio.h>
#include <include/c_stdlib.h>
#include <include/c_string.h>
#include <MarioKartWii/RKSYS/RKSYSMgr.hpp>
#include <core/RK/RKSystem.hpp>
#include <core/rvl/DWC/NHTTP.hpp>
#include <core/rvl/NHTTP/NHTTP.hpp>
#include <core/rvl/OS/OS.hpp>
#include <Network/GPReport.hpp>
#include <Network/Json.hpp>
#include <Network/NHTTPHelper.hpp>
#include <Network/Rating/PlayerRating.hpp>
#include <Network/Rating/RatingSync.hpp>
#include <Network/WiiLink.hpp>
#include <MarioKartWii/RKNet/RKNetController.hpp>

namespace Pulsar {
namespace PointRating {

static bool s_syncReportingSuppressed = false;
static const u32 s_nhttpWorkBufSize = 0x1000;
static u32 s_requestGeneration = 0;
static void *s_requestWorkBuf = nullptr;
static char s_requestUrl[160];
static s32 s_pendingInitialReportProfileId = 0;
static u32 s_pendingInitialReportLicenseId = 0;
static bool s_pendingLoginDownload = false;
static bool s_pendingLoginEstablished = false;
static s32 s_pendingProfileId = 0;
static u32 s_pendingLicenseId = 0;

struct RequestCtx {
    u32 generation;
    s32 profileId;
    u32 licenseId;
    float startVr;
    float startBr;
};

static RequestCtx s_requestCtx;
static volatile bool s_requestActive = false;
static volatile bool s_completionReady = false;
static RequestCtx s_completedCtx;
static char s_completedJson[256];
static bool s_completedBodyValid = false;
static bool s_downloadQueued = false;
static s32 s_queuedProfileId = 0;
static u32 s_queuedLicenseId = 0;

static int ClampRatingForSync(float rating) {
    int scaled = (int)(rating * 100.0f + 0.5f);
    if (scaled < 1) return 1;
    if (scaled > 1000000) return 1000000;
    return scaled;
}

static bool ParseJsonScaledValue(const char *json, const char *key, int &out) {
    if (json == nullptr || key == nullptr) return false;

    const char *pos = strstr(json, key);
    if (pos == nullptr) return false;

    const char *colon = strchr(pos, ':');
    if (colon == nullptr) return false;

    const char *valueStart = Network::Json::SkipWhitespace(colon + 1);
    char *end = nullptr;
    const long value = strtol(valueStart, &end, 10);
    if (end == nullptr || end == valueStart || value < 1 || value > 1000000) return false;
    const char *tail = Network::Json::SkipWhitespace(end);
    if (*tail != ',' && *tail != '}') return false;
    out = (int)value;
    return true;
}

static bool ParseJsonFoundFlag(const char *json, bool &found) {
    if (json == nullptr) return false;
    const char *pos = strstr(json, "\"found\"");
    if (pos == nullptr) return false;
    const char *colon = strchr(pos, ':');
    if (colon == nullptr) return false;
    const char *value = Network::Json::SkipWhitespace(colon + 1);
    if (*value != '0' && *value != '1') return false;
    const char *tail = Network::Json::SkipWhitespace(value + 1);
    if (*tail != ',' && *tail != '}') return false;
    found = *value == '1';
    return true;
}

void SetSyncReportingSuppressed(bool suppress) {
    s_syncReportingSuppressed = suppress;
}

void ReportCurrentRatings(u32 licenseId) {
    if (s_syncReportingSuppressed) return;

    const int vrScaled = ClampRatingForSync(GetUserVR(licenseId));
    const int brScaled = ClampRatingForSync(GetUserBR(licenseId));

    char buffer[64];
    if (snprintf(buffer, sizeof(buffer), "vr=%d|br=%d", vrScaled, brScaled) < 0) return;
    Network::Report("wl:mkw_vrbr", buffer);
}

static bool IsRequestStillRelevant(const RequestCtx &ctx) {
    if (ctx.generation != s_requestGeneration) return false;
    if (ctx.profileId <= 0) return false;

    RKSYS::Mgr *rksys = RKSYS::Mgr::sInstance;
    if (rksys == nullptr || ctx.licenseId >= 4) return false;

    const RKSYS::LicenseMgr &license = rksys->licenses[ctx.licenseId];
    if ((s32)license.dwcAccUserData.gsProfileId != ctx.profileId) return false;

    const float currentVr = GetUserVR(ctx.licenseId);
    const float currentBr = GetUserBR(ctx.licenseId);
    if (currentVr != ctx.startVr || currentBr != ctx.startBr) return false;

    return true;
}

static void OnRatingsDownloaded(s32 result, void *response, void *userdata) {
    // The callback only copies a bounded result. Save IO and report generation
    // run on the frame thread, not inside the HTTP worker.
    const RequestCtx *ctx = reinterpret_cast<const RequestCtx *>(userdata);
    RequestCtx completed = {};
    if (ctx != nullptr) completed = *ctx;
    char json[256] = {};
    bool valid = false;
    if (ctx != nullptr && response != nullptr && result == 0) {
        char *body = nullptr;
        const int length = NHTTP::GetBodyAll(reinterpret_cast<NHTTP::Res *>(response), &body);
        if (body != nullptr && length > 0 && length < (int)sizeof(json)) {
            memcpy(json, body, length);
            json[length] = '\0';
            valid = true;
        }
    }
    if (response != nullptr) NHTTPDestroyResponse(response);
    Network::FinishNHTTPRequest();
    const s32 interrupts = OS::DisableInterrupts();
    s_completedCtx = completed;
    memcpy(s_completedJson, json, sizeof(json));
    s_completedBodyValid = valid;
    s_completionReady = true;
    s_requestActive = false;
    OS::RestoreInterrupts(interrupts);
}

static void ProcessCompletedRatingDownload() {
    if (!s_completionReady) return;
    RequestCtx completed;
    char json[256];
    const s32 interrupts = OS::DisableInterrupts();
    completed = s_completedCtx;
    memcpy(json, s_completedJson, sizeof(json));
    const bool valid = s_completedBodyValid;
    s_completionReady = false;
    OS::RestoreInterrupts(interrupts);
    if (!valid || !IsRequestStillRelevant(completed)) return;
    bool found = false;
    if (!ParseJsonFoundFlag(json, found)) return;
    if (!found) {
        ReportCurrentRatings(completed.licenseId);
        return;
    }
    int vrScaled = 0;
    int brScaled = 0;
    if (!ParseJsonScaledValue(json, "\"vr\"", vrScaled) ||
        !ParseJsonScaledValue(json, "\"br\"", brScaled)) return;
    SetSyncReportingSuppressed(true);
    SaveProfileVR(completed.profileId, (float)vrScaled / 100.0f);
    SaveProfileBR(completed.profileId, (float)brScaled / 100.0f);
    SetSyncReportingSuppressed(false);
}

void BeginLoginRatingDownload(s32 profileId, u32 licenseId) {
    if (profileId <= 0) return;

    RKSYS::Mgr *rksys = RKSYS::Mgr::sInstance;
    if (rksys == nullptr || licenseId >= 4) return;
    if ((s32)rksys->licenses[licenseId].dwcAccUserData.gsProfileId != profileId) return;
    if (s_requestActive || s_completionReady) {
        // Invalidate an obsolete result without changing its still-owned
        // context or buffer. The latest requested profile is queued for a frame.
        ++s_requestGeneration;
        s_downloadQueued = true;
        s_queuedProfileId = profileId;
        s_queuedLicenseId = licenseId;
        return;
    }
    BindLicenseProfileId(licenseId, profileId);
    if (!Network::PrepareNHTTPRequest()) return;

    if (s_requestWorkBuf == nullptr) {
        s_requestWorkBuf = Network::NHTTPAlloc(s_nhttpWorkBufSize, 0x20);
        if (s_requestWorkBuf == nullptr) return;
    }
    memset(s_requestWorkBuf, 0, s_nhttpWorkBufSize);

    ++s_requestGeneration;
    s_requestCtx.generation = s_requestGeneration;
    s_requestCtx.profileId = profileId;
    s_requestCtx.licenseId = licenseId;
    s_requestCtx.startVr = GetUserVR(licenseId);
    s_requestCtx.startBr = GetUserBR(licenseId);

    if (snprintf(s_requestUrl, sizeof(s_requestUrl), "http://nas.%s/api/mkw_rr_ratings?pid=%ld",
                 WWFC_DOMAIN, (long)profileId) < 0) {
        return;
    }

    void *request = NHTTPCreateRequest(s_requestUrl, 0, s_requestWorkBuf, s_nhttpWorkBufSize,
                                       reinterpret_cast<void *>(&OnRatingsDownloaded),
                                       reinterpret_cast<void *>(&s_requestCtx));
    if (request == nullptr) return;

    // Count before dispatch: even an immediate callback must balance it.
    Network::MarkNHTTPRequestActive();
    s_requestActive = true;
    const s32 sendRet = NHTTPSendRequestAsync(request);
    if (sendRet < 0 && s_requestActive) {
        Network::FinishNHTTPRequest();
        s_requestActive = false;
        ++s_requestGeneration;
    }
}

static bool CanStartLoginRatingDownload() {
    RKNet::Controller *controller = RKNet::Controller::sInstance;
    return controller != nullptr && controller->GetConnectionState() == RKNet::CONNECTIONSTATE_IDLE;
}

static void TryStartPendingLoginRatingDownload() {
    if (!s_pendingLoginDownload) return;

    RKNet::Controller *controller = RKNet::Controller::sInstance;
    if (controller == nullptr) return;

    const RKNet::ConnectionState state = controller->GetConnectionState();
    if (state == RKNet::CONNECTIONSTATE_LOGIN_AUTHORISED ||
        state == RKNet::CONNECTIONSTATE_LOGIN_FRIENDS_SYNCED) {
        s_pendingLoginEstablished = true;
        return;
    }

    if (state != RKNet::CONNECTIONSTATE_IDLE) return;

    // Both a completed login and a cancelled login end in IDLE. Only launch the
    // deferred request if this login progressed far enough to be established.
    // Otherwise the request would start while the WFC section is being torn down.
    if (!s_pendingLoginEstablished) {
        s_pendingLoginDownload = false;
        s_pendingProfileId = 0;
        s_pendingLicenseId = 0;
        return;
    }

    const s32 profileId = s_pendingProfileId;
    const u32 licenseId = s_pendingLicenseId;
    s_pendingLoginDownload = false;
    s_pendingLoginEstablished = false;
    s_pendingProfileId = 0;
    s_pendingLicenseId = 0;
    BeginLoginRatingDownload(profileId, licenseId);
}

// One frame-thread entry point owns completion application and queue dispatch.
void ProcessLoginRatingDownloads() {
    ProcessCompletedRatingDownload();
    if (!s_requestActive && !s_completionReady && s_downloadQueued) {
        const s32 profileId = s_queuedProfileId;
        const u32 licenseId = s_queuedLicenseId;
        s_downloadQueued = false;
        BeginLoginRatingDownload(profileId, licenseId);
    }
    TryStartPendingLoginRatingDownload();
}
static FrameLoadHook startPendingLoginRatingDownload(ProcessLoginRatingDownloads);

void StartLoginRatingDownload(s32 profileId, u32 licenseId) {
    if (profileId <= 0) return;

    RKSYS::Mgr *rksys = RKSYS::Mgr::sInstance;
    if (rksys == nullptr || licenseId >= 4) return;
    BindLicenseProfileId(licenseId, profileId);

    if (!CanStartLoginRatingDownload()) {
        s_pendingLoginDownload = true;
        s_pendingLoginEstablished = false;
        s_pendingProfileId = profileId;
        s_pendingLicenseId = licenseId;
        return;
    }

    s_pendingLoginDownload = false;
    s_pendingLoginEstablished = false;
    BeginLoginRatingDownload(profileId, licenseId);
}

}  // namespace PointRating
}  // namespace Pulsar
