# Source publication status

Updated 21 October 2026.

This page describes the current source publication. Earlier progress reports are preserved in [the previous revision](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/blob/767d098f9387460116d4b218cbc4a569c4fa462f/PUBLICATION_STATUS.md) and the component validation folders.

## Current position

| Component | Verified | Still to complete |
| --- | --- | --- |
| NitroWFC server | Published source built on the host; tests and focused race checks passed; running executable matches the staged build and a second on-host build. Public pagination and website navigation were checked. | Real ratings report/readback integration, remaining runtime-input review and the source link for this deployed version. |
| Connection payloads | Stage1 and four RMC payload rebuilds match the recorded on-disk deployment references. | Independently verify the bytes served over HTTP and review the other retained build paths. |
| Game client | Source-built candidate with recorded inputs, regional builds and controlled regression checks. Released loader v15 is reproducible from assembly/data. | Identify the active distributed client, complete historical release mapping, and test the identified candidate with its full runtime pack. |
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

The latest review candidate is `nitro-paging-20261018`. Its build records are in [client/Validation/Paging-2026-10-18](client/Validation/Paging-2026-10-18/), with reproduction instructions in the [paging update](client/docs/paging-update-2026-10-18.md).

The client file supplied on 21 October matches the historical released core, not that review candidate. See the [file comparison](client/docs/uploaded-code-review-2026-10-21.md). The operator's successful game smoke test does not identify which client binary was loaded.

The verified [9 October checkpoint](client/Recovery/IntegrityCheckpoint-2026-10-09/) and older candidate records retain their own scope. They are not replacements for the missing released-version mapping.

## Inputs outside this tree

Runtime pack assets, some editor resources, precompiled comparison references and proprietary compiler executables are omitted. Client builds require an authorised CodeWarrior toolchain. Some regression and integration checks also require the separately held reference binaries or full pack.

The [omitted-input manifest](publication/omitted-client-inputs.json), [client source status](client/SOURCE_STATUS.md) and [server runtime-input checklist](server/docs/runtime-inputs.md) document these boundaries. Private credentials, signing keys and player database contents are not part of this publication.

## Review and attribution

Start with [SOURCE_REVIEW.md](SOURCE_REVIEW.md) for the source locations and evidence. Original notices and component licences remain in the source; upstream credits are listed in the [project README](README.md#credits-and-licences).

The source review remains open in [pull request #3](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/pull/3). Existing releases have not been replaced by this documentation update.
