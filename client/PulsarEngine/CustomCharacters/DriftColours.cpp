// Reconstructed from the released PAL effect functions, 16 October 2026; GPLv3.
// Palette and native-call behavior are verified against the supplied release.
#include <CustomCharacters/CustomCharacters.hpp>
#include <core/egg/Effect/Effect.hpp>

namespace Pulsar { namespace CustomCharacters {
#include <CustomCharacters/DriftColours.inc>

static bool HasEffectPrefix(const char *name, const char *prefix) {
    while (*prefix != '\0') {
        if (*name++ != *prefix++) return false;
    }
    return true;
}

void ApplySkinDriftColour(EGG::Effect *effect) {
    if (effect == nullptr) return;
    const bool spark = HasEffectPrefix(effect->name, "rk_driftSpark");
    const bool purple = HasEffectPrefix(effect->name, "rk_purpleTurbo");
    if (!spark && !purple && !HasEffectPrefix(effect->name, "rk_miniTurbo")) return;
    const u32 playerId = static_cast<u32>(effect->creatorIdx) - 2u;
    const Racedata *racedata = Racedata::sInstance;
    if (playerId >= ONLINE_PLAYER_COUNT || racedata == nullptr || playerId >= racedata->racesScenario.playerCount) return;
    const CharacterId character = racedata->racesScenario.players[playerId].characterId;
    if (static_cast<u32>(character) >= CHARACTER_COUNT) return;
    u8 table = RaceSkinTable(static_cast<u8>(playerId), character);
    if (table >= TABLE_COUNT) table = TABLE_DEFAULT;
    const u8 *rgb = kSkinDriftColours[character][table];
    u32 white = spark && effect->name[13] == '1' ? 30 : 0;
    if (purple || (spark && effect->name[13] == '3')) white = 16;
    const u8 red = static_cast<u8>((rgb[0] * (100 - white) + 255 * white) / 100);
    const u8 green = static_cast<u8>((rgb[1] * (100 - white) + 255 * white) / 100);
    const u8 blue = static_cast<u8>((rgb[2] * (100 - white) + 255 * white) / 100);
    effect->EGG::Effect::SetColor(red, green, blue, 255);
}

void CreateSkinDriftEffect(EGG::Effect *effect) {
    effect->EGG::Effect::Create();
    ApplySkinDriftColour(effect);
}

void UpdateSkinDriftEffect(EGG::Effect *effect) {
    effect->EGG::Effect::Update();
    ApplySkinDriftColour(effect);
}
// The supplied release installs these vtable slots in PAL only. The post-link
// regional policy removes the untranslated writes in the other two regions.
kmWritePointer(0x802a2dd4, CreateSkinDriftEffect);
kmWritePointer(0x802a2e48, UpdateSkinDriftEffect);
} }
