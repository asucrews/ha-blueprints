# Vacuum Job Manager v1 Examples

Blueprint source:
- `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`

## Files

- `packages/roomba_vacjob.yaml`
- `roomba_vacjob_automation.yaml`

## How To Use

1. Copy `packages/roomba_vacjob.yaml` into your Home Assistant packages directory.
2. Ensure packages are enabled (`!include_dir_merge_named`).
3. Create automation from `roomba_vacjob_automation.yaml` and update:
   - `use_blueprint.path`
   - vacuum entity
   - iRobot mission sensors
   - optional lights/occupancy/WITB override entities
