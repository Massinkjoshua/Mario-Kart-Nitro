#ifndef NITRO_INTEGRITY_CONFIG_HPP
#define NITRO_INTEGRITY_CONFIG_HPP
// First build is explicitly AUDIT ONLY. Runtime-generated WFC patches are unknown.
// After clean-session review, also set ManifestRuntimeReviewed in Manifest.hpp.
#ifndef MKNITRO_AC_ENFORCE_INTEGRITY
#define MKNITRO_AC_ENFORCE_INTEGRITY 0
#endif
namespace Pulsar { namespace NitroIntegrity {
static const bool Enforce = MKNITRO_AC_ENFORCE_INTEGRITY != 0;
static const unsigned int CheckEveryCallbacks = 60;
} }
#endif
