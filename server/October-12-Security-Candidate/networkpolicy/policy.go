// Package networkpolicy checks actual connection IPs before account creation.
package networkpolicy

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/netip"
	"os"
	"strings"
	"sync"
	"time"
)

type Config struct {
	Enabled        bool     `xml:"enabled"`
	APIKey         string   `xml:"apiKey"`
	APIKeyFile     string   `xml:"apiKeyFile"`
	FailClosed     bool     `xml:"failClosed"`
	BlockUncertain bool     `xml:"blockUncertain"`
	AllowCIDRs     []string `xml:"allowCIDR"`
	DenyCIDRs      []string `xml:"denyCIDR"`
}

type result struct {
	block   int
	err     error
	expires time.Time
}
type flight struct {
	done   chan struct{}
	result result
}

type Policy struct {
	config      Config
	key         string
	allow, deny []netip.Prefix
	client      *http.Client
	endpoint    string
	timeout     time.Duration
	mu          sync.Mutex
	cache       map[netip.Addr]result
	inflight    map[netip.Addr]*flight
	slots       chan struct{}
}

func New(c Config) (*Policy, error) {
	p := &Policy{config: c, endpoint: "https://v2.api.iphub.info/ip/", timeout: 5 * time.Second,
		cache: make(map[netip.Addr]result), inflight: make(map[netip.Addr]*flight), slots: make(chan struct{}, 8)}
	var err error
	if p.allow, err = parsePrefixes(c.AllowCIDRs); err != nil {
		return nil, fmt.Errorf("invalid VPN allow list: %w", err)
	}
	if p.deny, err = parsePrefixes(c.DenyCIDRs); err != nil {
		return nil, fmt.Errorf("invalid VPN deny list: %w", err)
	}
	p.client = &http.Client{Timeout: p.timeout, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	if c.Enabled {
		p.key = strings.TrimSpace(os.Getenv("MKNITRO_IPHUB_API_KEY"))
		if p.key == "" {
			p.key = strings.TrimSpace(c.APIKey)
		}
		if p.key == "" && c.APIKeyFile != "" {
			b, readErr := os.ReadFile(c.APIKeyFile)
			if readErr != nil {
				return nil, errors.New("cannot read VPN API-key file")
			}
			p.key = strings.TrimSpace(string(b))
		}
		if p.key == "" {
			return nil, errors.New("VPN filtering enabled but IPHub API key is missing")
		}
	}
	return p, nil
}

func parsePrefixes(values []string) ([]netip.Prefix, error) {
	var out []netip.Prefix
	for _, value := range values {
		value = strings.TrimSpace(value)
		if addr, err := netip.ParseAddr(value); err == nil {
			addr = addr.Unmap()
			out = append(out, netip.PrefixFrom(addr, addr.BitLen()))
			continue
		}
		prefix, err := netip.ParsePrefix(value)
		if err != nil {
			return nil, errors.New("entry must be an IP address or CIDR")
		}
		if prefix.Addr().Is4In6() {
			if prefix.Bits() < 96 {
				return nil, errors.New("IPv4-mapped CIDR must be at least /96")
			}
			prefix = netip.PrefixFrom(prefix.Addr().Unmap(), prefix.Bits()-96)
		}
		out = append(out, prefix.Masked())
	}
	return out, nil
}

// ClientIP parses the actual TCP peer, including IPv6; client headers are unused.
func ClientIP(address string) (netip.Addr, error) {
	host, _, err := net.SplitHostPort(address)
	if err != nil {
		host = address
	}
	addr, err := netip.ParseAddr(host)
	if err != nil || addr.Zone() != "" {
		return netip.Addr{}, errors.New("invalid connection IP")
	}
	return addr.Unmap(), nil
}

func contains(prefixes []netip.Prefix, addr netip.Addr) bool {
	for _, prefix := range prefixes {
		if prefix.Contains(addr) {
			return true
		}
	}
	return false
}

// Check returns blocked=true for a deny-list match or a flagged IP. Allow-list
// entries override both. Lookup failures follow the configured outage policy.
func (p *Policy) Check(parent context.Context, addr netip.Addr) (blocked bool, err error) {
	addr = addr.Unmap()
	if !addr.IsValid() {
		return true, errors.New("invalid connection IP")
	}
	if contains(p.allow, addr) {
		return false, nil
	}
	if contains(p.deny, addr) {
		return true, nil
	}
	if !p.config.Enabled || !addr.IsGlobalUnicast() || addr.IsPrivate() {
		return false, nil
	}
	ctx, cancel := context.WithTimeout(parent, p.timeout)
	defer cancel()
	r := p.lookup(ctx, addr)
	if r.err != nil {
		return p.config.FailClosed, r.err
	}
	return r.block == 1 || (r.block == 2 && p.config.BlockUncertain), nil
}

func (p *Policy) lookup(ctx context.Context, addr netip.Addr) result {
	p.mu.Lock()
	if r, ok := p.cache[addr]; ok && time.Now().Before(r.expires) {
		p.mu.Unlock()
		return r
	}
	if f, ok := p.inflight[addr]; ok {
		p.mu.Unlock()
		select {
		case <-f.done:
			return f.result
		case <-ctx.Done():
			return result{err: ctx.Err()}
		}
	}
	f := &flight{done: make(chan struct{})}
	p.inflight[addr] = f
	p.mu.Unlock()
	r := p.fetch(ctx, addr)
	ttl := 6 * time.Hour
	if r.err != nil {
		ttl = 30 * time.Second
	}
	r.expires = time.Now().Add(ttl)
	p.mu.Lock()
	if len(p.cache) >= 4096 {
		for ip, entry := range p.cache {
			if time.Now().After(entry.expires) {
				delete(p.cache, ip)
			}
		}
		if len(p.cache) >= 4096 {
			for ip := range p.cache {
				delete(p.cache, ip)
				break
			}
		}
	}
	p.cache[addr] = r
	f.result = r
	delete(p.inflight, addr)
	close(f.done)
	p.mu.Unlock()
	return r
}

func (p *Policy) fetch(ctx context.Context, addr netip.Addr) result {
	select {
	case p.slots <- struct{}{}:
		defer func() { <-p.slots }()
	case <-ctx.Done():
		return result{err: ctx.Err()}
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, p.endpoint+addr.String(), nil)
	if err != nil {
		return result{err: errors.New("cannot create VPN lookup")}
	}
	req.Header.Set("X-Key", p.key)
	resp, err := p.client.Do(req)
	if err != nil {
		return result{err: errors.New("VPN lookup unavailable or timed out")}
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return result{err: fmt.Errorf("VPN lookup HTTP status %d", resp.StatusCode)}
	}
	body, err := io.ReadAll(io.LimitReader(resp.Body, 65537))
	if err != nil || len(body) > 65536 {
		return result{err: errors.New("invalid VPN lookup body")}
	}
	var data struct {
		IP    string `json:"ip"`
		Block *int   `json:"block"`
	}
	if json.Unmarshal(body, &data) != nil || data.Block == nil || *data.Block < 0 || *data.Block > 2 {
		return result{err: errors.New("invalid VPN lookup decision")}
	}
	returned, err := netip.ParseAddr(data.IP)
	if err != nil || returned.Unmap() != addr {
		return result{err: errors.New("VPN lookup returned a different IP")}
	}
	return result{block: *data.Block}
}
