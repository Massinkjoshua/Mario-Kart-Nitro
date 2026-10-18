#include <kamek.hpp>
#include <MarioKartWii/RKNet/USER.hpp>
#include <MarioKartWii/RKSYS/RKSYSMgr.hpp>
#include <Network/Rating/PlayerRating.hpp>

namespace Pulsar { namespace PointRating {
#ifdef MKNITRO_SERVER
// USER packets carry the integer component; decimal digits use the existing
// packet expansion. Sending the stock save's scaled rating caused inflated VR.
static void SetSendNitroVR(RKNet::USERHandler *handler) {
    RKSYS::Mgr *save = RKSYS::Mgr::sInstance;
    if (save && save->curLicenseId >= 0 && save->curLicenseId <= 3)
        handler->toSendPacket.vr = static_cast<u16>(GetUserVR(save->curLicenseId));
}
static void SetSendNitroBR(RKNet::USERHandler *handler) {
    RKSYS::Mgr *save = RKSYS::Mgr::sInstance;
    if (save && save->curLicenseId >= 0 && save->curLicenseId <= 3)
        handler->toSendPacket.br = static_cast<u16>(GetUserBR(save->curLicenseId));
}
kmBranch(0x80662d80, SetSendNitroVR);
kmBranch(0x80662dc4, SetSendNitroBR);
#endif
} }
