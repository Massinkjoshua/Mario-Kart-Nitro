#include <kamek.hpp>
#include <core/rvl/OS/OS.hpp>
#include <MarioKartWii/Item/ItemManager.hpp>
#include <MarioKartWii/Kart/KartManager.hpp>
#include <MarioKartWii/Kart/KartBody.hpp>
#include <MarioKartWii/Race/RaceInfo/RaceInfo.hpp>
#include <MarioKartWii/RKNet/RKNetController.hpp>
#include <Security/NitroIntegrity/Policy.hpp>

namespace Pulsar { namespace NitroIntegrity {
static Word sStateCallbacks;
static void ResetStateAudit() { sStateCallbacks = 0; }

static void AuditLocalState() {
    if (++sStateCallbacks < 300) return;
    sStateCallbacks = 0;
#ifdef NITRO_INTEGRITY_HOST_TEST
    extern Word TestReadWord(Word);
    if (TestReadWord(0x80000000u) != 0x524d4350u) return;
#else
    if (*reinterpret_cast<const volatile Word *>(0x80000000) != 0x524d4350u) return;
#endif
    const RKNet::Controller *network = RKNet::Controller::sInstance;
    const Raceinfo *race = Raceinfo::sInstance;
    if (!network || network->currentSub < 0 || network->currentSub > 1
        || network->roomType == RKNet::ROOMTYPE_NONE || !race || race->stage != RACESTAGE_RACE) return;
    const Item::Manager *items = Item::Manager::sInstance;
    const Kart::Manager *karts = Kart::Manager::sInstance;
    if (!items || !items->players || !items->playerCount || items->playerCount > 12
        || !karts || !karts->players || !karts->playerCount || karts->playerCount > 12) return;
    for (Word i = 0; i < items->playerCount; ++i) {
        const Item::Player &item = items->players[i];
        if (!item.isHuman || item.isRemote || item.id >= karts->playerCount) continue;
        const Kart::Player *kart = karts->players[item.id];
        if (!kart || !kart->pointers.kartMovement || !kart->pointers.kartBody
            || !kart->pointers.kartBody->kartPhysicsHolder) continue;
        const Kart::Movement &move = *kart->pointers.kartMovement;
        const Vec3 &position = kart->pointers.kartBody->kartPhysicsHolder->position;
        const bool finite = Finite(move.engineSpeed) && Finite(move.hardSpeedLimit)
            && Finite(position.x) && Finite(position.y) && Finite(position.z);
        const int id = static_cast<int>(item.inventory.currentItemId);
        const bool enumInBaseRange = id >= 0 && id <= 20;
        OS::Report("[NitroIntegrity state] local=%u item=%d count=%u base_enum=%u finite=%u speed=%.2f hard=%.2f xyz=%.2f,%.2f,%.2f\n",
            static_cast<Word>(item.id), id, static_cast<Word>(item.inventory.currentItemCount),
            enumInBaseRange ? 1u : 0u, finite ? 1u : 0u,
            move.engineSpeed, move.hardSpeedLimit, position.x, position.y, position.z);
        // Diagnostics only. A value range is not an entitlement proof; speed caps
        // are mutable too. Never punish an unchanged inventory or current place.
    }
}
static RaceLoadHook stateResetHook(ResetStateAudit);
static RaceFrameHook stateAuditHook(AuditLocalState);
} }
