package api

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/jackc/pgconn"
	"github.com/jackc/pgx/v4"
	"net/http/httptest"
	"strings"
	"testing"
)

type ratingsAPIStub struct {
	calls  int
	vr, br int
	err    error
}

func (d *ratingsAPIStub) Exec(context.Context, string, ...interface{}) (pgconn.CommandTag, error) {
	panic("GET attempted write")
}
func (d *ratingsAPIStub) QueryRow(context.Context, string, ...interface{}) pgx.Row {
	d.calls++
	return d
}
func (d *ratingsAPIStub) Scan(v ...interface{}) error {
	if d.err != nil {
		return d.err
	}
	*v[0].(*int) = d.vr
	*v[1].(*int) = d.br
	return nil
}
func TestNitroResponseContract(t *testing.T) {
	for _, tc := range []struct {
		pid      string
		err      error
		status   int
		fragment string
	}{{"42", nil, 200, `"found":1`}, {"42", pgx.ErrNoRows, 200, `"found":0`}, {"42", errors.New("secret database detail"), 503, ""}, {"", nil, 400, ""}, {"0", nil, 400, ""}, {"-1", nil, 400, ""}, {"2147483648", nil, 400, ""}, {"abc", nil, 400, ""}} {
		d := &ratingsAPIStub{vr: 5000, br: 6000, err: tc.err}
		result, code, e := queryNitroRatings(d, httptest.NewRequest("GET", "/?pid="+tc.pid, nil))
		b, _ := json.Marshal(result)
		if code != tc.status || len(b) >= 256 {
			t.Fatal(tc, string(b), code)
		}
		if code == 200 {
			if e != nil || !strings.Contains(string(b), tc.fragment) {
				t.Fatal(string(b), e)
			}
		} else {
			if e == nil || strings.Contains(string(b), "found") || strings.Contains(e.Error(), "secret") {
				t.Fatal(string(b), e)
			}
		}
		if code == 400 && d.calls != 0 {
			t.Fatal("invalid input queried database")
		}
	}
	if NitroRatingsRoute.Path != "/api/mkw_rr_ratings" || len(NitroRatingsRoute.AllowedMethods) != 1 || NitroRatingsRoute.AllowedMethods[0] != "GET" {
		t.Fatal(NitroRatingsRoute)
	}
}
func TestNitroPagination(t *testing.T) {
	for _, tc := range []struct {
		q       string
		game    bool
		p, l, o int
		bad     bool
	}{{"", false, 1, 100, 0, false}, {"?page=2", false, 2, 100, 100, false}, {"?page=3&limit=200", false, 3, 200, 400, false}, {"?page=2&limit=1", false, 2, 1, 1, false}, {"?page=11", true, 11, 50, 500, false}, {"?page=52&limit=200", true, 52, 50, 2550, false}, {"?page=1000000&limit=200", false, 1000000, 200, 199999800, false}, {"?page=0", false, 0, 0, 0, true}, {"?page=-1", false, 0, 0, 0, true}, {"?page=1000001", false, 0, 0, 0, true}, {"?page=no", true, 0, 0, 0, true}, {"?page=99999999999999999999", false, 0, 0, 0, true}, {"?limit=201", false, 0, 0, 0, true}, {"?limit=0", false, 0, 0, 0, true}, {"?limit=x", false, 0, 0, 0, true}} {
		p, l, o, e := nitroLeaderboardPagination(httptest.NewRequest("GET", "/"+tc.q, nil), tc.game)
		if (e != nil) != tc.bad || (!tc.bad && (p != tc.p || l != tc.l || o != tc.o)) {
			t.Fatal(tc, p, l, o, e)
		}
	}
}
