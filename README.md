# Mario Kart Nitro

Official releases of Mario Kart Nitro, with recovered client and NitroWFC source
prepared for review on the source-recovery branch.

**This is a source-recovery draft. It is not yet verified as complete
Corresponding Source for every distributed version and all required inputs.**
See [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md) for the precise limits.

- [Client source and build instructions](client/README.md): Pulsar C++/assembly,
  game headers, Pack Creator C#/XAML, editable configs and recovery scripts.
- [NitroWFC server source](server/README.md): archived October source and the
  verified live export and separately repaired AGPL candidate.
- [Verified patcher source](patcher/README.md): stage1 and four RMC payloads,
  pinned build environment and matching hashes.
- [Team next steps](client/NEXT_STEPS.txt) and [validation evidence](client/docs/).
- [Existing game downloads](https://github.com/Massinkjoshua/Mario-Kart-Nitro-Releases/releases).

The published source tree excludes runtime pack assets, precompiled client
references and proprietary compiler executables. The omitted-input manifest
records resource names and hashes needed for the fuller editor/integration work.
The source ZIP handoff remains a separate recovery snapshot.

## Credits and licences

Mario Kart Nitro uses Retro Rewind's rr-pulsar source, with Pulsar, MKW-SP,
WiiLink WFC and other credited contributions. Original notices are retained in
[client/CREDITS.txt](client/CREDITS.txt), [client/THIRD_PARTY_NOTICES.md](client/THIRD_PARTY_NOTICES.md)
and the individual sources. New recovery changes are dated 16 October 2026.

The client is under [GPLv3](LICENSE-GPL-3.0.txt), with original component licences
retained. NitroWFC server source is under [AGPLv3](LICENSE-AGPL-3.0.txt).
Original upstream repositories:

- https://github.com/Retro-Rewind-Team/rr-pulsar
- https://github.com/Retro-Rewind-Team/wfc-server
- https://github.com/Retro-Rewind-Team/wfc-patcher-wii

Online communications credit to WiiLink WFC - https://wfc.wiilink24.com

Assets and tools retain their own rights. This independent project is not
endorsed by Nintendo, Retro Rewind or WiiLink.
