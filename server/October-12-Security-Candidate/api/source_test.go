// Mario Kart Nitro source-offer regression tests, 16 October 2026; GNU AGPLv3.
package api

import (
	"encoding/json"
	"net/http"
	"strings"
	"testing"
)

func TestPublicSourceOffer(t *testing.T) {
	previous := sourceArchiveURL
	t.Cleanup(func() { sourceArchiveURL = previous })
	if SourceRoute.RequiresSecret || SourceRoute.Path != "/api/source" ||
		len(SourceRoute.AllowedMethods) != 1 || SourceRoute.AllowedMethods[0] != http.MethodGet {
		t.Fatal("source must be a public GET route")
	}
	for _, test := range []struct {
		location string
		valid    bool
	}{
		{"", false},
		{"REPLACE_WITH_SOURCE_URL", false},
		{"file:///private/config.xml", false},
		{"https://private:secret@example.com/source.zip", false},
		{"https://example.com/nitro/source-v1.zip", true},
	} {
		sourceArchiveURL = test.location
		value, status, err := handleSource(nil, false, nil)
		response := value.(SourceResponse)
		if test.valid {
			if err != nil || status != http.StatusOK || response.SourceURL != test.location {
				t.Fatalf("valid source offer failed: %v, %d", err, status)
			}
		} else if err == nil || status != http.StatusServiceUnavailable || response.SourceURL != "" {
			t.Fatalf("invalid source location was offered: %q", test.location)
		}
		encoded, err := json.Marshal(response)
		if err != nil || strings.Contains(string(encoded), "private:secret") {
			t.Fatal("source response leaked credentials or failed encoding")
		}
	}
}
