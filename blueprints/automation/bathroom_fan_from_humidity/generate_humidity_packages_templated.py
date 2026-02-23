#!/usr/bin/env python3
"""generate_humidity_packages_templated.py

Render Home Assistant package YAML files from a package template, for per-room humidity baseline + delta sensors.

Template tokens replaced:
  - room_slug
  - Room Friendly Name
  - __HUMIDITY_SENSOR__
  - __FAN_ENTITY__

Usage examples:
  python generate_humidity_packages_templated.py --rooms "Master Bathroom" "Guest Bath" \
    --template room_humidity_baseline_delta_package.template.yaml --out ./packages \
    --humidity-pattern "sensor.{room_slug}_humidity" --fan-pattern "switch.{room_slug}_fan"

  python generate_humidity_packages_templated.py --rooms-file rooms.yaml \
    --template room_humidity_baseline_delta_package.template.yaml --out ./packages

rooms.yaml example:
  rooms:
    - name: Master Bathroom
      slug: master_bathroom
      humidity_sensor: sensor.master_bathroom_humidity
      fan_entity: switch.master_bathroom_fan
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    print("Missing dependency: pyyaml. Install with: pip install pyyaml", file=sys.stderr)
    raise

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def render(template: str, room_slug: str, room_name: str, humidity_sensor: str, fan_entity: str) -> str:
    out = template
    out = out.replace("room_slug", room_slug)
    out = out.replace("Room Friendly Name", room_name)
    out = out.replace("__HUMIDITY_SENSOR__", humidity_sensor)
    out = out.replace("__FAN_ENTITY__", fan_entity)
    return out

def load_rooms_file(path: Path):
    data = yaml.safe_load(path.read_text())
    if not data:
        return []
    rooms = data.get("rooms", data)
    if not isinstance(rooms, list):
        raise SystemExit(f"rooms file must be a list or have a top-level 'rooms:' list. Got: {type(rooms)}")
    norm = []
    for r in rooms:
        if not isinstance(r, dict) or "name" not in r:
            raise SystemExit("Each room entry must be a mapping with at least 'name'.")
        name = r["name"]
        slug = r.get("slug") or slugify(name)
        humidity = r.get("humidity_sensor")
        fan = r.get("fan_entity")
        if not humidity or not fan:
            raise SystemExit(f"Room '{name}' missing humidity_sensor or fan_entity.")
        norm.append({"name": name, "slug": slug, "humidity_sensor": humidity, "fan_entity": fan})
    return norm

def main():
    ap = argparse.ArgumentParser(description="Generate per-room humidity baseline+delta HA packages from a template.")
    ap.add_argument("--template", required=True, help="Path to the package template YAML.")
    ap.add_argument("--out", required=True, help="Output folder (packages).")

    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--rooms", nargs="+", help="Room friendly names (slugs auto-derived).")
    group.add_argument("--rooms-file", help="YAML file with room mappings (name/slug/humidity_sensor/fan_entity).")

    ap.add_argument("--humidity-pattern", default=None,
                    help='Pattern to derive humidity sensor from room_slug, e.g. "sensor.{room_slug}_humidity"')
    ap.add_argument("--fan-pattern", default=None,
                    help='Pattern to derive fan entity from room_slug, e.g. "switch.{room_slug}_fan"')

    ap.add_argument("--filename-suffix", default="humidity", help="Output filename suffix (default: humidity).")
    args = ap.parse_args()

    template_path = Path(args.template)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    template_text = template_path.read_text(encoding="utf-8")

    rooms = []
    if args.rooms_file:
        rooms = load_rooms_file(Path(args.rooms_file))
    else:
        if not args.humidity_pattern or not args.fan_pattern:
            raise SystemExit("When using --rooms, you must provide --humidity-pattern and --fan-pattern.")
        for name in args.rooms:
            slug = slugify(name)
            humidity = args.humidity_pattern.format(room_slug=slug, room_name=name)
            fan = args.fan_pattern.format(room_slug=slug, room_name=name)
            rooms.append({"name": name, "slug": slug, "humidity_sensor": humidity, "fan_entity": fan})

    for r in rooms:
        rendered = render(
            template_text,
            room_slug=r["slug"],
            room_name=r["name"],
            humidity_sensor=r["humidity_sensor"],
            fan_entity=r["fan_entity"],
        )
        out_path = out_dir / f"{r['slug']}_{args.filename_suffix}.yaml"
        out_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
