package database

import "testing"

func TestValidateHashRejectsUnapprovedPacks(t *testing.T) {
	mutex.Lock()
	old := hashes
	hashes = HashStore{7: {3: {PAL: "0123456789012345678901234567890123456789"}}}
	mutex.Unlock()
	t.Cleanup(func() { mutex.Lock(); hashes = old; mutex.Unlock() })
	for _, tc := range []struct {
		pack, version uint32
		region        Region
		hash          string
		want          bool
	}{
		{7, 3, R_PAL, "0123456789012345678901234567890123456789", true},
		{7, 3, R_PAL, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", false},
		{8, 3, R_PAL, "0123456789012345678901234567890123456789", false},
		{7, 4, R_PAL, "0123456789012345678901234567890123456789", false},
		{7, 3, R_NTSCU, "", false},
		{7, 3, Region(255), "0123456789012345678901234567890123456789", false},
	} {
		if got := ValidateHash(tc.pack, tc.version, tc.region, tc.hash); got != tc.want {
			t.Errorf("pack %d version %d region %d: got %v, want %v", tc.pack, tc.version, tc.region, got, tc.want)
		}
	}
}
