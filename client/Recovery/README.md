# Recovery evidence

The current root source project incorporates later recovered C++ implementations.
`OriginalRecipes/` retains the historic authors' patch and verification scripts.
They refer to their original workspace, inputs and intermediate files; they are
historical source, not standalone rebuild commands for this project.

`LatestPAL/` is a newly reconstructed, runnable assembly/data recipe for the final
PAL changes. Its dependence on a precompiled core is explicit. `Reference/` holds
that unchanged core reference. `CheckpointHistory/` contains the older checkpoint's
own status and build record. The current status is defined by the root
`SOURCE_STATUS.md`, not by historical READMEs.
