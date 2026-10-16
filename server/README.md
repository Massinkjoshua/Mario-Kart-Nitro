# NitroWFC source recovery — 16 October 2026

NitroWFC is derived from Retro Rewind's `wfc-server`, itself a fork of WiiLink
WFC. This archive restores the GNU AGPLv3 licence and explicit attribution,
retains recovered source and supplies a separately labelled repaired candidate.
It is not confirmation that these files match the server currently running.

## Live export now received

`Live-Export-2026-10-16/` preserves 134 files exported from the running
server working directory, plus its executable-hash manifest. Its source builds
and passes race tests with vet disabled for inherited formatting warnings.
The source-to-running-binary match and payload source remain unverified. See
[the live export review](docs/live-export-2026-10-16.md) for exact scope and gaps.

## Contents

- `Archived-October-11/`: recovered active-source archive, excluding a clearly
  named unrelated backup directory. Its Go files are preserved byte for byte.
- `October-12-Security-Candidate/`: recovered 12 October source plus the matching
  archived `go.mod`/`go.sum`, formatting-check repairs and a new public source
  offer route. This is a local candidate, not a deployed server.
- `docs/`: source hashes, differences, upstream notice provenance and build/test
  records. `docs/upstream/schema.sql` is an upstream reference, not an export of
  your live database or proof of its schema version.
- `scripts/export_running_source.py`: a read-only exporter for obtaining the
  actual server source and the hash of its running executable. No credentials,
  live database, keys or player records are needed for this verification.

## Build and test

Use Go 1.25.5 or a compatible version, and a native C compiler for race checks:

```sh
cd October-12-Security-Candidate
go test -buildvcs=false -race ./...
go build -buildvcs=false -o ../build/nitrowfc .
```

Both archived and candidate runtime modules compiled in this review. The repaired
candidate passes its complete test suite with race detection. The unchanged
October archive fails Go's newer formatting checks at two inherited source
areas; those files are preserved as historical evidence.

Building does not connect to a database, change the live server or restart a
service. Running the server also requires a PostgreSQL database, your private
configuration, and the matching WiiLink/Retro Rewind payload. The payload source,
build recipe and original notices must be accounted for separately if modified
or distributed. No payload or private signing key is included here.

## Public source offer

The candidate adds a public `GET /api/source` route. After publishing the complete
source for the version actually deployed, add its permanent public URL to the
existing private config, within its root element:

```xml
<sourceUrl>YOUR_PUBLIC_SOURCE_ARCHIVE_OR_REPOSITORY_URL</sourceUrl>
```

The route requires no API secret and returns only the public URL, licence and
upstream attribution. It returns HTTP 503 if no valid public URL is configured.
It does not upload or host source automatically. A route, placeholder, link to
this incomplete recovery bundle, or unpublished repository is insufficient.
Place a visible source link on the player-facing NitroWFC website and source
information in the game's online credits/help or message of the day as well.

Before using this candidate, compare it with the source of the actual deployed
executable. Publishing a new candidate alone does not address missing source
for an older deployed version. No activation or publication was performed.

## Attribution and licence

Original upstream: https://github.com/Retro-Rewind-Team/wfc-server
WiiLink WFC: https://github.com/WiiLink24/wfc-server
Matching client payload: https://github.com/Retro-Rewind-Team/wfc-patcher-wii

The complete GNU AGPLv3 text is retained in `LICENSE` and each module. The restored
copy came from the pinned upstream commit recorded in
`docs/upstream-notice-provenance.json`; that reference is not asserted to be the
base commit of the recovered Nitro source. Existing per-file notices remain.
Nitro changes and recovery repairs are dated and listed in `docs/changes.json`.
This is an independent Mario Kart Nitro project, not an endorsed Retro Rewind
release. Assets and other projects retain their own licences.

Online communications credit to WiiLink WFC - https://wfc.wiilink24.com

The original payload licence is retained in docs/upstream/wfc-patcher-wii-LICENSE.

## Current follow-up

The client handoff now includes an independently rebuilt released loader, named
client source repairs and the verified public 1.0 binary hashes. The public 1.0
client differs from the latest upload. See docs/public/ and NEXT_STEPS.txt.
This server package remains a recovery candidate until its live source/executable
and separately built payload have been matched. The recovery branch and draft pull request are public; this is still an incomplete source offer.
