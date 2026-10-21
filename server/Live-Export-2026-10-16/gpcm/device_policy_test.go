package gpcm

import "testing"

func TestDefaultAndLeakedDevicePolicies(t *testing.T) {
	for _, allowDefault := range []bool{false, true} {
		if got := prohibitedDeviceID(defaultDolphinDeviceID, allowDefault); got == allowDefault {
			t.Errorf("default Dolphin policy ignored: allowDefault=%v", allowDefault)
		}
		if !prohibitedDeviceID(commonDeviceIds[0], allowDefault) {
			t.Fatal("leaked console keys must be rejected under either policy")
		}
		if prohibitedDeviceID(0x12345678, allowDefault) {
			t.Fatal("individual console ID rejected")
		}
	}
}
