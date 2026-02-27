# Documentation TODO

## Completed

- [x] Add examples for:
  - `vacuum_job_manager_v1`
  - `witb_lights_v1` hook scripts and WITB actions binding snippet
- [x] Add docs QA validation script + CI workflow:
  - `tools/check_blueprint_docs.py`
  - `.github/workflows/docs-blueprint-check.yml`
- [x] Add YAML syntax validation CI workflow:
  - `.github/workflows/yaml-lint.yml`
- [x] Make key README navigation links clickable:
  - `README.md`
  - `references/README.md`

## Next

1. Getting Started walkthrough in root docs
- Add a single end-to-end quickstart in `README.md`:
  - generate helpers
  - load packages
  - create automation/script instances
  - verify core entities and first run

2. Migration mapping for older WITB light hook names
- Add a mapping table from older filenames/variants to v1.7 files in:
  - `docs/blueprints/witb_lights_hooks_v1_7.md`
  - `blueprints/script/witb_lights/v1/README.md`

3. Troubleshooting sections
- Add `Troubleshooting` sections with concrete checks and expected states to:
  - `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
  - `docs/blueprints/vacuum_job_manager_v1.md`
  - `docs/blueprints/witb_lights_on_hook_vzw31_sn_v1_7.md`
  - `docs/blueprints/witb_lights_off_hook_vzw31_sn_v1_7.md`

Suggested coverage:
- common misbindings
- helper state mismatches
- timer/cooldown edge cases
- unavailable entity handling

4. Migration notes for versioned docs
- Add `Migration Notes` sections with:
  - behavior changes by version
  - renamed/added inputs
  - safe rollout sequence for existing automations

Priority targets:
- `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
- `docs/blueprints/witb_lights_hooks_v1_7.md`
