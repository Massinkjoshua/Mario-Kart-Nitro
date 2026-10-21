package gpcm

import (
	"context"
	"fmt"
	"time"
	"wwfc/database"
)

func (g *GameSpySession) saveNitroRatingsReport(db database.NitroRatingsDB, value string) error {
	if !g.LoggedIn || !g.DeviceAuthenticated || g.GameName != "mariokartwii" || g.User.Restricted || g.User.ProfileId == 0 {
		return fmt.Errorf("unauthorized rating report")
	}
	r, err := database.ParseNitroRatingsReport(value)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return database.SaveNitroRatings(db, ctx, g.User.ProfileId, r)
}
