// Modified for Mario Kart Nitro on 2026-10-16; see docs/source_changes.json.
#ifndef MKNITRO_CUP_ORDER_HPP
#define MKNITRO_CUP_ORDER_HPP

namespace Pulsar {
// Use the config's permutation for any pack size, not RR's fixed track ranges.
// Malformed orders fall back to identity so lookups stay within the allocation.
inline bool BuildCupOrder(const unsigned short *source, unsigned int count,
                         unsigned short *order, unsigned short *inverse) {
    for (unsigned int i = 0; i < count; ++i) inverse[i] = 0xFFFF;
    bool valid = true;
    for (unsigned int i = 0; i < count; ++i) {
        const unsigned int track = source[i];
        if (track >= count || inverse[track] != 0xFFFF) {
            valid = false;
            break;
        }
        order[i] = static_cast<unsigned short>(track);
        inverse[track] = static_cast<unsigned short>(i);
    }
    if (!valid) {
        for (unsigned int i = 0; i < count; ++i) {
            order[i] = static_cast<unsigned short>(i);
            inverse[i] = static_cast<unsigned short>(i);
        }
    }
    return valid;
}
}  // namespace Pulsar
#endif
