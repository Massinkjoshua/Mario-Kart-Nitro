# NitroWFC server candidate — 21 October 2026

This candidate is based on server/Live-Export-2026-10-16 from source commit 46dbe695c693b5c427701c8510eba63bd508b637. The historical export is preserved. Game Code.pul, Loader.pul, configs, tracks and launcher are not changed.

## Changes

The website API `/api/nitro/leaderboard` now honors `page` (1–1,000,000) and `limit` (1–200, default 100). Responses add `page`, `limit`, and `has_more`. The database fetches one extra row and trims it before responding, so requests stay bounded. Existing ranking, search and banned-user filtering remain. The in-game endpoint retains its fixed 50-row batches and receives the same additive metadata.

`GET /api/mkw_rr_ratings?pid=42` supplies the client's expected integer `found` flag and displayed-scale `vr`/`br`. Missing saved ratings return found=0; database errors return an error with no found field so an outage does not masquerade as a new profile. The route uses no-store caching and exposes only ratings. The existing NAS dispatcher routes it through the API; reverse-proxy routing still needs staging verification.

GPCM handles `wl:mkw_vrbr` reports (`vr=5000|br=6000`). It requires a logged-in, device-authenticated Mario Kart Wii session that is not restricted. The profile ID comes from that session, never report input. Fields must be exactly VR and BR with decimal values from 1 to 1,000,000. Writes recheck the current database ban state.

Ratings persist in a new `nitro_profile_ratings` table, with range checks, a user foreign key and deletion cascade. API/GPCM startup serializes table initialization within the process. Existing ratings/leaderboard tables are not migrated or overwritten: a profile without a new saved record is initialized by its client's normal report. This remains client-reported rating synchronization, not server-computed anti-cheat scoring; authenticated clients can still lie about their own in-range ratings.

Two existing nonconstant format-string issues were corrected so normal Go 1.25.5 test/vet checks pass.

## Build and verification

Use Go 1.25.5. From this source directory:

```sh
go test ./...
go test -race ./api ./database ./gpcm
go build -trimpath -buildvcs=false -o NitroWFC-linux-amd64 .
```

Logs and source/binary hashes are in the adjacent Validation folder in the GitHub project and Reports in the handoff. Unit tests mock database calls and cover valid/invalid values, session identity, error/not-found distinction, client response size, paging boundaries and concurrent startup. They do not exercise a real PostgreSQL migration, native game HTTP, current reverse proxies or a live VPS. Those remain staging checks.

## Website integration still required

The current website belongs to another account and was not edited or deployed. On 18 October the connected account returned no editable Sites. The available v32 snapshot is older than the live site and must not replace it wholesale.

In the current website's Worker, forward `page`, `limit` and `q` to the updated endpoint. In the UI, fetch each requested page (for example limit=10), show Previous for page>1 and Next only when `has_more` is true. Reset page to 1 when search changes. Ignore stale responses after a new request, keep navigation usable on errors, and do not fetch the entire leaderboard at once. Preserve room listings, friend codes, styling and existing Site identity. This requires the latest website source or access through its owning account.

## Operator staging and rollout

1. Back up the current server executable/config and database. Confirm the target architecture is Linux amd64 before using the supplied executable; otherwise rebuild on the target.
2. Test against a disposable database using your normal server schema/config. Startup requires permission to create the new table. Do not point a staging instance at the production database.
3. Seed at least 205 synthetic leaderboard users and verify pages 1/2/3 with limit=100 contain distinct ordered records, then a final empty page. Verify search and banned-user exclusion.
4. With two test profiles, verify an authenticated report affects only its sender, a fresh login retrieves the stored VR/BR, and a banned session cannot save. Verify a database outage produces an error rather than found=0.
5. Confirm the NAS hostname and public API reverse proxy reach the intended process. No service name, installation path, credentials or proxy changes are assumed by this handoff.
6. Deploy the server after staging passes, then update the current website to use pagination. Keep the tested game binary and its matching published source identified separately.
7. For rollback, restore the previous server executable and website version. The new table can remain unused; do not drop it or restore a whole production database merely to roll back this code.

No server process was started, no production database changed, no launcher updated and no online build hash approved here.
