# Source publication status

Updated 23 October 2026.

This page describes the current source publication. Earlier progress reports are preserved in [the previous revision](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/767d098f9387460116d4b218cbc4a569c4fa462f/PUBLICATION_STATUS.md) and the component validation folders.

## Current review scope

Following Patchzy's reply provided by the maintainer on 23 October, this handoff focuses on the newest source. Historical correspondence is retained as a technical limitation, rather than a prerequisite requested by Patchzy for this review. His asset reply requests Retro Rewind attribution; see [ASSET_CREDITS.md](ASSET_CREDITS.md). Neither reply is recorded as approval of the delivered source.

## Current position

| Component | Verified | Still to complete |
| --- | --- | --- |
| NitroWFC server | Published source built on the host; tests and focused race checks passed; running executable matches the staged build and a second on-host build. Public pagination and website navigation were checked. | Real ratings report/readback integration and remaining runtime-input review. Website source access was verified on 23 October; see publication/follow-up-2026-10-23.md. |
| Connection payloads | Stage1 and four RMC payload rebuilds match the recorded on-disk deployment references. | Independently verify the bytes served over HTTP and review the other retained build paths. |
| Game client | Exact source and build manifest for `nitro-ghost-reader-20261023`; maintainer confirmed it working in Dolphin on 23 October. Released loader v15 is reproducible from assembly/data. | Public release rollout, Wii/other-region testing and historical release mapping remain separate. |
| Pack Creator and assets | C#/XAML source and omitted-input records are included. A prior editor build with private resource inputs passed. | Supply or resolve missing editor resources, preferred editable asset sources and redistribution permissions. |

The publication is not yet verified as complete Corresponding Source for every distributed version. The verified server build does not establish a matching source release for the game client.

## Deployed server

The server uses [Server-Fixes-2026-10-21](server/Server-Fixes-2026-10-21/) from source commit `8f0ca79513102480c0d8a53a723d7e902c98c5ca`.

The running executable, staged candidate and second on-host build share SHA-256:

```text
9e4dda5664349cfe985662ed4a2086b87a3fa04b09aed01338e838cc3fc572ed
```

See the [deployment record](server/docs/deployment-2026-10-21.md) for build settings, operator evidence, database checks and test limits. The separately archived October-12 candidate's `/api/source` route is not assumed to exist in this version.

## Client versions

The confirmed current client is `nitro-ghost-reader-20261023`, with Code.pul SHA-256 `735b7d0e3d674de031325f240dd07eebe7fb2d5d820e7d9c8372eb492fe0e1c2`. The maintainer confirmed the Time Trials fix working and reported that everything worked in their testing on 23 October. See the [build instructions](client/docs/confirmed-build-2026-10-23.md) and [confirmation](client/Validation/Confirmed-2026-10-23/runtime-confirmation.json).

The earlier paging build and historical backup retain their own records. This confirmation does not establish that the public launcher distributes this new binary or that its online hash has been approved.

The verified [9 October checkpoint](client/Recovery/IntegrityCheckpoint-2026-10-09/) and older candidate records retain their own scope. They are not replacements for the missing released-version mapping.

## Inputs outside this tree

Runtime pack assets, some editor resources, precompiled comparison references and proprietary compiler executables are omitted. Client builds require an authorised CodeWarrior toolchain. Some regression and integration checks also require the separately held reference binaries or full pack.

The [omitted-input manifest](publication/omitted-client-inputs.json), [client source status](client/SOURCE_STATUS.md) and [server runtime-input checklist](server/docs/runtime-inputs.md) document these boundaries. Private credentials, signing keys and player database contents are not part of this publication.

## Review and attribution

Start with [SOURCE_REVIEW.md](SOURCE_REVIEW.md) for the source locations and evidence. Original notices and component licences remain in the source; upstream credits are listed in the [project README](README.md#credits-and-licences).

The source review remains open in [pull request #3](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/pull/3). Existing releases have not been replaced by this documentation update.
