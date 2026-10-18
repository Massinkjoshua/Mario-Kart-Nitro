#ifndef NITRO_INTEGRITY_POLICY_HPP
#define NITRO_INTEGRITY_POLICY_HPP
// Portable C++98. Checks signal a modified instruction, not an account conviction.
namespace Pulsar { namespace NitroIntegrity {
typedef unsigned int Word;
typedef char WordMustBe32Bit[sizeof(Word) == 4 ? 1 : -1];
struct CheckWord { Word address, expected, phase; }; // 0: DOL, 1: StaticR
typedef Word (*ReadWord)(Word address);
struct Scan {
    Word checked, mismatches, firstAddress, expected, actual;
    bool valid;
    Scan() : checked(0), mismatches(0), firstAddress(0), expected(0), actual(0), valid(true) {}
};
inline Scan Inspect(const CheckWord *checks, Word count, bool relReady, ReadWord read) {
    Scan result;
    if (!checks || !read || !count || count > 256) { result.valid = false; return result; }
    // Validate the entire table before making even the first memory read.
    for (Word i = 0; i < count; ++i) {
        const CheckWord &c = checks[i];
        if ((c.address & 3) || c.address < 0x80004000u || c.address > 0x817ffffcu
            || c.phase > 1) { result.valid = false; return result; }
    }
    for (Word i = 0; i < count; ++i) {
        const CheckWord &c = checks[i];
        if (c.phase && !relReady) continue;
        const Word value = read(c.address);
        ++result.checked;
        if (value == c.expected) continue;
        if (!result.mismatches) {
            result.firstAddress = c.address; result.expected = c.expected; result.actual = value;
        }
        ++result.mismatches;
    }
    return result;
}
inline bool DenyOnline(bool enforce, bool runtimeReviewed, bool supportedRegion,
                       bool relReady, const Scan &scan) {
    return enforce && (!runtimeReviewed || !supportedRegion || !relReady
                       || !scan.valid || !scan.checked || scan.mismatches != 0);
}
// This identifies a GCT HEADER, not an active interpreter. Never an enforcement input.
inline Word FindGctHeader(ReadWord read) {
    if (!read) return 0;
    for (Word address = 0x80001800u; address <= 0x80002ff8u; address += 4)
        if (read(address) == 0x00d0c0deu && read(address + 4) == 0x00d0c0deu)
            return address;
    return 0;
}
inline bool Finite(float value) { return value >= -3.402823e38f && value <= 3.402823e38f; }
} }
#endif
