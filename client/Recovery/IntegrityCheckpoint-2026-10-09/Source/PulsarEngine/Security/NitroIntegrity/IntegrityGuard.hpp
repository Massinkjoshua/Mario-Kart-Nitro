#ifndef NITRO_INTEGRITY_GUARD_HPP
#define NITRO_INTEGRITY_GUARD_HPP
namespace Pulsar { namespace NitroIntegrity {
// Call at the top of the EXISTING auth-send hook, before its payloadReady path.
// In audit mode: always returns true. In enforcement mode: rejects unverified state.
bool CanEnterOnline();
} }
#endif
