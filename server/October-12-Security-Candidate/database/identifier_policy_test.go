package database

import "testing"

func TestPlaceholdersCannotReplaceKnownIdentifiers(t *testing.T) {
	if hasKnownIdentifier([]uint32{0}, uint32(0)) {
		t.Fatal("initial device placeholder treated as a recorded console")
	}
	if !hasKnownIdentifier([]uint32{123, 0}, uint32(0)) {
		t.Fatal("device placeholder masked an existing console")
	}
	if hasKnownIdentifier([]string{""}, "") {
		t.Fatal("initial serial placeholder treated as a recorded serial")
	}
	if !hasKnownIdentifier([]string{"LEH123456789", ""}, "") {
		t.Fatal("serial placeholder masked an existing serial")
	}
}

func TestAdditionalIdentifierPolicies(t *testing.T) {
	old := "203.0.113.10"
	empty := ""
	for _, tc := range []struct {
		policy   string
		previous *string
		current  string
		want     bool
	}{
		{"never", &old, old, false},
		{"", &old, old, false},
		{"typo", &old, old, false},
		{"always", nil, "203.0.113.11", true},
		{"SameIPAddress", &old, old, true},
		{"SameIPAddress", &old, "203.0.113.11", false},
		{"SameIPAddress", nil, old, false},
		{"SameIPAddress", &empty, "", false},
	} {
		if got := allowAdditionalIdentifier(tc.policy, tc.previous, tc.current); got != tc.want {
			t.Errorf("policy %q: got %v, want %v", tc.policy, got, tc.want)
		}
	}
}
