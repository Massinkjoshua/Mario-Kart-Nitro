package common

import (
	"bytes"
	"encoding/base64"
	"testing"
)

func TestNitroPublicMiiFormatsPrivacyAndCRC(t *testing.T) {
	fixture := make([]byte, 0x4A)
	for i := range fixture {
		fixture[i] = byte(i + 1)
	}
	fixture[0x18] = 0xAB
	for _, size := range []int{74, 76, 96} {
		input := append(append([]byte{}, fixture...), bytes.Repeat([]byte{0xFF}, size-74)...)
		for _, encoding := range []*base64.Encoding{base64.StdEncoding, base64.RawStdEncoding, base64.URLEncoding, base64.RawURLEncoding} {
			output := NitroPublicMii(encoding.EncodeToString(input))
			decoded, err := base64.StdEncoding.DecodeString(output)
			if err != nil || len(decoded) != 76 {
				t.Fatalf("input size %d: invalid output", size)
			}
			mii := Mii(decoded)
			if mii.RFLCalculateCRC() != 0 {
				t.Fatal("sanitized Mii must retain a valid RFL checksum")
			}
			if !bytes.Equal(decoded[2:0x18], fixture[2:0x18]) || !bytes.Equal(decoded[0x20:0x36], fixture[0x20:0x36]) {
				t.Fatal("display name or appearance changed")
			}
			if decoded[0] != fixture[0]&0xC0 || decoded[1] != fixture[1]&0x1F || decoded[0x18] != 0xA0 || !bytes.Equal(decoded[0x19:0x20], make([]byte, 7)) || !bytes.Equal(decoded[0x36:0x4A], make([]byte, 20)) {
				t.Fatal("private Mii metadata was retained")
			}
			if NitroPublicMii(output) != output {
				t.Fatal("normalization must be stable")
			}
		}
	}
}

func TestNitroPublicMiiRejectsMissingOrTruncatedData(t *testing.T) {
	for _, value := range []string{"", "bad!", base64.StdEncoding.EncodeToString(make([]byte, 73)), base64.StdEncoding.EncodeToString(make([]byte, 76))} {
		if NitroPublicMii(value) != "" {
			t.Fatal("missing or malformed Mii accepted")
		}
	}
}
