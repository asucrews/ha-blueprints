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
    # Always quote friendly names to avoid YAML edge cases
    return '"' + s.replace('"', '\\"') + '"'


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join((pad + line) if line.strip() else line for line in text.splitlines())


@dataclass
class Room:
    name: str
    slug: str
    package_key: str
    door_entity: str
    motion_entity: str


def build_room(
    name: str,
    door_pattern: str,
    motion_pattern: str,
    key_suffix: str,
) -> Room:
    slug = slugify(name)
    package_key = f"{slug}{key_suffix}"  # e.g. master_bedroom_witb
    door = door_pattern.format(slug=slug)
    motion = motion_pattern.format(slug=slug)
    return Room(name=name, slug=slug, package_key=package_key, door_entity=door, motion_entity=motion)


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
            f"          {{ {{ is_state('input_boolean.{room.slug}_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_force_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_manual_occupied','on') }} }}",
            "",
            f"      - name: {q(room.name + ' WITB Override Active')}",
            f"        unique_id: {room.slug}_witb_override_active",
            "        state: >",
            f"          {{ {{ is_state('input_boolean.{room.slug}_automation_override','on')",
            f"             or is_state('input_boolean.{room.slug}_force_occupied','on')",
            f"             or is_state('input_boolean.{room.slug}_manual_occupied','on') }} }}",
            "        icon: mdi:shield-check",
        ]
    else:
        lines += [
            f"      - name: {q(room.name + ' Occupied Effective')}",
            f"        unique_id: {room.slug}_occupied_effective",
            "        device_class: occupancy",
            "        state: >",
            f"          {{ {{ is_state('input_boolean.{room.slug}_occupied','on') }} }}",
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


def automation_block(
    room: Room,
    blueprint_path: str,
    include_controls: bool,
    include_latched: bool,
    include_failsafe: bool,
    exit_timeout: int,
    entry_gating: bool,
    entry_window: int,
    failsafe_minutes: int,
) -> str:
    lines: list[str] = []
    lines += [
        "automation:",
        f'  - alias: "WITB - {room.name}"',
        f'    description: "Occupancy for {room.name} using WITB blueprint"',
        "    use_blueprint:",
        f"      path: {blueprint_path}",
        "      input:",
        f"        door_sensor: {room.door_entity}",
        f"        motion_sensor: {room.motion_entity}",
        "",
        f"        occupancy_helper: input_boolean.{room.slug}_occupied",
        f"        last_motion_helper: input_datetime.{room.slug}_last_motion",
        f"        last_door_helper: input_datetime.{room.slug}_last_door",
    ]

    if include_latched:
        lines += [f"        latched_helper: input_boolean.{room.slug}_latched"]

    if include_controls:
        lines += [
            "",
            f"        automation_override: input_boolean.{room.slug}_automation_override",
            f"        force_occupied: input_boolean.{room.slug}_force_occupied",
            f"        manual_occupied: input_boolean.{room.slug}_manual_occupied",
        ]

    lines += [
        "",
        f"        exit_timeout_seconds: {exit_timeout}",
        f"        require_door_for_entry: {'true' if entry_gating else 'false'}",
        f"        entry_window_seconds: {entry_window}",
    ]

    if include_failsafe:
        lines += [
            "",
            "        enable_failsafe: true",
            f"        failsafe_timer: timer.{room.slug}_failsafe",
            f"        failsafe_minutes: {failsafe_minutes}",
        ]
    else:
        lines += ["", "        enable_failsafe: false"]

    return "\n".join(lines)


def build_package_file(
    room: Room,
    blueprint_path: str,
    include_helpers: bool,
    include_templates: bool,
    include_automation: bool,
    include_controls: bool,
    include_latched: bool,
    include_failsafe: bool,
    exit_timeout: int,
    entry_gating: bool,
    entry_window: int,
    failsafe_minutes: int,
) -> str:
    blocks: list[str] = []

    if include_helpers:
        blocks.append(helpers_block(room, include_controls, include_latched, include_failsafe))
    if include_templates:
        blocks.append(templates_block(room, include_controls))
    if include_automation:
        blocks.append(
            automation_block(
                room,
                blueprint_path,
                include_controls,
                include_latched,
                include_failsafe,
                exit_timeout,
                entry_gating,
                entry_window,
                failsafe_minutes,
            )
        )

    inner = "\n\n".join(blocks).rstrip() + "\n"

    # This is the critical merge_named package wrapper the HA docs describe:
    # <package_name>:
    #   <domains...>
    return (
        "---\n"
        f"{room.package_key}:\n"
        + indent(inner, 2)
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate merge_named Home Assistant package files for WITB rooms.")
    ap.add_argument("--rooms", nargs="+", required=True, help='Room names e.g. --rooms "Master Bedroom" "Loft"')
    ap.add_argument("--out", required=True, help="Output directory (e.g. ./packages/ or ./config/packages/)")
    ap.add_argument("--blueprint", required=True, help='Blueprint path used by use_blueprint.path (e.g. "asucrews/witb_plus_occupancy_v3_2.yaml")')

    ap.add_argument("--key-suffix", default="_witb", help='Suffix for the package key (default: "_witb")')

    ap.add_argument("--door-pattern", default="binary_sensor.REPLACE_DOOR_SENSOR",
                    help='Door entity id pattern supports {slug} (default placeholder).')
    ap.add_argument("--motion-pattern", default="binary_sensor.REPLACE_MOTION_SENSOR",
                    help='Motion entity id pattern supports {slug} (default placeholder).')

    # Emit controls
    ap.add_argument("--emit-helpers", action="store_true")
    ap.add_argument("--emit-templates", action="store_true")
    ap.add_argument("--emit-automation", action="store_true")

    # Feature toggles
    ap.add_argument("--no-controls", action="store_true")
    ap.add_argument("--no-latched", action="store_true")
    ap.add_argument("--no-failsafe", action="store_true")

    # Defaults / tuning
    ap.add_argument("--exit-timeout", type=int, default=45)
    ap.add_argument("--entry-gating", action="store_true")
    ap.add_argument("--entry-window", type=int, default=15)
    ap.add_argument("--failsafe-minutes", type=int, default=180)

    ap.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    # If user didn't specify emit flags, default to all (nice dev behavior)
    if not (args.emit_helpers or args.emit_templates or args.emit_automation):
        args.emit_helpers = args.emit_templates = args.emit_automation = True

    include_controls = not args.no_controls
    include_latched = not args.no_latched
    include_failsafe = not args.no_failsafe

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for name in args.rooms:
        room = build_room(
            name=name,
            door_pattern=args.door_pattern,
            motion_pattern=args.motion_pattern,
            key_suffix=args.key_suffix,
        )
        content = build_package_file(
            room=room,
            blueprint_path=args.blueprint,
            include_helpers=args.emit_helpers,
            include_templates=args.emit_templates,
            include_automation=args.emit_automation,
            include_controls=include_controls,
            include_latched=include_latched,
            include_failsafe=include_failsafe,
            exit_timeout=args.exit_timeout,
            entry_gating=args.entry_gating,
            entry_window=args.entry_window,
            failsafe_minutes=args.failsafe_minutes,
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
