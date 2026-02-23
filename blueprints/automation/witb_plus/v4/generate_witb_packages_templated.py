#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re
from typing import Iterable


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


@dataclass(frozen=True)
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
        "",
        f"  {room.slug}_last_exit_door:",
        f"    name: {q(room.name + ' Last Exit Door')}",
        "    has_date: true",
        "    has_time: true",
        "",
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


_MARK_BEGIN = re.compile(r"^\s*#\s*---\s*BEGIN\s+([A-Za-z0-9_]+)\s*---\s*$")
_MARK_END = re.compile(r"^\s*#\s*---\s*END\s+([A-Za-z0-9_]+)\s*---\s*$")


def _render_marked_blocks(template_text: str, enabled_blocks: set[str]) -> str:
    """
    Simple line-oriented "template" processor.

    Supports optional blocks using comment markers:
      # --- BEGIN <name> ---
        ... lines ...
      # --- END <name> ---

    Blocks can be nested. Marker lines are always removed.
    Any block whose <name> is NOT in enabled_blocks is omitted entirely.
    """
    out_lines: list[str] = []
    stack: list[tuple[str, bool]] = []  # (block_name, include?)

    def currently_included() -> bool:
        return all(inc for _, inc in stack)

    for line in template_text.splitlines():
        m = _MARK_BEGIN.match(line)
        if m:
            name = m.group(1)
            include = (name in enabled_blocks) and currently_included()
            stack.append((name, include))
            continue

        m = _MARK_END.match(line)
        if m:
            name = m.group(1)
            if not stack or stack[-1][0] != name:
                raise ValueError(f"Template block marker mismatch: END {name} without matching BEGIN")
            stack.pop()
            continue

        if currently_included():
            out_lines.append(line)

    if stack:
        raise ValueError(f"Template block marker mismatch: missing END for {stack[-1][0]}")

    return "\n".join(out_lines).rstrip() + "\n"


def render_from_template(
    template_path: Path,
    room: Room,
    *,
    include_helpers: bool,
    include_templates: bool,
    include_controls: bool,
    include_latched: bool,
    include_failsafe: bool,
    slug_token: str,
    name_token: str,
) -> str:
    raw = template_path.read_text(encoding="utf-8")

    enabled_blocks: set[str] = set()
    if include_helpers:
        enabled_blocks.add("helpers")
    if include_templates:
        enabled_blocks.add("templates")

    # Mutually exclusive blocks:
    if include_controls:
        enabled_blocks.add("controls")
    else:
        enabled_blocks.add("no_controls")

    if include_latched:
        enabled_blocks.add("latched")
    if include_failsafe:
        enabled_blocks.add("failsafe")

    # If the template doesn't use markers, this is essentially a no-op.
    rendered = _render_marked_blocks(raw, enabled_blocks)

    # Token replacement (use tokens that do NOT clash with HA's Jinja `{{ }}` templates).
    rendered = rendered.replace(slug_token, room.slug).replace(name_token, room.name)

    return rendered


def wrap_package(package_key: str, inner_yaml: str) -> str:
    inner = inner_yaml.rstrip() + "\n"
    return "---\n" + f"{package_key}:\n" + indent(inner, 2)


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

    ap.add_argument(
        "--template",
        type=str,
        default=None,
        help="Path to a YAML template file (recommended) instead of the built-in generator.",
    )
    ap.add_argument(
        "--template-slug-token",
        default="room_slug",
        help="Token in the template to replace with the generated room slug (default: room_slug)",
    )
    ap.add_argument(
        "--template-name-token",
        default="Room Friendly Name",
        help='Token in the template to replace with the room friendly name (default: "Room Friendly Name")',
    )

    ap.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing files")

    args = ap.parse_args()

    # Default behavior if neither flag is specified.
    if not (args.emit_helpers or args.emit_templates):
        args.emit_helpers = args.emit_templates = True

    include_controls = not args.no_controls
    include_latched = not args.no_latched
    include_failsafe = not args.no_failsafe

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    template_path = Path(args.template) if args.template else None
    if template_path and not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")

    for name in args.rooms:
        room = build_room(name, args.key_suffix)

        if template_path:
            inner = render_from_template(
                template_path,
                room,
                include_helpers=args.emit_helpers,
                include_templates=args.emit_templates,
                include_controls=include_controls,
                include_latched=include_latched,
                include_failsafe=include_failsafe,
                slug_token=args.template_slug_token,
                name_token=args.template_name_token,
            )
            content = wrap_package(room.package_key, inner)
        else:
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
