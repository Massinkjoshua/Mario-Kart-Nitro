# Recovered final PAL patch source

Reconstructed on 16 October 2026 from the supplied latest `Code.pul`.
These are editable assembly instructions, typed Kamek patch operations and RGB
palette data. The original patch author's source was not recovered for this part.
The code is provided under the project GPLv3 licence.

The exact October reference's USA and Japan sections already match the latest
release. PAL adds 181 assembly instructions, 48 × 51 RGB colours, three effect
prefixes, four instruction edits and six edits to the Kamek command list. The
palette handles `rk_driftSpark`, `rk_purpleTurbo` and `rk_miniTurbo` effects using
the driver's race skin. The INFO copy wrapper also enables the UMT and Feather
capability flags; it does not change the 200cc flag or the configuration files.

```sh
python3 -m pip install -r Recovery/LatestPAL/requirements-recovery.txt
python3 Recovery/LatestPAL/reproduce.py --output build/recovered-latest-Code.pul \
  --report build/recovered-latest-report.json
```

An unchanged recipe reproduces the supplied 2,688,428-byte release exactly:
`58de1c05cfd1a39c80552ec5bef20582b68460606eac98ec7f540d88a81ec364`.
The input is hash-checked and existing output files are never overwritten.

**This is a binary-dependent patch recipe.** It requires the labelled October
reference in `Recovery/Reference/`. It does not establish that the entire core
can be rebuilt from the supplied C++ source. A binary-dependent reproduction
must not be presented as complete matching source for the release.
