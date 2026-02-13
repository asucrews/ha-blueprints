# Documentation TODO

## 5. Troubleshooting Sections

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

## 6. Migration Notes

- Add `Migration Notes` sections for versioned docs, including:
  - behavior changes by version
  - renamed/added inputs
  - safe rollout sequence for existing automations

Priority targets:
- `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
- `docs/blueprints/witb_lights_hooks_v1_7.md`

## 7. Docs QA Check (Script + CI)

- Add a lightweight docs validation script (for example under `tools/`) that checks:
  - every `blueprints/**` YAML containing `blueprint:` has a sibling `README.md`
  - every active blueprint YAML is referenced by `docs/blueprints/README.md`
  - every active blueprint has a corresponding page in `docs/blueprints/`

- Add CI workflow to run this check on pull requests.
