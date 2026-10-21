package qr2

import (
	"strconv"
	"time"
	"wwfc/common"
)

// Read-only snapshots: do not use GetSessionServers, which averages room VR.
type NitroRatingSnapshot struct {
	ProfileID  uint32
	Name       string
	FriendCode string
	VR         int
	MiiData    string
}

func GetNitroRatingSnapshots() []NitroRatingSnapshot {
	mutex.Lock()
	defer mutex.Unlock()
	out := []NitroRatingSnapshot{}
	now := time.Now().Unix()
	for _, s := range sessions {
		if !s.Authenticated || s.LastKeepAlive < now-60 || s.login == nil || s.login.Restricted || s.Data["gamename"] != "mariokartwii" {
			continue
		}
		vr, err := strconv.Atoi(s.Data["ev"])
		if err != nil || vr < 1 || vr > 1000000 {
			continue
		}
		name := s.Data["+mii_name0"]
		if name == "" {
			name = s.login.InGameName
		}
		fc := ""
		if len(s.login.FriendKeyGame) == 4 {
			fc = common.CalcFriendCodeString(s.login.ProfileID, s.login.FriendKeyGame)
		}
		out = append(out, NitroRatingSnapshot{ProfileID: s.login.ProfileID, Name: name, FriendCode: fc, VR: vr, MiiData: common.NitroPublicMii(s.Data["+mii0"])})
	}
	return out
}
