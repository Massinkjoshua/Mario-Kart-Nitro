# NitroWFC live-source export review — 16 October 2026

## Evidence

The operator exported `/opt/mknitro` on 2026-10-16 at 12:59:31 UTC using
scripts/export_running_source.py. Process 136701 resolved to `/opt/mknitro/wwfc`
and used `/opt/mknitro` as its working directory. Processes 136701 and 136711
had the same executable SHA-256 in the supplied terminal evidence.

- Uploaded archive SHA-256: `48272f42a664f96e161dcc24f6ed526aaaf847c39bb0e8b282292ab76672c552`
- Running executable SHA-256: `f36e1cb75c34a4f44f93c59aacf441950fa3239a2c1f636d3f3b2c9e58dcfc6a`
- All 134 exported files match the included manifest's lengths and SHA-256 values.
- Terminal build information: Go 1.26.0, linux/amd64, CGO_ENABLED=1,
  -trimpath=true, no recorded VCS revision. go.mod declares Go 1.25.5.

This establishes the source directory and executable hash observed by the
operator. It does not establish that those source files generated that binary.
The running binary itself has not been uploaded or independently inspected.

## Comparison and validation

Compared with October-12-Security-Candidate, 123 exported files are identical,
six existing files differ, and five files are newly available (Makefile,
README.md, schema.sql, dlc/README.md, translations/README.md). The candidate's
api/source.go is absent from the live export. The six differences are
api/main.go, common/config.go, gpcm/error_messages.go, nhttp/server.go,
serverbrowser/filter/tokens.go and serverbrowser/filter/scanner_helper.go.
The live export has no sourceUrl config field or public /api/source route.

The exported files are preserved byte for byte, including original AGPL licence
and upstream README attribution. Credential-pattern review found only test and
protocol example strings; no actual private keys or embedded credentials were
identified in the exported files. Private runtime configuration was not exported.
This review is not a guarantee that arbitrary unexported files are safe to publish.

Using Go 1.25.5 locally:

- `go build -buildvcs=false -trimpath -o ../wwfc .` passed.
- `go test -race -vet=off ./...` passed.
- Normal `go test -race ./...` fails inherited nonconstant-format vet checks in
  nhttp/server.go:472 and serverbrowser/filter/tokens.go:55. These are preserved
  here; the separate repaired candidate addresses them.
- No live database connections, service changes or game/network runtime tests
  were performed. No byte-for-byte match with the Go 1.26.0 binary is claimed.

## Remaining inputs

The export intentionally filters file types and omits private configs, player
state, logs, keys and backups. It is not a complete deployment/source package.
In particular, game_list.tsv, safe example configuration, translation data,
other runtime data (such as multiplier.txt/motd.txt where used) and the payload
source/build recipe must be reviewed separately. The runtime expects
payload/stage1.bin, payload/binary/payload.<game>.bin and potentially
payload/sbcm/payload.<game>.bin. Binary payloads alone do not supply their source.
Never publish payload/private-key.pem, API keys, database credentials or player data.

Next: identify payload build/source revision, collect safe required resources,
and reproduce/compare the running Go 1.26.0 executable from this snapshot.
The public player-facing source offer still needs to be completed and deployed.
