# NitroWFC deployment record — 21 October 2026

## Deployed source

Repository: Massinkjoshua/Mario-Kart-Nitro-Releases  
Source commit: `8f0ca79513102480c0d8a53a723d7e902c98c5ca`  
Source directory: [Server-Fixes-2026-10-21](../Server-Fixes-2026-10-21/)  
Licence: GNU AGPLv3; derived from Retro Rewind's wfc-server and WiiLink WFC.

All 142 files in that source directory were compared with the published Git blobs and matched. Before rollout, the operator compared the production working-directory Go sources (excluding tests), go.mod and go.sum with Live-Export-2026-10-16: all 120 selected files matched, with no missing, differing or extra files reported by that comparison. That check covered the baseline source packages, not every runtime asset or directory.

The operator downloaded the repository archive pinned to the source commit above and built the candidate from that directory. The assistant did not have SSH access: host results were inspected through operator screenshots.

## Host build and rollout evidence

The host is Linux amd64. The candidate was built using Go 1.25.5 with:

```sh
export GOTOOLCHAIN=go1.25.5
go test ./...
go test -race ./api ./database ./gpcm
go build -trimpath -buildvcs=false -o /root/nitro-pagination-review/wwfc.candidate .
```

All package tests and focused race checks passed. The inspected build metadata included GOOS=linux, GOARCH=amd64, GOAMD64=v1, CGO_ENABLED=1 and trimpath=true. The host build hash differs from the earlier handoff executable; do not substitute the handoff hash for the deployed build. An independent fresh rebuild comparison and a hash of the running process executable are not yet recorded here.

Before rollout, the operator backed up the executable and private configuration and verified both backups matched their originals. A private pg_dumpall backup was created with restricted permissions and its completion marker checked. No secrets, configuration contents, database dumps or player records are published.

A PostgreSQL transaction under role mknitro successfully created the candidate ratings-table definition and then rolled back. This verifies schema compatibility and creation privileges; it is not an end-to-end ratings persistence test.

The candidate was installed at /opt/mknitro/wwfc using an atomic rename and mknitro.service was restarted. The inspected result reported ActiveState=active, SubState=running and NRestarts=0 after the initial startup check. The previous executable and config backups remain available for rollback. Keep the new ratings table when rolling back code; do not restore the production database merely for a code rollback.

## Live checks

The operator requested the public backend endpoint with limit=10:
- Page 1 returned page=1, limit=10, has_more=true and ranks 1–10.
- Page 2 returned page=2, limit=10, has_more=true and ranks 11–20.

The owning website account reported publishing v42 to the existing mknitro.com Site, passing all nine website checks and receiving backend ranks beyond 200. This is an external account report, not an independently inspected website source commit. The operator then supplied published-site screenshots showing page 11/ranks 101–110 and Previous returning to page 10/ranks 91–100.

The operator separately confirmed that friend codes appeared correctly in active rooms and that online racing and VR after disconnect/reconnect worked. These are operator smoke-test reports. They do not establish the exact loaded game-client binary, nor prove that the new ratings storage/report path was exercised.

## Remaining verification boundaries

- Independently hash the running executable and compare it with the staged candidate; preserve exact build settings and inputs for reproduction.
- Test the new ratings endpoint and authenticated report/readback against real PostgreSQL with identified test profiles. The unit tests use mocked database calls; the schema transaction and game smoke report do not replace those integration checks.
- A fresh disposable-database integration suite, banned-report rejection, outage behavior and full game-client identity verification remain unrecorded.
- The public source-offer visibility/routing for this precise deployed server version still needs checking. The separately archived October-12 candidate's /api/source route must not be assumed present in this deployment.
- Historical client source correspondence, omitted pack assets and asset permissions retain their separate existing status. This server deployment record does not establish completion of the overall licence-notice remediation.

The older validation logs, candidate handoff and historical exports remain unchanged as records of their original scope.
