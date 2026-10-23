# Source review

This guide identifies the current server source and the client material available for review. Build results apply to the versions named below.

## NitroWFC server

The server deployed on 21 October 2026 was built from commit [8f0ca795](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/commit/8f0ca79513102480c0d8a53a723d7e902c98c5ca), directory [server/Server-Fixes-2026-10-21](server/Server-Fixes-2026-10-21/).

To inspect that exact source revision:

```sh
git clone --branch source-recovery-2026-10-16 https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases.git
cd Mario-Kart-Nitro-Releases
git checkout 8f0ca79513102480c0d8a53a723d7e902c98c5ca
cd server/Server-Fixes-2026-10-21
export GOTOOLCHAIN=go1.25.5
go test ./...
go test -race ./api ./database ./gpcm
go build -trimpath -buildvcs=false -o NitroWFC-linux-amd64 .
```

Go 1.25.5 and a native C compiler are required for these checks. The host used Linux amd64 with CGO enabled. Rebuilding elsewhere may produce a different hash.

The operator compared the running executable with the staged build and a second on-host build. All three matched. The exact hash, settings and live checks are recorded in the [deployment record](server/docs/deployment-2026-10-21.md). The [source manifest and original test logs](server/Validation/Server-Fixes-2026-10-21/) cover the earlier handoff build; that binary has a separate hash.

The previous deployment source remains in [Live-Export-2026-10-16](server/Live-Export-2026-10-16/). Build instructions and runtime requirements are in the [server README](server/README.md).

## Game client and Pack Creator

The [client directory](client/README.md) contains engine and loader source, Pack Creator C#/XAML, configuration inputs and build scripts.

The confirmed current client is `nitro-ghost-reader-20261023`. Its [build instructions](client/docs/confirmed-build-2026-10-23.md), [compiled-source manifest](client/Validation/Confirmed-2026-10-23/compiled-source-manifest.json) and [runtime confirmation](client/Validation/Confirmed-2026-10-23/runtime-confirmation.json) identify the exact inputs and maintainer-reported Dolphin result.

The source includes the Items-menu memory correction, released character rules, Pauline routing, preserved mini-turbo colours and bounded ghost-folder reads. Earlier review builds and historical backups retain their own records; matching this client does not establish matching source for every older release.

An authorised CodeWarrior toolchain is needed to build the client. Some editor and runtime inputs are missing from the public tree; see [client source status](client/SOURCE_STATUS.md) and the [omitted-input manifest](publication/omitted-client-inputs.json).

## Connection payloads

The [patcher directory](patcher/README.md) contains the exported payload source, public verification key, notices and pinned Docker build instructions. Stage1 and all four RMC payload rebuilds matched the recorded on-disk references. [VERIFICATION.json](patcher/VERIFICATION.json) lists the results and limits.

## Notices and open work

The client is under [GPLv3](LICENSE-GPL-3.0.txt), and NitroWFC under [AGPLv3](LICENSE-AGPL-3.0.txt). Original component notices and upstream attribution remain in the source. See the [project credits](README.md#credits-and-licences).

The [publication status](PUBLICATION_STATUS.md) tracks the remaining work, including historical client mapping, missing assets and resources, ratings integration tests and player-facing source access. This repository is not presented as verified complete Corresponding Source for every distributed version.

The [open source-review pull request](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/pull/3) retains the development history. Historical logs remain available alongside the current summaries.
