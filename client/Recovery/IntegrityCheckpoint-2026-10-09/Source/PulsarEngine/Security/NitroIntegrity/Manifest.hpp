#ifndef NITRO_INTEGRITY_MANIFEST_HPP
#define NITRO_INTEGRITY_MANIFEST_HPP
#include <Security/NitroIntegrity/Policy.hpp>
// GENERATED: selected original code words; live online compatibility is NOT verified.
// Reference Code.pul SHA256: 0f5364590f8ec8164f06a934666bdbd9252b87edf7d31c79bf93e189f30c15bc
namespace Pulsar { namespace NitroIntegrity {
static const bool ManifestRuntimeReviewed = false;
static const CheckWord kChecks[] = {
    {0x800ed018u, 0x80c30004u, 0u}, // network_identity_b
    {0x801d0e50u, 0x38a00006u, 0u}, // network_identity_a
    {0x805334b0u, 0x38000001u, 1u}, // start_countdown_a
    {0x80533510u, 0x2c000002u, 1u}, // start_countdown_b
    {0x80534a00u, 0xb0a30024u, 1u}, // checkpoint_progress
    {0x80535c74u, 0x807d0048u, 1u}, // race_clock_value
    {0x80535c78u, 0x38030001u, 1u}, // race_clock_increment
    {0x80567e6cu, 0xc05f0004u, 1u}, // hit_response_b
    {0x8057ac2cu, 0xd01d0020u, 1u}, // engine_speed_write
    {0x8057c438u, 0xd00300b8u, 1u}, // terrain_penalty_a
    {0x8057c4b4u, 0xd01f00b8u, 1u}, // terrain_penalty_b
    {0x8057c510u, 0xd01f00b8u, 1u}, // terrain_penalty_c
    {0x8058187cu, 0x90030008u, 1u}, // damage_immunity
    {0x80581aa8u, 0x4082005cu, 1u}, // ink_effect
    {0x805872d8u, 0x38630001u, 1u}, // drafting_charge
    {0x805884e4u, 0x38840001u, 1u}, // wheelie_duration
    {0x805b5628u, 0xd03e0068u, 1u}, // position_x_write
    {0x805b5634u, 0xd33e006cu, 1u}, // position_y_write
    {0x805b5640u, 0xd2fe0070u, 1u}, // position_z_write
    {0x807a4ac8u, 0x3800005au, 1u}, // bomb_timer_b
    {0x807a5bf4u, 0x38a0012cu, 1u}, // bomb_timer_a
    {0x807b1dd0u, 0x3800009fu, 1u}, // pow_delay
    {0x807b5e58u, 0x901a01c8u, 1u}, // projectile_lifetime
};
static const unsigned int kCheckCount = sizeof(kChecks) / sizeof(kChecks[0]);
} }
#endif
