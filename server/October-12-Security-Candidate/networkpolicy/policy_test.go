package networkpolicy

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/netip"
	"sync"
	"sync/atomic"
	"testing"
)

func TestClientIP(t *testing.T) {
	for input, want := range map[string]string{
		"203.0.113.2:1234":          "203.0.113.2",
		"[2001:db8::2]:1234":        "2001:db8::2",
		"[::ffff:203.0.113.2]:1234": "203.0.113.2",
		"2001:db8::2":               "2001:db8::2",
	} {
		got, err := ClientIP(input)
		if err != nil || got.String() != want {
			t.Errorf("%s: got %s, err %v", input, got, err)
		}
	}
	for _, input := range []string{"hostname:12", "not-an-ip", "[fe80::1%eth0]:12", ""} {
		if _, err := ClientIP(input); err == nil {
			t.Errorf("invalid peer accepted: %q", input)
		}
	}
}

func TestLocalCIDRRulesWithoutAPI(t *testing.T) {
	p, err := New(Config{DenyCIDRs: []string{"203.0.113.0/24", "2001:db8::/32"}, AllowCIDRs: []string{"203.0.113.9"}})
	if err != nil {
		t.Fatal(err)
	}
	for input, want := range map[string]bool{
		"203.0.113.1": true, "203.0.113.9": false, "203.0.114.1": false,
		"2001:db8::5": true, "::ffff:203.0.113.1": true,
	} {
		got, err := p.Check(context.Background(), netip.MustParseAddr(input))
		if err != nil || got != want {
			t.Errorf("%s: blocked=%v, err=%v", input, got, err)
		}
	}
	for _, entry := range []string{"bad-prefix", "203.0.113.0/99", "::ffff:203.0.113.1/80"} {
		if _, err := New(Config{DenyCIDRs: []string{entry}}); err == nil {
			t.Errorf("bad CIDR accepted: %s", entry)
		}
	}
}

func testPolicy(t *testing.T, c Config, handler http.HandlerFunc) *Policy {
	t.Helper()
	t.Setenv("MKNITRO_IPHUB_API_KEY", "")
	c.Enabled = true
	c.APIKey = "test-key"
	p, err := New(c)
	if err != nil {
		t.Fatal(err)
	}
	s := httptest.NewServer(handler)
	t.Cleanup(s.Close)
	p.endpoint = s.URL + "/"
	return p
}

func TestProviderClassifications(t *testing.T) {
	for _, tc := range []struct {
		block           int
		uncertain, want bool
	}{
		{0, false, false}, {1, false, true}, {2, false, false}, {2, true, true},
	} {
		t.Run(fmt.Sprintf("block%d-uncertain%v", tc.block, tc.uncertain), func(t *testing.T) {
			p := testPolicy(t, Config{BlockUncertain: tc.uncertain}, func(w http.ResponseWriter, r *http.Request) {
				if r.Header.Get("X-Key") != "test-key" {
					t.Error("API key missing from header")
				}
				fmt.Fprintf(w, `{"ip":"203.0.113.1","block":%d}`, tc.block)
			})
			got, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
			if err != nil || got != tc.want {
				t.Fatalf("blocked=%v, err=%v", got, err)
			}
		})
	}
}

func TestLookupFailuresUseOutagePolicy(t *testing.T) {
	for _, tc := range []struct {
		name, body string
		status     int
	}{
		{"rate-limit", "", 429}, {"server-error", "", 503},
		{"malformed", "invalid", 200}, {"missing-block", `{"ip":"203.0.113.1"}`, 200},
		{"wrong-ip", `{"ip":"203.0.113.2","block":0}`, 200},
		{"bad-class", `{"ip":"203.0.113.1","block":3}`, 200},
	} {
		for _, closed := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s-closed%v", tc.name, closed), func(t *testing.T) {
				p := testPolicy(t, Config{FailClosed: closed}, func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(tc.status)
					fmt.Fprint(w, tc.body)
				})
				got, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
				if err == nil || got != closed {
					t.Fatalf("blocked=%v, err=%v", got, err)
				}
			})
		}
	}
}

func TestLookupCacheAndConcurrentLogins(t *testing.T) {
	var calls atomic.Int32
	started := make(chan struct{})
	release := make(chan struct{})
	var first sync.Once
	p := testPolicy(t, Config{}, func(w http.ResponseWriter, r *http.Request) {
		calls.Add(1)
		first.Do(func() { close(started) })
		<-release
		fmt.Fprint(w, `{"ip":"203.0.113.1","block":1}`)
	})
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			blocked, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
			if !blocked || err != nil {
				t.Errorf("blocked=%v, err=%v", blocked, err)
			}
		}()
	}
	<-started
	close(release)
	wg.Wait()
	if calls.Load() != 1 {
		t.Fatalf("concurrent logins used %d lookups", calls.Load())
	}
	blocked, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
	if !blocked || err != nil || calls.Load() != 1 {
		t.Fatal("cached blocked IP was not reused")
	}
}

func TestAllowListSkipsProvider(t *testing.T) {
	p := testPolicy(t, Config{AllowCIDRs: []string{"203.0.113.1"}, DenyCIDRs: []string{"203.0.113.0/24"}}, func(w http.ResponseWriter, r *http.Request) { t.Error("allow-listed address sent to provider") })
	blocked, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
	if blocked || err != nil {
		t.Fatal("administrator allow list not honored")
	}
}

func TestEnabledFilterRequiresKey(t *testing.T) {
	t.Setenv("MKNITRO_IPHUB_API_KEY", "")
	if _, err := New(Config{Enabled: true}); err == nil {
		t.Fatal("enabled filter accepted missing key")
	}
}

func TestCanceledLookup(t *testing.T) {
	p := testPolicy(t, Config{FailClosed: true}, func(w http.ResponseWriter, r *http.Request) { t.Error("canceled request reached provider") })
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	blocked, err := p.Check(ctx, netip.MustParseAddr("203.0.113.1"))
	if !blocked || err == nil {
		t.Fatal("canceled lookup did not follow fail-closed policy")
	}
}

func TestRedirectDoesNotForwardKey(t *testing.T) {
	var leaked atomic.Bool
	destination := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { leaked.Store(r.Header.Get("X-Key") != "") }))
	defer destination.Close()
	p := testPolicy(t, Config{FailClosed: true}, func(w http.ResponseWriter, r *http.Request) { http.Redirect(w, r, destination.URL, http.StatusFound) })
	blocked, err := p.Check(context.Background(), netip.MustParseAddr("203.0.113.1"))
	if !blocked || err == nil || leaked.Load() {
		t.Fatal("VPN API redirect was followed")
	}
}
