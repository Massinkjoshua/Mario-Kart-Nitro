package nas

import (
	"context"
	"errors"
	"io"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
	"wwfc/api"
	"wwfc/common"
	"wwfc/gamestats"
	"wwfc/logging"
	"wwfc/nhttp"
	"wwfc/race"
	"wwfc/sake"

	"github.com/logrusorgru/aurora/v3"
)

var (
	serverName           string
	server               *nhttp.Server
	payloadServerAddress string
)

func StartServer(reload bool) {
	// Get config
	config := common.GetConfig()

	serverName = config.ServerName

	address := *config.NASAddress + ":" + config.NASPort

	payloadServerAddress = config.PayloadServerAddress

	if config.EnableHTTPS {
		go startHTTPSProxy(config)
	}

	err := InitProfanity()
	if err != nil {
		logging.Info("NAS", err)
	}

	server = &nhttp.Server{
		Addr:        address,
		Handler:     http.HandlerFunc(handleRequest),
		IdleTimeout: 20 * time.Second,
		ReadTimeout: 10 * time.Second,
	}

	go func() {
		logging.Notice("NAS", "Starting HTTP server on", aurora.BrightCyan(address))

		err := server.ListenAndServe()
		if err != nil && !errors.Is(err, nhttp.ErrServerClosed) {
			panic(err)
		}
	}()
}

func Shutdown() {
	if server == nil {
		return
	}

	err := ProfanityWatcher.Close()
	if err != nil {
		logging.Error("NAS", "Failed to close ProfanityWatcher:", err)
	}

	ctx, release := context.WithTimeout(context.Background(), 10*time.Second)
	defer release()

	err = server.Shutdown(ctx)
	if err != nil {
		logging.Error("NAS", "Error on HTTP shutdown:", err)
	}
}

var regexRaceHost = regexp.MustCompile(`^([a-z\-]+\.)?race\.gs\.`)
var regexSakeHost = regexp.MustCompile(`^([a-z\-]+\.)?sake\.gs\.`)
var regexGamestatsHost = regexp.MustCompile(`^([a-z\-]+\.)?gamestats2?\.gs\.`)
var regexStage1URL = regexp.MustCompile(`^/w([0-9])$`)

func handleRequest(w http.ResponseWriter, r *http.Request) {
	// Check for *.sake.gs.* or sake.gs.*
	if regexSakeHost.MatchString(r.Host) {
		// Redirect to the sake server
		sake.HandleRequest(w, r)
		return
	}

	// Check for *.gamestats(2).gs.* or gamestats(2).gs.*
	if regexGamestatsHost.MatchString(r.Host) {
		// Redirect to the gamestats server
		gamestats.HandleWebRequest(w, r)
		return
	}

	// Check for *.race.gs.* or race.gs.*
	if regexRaceHost.MatchString(r.Host) {
		// Redirect to the race server
		race.HandleRequest(w, r)
		return
	}

	moduleName := "NAS:" + r.RemoteAddr

	// Handle conntest server
	if strings.HasPrefix(r.Host, "conntest.") {
		handleConnectionTest(w)
		return
	}

	// Handle DWC auth requests
	if r.URL.String() == "/ac" || r.URL.String() == "/pr" || r.URL.String() == "/download" {
		handleAuthRequest(moduleName, w, r)
		return
	}

	// Handle /nastest.jsp
	if r.URL.Path == "/nastest.jsp" {
		handleNASTest(w)
		return
	}

	// Check for /payload
	if strings.HasPrefix(r.URL.String(), "/payload") {
		logging.Info("NAS", aurora.Yellow(r.Method), aurora.Cyan(r.URL), "via", aurora.Cyan(r.Host), "from", aurora.BrightCyan(r.RemoteAddr))
		if payloadServerAddress != "" {
			// Forward the request to the payload server
			forwardPayloadRequest(moduleName, w, r)
		} else {
			handlePayloadRequest(moduleName, w, r)
		}
		return
	}

	// Stage 1
	if match := regexStage1URL.FindStringSubmatch(r.URL.String()); match != nil {
		val, err := strconv.Atoi(match[1])
		if err != nil {
			panic(err)
		}

		logging.Info("NAS", "Get stage 1:", aurora.Yellow(r.Method), aurora.Cyan(r.URL), "via", aurora.Cyan(r.Host), "from", aurora.BrightCyan(r.RemoteAddr))
		downloadStage1(w, val)
		return
	}

	// Nitro clients read a plain-text multiplier when connecting online.
	if r.URL.Path == "/api/game/multiplier.txt" || r.URL.Path == "/api/game/multiplierBeta.txt" {
		handleNitroMultiplier(w, r)
		return
	}

	// Check for /api/groups
	if r.URL.Path == "/api/groups" {
		api.HandleGroups(w, r)
		return
	}

	// Check for /api/mkw_rr
	if r.URL.Path == "/api/mkw_rr" {
		api.HandleMKWRR(w, r)
		return
	}

	// Check for /api/stats
	if r.URL.Path == "/api/stats" {
		api.HandleStats(w, r)
		return
	}

	if api.HandleRequest(r.URL.Path, w, r) {
		return
	}

	logging.Info("NAS", aurora.Yellow(r.Method), aurora.Cyan(r.URL), "via", aurora.Cyan(r.Host), "from", aurora.BrightCyan(r.RemoteAddr))
	replyHTTPError(w, 404, "404 Not Found")
}

func replyHTTPError(w http.ResponseWriter, errorCode int, errorString string) {
	response := "<html>\n" +
		"<head><title>" + errorString + "</title></head>\n" +
		"<body>\n" +
		"<center><h1>" + errorString + "</h1></center>\n" +
		"<hr><center>" + serverName + "</center>\n" +
		"</body>\n" +
		"</html>\n"

	w.Header().Set("Content-Type", "text/html")
	w.Header().Set("Content-Length", strconv.Itoa(len(response)))
	w.Header().Set("Connection", "close")
	w.Header().Set("Server", "Nintendo")
	w.WriteHeader(errorCode)
	w.Write([]byte(response))
}

func handleNASTest(w http.ResponseWriter) {
	response := "" +
		"<html>\n" +
		"<body>\n" +
		"</br>AuthServer is up</br> \n" +
		"\n" +
		"</body>\n" +
		"</html>\n"

	w.Header().Set("Content-Type", "text/html;charset=ISO-8859-1")
	w.Header().Set("Content-Length", strconv.Itoa(len(response)))
	w.Header().Set("Connection", "close")
	w.Header().Set("NODE", "authserver-service.authserver.svc.cluster.local")
	w.Header().Set("Server", "Nintendo")

	w.WriteHeader(200)
	w.Write([]byte(response))
}

func forwardPayloadRequest(moduleName string, w http.ResponseWriter, r *http.Request) {
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	r.URL.Scheme = "http"
	r.URL.Host = payloadServerAddress
	r.RequestURI = ""
	r.Host = payloadServerAddress

	resp, err := client.Do(r)
	if err != nil {
		logging.Error(moduleName, "Error forwarding payload request:", err)
		replyHTTPError(w, http.StatusBadGateway, "502 Bad Gateway")
		return
	}
	defer resp.Body.Close()

	// Copy the response headers and status code
	for key, values := range resp.Header {
		for _, value := range values {
			w.Header().Add(key, value)
		}
	}
	w.WriteHeader(resp.StatusCode)

	// Copy the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		logging.Error(moduleName, "Error reading response body:", err)
		replyHTTPError(w, http.StatusInternalServerError, "500 Internal Server Error")
		return
	}
	w.Write(body)
}

// Missing or invalid configuration means normal (1x) rating. Read on each
// request so changing the file does not require another server restart.
func handleNitroMultiplier(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet && r.Method != http.MethodHead {
		w.Header().Set("Allow", "GET, HEAD")
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	path := "/opt/mknitro-rwfc/multiplier.txt"
	if r.URL.Path == "/api/game/multiplierBeta.txt" {
		path = "/opt/mknitro-rwfc/multiplierBeta.txt"
	}

	value := "1"
	if file, err := os.Open(path); err == nil {
		body, readErr := io.ReadAll(io.LimitReader(file, 65))
		file.Close()
		if readErr == nil && len(body) <= 64 {
			text := strings.TrimSpace(string(body))
			// Match the client's decimal parser: no exponent or sign.
			valid := text != ""
			dots := 0
			digits := 0
			for _, ch := range text {
				if ch == '.' {
					dots++
				} else if ch >= '0' && ch <= '9' {
					digits++
				} else {
					valid = false
				}
			}
			if valid && dots <= 1 && digits > 0 {
				if number, err := strconv.ParseFloat(text, 64); err == nil && number >= 1 && number <= 2.5 {
					value = strconv.FormatFloat(number, 'f', -1, 64)
				}
			}
		}
	}

	body := value + "\n"
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Content-Length", strconv.Itoa(len(body)))
	w.WriteHeader(http.StatusOK)
	if r.Method != http.MethodHead {
		io.WriteString(w, body)
	}
}
