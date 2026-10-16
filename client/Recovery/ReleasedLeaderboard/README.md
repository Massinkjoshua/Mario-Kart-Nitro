# Released PAL leaderboard request-flow source recovery

This optional source overlay recovers four request-lifecycle functions from the
supplied latest PAL release: OnActivate, OnDeactivate, StartFetch and
OnLeaderboardReceived. It is based on the original supplied v5 module, retaining
its text/notices, and adds the observed numbered error states and reserved
16 KiB work buffer. Buffer alignment is explicit after Kamek section layout.

The compiler builds this C++ directly. The release binary is used only by the
comparison test, never as an input to build.py. The recovery profile links with
the already source-built candidate's other object files. It is separate from the
candidate's safer queued-callback implementation, which remains the default.

## Build and compare

First build the ordinary client project with the authorised CodeWarrior/Kamek
toolchain, as described in client/README.md. Then from client/:

```sh
python3 Recovery/ReleasedLeaderboard/build.py --compiler /path/to/mwcceppc.exe --runner /path/to/wibo --linker /path/to/Kamek
python3 tests/leaderboard_network_ppc.py
```

On Windows omit --runner if the compiler is directly executable. The Python
script expects the existing build/kamek.o and build/PulsarEngine objects. Choose
--output-dir NEW_DIRECTORY to retain an existing recovery build; pass the same
path to the test using --profile-dir NEW_DIRECTORY. Outputs are isolated under
build/released-leaderboard by default. The build never installs into a game pack.
The test requires Unicorn 2.1.4 and the authorised latest reference at
CurrentPack/MarioKartNitro_Test/Binaries/Code.pul.

252 compiled PowerPC executions passed across 63 distinct cases at two load
bases. The comparison checks state transitions, URL page calculation, generation
handling, reserved-buffer size/alignment, friend-key arguments, allocation/copy/
cleanup order, parsed synthetic responses and menu exit cleanup. Expected states
and calls are asserted independently as well as comparing both executions.
Exact hashes and cases are in ../../docs/leaderboard-network-emulation.json.

## Boundaries and remaining work

This is request-flow recovery, not a release-ready whole leaderboard replacement.
The surrounding methods remain original v5 source and have not been certified
against the latest release's diagnostic text and Mii display patches. The
historical callback parses directly and records active requests after dispatch;
its known lifetime/order limitations are preserved for correspondence checks.

The request-creation boundary is intercepted: the release calls its MEM2 wrapper,
while this overlay calls the native creator. Their internal equivalence is not
claimed. Allocator implementations, bookkeeping, own-Mii override, UI reset,
sounds, actual asynchronous scheduling and Wii/Dolphin runtime are outside the
controlled test. Existing editable assembly patch recipes remain in
../OriginalRecipes for the released MEM2/Mii changes. Further integration is
required before this profile could be considered for a gameplay build.

The complete latest core and older release source correspondence remain open.
