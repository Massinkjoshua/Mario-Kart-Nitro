# Mario Kart Nitro

Mario Kart Nitro is a custom Mario Kart Wii modpack for Wii and Dolphin, with seasonal track selections and online racing through NitroWFC.

[Website](https://mknitro.com/) · [Downloads](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/releases) · [Source code](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/tree/source-recovery-2026-10-16) · [Source review](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/SOURCE_REVIEW.md)

## Source code

The `source-recovery-2026-10-16` branch contains the client, server and connection-payload source, along with build instructions, original notices and verification records.

| Component | Source and build instructions | Current status |
| --- | --- | --- |
| Game client and Pack Creator | [client/](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/client/README.md) | Current client confirmed in Dolphin on 23 October 2026; historical released-version mapping remains open. |
| NitroWFC server | [server/](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/server/README.md) | Deployed on 21 October 2026; an on-host rebuild matches the running executable. |
| Connection payloads | [patcher/](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/patcher/README.md) | Stage1 and all four RMC payload rebuilds match the recorded deployment references. |

For a technical review, start with the [review guide](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/SOURCE_REVIEW.md). It identifies the deployed server source, client versions, build records and remaining work. The [publication status](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/PUBLICATION_STATUS.md) lists what has and has not been verified.

The source publication is still being completed. It has not been verified as complete Corresponding Source for every distributed version. Runtime pack assets and some editor resources are outside this source tree; the [omitted-input manifest](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/publication/omitted-client-inputs.json) records the missing client inputs.

## Review scope

This handoff focuses on the current confirmed client and deployed NitroWFC source. In the maintainer-provided conversation of 23 October, Patchzy said the newest source was sufficient for his review and that the reused Retro Rewind assets should be credited. This records the requested review scope, not acceptance of the delivered source or a blanket licence clearance. Historical records remain available.

## Credits and licences

Mario Kart Nitro uses work from the Retro Rewind Team and the projects credited in the source:

- [Retro Rewind rr-pulsar](https://github.com/Retro-Rewind-Team/rr-pulsar), with Pulsar, MKW-SP and other credited contributions.
- [Retro Rewind wfc-server](https://github.com/Retro-Rewind-Team/wfc-server), based on [WiiLink WFC](https://github.com/WiiLink24/wfc-server).
- [Retro Rewind wfc-patcher-wii](https://github.com/Retro-Rewind-Team/wfc-patcher-wii).

The client is published under [GPLv3](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/LICENSE-GPL-3.0.txt) and the server under [AGPLv3](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/LICENSE-AGPL-3.0.txt). Component licences, copyright notices and attribution are retained. See [client credits](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/client/CREDITS.txt), [third-party notices](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/client/THIRD_PARTY_NOTICES.md) and the [patcher notice](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/source-recovery-2026-10-16/patcher/NOTICE.md).

Online communications credit to [WiiLink WFC](https://wfc.wiilink24.com). Tracks, music, artwork and tools retain their respective rights and licences.

Mario Kart Nitro is an independent fan project, unaffiliated with Nintendo, Retro Rewind or WiiLink.

See [UI and asset credits](ASSET_CREDITS.md) for the reused Retro Rewind menu assets.
