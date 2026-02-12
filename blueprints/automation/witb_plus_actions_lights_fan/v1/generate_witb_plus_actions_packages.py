#!/usr/bin/env python3
from __future__ import annotations

# Helpers-only generator for: WITB+ v3.5 Actions - Lights + Fan (blueprint v1.4.1+)
#
# This script generates Home Assistant *package YAML files* (merge_named compatible)
# that contain helper entities for the actions blueprint:
#   - REQUIRED/RECOMMENDED safety tags: auto_lights_on / auto_fan_on
#   - OPTIONAL timers (restart-safe with restore: true):
#       * actions_cooldown
#       * fan_runon
#   - OPTIONAL UI tuning helpers (dashboard sliders / times):
#       * night_start / night_end (input_datetime)
#       * brightness day/night % (input_number)
#       * fan day/night % (input_number)
#       * fan run-on minutes (input_number)
#       * lux threshold (input_number)
#       * humidity high/low (input_number)
#       * fan ON delay seconds (input_number)
#
# IMPORTANT:
# - This generator does NOT emit the automation block (use_blueprint). Create the automation in the UI.
# - Some helpers may be "future wiring" depending on your blueprint version. Generating them now ensures
#   you don't forget later, and costs basically nothing.
#
# Usage (single command that generates ALL helpers by default):
#   ./generate_witb_plus_actions_helpers_packages_v2.py --rooms "Office" "Master Bathroom Toilet" --out ./packages
#
# Dry run:
#   ./generate_witb_plus_actions_helpers_packages_v2.py --rooms "Office" --out ./packages --dry-run
#
# Optional config file (JSON or YAML):
#   ./generate_witb_plus_actions_helpers_packages_v2.py --config ./rooms_actions.json --out ./packages
#
# Flags to reduce output (defaults are ALL ON):
#   --no-timers
#   --no-night-window
#   --no-brightness
#   --no-fan-pct
#   --no-fan-runon-minutes
#   --no-lux
#   --no-humidity
#   --no-fan-on-delay
#
# Example rooms_actions.json:
# {
#   "key_suffix": "_witb_actions",
#   "file_suffix": "_witb_actions.yaml",
#   "emit_timers": true,
#   "emit_night_window": true,
#   "emit_brightness": true,
#   "emit_fan_pct": true,
#   "emit_fan_runon_minutes": true,
#   "emit_lux": true,
#   "emit_humidity": true,
#   "emit_fan_on_delay": true,
#   "rooms": [
#     { "name": "Master Bathroom Toilet" },
#     { "name": "Office" }
#   ]
# }

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def q(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join((pad + line) if line.strip() else line for line in text.splitlines())


def load_config(path: Path) -> dict[str, Any]:
    """Load config from JSON or YAML (if PyYAML installed)."""
    txt = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()
    if ext in [".yaml", ".yml"]:
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "YAML config requested but PyYAML is not installed. Install with: pip install pyyaml"
            ) from e
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


def build_room(name: str, key_suffix: str) -> Room:
    slug = slugify(name)
    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
    )


def room_from_obj(obj: dict[str, Any], key_suffix: str) -> Room:
    name = str(obj["name"])
    slug = str(obj.get("slug") or slugify(name))
    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
    )


def helpers_block(
    room: Room,
    *,
    emit_timers: bool,
    emit_night_window: bool,
    emit_brightness: bool,
    emit_fan_pct: bool,
    emit_fan_runon_minutes: bool,
    emit_lux: bool,
    emit_humidity: bool,
    emit_fan_on_delay: bool,
) -> str:
    lines: list[str] = []

    # Auto-tags are the big safety helpers: only turn OFF what automation turned ON.
    lines += [
        "input_boolean:",
        f"  {room.slug}_auto_lights_on:",
        f"    name: {q(room.name + ' auto lights on (tag)')}",
        "    icon: mdi:lightbulb-auto",
        "",
        f"  {room.slug}_auto_fan_on:",
        f"    name: {q(room.name + ' auto fan on (tag)')}",
        "    icon: mdi:fan-auto",
    ]

    if emit_timers:
        # restore: true makes timers survive HA restart (restart-safe).
        lines += [
            "",
            "timer:",
            f"  {room.slug}_fan_runon:",
            f"    name: {q(room.name + ' fan run-on')}",
            "    restore: true",
            "",
            f"  {room.slug}_actions_cooldown:",
            f"    name: {q(room.name + ' actions cooldown')}",
            "    restore: true",
        ]

    if emit_night_window:
        lines += [
            "",
            "input_datetime:",
            f"  {room.slug}_actions_night_start:",
            f"    name: {q(room.name + ' night start')}",
            "    has_date: false",
            "    has_time: true",
            "",
            f"  {room.slug}_actions_night_end:",
            f"    name: {q(room.name + ' night end')}",
            "    has_date: false",
            "    has_time: true",
        ]

    # UI tuning sliders
    input_number_lines: list[str] = []
    if emit_brightness:
        input_number_lines += [
            f"  {room.slug}_actions_brightness_day_pct:",
            f"    name: {q(room.name + ' brightness day %')}",
            "    min: 1",
            "    max: 100",
            "    step: 1",
            "    mode: slider",
            "",
            f"  {room.slug}_actions_brightness_night_pct:",
            f"    name: {q(room.name + ' brightness night %')}",
            "    min: 1",
            "    max: 100",
            "    step: 1",
            "    mode: slider",
            "",
        ]

    if emit_fan_pct:
        input_number_lines += [
            f"  {room.slug}_actions_fan_pct_day:",
            f"    name: {q(room.name + ' fan day %')}",
            "    min: 0",
            "    max: 100",
            "    step: 5",
            "    mode: slider",
            "",
            f"  {room.slug}_actions_fan_pct_night:",
            f"    name: {q(room.name + ' fan night %')}",
            "    min: 0",
            "    max: 100",
            "    step: 5",
            "    mode: slider",
            "",
        ]

    if emit_fan_runon_minutes:
        input_number_lines += [
            f"  {room.slug}_actions_fan_runon_minutes:",
            f"    name: {q(room.name + ' fan run-on (minutes)')}",
            "    min: 0",
            "    max: 60",
            "    step: 1",
            "    mode: slider",
            "",
        ]

    if emit_lux:
        input_number_lines += [
            f"  {room.slug}_actions_lux_threshold:",
            f"    name: {q(room.name + ' lux threshold')}",
            "    min: 0",
            "    max: 500",
            "    step: 1",
            "    mode: slider",
            "",
        ]

    if emit_humidity:
        input_number_lines += [
            f"  {room.slug}_actions_humidity_high:",
            f"    name: {q(room.name + ' humidity high %')}",
            "    min: 30",
            "    max: 100",
            "    step: 1",
            "    mode: slider",
            "",
            f"  {room.slug}_actions_humidity_low:",
            f"    name: {q(room.name + ' humidity low %')}",
            "    min: 30",
            "    max: 100",
            "    step: 1",
            "    mode: slider",
            "",
        ]

    if emit_fan_on_delay:
        input_number_lines += [
            f"  {room.slug}_actions_fan_on_delay_seconds:",
            f"    name: {q(room.name + ' fan ON delay (sec)')}",
            "    min: 0",
            "    max: 180",
            "    step: 5",
            "    mode: slider",
            "",
        ]

    # Attach input_number section if anything is enabled
    input_number_lines = [ln for ln in input_number_lines if ln != "" or (input_number_lines and input_number_lines[-1] != "")]
    if input_number_lines:
        # trim trailing blank lines
        while input_number_lines and input_number_lines[-1] == "":
            input_number_lines.pop()
        lines += ["", "input_number:"] + input_number_lines

    return "\n".join(lines)


def build_package_file(room: Room, **kwargs: Any) -> str:
    inner = helpers_block(room, **kwargs).rstrip() + "\n"
    return (
        "---\n"
        f"{room.package_key}:\n"
        + indent(inner, 2)
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate HA merge_named package YAML files for WITB+ actions helpers ONLY (no automation)."
    )

    ap.add_argument("--out", required=True, help="Output directory (e.g. ./packages/)")
    ap.add_argument("--rooms", nargs="+", help='Room names e.g. --rooms "Office" "Loft" (used if --config not set)')
    ap.add_argument("--config", help="Optional JSON/YAML config file (rooms list + generator options).")

    ap.add_argument("--key-suffix", default="_witb_actions", help='Suffix for the package key (default: "_witb_actions")')
    ap.add_argument("--file-suffix", default="_witb_actions.yaml", help='Suffix for output file name (default: "_witb_actions.yaml")')

    # Defaults are ALL ON; these flags only reduce output.
    ap.add_argument("--no-timers", action="store_true", help="Do not emit timers (cooldown + fan_runon)")
    ap.add_argument("--no-night-window", action="store_true", help="Do not emit input_datetime night_start/night_end")
    ap.add_argument("--no-brightness", action="store_true", help="Do not emit brightness sliders")
    ap.add_argument("--no-fan-pct", action="store_true", help="Do not emit fan % sliders")
    ap.add_argument("--no-fan-runon-minutes", action="store_true", help="Do not emit fan run-on minutes slider")
    ap.add_argument("--no-lux", action="store_true", help="Do not emit lux threshold slider")
    ap.add_argument("--no-humidity", action="store_true", help="Do not emit humidity high/low sliders")
    ap.add_argument("--no-fan-on-delay", action="store_true", help="Do not emit fan ON delay slider")

    ap.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing files")

    args = ap.parse_args()

    # Defaults (ALL ON)
    emit_timers = not args.no_timers
    emit_night_window = not args.no_night_window
    emit_brightness = not args.no_brightness
    emit_fan_pct = not args.no_fan_pct
    emit_fan_runon_minutes = not args.no_fan_runon_minutes
    emit_lux = not args.no_lux
    emit_humidity = not args.no_humidity
    emit_fan_on_delay = not args.no_fan_on_delay

    key_suffix = args.key_suffix
    file_suffix = args.file_suffix

    rooms: list[Room] = []

    if args.config:
        cfg = load_config(Path(args.config))
        key_suffix = cfg.get("key_suffix", key_suffix)
        file_suffix = cfg.get("file_suffix", file_suffix)

        emit_timers = bool(cfg.get("emit_timers", emit_timers))
        emit_night_window = bool(cfg.get("emit_night_window", emit_night_window))
        emit_brightness = bool(cfg.get("emit_brightness", emit_brightness))
        emit_fan_pct = bool(cfg.get("emit_fan_pct", emit_fan_pct))
        emit_fan_runon_minutes = bool(cfg.get("emit_fan_runon_minutes", emit_fan_runon_minutes))
        emit_lux = bool(cfg.get("emit_lux", emit_lux))
        emit_humidity = bool(cfg.get("emit_humidity", emit_humidity))
        emit_fan_on_delay = bool(cfg.get("emit_fan_on_delay", emit_fan_on_delay))

        for obj in cfg.get("rooms", []):
            if isinstance(obj, str):
                rooms.append(build_room(obj, key_suffix))
            elif isinstance(obj, dict):
                rooms.append(room_from_obj(obj, key_suffix))
            else:
                raise ValueError("Each rooms[] entry must be a string or object with at least {name: ...}.")
    else:
        if not args.rooms:
            ap.error("Either --config or --rooms must be provided.")
        rooms = [build_room(name, key_suffix) for name in args.rooms]

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for room in rooms:
        content = build_package_file(
            room,
            emit_timers=emit_timers,
            emit_night_window=emit_night_window,
            emit_brightness=emit_brightness,
            emit_fan_pct=emit_fan_pct,
            emit_fan_runon_minutes=emit_fan_runon_minutes,
            emit_lux=emit_lux,
            emit_humidity=emit_humidity,
            emit_fan_on_delay=emit_fan_on_delay,
        )

        file_path = out_dir / f"{room.slug}{file_suffix}"
        if args.dry_run:
            print("\n" + "=" * 80)
            print(f"# {file_path.name}")
            print("=" * 80)
            print(content)
        else:
            file_path.write_text(content, encoding="utf-8")
            print(f"Wrote: {file_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
