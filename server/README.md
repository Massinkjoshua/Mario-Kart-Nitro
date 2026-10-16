# NitroWFC source recovery — 16 October 2026

NitroWFC is derived from Retro Rewind's `wfc-server`, itself a fork of WiiLink
WFC. This archive restores the GNU AGPLv3 licence and explicit attribution,
retains recovered source and supplies a separately labelled repaired candidate.
The live export and historical candidates are kept separate below.

## Live export now received

`Live-Export-2026-10-16/` preserves 134 files exported from the running
server working directory, plus its executable-hash manifest. Its source builds
and passes race tests with vet disabled for inherited formatting warnings.
An operator rebuild on the original host matched the running executable exactly.
Matching stage1 and four RMC payload sources are in [../patcher](../patcher/README.md). See
[the live export review](docs/live-export-2026-10-16.md) for exact scope and gaps.

## Contents

- `Live-Inputs-2026-10-16/`: reviewed game list, original Lua translation
  generator/helpers and the separate live multiplier setting, with manifests.

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
configuration, and the matching WiiLink/Retro Rewind payload. The separately verified
payload source, build recipe and original notices are in ../patcher/. No compiled
payload or private signing key is included here.

## Safe configuration and remaining runtime inputs

See [the runtime input checklist](docs/runtime-inputs.md), the separately prepared
[configuration example](examples/config_example.xml), and the fixed-allowlist
collector in scripts/export_public_inputs.py. These additions do not alter the
verified source snapshots or deployed service.

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
for an older deployed version. This candidate has not been activated; source is published on the recovery branch.

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
The live executable rebuild and five payload rebuilds matched their reference
hashes. Required safe runtime inputs and the player-facing source offer remain
open. The recovery branch and draft pull request are public; this is still an
incomplete source offer.
