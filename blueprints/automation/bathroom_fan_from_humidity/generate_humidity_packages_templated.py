#!/usr/bin/env python3
from __future__ import annotations

"""
Template-driven generator for Home Assistant merge_named packages for:

  - Adaptive Humidity Baseline (as a trigger-based template sensor)
  - Humidity Delta From Baseline (template sensor)

Reads a YAML template file and does:
  - token replacement (room_slug, Room Friendly Name, __HUMIDITY_SENSOR__, __FAN_ENTITY__)
  - optional block removal via markers (# --- BEGIN <block> --- / # --- END <block> ---)
  - wraps the result under a per-room package key and writes one file per room

Usage (pattern-based entities):
  ./generate_humidity_packages_templated.py \
      --rooms "Master Bathroom" "Guest Bath" \
      --out ./packages \
      --template ./room_humidity_baseline_delta_package.template.yaml \
      --humidity-pattern "sensor.{room_slug}_humidity" \
      --fan-pattern "switch.{room_slug}_fan"

Usage (rooms file JSON/YAML):
  rooms:
    - name: Master Bathroom
      humidity_sensor: sensor.mb_humidity
      fan_entity: switch.mb_fan
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join((pad + line) if line.strip() else line for line in text.splitlines())


def load_config(path: Path) -> dict[str, Any]:
    txt = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()
    if ext in [".yaml", ".yml"]:
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise RuntimeError("YAML config requested but PyYAML is not installed. Install with: pip install pyyaml") from e
        cfg = yaml.safe_load(txt)
        if not isinstance(cfg, dict):
            raise ValueError("Config file must contain a mapping/object at the top level.")
        return cfg
    cfg = json.loads(txt)
    if not isinstance(cfg, dict):
        raise ValueError("Config file must contain a JSON object at the top level.")
    return cfg


@dataclass
class Room:
    name: str
    slug: str
    package_key: str
    humidity_sensor: str
    fan_entity: str


def build_room(name: str, key_suffix: str, humidity_sensor: str, fan_entity: str) -> Room:
    slug = slugify(name)
    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
        humidity_sensor=humidity_sensor,
        fan_entity=fan_entity,
    )


def room_from_obj(obj: dict[str, Any], key_suffix: str) -> Room:
    name = str(obj["name"])
    slug = str(obj.get("slug") or slugify(name))
    humidity_sensor = str(obj["humidity_sensor"])
    fan_entity = str(obj["fan_entity"])
    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
        humidity_sensor=humidity_sensor,
        fan_entity=fan_entity,
    )


_MARK_BEGIN = re.compile(r"^\s*#\s*---\s*BEGIN\s+([A-Za-z0-9_]+)\s*---\s*$")
_MARK_END = re.compile(r"^\s*#\s*---\s*END\s+([A-Za-z0-9_]+)\s*---\s*$")


def render_marked_blocks(template_text: str, enabled_blocks: set[str]) -> str:
    out: list[str] = []
    stack: list[tuple[str, bool]] = []
    keep = True

    for line in template_text.splitlines():
        m1 = _MARK_BEGIN.match(line)
        if m1:
            name = m1.group(1)
            this_keep = (name in enabled_blocks) and keep
            stack.append((name, this_keep))
            keep = this_keep
            continue

        m2 = _MARK_END.match(line)
        if m2:
            name = m2.group(1)
            if not stack or stack[-1][0] != name:
                raise ValueError(f"Template marker mismatch: END {name} without matching BEGIN")
            stack.pop()
            keep = stack[-1][1] if stack else True
            continue

        if keep:
            out.append(line)

    if stack:
        raise ValueError(f"Unclosed template block(s): {', '.join(n for n, _ in stack)}")

    return "\n".join(out).rstrip() + "\n"


def extract_inner_if_single_package(text: str) -> tuple[str, str | None]:
    lines = text.splitlines()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    if not lines:
        return text, None

    if lines[0].strip() == "---":
        lines = lines[1:]
        while lines and lines[0].strip() == "":
            lines.pop(0)
    if not lines:
        return "", None

    m = re.match(r"^([A-Za-z0-9_]+):\s*$", lines[0])
    if not m:
        return text, None

    key = m.group(1)
    inner_lines = lines[1:]
    out: list[str] = []
    for ln in inner_lines:
        out.append(ln[2:] if ln.startswith("  ") else ln)
    return "\n".join(out).lstrip("\n"), key


def apply_tokens(text: str, room: Room, slug_token: str, name_token: str, humidity_token: str, fan_token: str) -> str:
    text = text.replace(slug_token, room.slug)
    text = text.replace(name_token, room.name)
    text = text.replace(humidity_token, room.humidity_sensor)
    text = text.replace(fan_token, room.fan_entity)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rooms", nargs="*", default=[], help="Room friendly names")
    ap.add_argument("--rooms-file", help="JSON/YAML config file with rooms list")
    ap.add_argument("--out", required=True, help="Output folder for generated package YAML files")
    ap.add_argument("--template", required=True, help="Path to a YAML template file")

    ap.add_argument("--humidity-pattern", help="Pattern like sensor.{room_slug}_humidity (used with --rooms)")
    ap.add_argument("--fan-pattern", help="Pattern like switch.{room_slug}_fan (used with --rooms)")

    ap.add_argument("--package-key-suffix", default="_humidity", help="Suffix for merge_named package key (default: _humidity)")
    ap.add_argument("--file-suffix", default="_humidity.yaml", help="Suffix for output filename (default: _humidity.yaml)")
    ap.add_argument("--dry-run", action="store_true", help="Print rendered YAML to stdout instead of writing files")

    ap.add_argument("--no-tuning-helpers", action="store_true", help="Omit input_boolean/input_number tuning helpers (template defaults still apply)")

    ap.add_argument("--template-slug-token", default="room_slug")
    ap.add_argument("--template-name-token", default="Room Friendly Name")
    ap.add_argument("--template-humidity-token", default="__HUMIDITY_SENSOR__")
    ap.add_argument("--template-fan-token", default="__FAN_ENTITY__")

    args = ap.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")

    rooms: list[Room] = []
    if args.rooms_file:
        cfg = load_config(Path(args.rooms_file))
        raw_rooms = cfg.get("rooms")
        if not isinstance(raw_rooms, list) or not raw_rooms:
            raise SystemExit("rooms-file must contain: rooms: [ {name, humidity_sensor, fan_entity, ...}, ... ]")
        for obj in raw_rooms:
            if not isinstance(obj, dict) or "name" not in obj or "humidity_sensor" not in obj or "fan_entity" not in obj:
                raise SystemExit("Each room object must include: name, humidity_sensor, fan_entity")
            rooms.append(room_from_obj(obj, args.package_key_suffix))

    if args.rooms:
        if not args.humidity_pattern or not args.fan_pattern:
            raise SystemExit("--humidity-pattern and --fan-pattern are required when using --rooms (unless you use --rooms-file).")
        for name in args.rooms:
            slug = slugify(name)
            hum = args.humidity_pattern.format(room_slug=slug)
            fan = args.fan_pattern.format(room_slug=slug)
            rooms.append(build_room(name, args.package_key_suffix, hum, fan))

    if not rooms:
        raise SystemExit("No rooms provided. Use --rooms ... (+ patterns) or --rooms-file ...")

    enabled_blocks: set[str] = set()
    if not args.no_tuning_helpers:
        enabled_blocks.add("tuning_helpers")

    raw = template_path.read_text(encoding="utf-8")
    inner, _ = extract_inner_if_single_package(raw)
    inner = render_marked_blocks(inner, enabled_blocks)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    for room in rooms:
        inner_room = apply_tokens(
            inner,
            room,
            slug_token=args.template_slug_token,
            name_token=args.template_name_token,
            humidity_token=args.template_humidity_token,
            fan_token=args.template_fan_token,
        ).rstrip() + "\n"

        full = "---\n" + f"{room.package_key}:\n" + indent(inner_room, 2)
        if not full.endswith("\n"):
            full += "\n"

        if args.dry_run:
            print(f"# ===== {room.package_key} ({room.slug}) =====")
            print(full)
        else:
            out_path = outdir / f"{room.slug}{args.file_suffix}"
            out_path.write_text(full, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
