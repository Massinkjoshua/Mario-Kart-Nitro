package gpcm

import (
	"context"
	"github.com/jackc/pgconn"
	"github.com/jackc/pgx/v4"
	"testing"
	"wwfc/database"
)

type ratingSessionStub struct {
	calls int
	pid   interface{}
}

func (d *ratingSessionStub) Exec(_ context.Context, _ string, args ...interface{}) (pgconn.CommandTag, error) {
	d.calls++
	d.pid = args[0]
	return pgconn.CommandTag("INSERT 0 1"), nil
}
func (d *ratingSessionStub) QueryRow(context.Context, string, ...interface{}) pgx.Row {
	panic("unexpected query")
}
func TestNitroSessionIdentity(t *testing.T) {
	valid := GameSpySession{LoggedIn: true, DeviceAuthenticated: true, GameName: "mariokartwii", User: database.User{ProfileId: 42}}
	d := &ratingSessionStub{}
	if e := valid.saveNitroRatingsReport(d, "vr=5000|br=6000"); e != nil || d.pid != uint32(42) {
		t.Fatal(e, d)
	}
	for i := 0; i < 6; i++ {
		g := valid
		switch i {
		case 0:
			g.LoggedIn = false
		case 1:
			g.DeviceAuthenticated = false
		case 2:
			g.GameName = "other"
		case 3:
			g.User.Restricted = true
		case 4:
			g.User.ProfileId = 0
		case 5:
			g.User.ProfileId = 2147483648
		}
		d := &ratingSessionStub{}
		if e := g.saveNitroRatingsReport(d, "vr=5000|br=6000"); e == nil || d.calls != 0 {
			t.Fatal(i, e, d)
		}
	}
	for _, v := range []string{"pid=99|vr=5000|br=6000", "vr=NaN|br=6000", "vr=5000|br=1000001"} {
		d := &ratingSessionStub{}
		if e := valid.saveNitroRatingsReport(d, v); e == nil || d.calls != 0 {
			t.Fatal(v, e)
		}
	}
}
