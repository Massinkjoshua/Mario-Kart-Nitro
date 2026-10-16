package api

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
	"wwfc/common"
	"wwfc/logging"
	"wwfc/qr2"
)

type NitroLeaderboardPlayer struct {
	Rank       int       `json:"rank"`
	ProfileID  uint32    `json:"profile_id"`
	Name       string    `json:"name"`
	FriendCode string    `json:"friend_code"`
	VR         int       `json:"vr"`
	LastSeen   time.Time `json:"last_seen"`
	MiiData    string    `json:"miiData,omitempty"`
}
type NitroLeaderboardResponse struct {
	Players   []NitroLeaderboardPlayer `json:"players"`
	UpdatedAt time.Time                `json:"updated_at"`
	Source    string                   `json:"source"`
	Success   bool                     `json:"success"`
	Error     string                   `json:"error,omitempty"`
}

var NitroLeaderboardRoute = MakeRouteSpec[struct{}, NitroLeaderboardResponse](false, "/api/nitro/leaderboard", handleNitroLeaderboard, http.MethodGet)
var NitroInGameLeaderboardRoute = MakeRouteSpec[struct{}, NitroLeaderboardResponse](false, "/api/leaderboard/in-game", handleNitroInGameLeaderboard, http.MethodGet)

var nitroLeaderboardOnce sync.Once
var nitroStateMu sync.RWMutex
var nitroReady bool
var nitroUpdated time.Time

func initNitroLeaderboard() {
	nitroLeaderboardOnce.Do(func() {
		go func() {
			ticker := time.NewTicker(15 * time.Second)
			defer ticker.Stop()
			for {
				if err := refreshNitroLeaderboard(); err != nil {
					logging.Error("API:NitroLeaderboard", err)
				}
				select {
				case <-ticker.C:
				case <-PCountTickerQuit:
					return
				}
			}
		}()
	})
}
func refreshNitroLeaderboard() error {
	c, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	nitroStateMu.RLock()
	ready := nitroReady
	nitroStateMu.RUnlock()
	if !ready {
		_, err := pool.Exec(c, `CREATE TABLE IF NOT EXISTS nitro_vr_leaderboard (profile_id BIGINT PRIMARY KEY, name TEXT NOT NULL, friend_code TEXT NOT NULL, vr INTEGER NOT NULL CHECK (vr BETWEEN 1 AND 1000000), last_seen TIMESTAMPTZ NOT NULL)`)
		if err != nil {
			return fmt.Errorf("leaderboard table: %w", err)
		}
		_, err = pool.Exec(c, `CREATE TABLE IF NOT EXISTS nitro_player_miis (profile_id BIGINT PRIMARY KEY, mii_data TEXT NOT NULL, last_seen TIMESTAMPTZ NOT NULL)`)
		if err != nil {
			return fmt.Errorf("leaderboard Mii table: %w", err)
		}
		nitroStateMu.Lock()
		nitroReady = true
		nitroStateMu.Unlock()
	}
	players := qr2.GetNitroRatingSnapshots()
	if len(players) > 0 {
		tx, err := pool.Begin(c)
		if err != nil {
			return err
		}
		defer tx.Rollback(c)
		for _, p := range players {
			_, err = tx.Exec(c, `INSERT INTO nitro_vr_leaderboard VALUES ($1,$2,$3,$4,CURRENT_TIMESTAMP) ON CONFLICT (profile_id) DO UPDATE SET name=EXCLUDED.name,friend_code=EXCLUDED.friend_code,vr=EXCLUDED.vr,last_seen=EXCLUDED.last_seen`, p.ProfileID, p.Name, p.FriendCode, p.VR)
			if err != nil {
				return err
			}
			if p.MiiData != "" {
				_, err = tx.Exec(c, `INSERT INTO nitro_player_miis (profile_id,mii_data,last_seen) VALUES ($1,$2,CURRENT_TIMESTAMP) ON CONFLICT (profile_id) DO UPDATE SET mii_data=EXCLUDED.mii_data,last_seen=EXCLUDED.last_seen`, p.ProfileID, p.MiiData)
				if err != nil {
					return err
				}
			}
		}
		if err = tx.Commit(c); err != nil {
			return err
		}
	}
	nitroStateMu.Lock()
	nitroUpdated = time.Now().UTC()
	nitroStateMu.Unlock()
	return nil
}
func handleNitroLeaderboard(_ any, _ bool, r *http.Request) (any, int, error) {
	return handleNitroLeaderboardMode(r, false)
}

func handleNitroInGameLeaderboard(_ any, _ bool, r *http.Request) (any, int, error) {
	return handleNitroLeaderboardMode(r, true)
}

func handleNitroLeaderboardMode(r *http.Request, inGame bool) (any, int, error) {
	res := NitroLeaderboardResponse{Players: []NitroLeaderboardPlayer{}, Source: "latest_observed_vr"}
	nitroStateMu.RLock()
	ready := nitroReady
	res.UpdatedAt = nitroUpdated
	nitroStateMu.RUnlock()
	if !ready {
		res.Error = "Leaderboard is initializing"
		return res, http.StatusServiceUnavailable, fmt.Errorf("leaderboard unavailable")
	}
	q := strings.TrimSpace(r.URL.Query().Get("q"))
	if len(q) > 100 {
		res.Error = "Search is too long"
		return res, http.StatusBadRequest, fmt.Errorf("search too long")
	}
	limit := 100
	if raw := r.URL.Query().Get("limit"); !inGame && raw != "" {
		n, err := strconv.Atoi(raw)
		if err != nil || n < 1 || n > 200 {
			res.Error = "Limit must be 1–200"
			return res, http.StatusBadRequest, fmt.Errorf("invalid limit")
		}
		limit = n
	}
	offset := 0
	if inGame {
		page := 1
		if raw := r.URL.Query().Get("page"); raw != "" {
			n, err := strconv.Atoi(raw)
			if err != nil || n < 1 || n > 1000000 {
				return res, http.StatusBadRequest, fmt.Errorf("page must be 1–1000000")
			}
			page = n
		}
		// The game fetches five screens of ten rows per API page.
		limit = 50
		offset = (page - 1) * limit
	}
	c, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	// Rank before filtering; omit banned users and all private account fields.
	rows, err := pool.Query(c, `WITH ranked AS (SELECT row_number() OVER (ORDER BY l.vr DESC,l.profile_id ASC) AS rank,l.*,COALESCE(m.mii_data,'') AS saved_mii,COALESCE(u.mariokartwii_friend_info,'') AS stored_mii FROM nitro_vr_leaderboard l JOIN users u USING(profile_id) LEFT JOIN nitro_player_miis m USING(profile_id) WHERE NOT COALESCE(u.has_ban,false)) SELECT rank,profile_id,name,friend_code,vr,last_seen,saved_mii,stored_mii FROM ranked WHERE $1='' OR strpos(lower(name),lower($1))>0 OR replace(friend_code,'-','')=replace($1,'-','') OR profile_id::text=$1 ORDER BY rank LIMIT $2 OFFSET $3`, q, limit, offset)
	if err != nil {
		res.Error = "Leaderboard temporarily unavailable"
		return res, http.StatusServiceUnavailable, err
	}
	defer rows.Close()
	for rows.Next() {
		var p NitroLeaderboardPlayer
		var liveMii, storedMii string
		if err = rows.Scan(&p.Rank, &p.ProfileID, &p.Name, &p.FriendCode, &p.VR, &p.LastSeen, &liveMii, &storedMii); err != nil {
			return res, http.StatusInternalServerError, err
		}
		p.MiiData = common.NitroPublicMii(liveMii)
		if p.MiiData == "" {
			p.MiiData = common.NitroPublicMii(storedMii)
		}
		res.Players = append(res.Players, p)
	}
	if err = rows.Err(); err != nil {
		return res, http.StatusInternalServerError, err
	}
	res.Success = true
	return res, http.StatusOK, nil
}
