#!/usr/bin/env python3
from __future__ import annotations

"""
Template-driven generator for Home Assistant merge_named *packages* for:

  WITB+ v3.5 Actions - Lights + Fan (helpers-only)

Unlike the older generator that hard-coded YAML in Python, this version reads a YAML
template file and only does:
  - token replacement (room_slug, Room Friendly Name)
  - optional block removal via markers (# --- BEGIN <block> --- / # --- END <block> ---)
  - wraps the result under a per-room package key and writes one file per room

Template tokens supported:
  - room_slug            -> office / master_bathroom_toilet / etc.
  - Room Friendly Name   -> "Office" / "Master Bathroom Toilet" / etc.

Legacy template support:
  If your template uses name: "Room ..." (like "Room lux threshold"), this script will
  replace "Room " at the start of *name values* with the friendly room name.

Optional blocks (remove with flags):
  timers, night_window, brightness, fan_pct, fan_runon_minutes, lux, humidity, fan_on_delay

Usage:
  ./generate_witb_plus_actions_packages_templated.py \
      --rooms "Office" "Master Bathroom Toilet" \
      --out ./packages \
      --template ./room_witb_actions_package.template.yaml

Dry-run (print only):
  ./generate_witb_plus_actions_packages_templated.py --rooms "Office" --out ./packages --dry-run
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
    return Room(name=name, slug=slug, package_key=f"{slug}{key_suffix}")


def room_from_obj(obj: dict[str, Any], key_suffix: str) -> Room:
    name = str(obj["name"])
    slug = str(obj.get("slug") or slugify(name))
    return Room(name=name, slug=slug, package_key=f"{slug}{key_suffix}")


BLOCK_NAMES = [
    "timers",
    "night_window",
    "brightness",
    "fan_pct",
    "fan_runon_minutes",
    "lux",
    "humidity",
    "fan_on_delay",
]


def strip_marked_block(text: str, block: str) -> str:
    """
    Remove a block delimited by:
      # --- BEGIN <block> ---
      ...
      # --- END <block> ---
    If markers aren't found, returns text unchanged.
    """
    start = re.escape(f"# --- BEGIN {block} ---")
    end = re.escape(f"# --- END {block} ---")
    pattern = rf"(?ms)^[ \t]*{start}[ \t]*\n.*?^[ \t]*{end}[ \t]*\n?"
    return re.sub(pattern, "", text)



def remove_empty_section(text: str, section: str) -> str:
    """
    Remove a top-level YAML mapping key (e.g. input_number:) if it has no children
    (only blank/comment lines) before the next top-level key or EOF.
    """
    # section header at column 0
    pat = rf"(?ms)^(?P<hdr>{re.escape(section)}:\s*\n)(?P<body>(?:[ \t]*#.*\n|[ \t]*\n)*)"
    def repl(m: re.Match) -> str:
        body = m.group("body")
        # if next nonblank/comment line is indented (child), keep; otherwise drop
        # We already matched only blanks/comments, so it's empty.
        return ""
    # Only remove when immediately followed by another top-level key or EOF (lookahead)
    pat2 = pat + r"(?=^[A-Za-z0-9_]+:\s*$|\Z)"
    return re.sub(pat2, repl, text)

def extract_inner_if_single_package(text: str) -> tuple[str, str | None]:
    """
    If template appears to be a full merge_named package file like:

      ---
      some_package_key:
        input_boolean:
          ...

    then return (inner_yaml_without_wrapper, detected_key).
    Otherwise return (text, None).
    """
    lines = text.splitlines()

    # drop leading BOM + blank lines
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

    # remove a single indent level (2 spaces) if present
    out: list[str] = []
    for ln in inner_lines:
        if ln.startswith("  "):
            out.append(ln[2:])
        else:
            out.append(ln)
    return "\n".join(out).lstrip("\n"), key


def apply_tokens(text: str, room: Room) -> str:
    # Preferred explicit tokens
    text = text.replace("room_slug", room.slug)
    text = text.replace("Room Friendly Name", room.name)

    # Legacy convenience: replace name: "Room ..." and name: 'Room ...'
    # Only when the value starts with Room + space.
    text = re.sub(
        r'(?m)^(?P<prefix>\s*name:\s*")Room(?P<rest>\s[^"]*)"$',
        lambda m: f'{m.group("prefix")}{room.name}{m.group("rest")}"',
        text,
    )
    text = re.sub(
        r"(?m)^(?P<prefix>\s*name:\s*')Room(?P<rest>\s[^']*)'$",
        lambda m: f"{m.group('prefix')}{room.name}{m.group('rest')}'",
        text,
    )
    return text


def build_package_file(room: Room, inner_yaml: str) -> str:
    inner = inner_yaml.rstrip() + "\n"
    return "---\n" + f"{room.package_key}:\n" + indent(inner, 2)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate HA merge_named package YAML files for WITB+ actions helpers using a YAML template."
    )

    ap.add_argument("--out", required=True, help="Output directory (e.g. ./packages/)")
    ap.add_argument("--template", required=True, help="Path to the YAML template file")

    ap.add_argument("--rooms", nargs="+", help='Room names e.g. --rooms "Office" "Loft" (used if --config not set)')
    ap.add_argument("--config", help="Optional JSON/YAML config file (rooms list + generator options).")

    ap.add_argument("--key-suffix", default="_witb_actions", help='Suffix for the package key (default: "_witb_actions")')
    ap.add_argument(
        "--file-suffix",
        default="_witb_actions.yaml",
        help='Suffix for output file name (default: "_witb_actions.yaml")',
    )

    # Defaults are ALL ON; these flags reduce output *if the template includes block markers*.
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

    key_suffix = args.key_suffix
    file_suffix = args.file_suffix

    # flags (ALL ON by default)
    emit = {
        "timers": not args.no_timers,
        "night_window": not args.no_night_window,
        "brightness": not args.no_brightness,
        "fan_pct": not args.no_fan_pct,
        "fan_runon_minutes": not args.no_fan_runon_minutes,
        "lux": not args.no_lux,
        "humidity": not args.no_humidity,
        "fan_on_delay": not args.no_fan_on_delay,
    }

    rooms: list[Room] = []
    if args.config:
        cfg = load_config(Path(args.config))
        key_suffix = cfg.get("key_suffix", key_suffix)
        file_suffix = cfg.get("file_suffix", file_suffix)

        # allow per-config overrides (true/false)
        for k in list(emit.keys()):
            cfg_key = f"emit_{k}"
            if cfg_key in cfg:
                emit[k] = bool(cfg[cfg_key])

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

    template_text = Path(args.template).read_text(encoding="utf-8")

    # If the template is already a merge_named package, unwrap it so we can re-wrap per room.
    inner_template, detected_key = extract_inner_if_single_package(template_text)

    # Strip optional blocks based on flags (only if markers exist)
    for block, enabled in emit.items():
        if not enabled:
            inner_template = strip_marked_block(inner_template, block)


    # Clean up empty sections that might be left behind after stripping blocks
    for sec in ("timer", "input_datetime", "input_number"):
        inner_template = remove_empty_section(inner_template, sec)

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for room in rooms:
        rendered_inner = apply_tokens(inner_template, room)
        content = build_package_file(room, rendered_inner)

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
