package database

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgconn"
	"github.com/jackc/pgx/v4"
	"strconv"
	"strings"
	"sync"
)

// Ratings use the client's displayed/wire scale, not internal floats.
type NitroRatings struct {
	VR int
	BR int
}
type NitroRatingsDB interface {
	Exec(context.Context, string, ...interface{}) (pgconn.CommandTag, error)
	QueryRow(context.Context, string, ...interface{}) pgx.Row
}

var nitroRatingsSchemaMu sync.Mutex

const nitroRatingsSchema = `CREATE TABLE IF NOT EXISTS nitro_profile_ratings (
 profile_id BIGINT PRIMARY KEY REFERENCES users(profile_id) ON DELETE CASCADE,
 vr INTEGER NOT NULL CHECK (vr BETWEEN 1 AND 1000000),
 br INTEGER NOT NULL CHECK (br BETWEEN 1 AND 1000000),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)`

func InitNitroRatings(db NitroRatingsDB, ctx context.Context) error {
	// API and GPCM are started concurrently in this server process.
	nitroRatingsSchemaMu.Lock()
	defer nitroRatingsSchemaMu.Unlock()
	_, err := db.Exec(ctx, nitroRatingsSchema)
	return err
}
func ParseNitroRatingsReport(value string) (NitroRatings, error) {
	var r NitroRatings
	if len(value) > 32 {
		return r, fmt.Errorf("rating report too long")
	}
	fields := strings.Split(value, "|")
	if len(fields) != 2 {
		return r, fmt.Errorf("expected vr and br")
	}
	seen := map[string]bool{}
	for _, field := range fields {
		pair := strings.Split(field, "=")
		if len(pair) != 2 || (pair[0] != "vr" && pair[0] != "br") || seen[pair[0]] || len(pair[1]) == 0 || len(pair[1]) > 7 {
			return NitroRatings{}, fmt.Errorf("invalid rating field")
		}
		for _, ch := range pair[1] {
			if ch < '0' || ch > '9' {
				return NitroRatings{}, fmt.Errorf("rating must be decimal digits")
			}
		}
		n, err := strconv.Atoi(pair[1])
		if err != nil || n < 1 || n > 1000000 {
			return NitroRatings{}, fmt.Errorf("rating out of range")
		}
		seen[pair[0]] = true
		if pair[0] == "vr" {
			r.VR = n
		} else {
			r.BR = n
		}
	}
	return r, nil
}
func SaveNitroRatings(db NitroRatingsDB, ctx context.Context, pid uint32, r NitroRatings) error {
	if pid == 0 || pid > 2147483647 || r.VR < 1 || r.VR > 1000000 || r.BR < 1 || r.BR > 1000000 {
		return fmt.Errorf("invalid profile or ratings")
	}
	// Identity comes from the logged-in session. Recheck the current ban in SQL.
	tag, err := db.Exec(ctx, `INSERT INTO nitro_profile_ratings (profile_id,vr,br)
 SELECT profile_id,$2,$3 FROM users WHERE profile_id=$1 AND NOT COALESCE(has_ban,false)
 ON CONFLICT (profile_id) DO UPDATE SET vr=EXCLUDED.vr,br=EXCLUDED.br,updated_at=CURRENT_TIMESTAMP`, pid, r.VR, r.BR)
	if err != nil {
		return err
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("profile unavailable")
	}
	return nil
}
func GetNitroRatings(db NitroRatingsDB, ctx context.Context, pid uint32) (NitroRatings, bool, error) {
	var r NitroRatings
	err := db.QueryRow(ctx, `SELECT r.vr,r.br FROM nitro_profile_ratings r JOIN users u USING(profile_id)
 WHERE r.profile_id=$1 AND NOT COALESCE(u.has_ban,false)`, pid).Scan(&r.VR, &r.BR)
	if errors.Is(err, pgx.ErrNoRows) {
		return r, false, nil
	}
	if err != nil {
		return r, false, err
	}
	if r.VR < 1 || r.VR > 1000000 || r.BR < 1 || r.BR > 1000000 {
		return NitroRatings{}, false, fmt.Errorf("stored rating out of range")
	}
	return r, true, nil
}
