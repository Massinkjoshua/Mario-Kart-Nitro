MARIO KART NITRO — WEBSITE SOURCE & CREDITS PATCH
16 October 2026

Prepared for the current website's owning account. This patch is not deployed.
It inserts a prominent Source & credits section immediately before Downloads,
using the existing website styles. It links the public server, payload and
client recovery sources, retains WiiLink's required acknowledgement, and states
that source recovery is incomplete. It makes no claim that the notice is cured.

In the account that owns your current website, upload this ZIP and say:

"Apply this source-and-credits patch to the latest source of mknitro.com.
Read README.txt. Keep the existing Site identity and all current website content.
Add the provided section before Downloads, rebuild the existing Worker, run the
checks, and publish the update to the same website. Do not restore the older v32
website copy or change its tracks, rooms, leaderboard, API or domain."

FOR THE PERSON APPLYING IT
1. Open the latest authorised website source, not a saved live HTML page.
2. Extract this patch outside the website's dist folder.
3. Run:
   python3 /path/to/patch/apply_source_credits.py /path/to/current-project/dist/index.html
   If the script cannot find the expected Downloads marker, insert the supplied
   HTML section manually before Downloads. Do not rebuild the site from scratch.
4. The script preserves every byte outside its own marked section. It creates
   a backup outside dist. Re-running is safe and updates only its marked section.
5. For the known plain HTML + Worker website project, from its root run:
   python3 scripts/build-worker.py
   node scripts/check-site.mjs
   node scripts/check-pagination.mjs
   node scripts/check-online.mjs
   node scripts/check-worker.mjs
   Use the current project's workflow if it has changed. Do not hand-edit the
   generated dist/server/index.js or publish an old bundled Worker.
6. Review at desktop/mobile sizes; verify the source links. Publish only this
   change through the existing Site owner's normal publishing workflow.

VALIDATION
The patch was applied to an isolated copy of the available v32 source, with
byte preservation outside its own section and repeat-run stability checked.
The Worker was rebuilt and the existing automated checks were run; see the
included VALIDATION.txt for results. No browser visual QA or live deployment.
The supplied patch has no API changes, credentials, compiled game code or keys.

LIMITS
The local v32 copy differs from the live website; this package intentionally
contains the narrow patch instead of that older website snapshot. Source and
credits links improve visibility but do not complete missing client source,
historical release mapping or asset permission requirements. Historical
translation sheet inputs also remain under review.
