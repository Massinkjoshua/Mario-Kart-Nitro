#include <kamek.hpp>
#include <core/rvl/OS/OS.hpp>
#include <MarioKartWii/RKNet/RKNetController.hpp>
#include <Security/NitroIntegrity/Policy.hpp>
#include <Security/NitroIntegrity/Config.hpp>
#include <Security/NitroIntegrity/Manifest.hpp>
#include <Security/NitroIntegrity/IntegrityGuard.hpp>

namespace Pulsar { namespace NitroIntegrity {
static bool sRelReady, sHeaderLogged;
static Word sCallbacks, sLastAddress, sLastActual, sLastMismatchCount;
static bool sHadMismatch, sViolationLatched;

static Word ReadNative(Word address) {
#ifdef NITRO_INTEGRITY_HOST_TEST
    extern Word TestReadWord(Word);
    return TestReadWord(address);
#else
    return *reinterpret_cast<const volatile Word *>(address);
#endif
}
static bool IsPAL() { return ReadNative(0x80000000u) == 0x524d4350u; }

static Scan Audit() {
    Scan scan;
    if (!IsPAL()) { scan.valid = false; return scan; }
    scan = Inspect(kChecks, kCheckCount, sRelReady, ReadNative);
    if (!scan.valid) OS::Report("[NitroIntegrity] invalid audit manifest\n");
    if (scan.mismatches && (!sHadMismatch || sLastAddress != scan.firstAddress
        || sLastActual != scan.actual || sLastMismatchCount != scan.mismatches)) {
        OS::Report("[NitroIntegrity] mismatch address=%08x expected=%08x actual=%08x total=%u enforce=%u\n",
                   scan.firstAddress, scan.expected, scan.actual, scan.mismatches, Enforce ? 1u : 0u);
        sLastAddress = scan.firstAddress; sLastActual = scan.actual;
        sLastMismatchCount = scan.mismatches;
        // Report all changed sites so a legitimate payload conflict can be reviewed.
        for (Word i = 0; i < kCheckCount; ++i) {
            const CheckWord &check = kChecks[i];
            if (check.phase && !sRelReady) continue;
            const Word actual = ReadNative(check.address);
            if (actual != check.expected)
                OS::Report("[NitroIntegrity word] address=%08x expected=%08x actual=%08x\n",
                           check.address, check.expected, actual);
        }
    }
    sHadMismatch = scan.mismatches != 0;
    return scan;
}
// Clean-session evidence must include successful words, not only mismatches.
// Audit snapshots are deliberately local logs; they do not accuse another player.
static void LogAuditBaseline(const char *stage) {
    if (Enforce || !IsPAL()) return;
    OS::Report("[NitroIntegrity baseline] stage=%s REL=%u words=%u\n", stage, sRelReady ? 1u : 0u, kCheckCount);
    for (Word i = 0; i < kCheckCount; ++i) {
        const CheckWord &check = kChecks[i];
        if (check.phase && !sRelReady) continue;
        OS::Report("[NitroIntegrity baseline word] address=%08x expected=%08x actual=%08x phase=%u\n",
            check.address, check.expected, ReadNative(check.address), check.phase);
    }
}
static void ObserveHeader() {
    if (sHeaderLogged || !IsPAL()) return;
    const Word address = FindGctHeader(ReadNative);
    if (address) {
        sHeaderLogged = true;
        OS::Report("[NitroIntegrity] GCT header at %08x; presence only, no action taken\n", address);
    }
}
static bool Online() {
    const RKNet::Controller *c = RKNet::Controller::sInstance;
    return c && c->currentSub >= 0 && c->currentSub <= 1 && c->roomType != RKNet::ROOMTYPE_NONE;
}
// Once a reviewed enforcement scan detects tampering while entering/playing
// online, keep this process blocked even if the instruction is restored.
static bool ShouldDeny(const Scan &scan) {
    if (Enforce && ManifestRuntimeReviewed && IsPAL() && sRelReady
        && scan.valid && scan.checked == kCheckCount && scan.mismatches)
        sViolationLatched = true;
    return (Enforce && sViolationLatched)
        || DenyOnline(Enforce, ManifestRuntimeReviewed, IsPAL(), sRelReady, scan);
}
static void HaltWithExplanation() {
    const GX::Color foreground = {255, 255, 255, 255};
    const GX::Color background = {0, 0, 0, 255};
    OS::Fatal(foreground, background,
        "MKNITRO integrity check failed.\n"
        "The online session has been stopped on this console.\n"
        "Use the approved build and restart the game.\n"
        "This check does not issue an account ban.");
}
static void OnBoot() {
    // Never dereference StaticR at BootHook, regardless of loader differences.
    sRelReady = false; sCallbacks = 0; sHeaderLogged = false; sHadMismatch = false; sViolationLatched = false;
    OS::Report("[NitroIntegrity] mode=%s manifest_words=%u region=%s runtime_reviewed=%u\n",
        Enforce ? "enforce" : "audit", kCheckCount, IsPAL() ? "PAL" : "unsupported",
        ManifestRuntimeReviewed ? 1u : 0u);
    Audit(); ObserveHeader();
}
static void OnSectionLoad() {
    // This callback belongs to a REL menu function; StaticR is now available.
    sRelReady = true;
    Audit(); ObserveHeader(); LogAuditBaseline("section-load");
}
bool CanEnterOnline() {
    const Scan scan = Audit();
    const bool deny = ShouldDeny(scan);
    if (deny) OS::Report("[NitroIntegrity] online denied: reviewed=%u PAL=%u REL=%u valid=%u checked=%u mismatches=%u latched=%u\n",
        ManifestRuntimeReviewed ? 1u : 0u, IsPAL() ? 1u : 0u, sRelReady ? 1u : 0u,
        scan.valid ? 1u : 0u, scan.checked, scan.mismatches, sViolationLatched ? 1u : 0u);
    return !deny;
}
static void OnRaceLoad() {
    sRelReady = true; sCallbacks = 0;
    const Scan scan = Audit();
    LogAuditBaseline("race-load");
    if (Online() && ShouldDeny(scan))
        HaltWithExplanation();
}
static void OnRaceFrame() {
    // Local callback count does not trust a peer timestamp or race clock value.
    if (++sCallbacks < CheckEveryCallbacks) return;
    sCallbacks = 0;
    const Scan scan = Audit(); ObserveHeader();
    if (Online() && ShouldDeny(scan))
        HaltWithExplanation();
}
// Register with existing dispatchers; do not patch their addresses a second time.
static BootHook bootHook(OnBoot, 0xffff);
static SectionLoadHook sectionHook(OnSectionLoad);
static RaceLoadHook loadHook(OnRaceLoad);
static RaceFrameHook frameHook(OnRaceFrame);
} }
