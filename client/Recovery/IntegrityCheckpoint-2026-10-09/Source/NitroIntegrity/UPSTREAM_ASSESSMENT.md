# Anti-cheat assessment for Mario Kart Nitro

## Verified inputs

| Input | Size | SHA256 |
| --- | ---: | --- |
| Code(10).pul | 2,680,200 bytes | `0f5364590f8ec8164f06a934666bdbd9252b87edf7d31c79bf93e189f30c15bc` |
| main(3).dol | 2,766,496 bytes | `80d18895b39c63bd80f457398bfcbb91b7d16ac116a41a88967e954080155b05` |
| StaticR(2).rel | 4,903,876 bytes | `16d9d146112541fefea701ecb5bc1a496f9d50e4a752fbb5b6778e7c6399f67d` |

The PUL contains PAL, USA and Japan modules using Kamek format v2; its Korea module is absent. The PAL command stream parses completely: 11,067 commands. The supplied REL matches the previously documented PAL original SHA1 `887bcc076781f5b005cc317a6e3cc8fd5f911300`.

Two original item-event call instructions were checked directly in the supplied REL:

| PAL site | Original target | Earlier prototype use |
| --- | --- | --- |
| `0x8065B760` | `0x8065BCE4` | Bounded incoming event import |
| `0x8065C000` | `0x8079C8EC` | Incoming event dispatch validation |

No command in Code(10).pul overlaps those instruction words. Its bytes also do not contain the earlier module's `NitroAC` diagnostic strings. This is evidence that the exact earlier EventGuard integration is absent from its patch table, not proof that every other form of protection is absent. A server-delivered payload could add runtime patches; that payload was not supplied or inspected.

## Existing source limitations

The retrieved `MKNITRO_NitroAC_Integrated_Source.zip` and 7 October release-candidate contain an experimental EventGuard. Its source checks packet bounds, origin-console ownership for selected events, exact replayed spawns and generous rate limits for a few items. Movement only produces local diagnostic output. Standard event ownership/rate policy is bypassed in several special modes to avoid breaking their intentional item behavior.

That prototype does not verify how an item was acquired. Someone sending valid-looking events at ordinary rates can still use an illegitimate item. It does not implement checkpoint enforcement, authoritative ratings or account sanctions.

The release-candidate README records real regressions with the active menus and characters. Rebuilding it would not preserve the working Code(10).pul. An inherited Gecko check in the archived WiiLink source is conditional on `PROD`; this source observation does not establish which checks are active in the current binary or downloaded payload.

## Interpreting the supplied links

The [Scribd list](https://www.scribd.com/document/655798657/Mario-Kart-Wii-Codelist) is headed RMCE01 and mixes gameplay changes, local conveniences, identity changes and offline-only behavior. It includes checkpoint bypasses, altered movement, item manipulation, altered effects and ratings. Some printed hook addresses are unaligned. Applying those addresses directly to the PAL game would be unsafe.

[LE-CODE's Item Cheat](https://mkwiiki.org/wiki/LE-CODE/Item_Cheat) is a built-in testing facility that assigns selected items. Its documentation says Wiimmfi detects usage. That does not establish that the user's independent server has the same detection, or provide the detector implementation. A detector for one standalone Gecko helper is not a detector for every LE-CODE implementation.

The [Cheat Code page](https://mkwiiki.org/wiki/Cheat_Code) explains the Gecko format and execution mechanism; it is not another exhaustive list. [Dolphin's implementation](https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/Core/GeckoCode.cpp) writes the doubled `0x00D0C0DE` words as a GCT header. Finding that data does not demonstrate current execution. Its [HLE implementation](https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/Core/HLE/HLE.cpp) also uses low memory for other purposes, which reinforces why a nonzero-word scan is unsuitable as a verdict.

## Coverage and remaining work

| Threat | This extension | Needed for stronger protection |
| --- | --- | --- |
| Specific instruction edits at selected movement, timing, progress or damage sites | 23 audit candidates; optional reviewed enforcement | Verify each site against the final Nitro build and server payload; maintain per-build baselines. |
| Gecko/Ocarina presence | GCT-header observation only | Reviewed handler/control-flow signatures plus code integrity. A reimplemented or removed detector remains a bypass risk. |
| Unlimited or chosen items, including LE-CODE behavior | No item entitlement enforcement | Track legitimate acquisition and consumption; validate events at receiving peers; use authenticated, race-bound server grants if introducing a new protocol. |
| Item-event spam or spoofed owner | Prior EventGuard source is a separate prototype; not installed by this package | Merge and validate it with actual mode rules, two local players, transfers, and packet timing. |
| Plausible-rate illicit item use | Not reliably detected | A trusted authority for awards/consumption, not merely an allowed item-ID range. |
| Speed, flight, teleport or altered gravity using live-data writes | Local state observations only | Track/mode-specific movement and progress rules; account for boosts, jumps, cannons, respawns and network interpolation. |
| Finish/lap/time forgery using state writes | No finish-state authority | Verified checkpoint sequences and race-bound result evidence; robust handling of custom lap rules and disconnects. |
| Effect duration, projectile parameters, stat files | Selected code edits only; mutable parameters excluded | Approved gameplay-data manifests and effect state machines. Preserve Nitro's intentional physics and custom items. |
| VR/BR or identity spoofing | No server enforcement | Authenticated sessions, server-owned rating updates and replay-resistant result processing. MAC addresses and temporary room indexes are not strong identities. |
| Cosmetic/UI/controller/unlock changes | No blanket signature ban | Explicitly approved mod behavior. Do not penalize the official speedometer, input display, music or texture changes. |

The generator considers 47 target records and emits 23 unique instruction checks. It excludes 24 records because the supplied PUL already owns the location, REL relocation changes it, the location is mutable data, the source address is unaligned, or region mapping is absent/ambiguous. See `manifest_review.json`. These exclusions are known coverage gaps. A region-map match is an address candidate, not proof that a particular foreign-region cheat has been fully ported and tested.

The checks use expected bytes derived from supplied original files, not values captured from a potentially modified running client. REL relocation sites are excluded. Any location already patched by the supplied Nitro PUL is excluded rather than silently overwriting its legitimate changes. Online payload changes still require separate review.

## Corrections to the pasted proposal

- A Bullet Bill or Lightning can legitimately remain in inventory after the racer moves into first place. Current position cannot establish acquisition legality.
- Inventory often stays unchanged until the player uses or loses the item. Repeated identical values are not a cheating test.
- An active Golden Mushroom permits repeated use without ordinary single-item consumption. Acquisitions, triples, transfers and damage need explicit transition rules.
- There is no one universal speed/displacement cutoff for Nitro's custom modes and tracks. Comparing against a writable local speed-limit field is also not a trust boundary.
- A client-side check can be disabled by a modified client. Signed updates and reported hashes alone do not prove that every participant executes the approved code.
- A matchmaking/authentication server cannot verify gameplay it never receives. Additional trusted evidence or protocol changes are required; relaying self-reported values does not make them authoritative.
- A controlled failure message or connection refusal is easier to diagnose than an unexplained intentional crash, and does not justify an automatic account ban.

## Work sequence

1. Recover the current source/build and binary-patch history, reproduce the working pack, and preserve current UI/gameplay features.
2. Integrate this audit module and inspect clean-session findings on Dolphin and Wii, including the downloaded payload.
3. Validate the bounded event filter separately, then add acquisition/consumption rules for ordinary and special modes. Never derive entitlement solely from position.
4. Review the actual server and payload source. Bind reports to authenticated sessions, room/race identifiers, sequence numbers and approved rules. Do not accept one untrusted peer's accusation as a ban decision.
5. Introduce server-owned ratings and race validation with an explicit evidence policy. Movement rules require clean examples for every supported track and mode.
6. Enable only individually verified enforcement rules, then test in an isolated room before release.

No guarantee is made that all known codes or future variants can be blocked. This package provides a tested source foundation and an explicit account of what is still missing.
