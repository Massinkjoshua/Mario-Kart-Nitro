package database

import (
	"context"
	"errors"
	"github.com/jackc/pgconn"
	"github.com/jackc/pgx/v4"
	"sync"
	"sync/atomic"
	"testing"
)

type ratingDB struct {
	calls  int
	args   []interface{}
	vr, br int
	err    error
	tag    pgconn.CommandTag
}

func (d *ratingDB) Exec(_ context.Context, _ string, args ...interface{}) (pgconn.CommandTag, error) {
	d.calls++
	d.args = args
	return d.tag, d.err
}
func (d *ratingDB) QueryRow(_ context.Context, _ string, args ...interface{}) pgx.Row {
	d.calls++
	d.args = args
	return d
}
func (d *ratingDB) Scan(dest ...interface{}) error {
	if d.err != nil {
		return d.err
	}
	*dest[0].(*int) = d.vr
	*dest[1].(*int) = d.br
	return nil
}
func TestNitroReportParsing(t *testing.T) {
	for _, v := range []string{"vr=1|br=1000000", "vr=5000|br=5000", "br=8000|vr=9000"} {
		if _, e := ParseNitroRatingsReport(v); e != nil {
			t.Fatal(v, e)
		}
	}
	for _, v := range []string{"", "vr=0|br=1", "vr=1000001|br=1", "vr=-1|br=1", "vr=+1|br=1", "vr=NaN|br=1", "vr=1.5|br=1", "vr= 1|br=1", "vr=1|br=1 ", "vr=1|vr=2", "br=1|br=2", "vr=1", "vr=1|br=2|pid=3", "pid=1|vr=2", "vr=1=2|br=1", "vr=99999999999999999999|br=1", "vr=1|br="} {
		if _, e := ParseNitroRatingsReport(v); e == nil {
			t.Error("accepted", v)
		}
	}
}
func TestNitroSaveIdentityBounds(t *testing.T) {
	d := &ratingDB{tag: pgconn.CommandTag("INSERT 0 1")}
	if e := SaveNitroRatings(d, context.Background(), 42, NitroRatings{5000, 6000}); e != nil {
		t.Fatal(e)
	}
	if d.args[0] != uint32(42) || d.args[1] != 5000 || d.args[2] != 6000 {
		t.Fatal(d.args)
	}
	for _, tc := range []struct {
		pid uint32
		r   NitroRatings
	}{{0, NitroRatings{1, 1}}, {2147483648, NitroRatings{1, 1}}, {42, NitroRatings{0, 1}}, {42, NitroRatings{1, 1000001}}} {
		d.calls = 0
		if e := SaveNitroRatings(d, context.Background(), tc.pid, tc.r); e == nil || d.calls != 0 {
			t.Fatal(tc)
		}
	}
	d.tag = pgconn.CommandTag("INSERT 0 0")
	if e := SaveNitroRatings(d, context.Background(), 42, NitroRatings{1, 1}); e == nil {
		t.Fatal("missing profile accepted")
	}
	d.err = errors.New("down")
	if e := SaveNitroRatings(d, context.Background(), 42, NitroRatings{1, 1}); e == nil {
		t.Fatal("database failure ignored")
	}
}
func TestNitroReadStates(t *testing.T) {
	for _, tc := range []struct {
		vr, br         int
		err            error
		found, wantErr bool
	}{{5000, 6000, nil, true, false}, {1, 1000000, nil, true, false}, {0, 0, pgx.ErrNoRows, false, false}, {0, 0, errors.New("down"), false, true}, {0, 1, nil, false, true}, {1, 1000001, nil, false, true}} {
		d := &ratingDB{vr: tc.vr, br: tc.br, err: tc.err}
		_, found, e := GetNitroRatings(d, context.Background(), 42)
		if found != tc.found || (e != nil) != tc.wantErr {
			t.Fatal(tc, found, e)
		}
	}
}

type schemaDB struct{ active, max, calls atomic.Int32 }

func (d *schemaDB) Exec(context.Context, string, ...interface{}) (pgconn.CommandTag, error) {
	n := d.active.Add(1)
	if n > 1 {
		d.max.Store(n)
	}
	d.calls.Add(1)
	d.active.Add(-1)
	return pgconn.CommandTag("CREATE TABLE"), nil
}
func (d *schemaDB) QueryRow(context.Context, string, ...interface{}) pgx.Row {
	panic("unexpected query")
}
func TestNitroSchemaConcurrentStartup(t *testing.T) {
	d := &schemaDB{}
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if e := InitNitroRatings(d, context.Background()); e != nil {
				t.Error(e)
			}
		}()
	}
	wg.Wait()
	if d.max.Load() > 1 || d.calls.Load() != 20 {
		t.Fatal("overlapping schema initialization")
	}
}
