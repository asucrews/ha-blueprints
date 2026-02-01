#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re


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


def helpers_block(room: Room, include_controls: bool, include_latched: bool, include_failsafe: bool) -> str:
    lines: list[str] = []

    lines += [
        "input_boolean:",
        f"  {room.slug}_occupied:",
        f"    name: {q(room.name + ' Occupied')}",
        "    icon: mdi:account",
    ]

    if include_controls:
        lines += [
            "",
            f"  {room.slug}_automation_override:",
            f"    name: {q(room.name + ' Automation Override')}",
            "    icon: mdi:toggle-switch-off-outline",
            "",
            f"  {room.slug}_force_occupied:",
            f"    name: {q(room.name + ' Force Occupied')}",
            "    icon: mdi:lock",
            "",
            f"  {room.slug}_manual_occupied:",
            f"    name: {q(room.name + ' Manual Occupied')}",
            "    icon: mdi:hand",
        ]

    if include_latched:
        lines += [
            "",
            f"  {room.slug}_latched:",
            f"    name: {q(room.name + ' Latched')}",
            "    icon: mdi:door-closed-lock",
        ]

    lines += [
        "",
        "input_datetime:",
        f"  {room.slug}_last_motion:",
        f"    name: {q(room.name + ' Last Motion')}",
        "    has_date: true",
        "    has_time: true",
        "",
        f"  {room.slug}_last_door:",
        f"    name: {q(room.name + ' Last Door')}",
        "    has_date: true",
        "    has_time: true",
    ]

    if include_failsafe:
        lines += [
            "",
            "timer:",
            f"  {room.slug}_failsafe:",
            f"    name: {q(room.name + ' Failsafe')}",
        ]

    return "\n".join(lines)


def templates_block(room: Room, include_controls: bool) -> str:
    lines: list[str] = []
    lines += [
        "template:",
        "  - binary_sensor:",
    ]

    if include_controls:
        lines += [
            f"      - name: {q(room.name + ' Occupied Effective')}",
            f"        unique_id: {room.slug}_occupied_effective",
            "        device_class: occupancy",
            "        state: >",
            f"          {{{{ is_state('input_boolean.{room.slug}_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_force_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_manual_occupied','on') }}}}",
            "",
            f"      - name: {q(room.name + ' WITB Override Active')}",
            f"        unique_id: {room.slug}_witb_override_active",
            "        state: >",
            f"          {{{{ is_state('input_boolean.{room.slug}_automation_override','on')",
            f"             or is_state('input_boolean.{room.slug}_force_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_manual_occupied','on') }}}}",
            "        icon: mdi:shield-check",
        ]
    else:
        lines += [
            f"      - name: {q(room.name + ' Occupied Effective')}",
            f"        unique_id: {room.slug}_occupied_effective",
            "        device_class: occupancy",
            "        state: >",
            f"          {{{{ is_state('input_boolean.{room.slug}_occupied','on') }}}}",
        ]

    lines += [
        "",
        "  - sensor:",
        f"      - name: {q(room.name + ' Minutes Since Motion')}",
        f"        unique_id: {room.slug}_minutes_since_motion",
        '        unit_of_measurement: "min"',
        "        state: >",
        f"          {{% set v = states('input_datetime.{room.slug}_last_motion') %}}",
        "          {% if v in ['unknown','unavailable','none',''] %}",
        "            999999",
        "          {% else %}",
        "            {{ ((as_timestamp(now()) - as_timestamp(v)) / 60) | int }}",
        "          {% endif %}",
    ]
    return "\n".join(lines)


def build_package_file(
    room: Room,
    include_helpers: bool,
    include_templates: bool,
    include_controls: bool,
    include_latched: bool,
    include_failsafe: bool,
) -> str:
    blocks: list[str] = []

    if include_helpers:
        blocks.append(helpers_block(room, include_controls, include_latched, include_failsafe))
    if include_templates:
        blocks.append(templates_block(room, include_controls))

    inner = "\n\n".join(blocks).rstrip() + "\n"

    return (
        "---\n"
        f"{room.package_key}:\n"
        + indent(inner, 2)
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate Home Assistant WITB helper-only package files (no automation)."
    )

    ap.add_argument("--rooms", nargs="+", required=True, help='Room names e.g. --rooms "Master Bedroom" "Loft"')
    ap.add_argument("--out", required=True, help="Output directory (e.g. ./packages/)")
    ap.add_argument("--key-suffix", default="_witb", help='Suffix for the package key (default: "_witb")')

    ap.add_argument("--emit-helpers", action="store_true", help="Emit helper definitions")
    ap.add_argument("--emit-templates", action="store_true", help="Emit template sensors")

    ap.add_argument("--no-controls", action="store_true", help="Omit override/force/manual")
    ap.add_argument("--no-latched", action="store_true", help="Omit latched helper/input")
    ap.add_argument("--no-failsafe", action="store_true", help="Omit failsafe timer/input")

    ap.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing files")

    args = ap.parse_args()

    if not (args.emit_helpers or args.emit_templates):
        args.emit_helpers = args.emit_templates = True

    include_controls = not args.no_controls
    include_latched = not args.no_latched
    include_failsafe = not args.no_failsafe

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for name in args.rooms:
        room = build_room(name, args.key_suffix)

        content = build_package_file(
            room=room,
            include_helpers=args.emit_helpers,
            include_templates=args.emit_templates,
            include_controls=include_controls,
            include_latched=include_latched,
            include_failsafe=include_failsafe,
        )

        file_path = out_dir / f"{room.slug}.yaml"
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
