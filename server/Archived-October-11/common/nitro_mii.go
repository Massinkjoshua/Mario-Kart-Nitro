package common

import (
	"encoding/base64"
	"encoding/binary"
	"strings"
)

// NitroPublicMii exports only the Wii Mii, without FriendInfo's trailing
// account data. QR2 sends 74 bytes; RFL::StoreData also needs a valid CRC.
func NitroPublicMii(value string) string {
	value = strings.TrimSpace(value)
	if value == "" || len(value) > 4096 {
		return ""
	}
	var data []byte
	for _, encoding := range []*base64.Encoding{base64.StdEncoding, base64.RawStdEncoding, base64.URLEncoding, base64.RawURLEncoding} {
		decoded, err := encoding.DecodeString(value)
		if err == nil {
			data = decoded
			break
		}
	}
	if len(data) < 0x4A {
		return ""
	}
	var mii Mii
	copy(mii[:0x4A], data[:0x4A])
	nonzero := false
	for _, b := range mii[:0x4A] {
		nonzero = nonzero || b != 0
	}
	if !nonzero {
		return ""
	}
	// Match the existing public Mii policy: remove birthdays, creation time,
	// console identifier and creator name, while preserving appearance/name.
	mii[0] &= 0xC0
	mii[1] &= 0x1F
	mii[0x18] &= 0xE0
	for i := 0x19; i < 0x20; i++ {
		mii[i] = 0
	}
	for i := 0x36; i < 0x4A; i++ {
		mii[i] = 0
	}
	// Appending this remainder makes RFLCalculateCRC over all 76 bytes zero.
	binary.BigEndian.PutUint16(mii[0x4A:], mii.RFLCalculateCRC())
	return base64.StdEncoding.EncodeToString(mii[:])
}
