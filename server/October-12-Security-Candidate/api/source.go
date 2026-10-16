// Modified for Mario Kart Nitro, 16 October 2026; GNU AGPLv3.
package api

import (
	"errors"
	"net/http"
	"net/url"
	"strings"
)

// This must identify source corresponding to the actual deployed server.
// A route or placeholder URL alone does not make the source available.
var sourceArchiveURL string

type SourceResponse struct {
	SourceURL string `json:"source_url,omitempty"`
	License   string `json:"license"`
	Upstream  string `json:"upstream"`
	Success   bool   `json:"success"`
	Error     string `json:"error,omitempty"`
}

var SourceRoute = MakeRouteSpec[struct{}, SourceResponse](false, "/api/source", handleSource, http.MethodGet)

func handleSource(_ any, _ bool, _ *http.Request) (any, int, error) {
	response := SourceResponse{
		License:  "GNU AGPLv3",
		Upstream: "https://github.com/Retro-Rewind-Team/wfc-server",
	}
	location := strings.TrimSpace(sourceArchiveURL)
	parsed, err := url.Parse(location)
	if err != nil || parsed.Host == "" || parsed.User != nil ||
		(parsed.Scheme != "https" && parsed.Scheme != "http") {
		return response, http.StatusServiceUnavailable, errors.New("Public source URL is not configured")
	}
	response.SourceURL = location
	return response, http.StatusOK, nil
}
