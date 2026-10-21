// Modified for Mario Kart Nitro on 2026-10-16; see docs/source_changes.json.
#ifndef MKNITRO_KAMEK_VALIDATION_HPP
#define MKNITRO_KAMEK_VALIDATION_HPP

// MKNitro, 2026-10-16. Portable validation shared by the game loader and host
// tests. This reconstructs observed guard behavior; it is not recovered v15
// source or a claim of binary identity. Inherits this project's GPLv3 licence.
namespace NitroKamek {
typedef unsigned char Byte;
typedef unsigned int Word;

inline Word Read32(const Byte *p) {
    return (Word(p[0]) << 24) | (Word(p[1]) << 16) | (Word(p[2]) << 8) | Word(p[3]);
}

struct Section {
    Word bss, code, ctorStart, ctorEnd;
};
struct Command {
    Word id, address, operands, values[2], next;
    bool absolute;
};

inline const char *SelectRegion(const Byte *header, Word fileLength, Word region,
                               Word &offset, Word &length) {
    if (fileLength < 16 || region > 3) return "Invalid Code.pul container header";
    Word end = 16;
    offset = 16;
    for (Word i = 0; i < 4; ++i) {
        Word size = Read32(header + i * 4);
        if (size > fileLength - end) return "Invalid Code.pul region bounds";
        if (i < region) offset += size;
        end += size;
    }
    length = Read32(header + region * 4);
    if (end != fileLength) return "Code.pul container length mismatch";
    if (length < 32) return "Missing or truncated Code.pul region";
    return 0;
}

inline Word OperandCount(Word command) {
    switch (command) {
        case 1: case 4: case 5: case 6: case 10:
        case 32: case 33: case 34: case 64: case 65: return 1;
        case 35: case 36: case 37: case 38: return 2;
        default: return 0;
    }
}

inline Word WriteWidth(Word command) {
    if (command == 34 || command == 38) return 1;
    if (command == 4 || command == 5 || command == 6 || command == 33 || command == 37) return 2;
    return 4;
}

inline bool HasTarget(Word command) {
    return command == 1 || command == 4 || command == 5 || command == 6 ||
           command == 10 || command == 35 || command == 64 || command == 65;
}

inline const char *ReadCommand(const Byte *data, Word length, Word cursor,
                              Word allocation, Command &out) {
    if (cursor > length || length - cursor < 4) return "Truncated Kamek command";
    Word header = Read32(data + cursor); cursor += 4;
    out.id = header >> 24;
    out.address = header & 0xffffff;
    out.operands = OperandCount(out.id);
    if (!out.operands) return "Unsupported Kamek command";
    out.absolute = out.address == 0xfffffe;
    if (out.absolute) {
        if (length - cursor < 4) return "Truncated Kamek address";
        out.address = Read32(data + cursor); cursor += 4;
    }
    if (length - cursor < out.operands * 4) return "Truncated Kamek operands";
    for (Word i = 0; i < out.operands; ++i) out.values[i] = Read32(data + cursor + i * 4);
    out.next = cursor + out.operands * 4;
    Word width = WriteWidth(out.id);
    // The supplied release intentionally has unaligned string/data writes.
    // Their addresses must not be rejected as malformed instruction patches.
    if (!out.absolute && (out.address > allocation || width > allocation - out.address))
        return "Kamek relative patch outside allocation";
    if (HasTarget(out.id) && !(out.values[0] & 0x80000000) && out.values[0] >= allocation)
        return "Kamek relative target outside allocation";
    return 0;
}

inline const char *ValidateSection(const Byte *data, Word length, Section &out) {
    if (length < 32) return "Truncated Kamek header";
    if (Read32(data) != 0x4b616d65 || data[4] != 'k' || data[5] != 0)
        return "Corrupted Kamek header";
    if (data[6] != 0 || data[7] != 2) return "Incompatible Kamek version";
    out.bss = Read32(data + 8); out.code = Read32(data + 12);
    out.ctorStart = Read32(data + 16); out.ctorEnd = Read32(data + 20);
    if (out.code > length - 32 || out.bss > 0xffffffffU - out.code)
        return "Invalid Kamek section bounds";
    if (out.ctorStart > out.ctorEnd || out.ctorEnd > out.code ||
        ((out.ctorStart | out.ctorEnd) & 3)) return "Invalid Kamek constructor bounds";
    Word cursor = 32 + out.code;
    while (cursor < length) {
        Command command;
        const char *error = ReadCommand(data, length, cursor, out.code + out.bss, command);
        if (error) return error;
        cursor = command.next;
    }
    if (cursor != length) return "Kamek command length mismatch";
    return 0;
}
} // namespace NitroKamek
#endif
