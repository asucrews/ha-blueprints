# Documentation TODO

## Completed

- [x] Add examples for:
  - `vacuum_job_manager`
  - `witb_lights` hook scripts and WITB actions binding snippet
- [x] Add docs QA validation script + CI workflow:
  - `tools/check_blueprint_docs.py`
  - `.github/workflows/docs-blueprint-check.yml`
- [x] Add YAML syntax validation CI workflow:
  - `.github/workflows/yaml-lint.yml`
- [x] Make key README navigation links clickable:
  - `README.md`
  - `references/README.md`
- [x] Fix all broken/stale file references across READMEs and docs:
  - Bathroom fan blueprint path corrected (missing `v1/`)
  - Generator script paths corrected (all point to `blueprints/generate_witb_packages_templated.py`)
  - Template filenames corrected (`_package_template.yaml` suffix)
  - Script hook filenames updated to current short names
  - Example folder names corrected in `examples/README.md`
  - Docs compatibility matrix de-duplicated
- [x] Create missing `blueprints/automation/bathroom_fan_from_humidity/README.md`
- [x] Establish and document naming standards:
  - `NAMING.md` created at repo root with slug rules, casing, version, paired file conventions
  - Linked from `README.md` Quick Links
- [x] Rename changelogs to consistent `CHANGELOG_<blueprint_slug>.md` format:
  - `bathroom_fan_from_humidity/v1/CHANGELOG.md` → `CHANGELOG_bathroom_fan_from_humidity_delta.md`
  - `vacuum_job_manager/v1/CHANGELOG.md` → `CHANGELOG_vacuum_job_manager.md`
  - `witb_switch_light_profiles/v1/CHANGELOG.md` → `CHANGELOG_witb_lights_hooks_vzw31sn.md`
- [x] Rename version-level READMEs to `README_<blueprint_slug>_v<N>.md`:
  - All 7 version-level READMEs renamed; all references updated
  - `tools/check_blueprint_docs.py` updated to accept `README*.md`

---

- [x] Getting Started docs:
  - `docs/GETTING_STARTED.md` — full walkthrough for all users
  - `docs/QUICKSTART.md` — condensed reference for experienced users
  - Both linked from root `README.md`

---

## Next

1. Troubleshooting sections
   - Add `Troubleshooting` sections with concrete checks and expected states to:
     - `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
     - `docs/blueprints/vacuum_job_manager_v1.md`
     - `docs/blueprints/witb_lights_on_hook_vzw31_sn_v1_7.md`
     - `docs/blueprints/witb_lights_off_hook_vzw31_sn_v1_7.md`
   - Suggested coverage:
     - common misbindings
     - helper state mismatches
     - timer/cooldown edge cases
     - unavailable entity handling

3. Migration notes for versioned docs
   - Add `Migration Notes` sections with:
     - behavior changes by version
     - renamed/added inputs
     - safe rollout sequence for existing automations
   - Priority targets:
     - `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
     - `docs/blueprints/witb_lights_hooks_v1_7.md`
