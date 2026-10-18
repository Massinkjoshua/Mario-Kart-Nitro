# Integrated NitroIntegrity

The live implementation is in `../PulsarEngine/Security/NitroIntegrity`.
The original WiiLink patch is already applied. Do not apply it again.

From the project root:

```sh
bash NitroIntegrity/tests/run.sh
python3 Verification/check_integration.py
```

Manifest regeneration for a later reconstructed binary:

```sh
python3 NitroIntegrity/tools/build_manifest.py \
  --dol /path/to/main.dol \
  --rel /path/to/StaticR.rel \
  --code /path/to/candidate/Code.pul \
  --versions GameSource/versions.txt \
  --targets NitroIntegrity/tools/targets.json \
  --out PulsarEngine/Security/NitroIntegrity
```

The generator intentionally accepts only the reviewed original PAL game inputs.
It rejects other revisions. The supplied original game files are not bundled.
Rebuild after generated-table changes and inspect the final baseline again.

The initial mode is audit-only. Follow the root README for project status;
`UPSTREAM_*` files record the attached prototype's earlier assessment and tests.
They are historical provenance, not a claim that their game tests or build
steps have been performed in this reconstructed source project.
