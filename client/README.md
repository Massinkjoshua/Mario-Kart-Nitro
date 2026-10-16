# Mario Kart Nitro — editable client source

This source-only publication contains the recovered engine, loader and Windows
Pack Creator source, editable config inputs, original notices, build scripts,
recovery assembly/data and validation records. Read ../PUBLICATION_STATUS.md
and SOURCE_STATUS.md before treating it as existing-release Corresponding Source.

## Build the Wii engine and C++ loader on Linux x86_64

Use make, Python, an authorised CodeWarrior 4.3 build 224 compiler/assembler and
the checksum-pinned wibo/Kamek downloads. Place your authorised executables and
required runtime DLLs under tools/codewarrior/ (not tracked here):

```sh
python3 scripts/fetch_linux_tools.py
bash build_linux.sh
```

This produces isolated build/Code.pul and build/Loader.pul, without installing
anything. Windows/MSYS2 can use build_msys2.sh with the authorised CodeWarrior
and Kamek tools described in START_HERE.md. Third-party tools retain their own
licences. C++ compiler flags follow the recovered October Makefile.

## Editor and reference-dependent checks

The C#/XAML and project files are included. Runtime/art resources needed by its
embedded .resx, application icon and copied font are not public in this draft.
Restore those inputs from your authorised handoff before building the Windows
net7.0-windows editor. Its earlier full-input Release compile passed; that is not
a claim that the editor builds from this source-only clone without resources.

The complete integration suite, emulation comparisons and final-PAL reproduction
also need the supplied reference binaries/current-pack fixtures. Restore those
privately before running the documented tests. No game disc/ISO is included.
Published validation records state exactly which original inputs were tested.

Recovery/LoaderV15/build.py rebuilds the released loader from its included
assembly/data alone (requires keystone-engine 0.9.2):

```sh
python3 -m pip install -r Recovery/LatestPAL/requirements-recovery.txt
python3 Recovery/LoaderV15/build.py --output build/Loader-v15.pul
```

## Attribution

Derived from Retro Rewind rr-pulsar (baseline revision documented in
 docs/source_baseline.json), Pulsar, MKW-SP and credited contributors. Original
notices remain in LICENSE, LICENSE_pulsar, LICENSE_mkw-sp, CREDITS.txt,
THIRD_PARTY_NOTICES.md and source headers. New reconstruction work is dated
16 October 2026 and licensed under the root client GPLv3 licence.

Online communications credit to WiiLink WFC - https://wfc.wiilink24.com
