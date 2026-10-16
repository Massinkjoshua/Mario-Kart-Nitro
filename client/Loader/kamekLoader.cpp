// Modified for Mario Kart Nitro on 2026-10-16; see docs/source_changes.json.
#include <core/nw4r/ut/Misc.hpp>
#include <kamekLoader.hpp>
#include "kamekValidation.hpp"

struct KBHeader {
    u32 magic1;  // 0x0
    u16 magic2;  // 0x2
    u16 version;  // 0x4
    u32 bssSize;  // 0x8
    u32 codeSize;  // 0xc
    u32 ctorStart;  // 0x10
    u32 ctorEnd;  // 0x14
    u32 length;  // 0x18
    u32 padding;  // 0x1c
};

#define kAddr32 1
#define kAddr16Lo 4
#define kAddr16Hi 5
#define kAddr16Ha 6
#define kRel24 10
#define kWrite32 32
#define kWrite16 33
#define kWrite8 34
#define kCondWritePointer 35
#define kCondWrite32 36
#define kCondWrite16 37
#define kCondWrite8 38
#define kBranch 64
#define kBranchLink 65

static void DisplayError(const LoaderParams *params, const char *str) {
    u32 fg = 0xFFFFFFFF, bg = 0;
    params->OSFatal(&fg, &bg, str);
    for (;;) {} // OSFatal is terminal even if an alternate implementation returns.
}

static inline u32 resolveAddress(u32 text, u32 address) {
    if (address & 0x80000000)
        return address;
    else
        return text + address;
}

#define kCommandHandler(name) \
    static inline const u8 *kHandle##name(const u8 *input, u32 text, u32 address)
#define kDispatchCommand(name)                       \
    case k##name:                                    \
        input = kHandle##name(input, text, address); \
        break

kCommandHandler(Addr32) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    *(u32 *)address = target;
    return input + 4;
}
kCommandHandler(Addr16Lo) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    *(u16 *)address = target & 0xFFFF;
    return input + 4;
}
kCommandHandler(Addr16Hi) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    *(u16 *)address = target >> 16;
    return input + 4;
}
kCommandHandler(Addr16Ha) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    *(u16 *)address = target >> 16;
    if (target & 0x8000)
        *(u16 *)address += 1;
    return input + 4;
}
kCommandHandler(Rel24) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    u32 delta = target - address;
    *(u32 *)address &= 0xFC000003;
    *(u32 *)address |= (delta & 0x3FFFFFC);
    return input + 4;
}
kCommandHandler(Write32) {
    u32 value = *(const u32 *)input;
    *(u32 *)address = value;
    return input + 4;
}
kCommandHandler(Write16) {
    u32 value = *(const u32 *)input;
    *(u16 *)address = value & 0xFFFF;
    return input + 4;
}
kCommandHandler(Write8) {
    u32 value = *(const u32 *)input;
    *(u8 *)address = value & 0xFF;
    return input + 4;
}
kCommandHandler(CondWritePointer) {
    u32 target = resolveAddress(text, *(const u32 *)input);
    u32 original = ((const u32 *)input)[1];
    if (*(u32 *)address == original)
        *(u32 *)address = target;
    return input + 8;
}
kCommandHandler(CondWrite32) {
    u32 value = *(const u32 *)input;
    u32 original = ((const u32 *)input)[1];
    if (*(u32 *)address == original)
        *(u32 *)address = value;
    return input + 8;
}
kCommandHandler(CondWrite16) {
    u32 value = *(const u32 *)input;
    u32 original = ((const u32 *)input)[1];
    if (*(u16 *)address == (original & 0xFFFF))
        *(u16 *)address = value & 0xFFFF;
    return input + 8;
}
kCommandHandler(CondWrite8) {
    u32 value = *(const u32 *)input;
    u32 original = ((const u32 *)input)[1];
    if (*(u8 *)address == (original & 0xFF))
        *(u8 *)address = value & 0xFF;
    return input + 8;
}
kCommandHandler(Branch) {
    *(u32 *)address = 0x48000000;
    return kHandleRel24(input, text, address);
}
kCommandHandler(BranchLink) {
    *(u32 *)address = 0x48000001;
    return kHandleRel24(input, text, address);
}

inline void cacheInvalidateAddress(register u32 address) {
    asm(dcbst 0, address;);
    asm(sync;);
    asm(icbi 0, address;);
}

// MKNitro 2026-10-16: guard reconstruction based on current release diagnostics.
// This is editable source and has host-tested parsing, not recovered v15 source.
static void LoadKamekBinary(LoaderParams *params, const void *binary, u32 binaryLength, bool isDol) {
    static u32 text = 0;
    const u8 *bytes = static_cast<const u8 *>(binary);
    NitroKamek::Section section;
    const char *error = NitroKamek::ValidateSection(bytes, binaryLength, section);
    if (error != nullptr) DisplayError(params, error);
    EGG::ExpHeap *heap = params->rkSystem->EGGSystem;
    if (isDol) text = reinterpret_cast<u32>(heap->alloc(section.code + section.bss, 0x20));
    if (text == 0) DisplayError(params, "FATAL ERROR: Out of code memory");
    if (isDol) {
        u8 *output = reinterpret_cast<u8 *>(text);
        for (u32 i = 0; i < section.code + section.bss; ++i) {
            output[i] = i < section.code ? bytes[32 + i] : 0;
            cacheInvalidateAddress(text + i);
        }
    }
    struct SHA1Context { u8 bytes[0x60]; } context;
    params->NETSHA1Init(&context);
    params->NETSHA1Update(&context, bytes + 32, section.code);
    params->NETSHA1GetDigest(&context, reinterpret_cast<void *>(0x800017b0));

    u32 cursor = 32 + section.code;
    u32 applied = 0, skipped = 0;
    while (cursor < binaryLength) {
        NitroKamek::Command command;
        error = NitroKamek::ReadCommand(bytes, binaryLength, cursor, section.code + section.bss, command);
        if (error != nullptr) DisplayError(params, error);
        // Consume the entire command before checking DOL/REL phase. The old
        // source skipped without consuming its address/operands on some paths.
        cursor = command.next;
        const bool inPhase = command.absolute
            ? (isDol ? command.address < params->relStart : command.address >= params->relStart)
            : isDol;
        if (!inPhase) { ++skipped; continue; }
        const u8 *input = bytes + command.next - command.operands * 4;
        const u8 cmd = static_cast<u8>(command.id);
        const u32 address = command.absolute ? command.address : text + command.address;
        switch (cmd) {
            case kAddr32:
                input = kHandleAddr32(input, text, address);
                break;
            case kAddr16Lo:
                input = kHandleAddr16Lo(input, text, address);
                break;
            case kAddr16Hi:
                input = kHandleAddr16Hi(input, text, address);
                break;
            case kAddr16Ha:
                input = kHandleAddr16Ha(input, text, address);
                break;
            case kRel24:
                input = kHandleRel24(input, text, address);
                break;
            case kWrite32:
                input = kHandleWrite32(input, text, address);
                break;
            case kWrite16:
                input = kHandleWrite16(input, text, address);
                break;
            case kWrite8:
                input = kHandleWrite8(input, text, address);
                break;
            case kCondWrite32:
                input = kHandleCondWrite32(input, text, address);
                break;
            case kCondWrite16:
                input = kHandleCondWrite16(input, text, address);
                break;
            case kCondWrite8:
                input = kHandleCondWrite8(input, text, address);
                break;
            case kCondWritePointer:
                input = kHandleCondWritePointer(input, text, address);
                break;
            case kBranch:
                input = kHandleBranch(input, text, address);
                break;
            case kBranchLink:
                input = kHandleBranchLink(input, text, address);
                break;
            default:
                params->OSReport("Unknown command: %d\n", cmd);
        }

        cacheInvalidateAddress(address);
        ++applied;
    }
    asmVolatile(sync;);
    asmVolatile(isync;);
    params->OSReport("[NitroSourceLoader] phase=%s applied=%u skipped=%u\n", isDol ? "DOL" : "REL", applied, skipped);
    typedef void (*Func)();
    if (isDol) {
        for (Func *f = reinterpret_cast<Func *>(text + section.ctorStart);
             f < reinterpret_cast<Func *>(text + section.ctorEnd); ++f) (*f)();
    }
}

void LoadKamekBinaryFromDisc(LoaderParams *params) {
    static void *codePulBuf = nullptr;
    static EGG::ExpHeap *codePulHeap = nullptr;
    static u32 sectionLength = 0;
    static bool relApplied = false;
    if (relApplied) return;
    const bool isDol = codePulBuf == nullptr;
    if (isDol) {
        const char *path = "/Binaries/Code.pul";
        const int entry = params->DVDConvertPathToEntrynum(path);
        if (entry < 0) DisplayError(params, "FATAL ERROR: Failed to locate /Binaries/Code.pul");
        DVD::FileInfo info;
        if (!params->DVDFastOpen(entry, &info)) DisplayError(params, "FATAL ERROR: Failed to open Code.pul");
        alignas(0x20) u8 header[32];
        if (info.length < sizeof(header) || params->DVDReadPrio(&info, header, sizeof(header), 0, 2) < static_cast<int>(sizeof(header)))
            DisplayError(params, "FATAL ERROR: Failed to read Code.pul header");
        u32 offset = 0;
        const char *error = NitroKamek::SelectRegion(header, info.length, params->region, offset, sectionLength);
        if (error != nullptr) DisplayError(params, error);
        if (sectionLength > 0xffffffe0U) DisplayError(params, "FATAL ERROR: Code.pul region size overflow");
        const u32 rounded = (sectionLength + 31) & ~31U;
        codePulHeap = params->rkSystem->EGGRootMEM2;
        if (codePulHeap != nullptr) codePulBuf = codePulHeap->alloc(rounded, -0x20);
        if (codePulBuf == nullptr) {
            codePulHeap = params->rkSystem->EGGSystem;
            codePulBuf = codePulHeap->alloc(rounded, -0x20);
        }
        if (codePulBuf == nullptr) DisplayError(params, "FATAL ERROR: Out of file memory");
        const int read = params->DVDReadPrio(&info, codePulBuf, rounded, offset, 2);
        params->DVDClose(&info);
        if (read < 0 || static_cast<u32>(read) < sectionLength)
            DisplayError(params, "FATAL ERROR: Failed to read Code.pul region");
    }
    LoadKamekBinary(params, codePulBuf, sectionLength, isDol);
    if (!isDol) {
        // Free with the heap that allocated the file, not an unrelated heap.
        codePulHeap->free(codePulBuf);
        codePulBuf = nullptr;
        sectionLength = 0;
        relApplied = true;
    }
}
