# Verified NitroWFC payload source

`Live-2026-10-16/` preserves the exported welcome-build source byte for byte,
including its public verification key and upstream notices. See NOTICE.md and
VERIFICATION.json. No production or test private signing key is supplied.

The operator rebuilt stage1 and all four RMC payloads from the exported source
in an isolated temporary directory. Every rebuilt SHA-256 matched the deployed
on-disk reference; see VERIFICATION.json for hashes and evidence limits.
This does not establish the completion of the overall client/server source offer.

## Reproduce without signing keys

Use a working Docker installation. The build uses the recorded immutable image,
with network disabled during compilation. Pull that image first if necessary.
Run this from this `patcher` directory; source is copied into a temporary folder:

```sh
image=devkitpro/devkitppc@sha256:44cb1a920e1ec3ec7c06767493c3b85f8d643d6137cc4661f0201895ac6e4967
nitro_build_dir=$(mktemp -d)
printf 'Build directory: %s\n' "$nitro_build_dir"
cp -a Live-2026-10-16 "$nitro_build_dir/source"
TZ=UTC touch -d '2026-09-25 07:27:39 UTC' "$nitro_build_dir/source/payload/wwfcPayload.cpp"
docker run --rm --network none --read-only --tmpfs /tmp -e TZ=UTC \
  -v "$nitro_build_dir:/work" --entrypoint /bin/sh "$image" -c \
  'cd /work/source/stage1 && python3 make-stage1.py && cd ../payload && python3 make-payload.py -gRMC -j2'
sha256sum "$nitro_build_dir/source/stage1/build/stage1.bin" "$nitro_build_dir"/source/payload/binary/payload.*.bin
```

The timestamp restoration reproduces the existing `__TIMESTAMP__` metadata;
it is not a change to executable source. Outputs remain in the printed temporary
folder. Calling individual build scripts avoids the top-level make.sh private-key
check and key-generation side effects. Do not use --all or --keys to reproduce
these outputs: those options may replace the public header and generate keys.
The binaries here are unsigned on-disk inputs; the server signs responses using
its private key at request time. Keep that key private.

The standalone launcher and stage0/exploit build paths are retained as upstream
source but were not built or runtime-tested in this verification.
