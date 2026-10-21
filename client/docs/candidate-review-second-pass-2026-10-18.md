# Second candidate review — ratings, saves and packet guard

18 October 2026. Candidate Code.pul SHA-256: `71af89931375f4fc46782401e54c243bee8fc657b8fb44d4fe6f52e627ac3075`. This supplements candidate-review-2026-10-18.md; earlier findings remain open. This is a review, not a replacement build. No user save, live server, approval list or launcher was modified.

## R4 — Overlapping VR downloads can target the wrong profile (P1, conditional on overlap)

In `PulsarEngine/Network/Rating/RatingSync.cpp:158–188`, every request reuses one mutable RequestCtx, work buffer and URL. There is no in-flight guard or per-request ownership. Starting a second request overwrites the first request's generation, profile and licence fields. The generation comparison at lines 116–118 therefore cannot reject the first reply: its userdata points to the overwritten context.

The offline reproducer executes the actual BeginLoginRatingDownload and callback instructions. It begins a download for profile 101/licence 0, then profile 202/licence 1 before replying to the first. Both requests receive the same context and response-buffer pointers. A valid profile-101 reply then passes IsRequestStillRelevant and calls SaveProfileVR/SaveProfileBR for profile 202 with profile 101's values. A single-request control correctly calls the save functions for profile 101. Both cases run at two allocation bases. Save functions are intercepted: no real rating file is written.

This proves the ownership bug under overlapping requests, not that a particular real login sequence has triggered it. Native NHTTP cancellation/scheduling and live response availability were not tested. The missing server contract below may prevent valid responses unless another service supplies them.

Repair direction: serialize/coalesce requests or allocate immutable per-request context and buffers; preserve ownership until callback/cancellation completes, and apply completed results safely to the intended profile only. Do not merely increment the shared generation again.

## R5 — Exported server lacks the client's VR-sync contract (P2 integration gap)

The client downloads `/api/mkw_rr_ratings?pid=...` from nas.play.mknitro.com and reports `wl:mkw_vrbr` from ReportCurrentRatings. A search of all 126 Go files in `server/Live-Export-2026-10-16` finds neither contract. The NAS dispatcher falls through to 404 for unknown routes; the GPCM report dispatcher logs unknown report keys without persisting these ratings.

Consequently, the supplied client and exported server do not implement end-to-end rating restoration through this path. This does NOT imply that local rating saves, QR2 ratings or the separate Nitro leaderboard are broken; they use different paths. A live reverse proxy or separately hosted service could supply the missing route, and was not inspected. See server-contract-review.json for source hashes and exact scope.

Repair direction: verify the live service arrangement, then implement one matching, validated client/server rating protocol or explicitly disable the unsupported path. Avoid making an unauthenticated client-reported value authoritative merely to fill the gap.

## R6 — Rating-file reader accepts invalid numeric values (P2 robustness)

`PulsarEngine/Network/Rating/RatingSave.cpp:149–160` validates file header/profile/flags, but copies the stored VR/BR floats without checking finite values or range. Setter clamping does not protect this load path.

The real compiled Load/GetUserVR functions were exercised against synthetic files with mocked IO. A valid 50.0 control returns 50.0; -5.0, 10001.0, NaN and positive infinity are all accepted and returned unchanged. Normal internal range is 1–10000. Both bases reproduce this. These are corrupt/invalid-file cases, not evidence that the user's existing save is corrupt. Downstream display/crash consequences were not executed.

Repair direction: reject non-finite and out-of-range entries before marking them usable, fall back safely, and preserve a backup when recovering a bad file. Never treat NaN as handled by an ordinary min/max comparison.

## Additional packet-validation gap — impact not yet established

`PulsarEngine/Network/PacketExpansion.cpp:46–74` verifies CRC and individual destination capacities, but does not verify that the declared section lengths fit the received byte count. An offline synthetic header with a valid CRC and sections exceeding the supplied length is forwarded by the compiled guard to ProcessRACEPacket. Bad-CRC and over-capacity controls are rejected.

The original native ProcessRACEPacket implementation was intercepted and may enforce further checks. This is a confirmed omission in this guard, NOT a demonstrated remote crash or exploit. Review the native boundary and add bounded envelope validation before making a stronger claim. No packets were sent to a server or player.

## Evidence and rerun

The accompanying report has 22 scenario records: single/overlapping downloads, five save-value cases and four packet cases at each of two bases. These are controlled PAL instruction tests; native IO, HTTP, libc and selected rating accessors are mocked. They supplement rather than replace Dolphin/Wii/online testing.

From client/, using tests/requirements-ppc.txt and the delivered candidate/map:

```sh
python3 tests/reproduce_rating_issues_20261018.py --source-root . --candidate /path/to/Code.pul --map /path/to/Code.map --report /path/to/review-result.json
```

The hash-pinned reproducer asserts the existing problematic behavior. Passing it confirms these observations, not that fixes have been applied. See Validation/ReviewCandidate-2026-10-18/second-review-reproduced-issues.json and server-contract-review.json.
