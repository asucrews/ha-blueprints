# Getting Started

**Audience:** Anyone new to this project — whether you are new to Home Assistant or just new to WITB+. This guide explains each step and why it exists.

> Already comfortable with HA blueprints, YAML packages, and Python? See [`QUICKSTART.md`](QUICKSTART.md) for the condensed version.

This guide walks you through setting up WITB+ room occupancy and light/fan automation from scratch for a standard enclosed room (e.g., an office or bedroom with a door).

---

## What Is WITB+?

WITB+ (Wasp-in-the-Box) infers whether a room is occupied by watching door and motion events — it does not poll sensors on a timer. The core idea:

- When someone enters (door opens + motion seen), the room is marked **occupied**.
- When they leave (door closes after motion stops), the room is marked **vacant**.
- A failsafe timer clears occupancy if nothing happens for a long time.

Two blueprints work together:

| Blueprint | What it does |
|---|---|
| **WITB+ Occupancy** | Watches doors and motion. Sets `input_boolean.<slug>_occupied`. |
| **WITB+ Actions - Lights + Fan** | Watches `binary_sensor.<slug>_occupied_effective`. Turns lights/fan on and off. |

They are deliberately separate so you can pair one occupancy source with multiple action automations, or swap in a different occupancy source (like the Transit Room driver) without changing your light/fan logic.

---

## Before You Begin

### Home Assistant version

Minimum: **2026.2.0**. Check at **Settings → About**.

### Packages support

These blueprints use helper entities (booleans, datetime inputs, timers, template sensors) defined in YAML package files. To load them, your `configuration.yaml` must include:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

If you don't have a `packages/` directory yet, create one alongside `configuration.yaml`.

### Sensors you need (minimum)

- **One door contact sensor** — the room's main door (`binary_sensor.*`, `on` = open)
- **One PIR motion sensor** — inside the room (`binary_sensor.*`, `on` = motion detected)

Optional but recommended:
- An mmWave presence sensor for more reliable occupancy hold
- An illuminance sensor to gate lights (only turn on when dark)

### Python 3 on your workstation

The helper generator is a Python script run from this repo on your computer — not on HA itself.

```bash
python3 --version   # should be 3.8+
```

---

## Step 1 — Import the blueprints into Home Assistant

Blueprints live in Home Assistant, not in this repo directly. You import them once and then create as many automations from them as you need.

1. In HA go to **Settings → Automations & Scenes → Blueprints**.
2. Click **Import Blueprint** (top right).
3. Paste the raw URL and click **Preview → Import**.

Import both:

**WITB+ Occupancy (v4)**
```
https://raw.githubusercontent.com/asucrews/ha-blueprints/main/blueprints/automation/witb_plus/v4/witb_plus.yaml
```

**WITB+ Actions - Lights + Fan (v2)**
```
https://raw.githubusercontent.com/asucrews/ha-blueprints/main/blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml
```

After importing, both appear in your blueprint list. You will create automations from them in Step 4.

---

## Step 2 — Generate helper packages

Each room needs its own set of helper entities. The generator reads a template and produces a ready-to-load YAML package file for each room you specify.

Run these commands from the root of this repo. Replace `"Office"` with your actual room name — use the full human-readable name, the generator handles the slug conversion.

**Occupancy helpers:**
```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" \
  --template blueprints/automation/witb_plus/v4/witb_plus_package_template.yaml \
  --out blueprints/automation/witb_plus/v4/packages
```

**Actions helpers:**
```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" \
  --template blueprints/automation/witb_plus_actions_lights_fan/v2/room_witb_actions_package_template.yaml \
  --out blueprints/automation/witb_plus_actions_lights_fan/v2/packages
```

This creates two files:
- `blueprints/automation/witb_plus/v4/packages/office.yaml`
- `blueprints/automation/witb_plus_actions_lights_fan/v2/packages/office_witb_actions.yaml`

> **Tip:** Add `--dry-run` to preview what would be generated without writing any files.

> **Multiple rooms:** List them all in one command — `--rooms "Office" "Master Bedroom" "Hallway"`.

---

## Step 3 — Load packages into Home Assistant

Copy the generated files into your HA `packages/` directory:

```bash
cp blueprints/automation/witb_plus/v4/packages/office.yaml \
   /path/to/homeassistant/packages/

cp blueprints/automation/witb_plus_actions_lights_fan/v2/packages/office_witb_actions.yaml \
   /path/to/homeassistant/packages/
```

Then reload the configuration so HA creates the helper entities:

**Developer Tools → YAML → Reload All YAML**

Or do a full restart if you changed `configuration.yaml` to add the `packages:` line for the first time.

### What entities get created?

After loading, you should see these new entities for `office`:

| Entity | Purpose |
|---|---|
| `input_boolean.office_occupied` | Core occupancy state — set by WITB+ automation |
| `input_boolean.office_automation_override` | Disables automation control when on |
| `input_boolean.office_force_occupied` | Forces occupancy on (e.g., from vacuum or bed sensor) |
| `input_boolean.office_manual_occupied` | Manual hold from a dashboard |
| `input_boolean.office_latched` | Debug latch — room entered but not yet confirmed occupied |
| `input_datetime.office_last_motion` | Timestamp of last motion event |
| `input_datetime.office_last_door` | Timestamp of last door event |
| `input_datetime.office_last_exit_door` | Timestamp of last exit-door close |
| `timer.office_failsafe` | Clears occupancy if nothing happens for too long |
| `binary_sensor.office_occupied_effective` | True when occupied OR any override is active |
| `binary_sensor.office_witb_override_active` | True when any override is active |
| `sensor.office_minutes_since_motion` | Minutes since last motion — useful for dashboards |

For actions:

| Entity | Purpose |
|---|---|
| `input_boolean.office_auto_lights_on` | Tagged by automation when it turns lights on |
| `input_boolean.office_auto_fan_on` | Tagged by automation when it turns fan on |
| `timer.office_actions_cooldown` | Prevents rapid re-triggering |
| `timer.office_fan_runon` | Keeps fan running after vacancy |

---

## Step 4 — Create automations in Home Assistant

Now create the actual automations from the imported blueprints.

### 4a — WITB+ Occupancy automation

1. Go to **Settings → Automations & Scenes → Create Automation**.
2. Choose **Use Blueprint** → select **WITB+ Occupancy**.
3. Fill in the inputs:

| Input | What to select |
|---|---|
| Seal Door | Your room's main door contact sensor |
| Motion Sensor | Your PIR sensor inside the room |
| Occupancy Helper | `input_boolean.office_occupied` |
| Last Motion Helper | `input_datetime.office_last_motion` |
| Last Door Helper | `input_datetime.office_last_door` |
| Last Exit Door Helper | `input_datetime.office_last_exit_door` |
| Latched Helper | `input_boolean.office_latched` |
| Automation Override | `input_boolean.office_automation_override` |
| Force Occupied | `input_boolean.office_force_occupied` |
| Manual Occupied | `input_boolean.office_manual_occupied` |
| Failsafe Timer | `timer.office_failsafe` |

4. Save the automation.

### 4b — WITB+ Actions automation

1. Create another automation → **Use Blueprint** → select **WITB+ Actions - Lights + Fan**.
2. Fill in the inputs:

| Input | What to select |
|---|---|
| Occupied Effective | `binary_sensor.office_occupied_effective` |
| Lights | Your room's light entities |
| Auto Tag Lights | `input_boolean.office_auto_lights_on` |
| Fan Entity | Your fan entity (if applicable) |
| Auto Tag Fan | `input_boolean.office_auto_fan_on` |
| Cooldown Timer | `timer.office_actions_cooldown` |
| Fan Run-On Timer | `timer.office_fan_runon` |
| Automation Override | `input_boolean.office_automation_override` |
| Force Occupied | `input_boolean.office_force_occupied` |
| Manual Occupied | `input_boolean.office_manual_occupied` |

3. Configure brightness, night mode, lux gating, and fan run-on to your preferences.
4. Save the automation.

---

## Step 5 — Verify it works

### Check entities exist

Go to **Developer Tools → States** and search for `office`. You should see all the entities from the table in Step 3.

### Trigger a test

1. Open your room's door — `input_boolean.office_latched` should turn `on`.
2. Trigger motion — `input_boolean.office_occupied` should turn `on`, and `binary_sensor.office_occupied_effective` should become `on`.
3. Stop moving and close the door — after the configured exit timeout, `office_occupied` should turn `off` and lights/fan should turn off.

### Check the automation trace

If something doesn't fire as expected:

1. Go to **Settings → Automations**.
2. Click your WITB+ automation → **Traces** (top right).
3. The trace shows exactly which trigger fired and which conditions passed or failed.

---

## Adding more room types

### Hallways and stairways (no door)

Use the **WITB Transit Room Driver** instead of WITB+ Occupancy. It uses PIR-only occupancy with a hold-timer decay and produces the same `occupied_effective` output consumed by WITB+ Actions.

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Hallway" \
  --template blueprints/automation/witb_transit_room/v1/transit_helpers_package_template.yaml \
  --out blueprints/automation/witb_transit_room/v1/packages
```

### Bathroom fan from humidity

Add humidity-driven fan control on top of (or instead of) occupancy-based control. Requires a humidity delta sensor.

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Master Bathroom" \
  --template blueprints/automation/bathroom_fan_from_humidity/v1/room_humidity_baseline_delta_package_template.yaml \
  --out blueprints/automation/bathroom_fan_from_humidity/v1/packages
```

### Bedroom sleep guard

Prevents WITB+ from clearing occupancy while someone is in bed. No separate helpers needed — reuses the WITB+ v4 helpers already generated for the bedroom.

Import `witb_plus_bed_force_occupied.yaml` and bind:
- Bed sensor → your bed presence sensor
- Occupied Effective → `binary_sensor.<slug>_occupied_effective`
- Force Occupied → `input_boolean.<slug>_force_occupied`

---

## Next steps

- [`docs/blueprints/README.md`](blueprints/README.md) — full compatibility matrix and links to per-blueprint reference docs
- [`examples/`](../examples/) — copy-ready YAML for packages and automations
- [`QUICKSTART.md`](QUICKSTART.md) — condensed reference once you know the flow
