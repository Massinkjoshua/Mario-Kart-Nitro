# Reconstructed released Loader v15

The received 4,192-byte Loader.pul can be rebuilt exactly from the 678 editable
PowerPC instructions in loader_v15.asm and the typed diagnostics, native API
addresses, command jump table and state in loader_data.json. No old binary is
used as an input. The original C++ source for this version was not recovered.

From the project root, install the assembly dependency and choose a new output:

```sh
python3 -m pip install -r Recovery/LatestPAL/requirements-recovery.txt
python3 Recovery/LoaderV15/build.py --output build/Loader-v15.pul
```

The default verifies the recorded SHA-256. Use --allow-modified only when making
an intentional changed loader. The builder refuses to overwrite its output.
Entry point: 0x80004000. DisplayError: 0x8000406c. LoadKamekBinary:
0x800040b4. LoadKamekBinaryFromDisc: 0x80004744. See the labelled assembly.

The normal make loader target remains the separately reconstructed C++ candidate
in Loader/. It has stricter parsing, terminal errors and explicit file ownership;
it is not claimed identical to this historic loader. This assembly target allows
review of the exact released implementation alongside that candidate.

Exact assembly reproduction establishes the loader output only. It does not
prove that the whole client/server Corresponding Source is complete, that the
original preferred source form has been recovered, or that a game boot passed.
Original project notices remain in the root licences. Reconstruction changes
are dated 16 October 2026 and supplied under GPLv3.
