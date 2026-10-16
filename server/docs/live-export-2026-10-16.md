# NitroWFC live-source export review — 16 October 2026

## Initial evidence (before binary upload and rebuild)

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

## Remaining inputs recorded at export

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

## Later verification — running binary received and server rebuild

The uploaded nitro-running-server.bin independently hashes to the recorded
`f36e1cb75c34a4f44f93c59aacf441950fa3239a2c1f636d3f3b2c9e58dcfc6a`.
Go build metadata independently confirms Go 1.26.0 and the flags recorded above.
A local Go 1.26.0 build succeeds. Its whole-file SHA differs under this host's
native CGO toolchain; all 813 project text symbols match in size and instructions
when only verified symbol-relative branch/RIP-relative relocations are normalized.
This is an instruction comparison, not whole-program runtime equivalence.

The operator then ran the following on the original server in /opt/mknitro:

```sh
nitro_check_dir=$(mktemp -d /tmp/nitro-build-check.XXXXXX)
go build -buildvcs=false -trimpath -o "$nitro_check_dir/wwfc" .
sha256sum "$nitro_check_dir/wwfc" /proc/136701/exe
```

Screenshot image(20261016-131732).png records both files hashing to
`f36e1cb75c34a4f44f93c59aacf441950fa3239a2c1f636d3f3b2c9e58dcfc6a`.
This verifies an exact rebuild from the server's source directory on its build
host. The archive export was separately verified as recorded above; no second
on-server source-manifest comparison was performed after that export.
No running service was replaced or restarted. Missing runtime inputs and public
source-offer deployment remain open.

## Later verification — matching payload source

The operator subsequently rebuilt stage1 and all four RMC payloads from the
exported patcher archive in an isolated temporary folder. All five SHA-256 pairs
matched their on-disk references. See ../../patcher/README.md and
../../patcher/VERIFICATION.json for the source, pinned compiler image, hashes and
evidence limits. No HTTP-served payload response or game runtime was tested.
