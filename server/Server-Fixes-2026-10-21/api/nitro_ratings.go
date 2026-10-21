package api

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"time"
	"wwfc/database"
)

// Omit found on errors: an outage must not look like a new profile to the client.
type NitroRatingsResponse struct {
	Found   *int   `json:"found,omitempty"`
	VR      int    `json:"vr,omitempty"`
	BR      int    `json:"br,omitempty"`
	Success bool   `json:"success"`
	Error   string `json:"error,omitempty"`
}

var NitroRatingsRoute = MakeRouteSpec[struct{}, NitroRatingsResponse](false, "/api/mkw_rr_ratings", handleNitroRatings, http.MethodGet)

func handleNitroRatings(_ any, _ bool, r *http.Request) (any, int, error) {
	return queryNitroRatings(pool, r)
}
func queryNitroRatings(db database.NitroRatingsDB, r *http.Request) (any, int, error) {
	res := NitroRatingsResponse{}
	raw := r.URL.Query().Get("pid")
	if raw == "" || len(raw) > 10 {
		return res, 400, fmt.Errorf("invalid profile ID")
	}
	for _, ch := range raw {
		if ch < '0' || ch > '9' {
			return res, 400, fmt.Errorf("invalid profile ID")
		}
	}
	pid, err := strconv.ParseUint(raw, 10, 31)
	if err != nil || pid == 0 {
		return res, 400, fmt.Errorf("invalid profile ID")
	}
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	ratings, found, err := database.GetNitroRatings(db, ctx, uint32(pid))
	if err != nil {
		return res, 503, fmt.Errorf("ratings temporarily unavailable")
	}
	flag := 0
	if found {
		flag = 1
		res.VR, res.BR = ratings.VR, ratings.BR
	}
	res.Found, res.Success = &flag, true
	return res, 200, nil
}
