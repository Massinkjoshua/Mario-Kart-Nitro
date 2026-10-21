# NitroWFC

NitroWFC provides Mario Kart Nitro's online services. It is derived from the Retro Rewind Team's [wfc-server](https://github.com/Retro-Rewind-Team/wfc-server), based on [WiiLink WFC](https://github.com/WiiLink24/wfc-server), and is published under the GNU AGPLv3.

## Deployed version

[Server-Fixes-2026-10-21](Server-Fixes-2026-10-21/) is the source used for the 21 October deployment, from commit `8f0ca79513102480c0d8a53a723d7e902c98c5ca`.

The running server, staged executable and a second build on the same host produced the same SHA-256:

```text
9e4dda5664349cfe985662ed4a2086b87a3fa04b09aed01338e838cc3fc572ed
```

Tests and focused race checks passed. Public API pages returned distinct ordered results, and the published website was checked beyond rank 100 and back. Online racing, room friend codes and VR after reconnecting were reported working by the operator.

The [deployment record](docs/deployment-2026-10-21.md) includes the build settings, rollout checks and remaining integration work. The [update notes](Server-Fixes-2026-10-21/SERVER-UPDATE.md) describe the pagination and ratings changes.

## Build and test

From the repository root, use Go 1.25.5 and a native C compiler for the race checks:

```sh
cd server/Server-Fixes-2026-10-21
export GOTOOLCHAIN=go1.25.5
go test ./...
go test -race ./api ./database ./gpcm
go build -trimpath -buildvcs=false -o NitroWFC-linux-amd64 .
```

The deployed build used Linux amd64, GOAMD64=v1 and CGO_ENABLED=1. An exact binary comparison requires the same build environment. The earlier handoff binary has a different hash; its records are retained in [Validation/Server-Fixes-2026-10-21](Validation/Server-Fixes-2026-10-21/).

Building does not start the service. Running it requires PostgreSQL, a private configuration and the connection payloads. See the [configuration example](examples/config_example.xml), [runtime-input checklist](docs/runtime-inputs.md) and [payload build instructions](../patcher/README.md). Keep credentials, player records and signing keys private.

## Source layout

| Directory | Purpose |
| --- | --- |
| [Server-Fixes-2026-10-21/](Server-Fixes-2026-10-21/) | Current deployed server source. |
| [Live-Export-2026-10-16/](Live-Export-2026-10-16/) | Earlier host export, with its original manifest. |
| [Live-Inputs-2026-10-16/](Live-Inputs-2026-10-16/) | Reviewed game list, translation scripts and multiplier setting. |
| [October-12-Security-Candidate/](October-12-Security-Candidate/) | Earlier, undeployed candidate with a separate source-offer implementation. |
| [Archived-October-11/](Archived-October-11/) | Historical source snapshot. |
| [docs/](docs/) and [Validation/](Validation/) | Deployment records, provenance, manifests and test results. |

The earlier export and candidates remain unchanged as historical records. The [live-export review](docs/live-export-2026-10-16.md) covers the previous executable.

## Source access and remaining checks

The current source is public on this branch. Review the player-facing source link against the precise deployed version. The `/api/source` route belongs to the separate October-12 candidate and must not be assumed available in the deployed tree.

The database schema check succeeded and was rolled back. Full ratings report/readback, banned-report rejection and outage behavior still need recorded integration tests. Ratings remain client-reported; the server does not calculate race results or prevent an authenticated client from submitting false in-range values.

## Credits and licence

Original notices remain in the individual modules and [LICENSE](LICENSE). The restored licence's upstream provenance is recorded in [upstream-notice-provenance.json](docs/upstream-notice-provenance.json); it does not identify the base commit of every recovered file. Earlier recovery changes are listed in [changes.json](docs/changes.json).

Connection-payload source and notices are under [patcher/](../patcher/README.md). Online communications credit to [WiiLink WFC](https://wfc.wiilink24.com).

NitroWFC is an independent Mario Kart Nitro service and is not endorsed by Retro Rewind or WiiLink.
