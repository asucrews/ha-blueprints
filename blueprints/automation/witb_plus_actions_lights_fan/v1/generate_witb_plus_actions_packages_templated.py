#!/usr/bin/env python3
from __future__ import annotations

"""
Template-driven generator for Home Assistant merge_named packages.
OPTIMIZED VERSION: Supports per-room configuration overrides.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --- Utilities ---

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
    if path.suffix.lower() in [".yaml", ".yml"]:
        try:
            import yaml
            return yaml.safe_load(txt)
        except ImportError:
            sys.exit("Error: YAML config requested but PyYAML not installed. Run: pip install pyyaml")
    return json.loads(txt)

# --- Data Structures ---

@dataclass
class Room:
    name: str
    slug: str
    package_key: str
    # Per-room overrides for feature flags (e.g., {'timers': False})
    overrides: dict[str, bool] = field(default_factory=dict)

def build_room(obj: str | dict[str, Any], key_suffix: str) -> Room:
    if isinstance(obj, str):
        name = obj
        overrides = {}
        slug = slugify(name)
    else:
        name = str(obj["name"])
        slug = str(obj.get("slug") or slugify(name))
        # Extract keys starting with "no_" or "emit_" to build overrides
        overrides = {}
        for k, v in obj.items():
            if k.startswith("no_"):
                # "no_timers": true  ->  "timers": False
                feature = k[3:]
                overrides[feature] = not bool(v)
            elif k.startswith("emit_"):
                # "emit_timers": false -> "timers": False
                feature = k[5:]
                overrides[feature] = bool(v)

    return Room(
        name=name, 
        slug=slug, 
        package_key=f"{slug}{key_suffix}",
        overrides=overrides
    )

# --- Text Processing ---

def strip_marked_block(text: str, block: str) -> str:
    """Removes blocks marked with # --- BEGIN block --- ... # --- END block ---"""
    start = re.escape(f"# --- BEGIN {block} ---")
    end = re.escape(f"# --- END {block} ---")
    # Matches the block and the newline following it
    pattern = rf"(?ms)^[ \t]*{start}.*?{end}[ \t]*\n?"
    return re.sub(pattern, "", text)

def remove_empty_section(text: str, section: str) -> str:
    """Removes a top-level key if it only contains comments/whitespace."""
    # Look for "key:", followed optionally by comments/whitespace, 
    # then followed by either another key (start of line) or End of String.
    pat = rf"(?ms)^(?P<hdr>{re.escape(section)}:\s*\n)(?P<body>(?:[ \t]*#.*\n|[ \t]*\n)*)(?=^[A-Za-z0-9_]+:\s*$|\Z)"
    return re.sub(pat, "", text)

def extract_inner_if_single_package(text: str) -> str:
    """Unwraps the top-level package key if present."""
    lines = text.splitlines()
    # Skip BOM or leading blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines: return text
    
    # Remove '---'
    if lines[0].strip() == "---":
        lines.pop(0)
    
    # Remove leading blanks again
    while lines and not lines[0].strip():
        lines.pop(0)
        
    if not lines: return ""

    # Check if first line is a key "something:"
    if re.match(r"^[A-Za-z0-9_]+:\s*$", lines[0]):
        # It is a package wrapper. De-indent everything below it.
        inner = []
        for line in lines[1:]:
            if line.startswith("  "):
                inner.append(line[2:])
            else:
                inner.append(line)
        return "\n".join(inner).strip()
    
    return text

def apply_tokens(text: str, room: Room) -> str:
    text = text.replace("room_slug", room.slug)
    text = text.replace("Room Friendly Name", room.name)
    return text

# --- Main ---

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate HA merge_named packages (Optimized)")
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    ap.add_argument("--template", required=True, type=Path, help="Template file")
    ap.add_argument("--rooms", nargs="+", help="Room names")
    ap.add_argument("--config", type=Path, help="JSON/YAML config file")
    ap.add_argument("--key-suffix", default="_witb_actions")
    ap.add_argument("--file-suffix", default="_witb_actions.yaml")
    
    # CLI flags for global defaults
    features = [
        "timers", "night_window", "brightness", "fan_pct", 
        "fan_runon_minutes", "lux", "humidity", "fan_on_delay"
    ]
    for f in features:
        ap.add_argument(f"--no-{f.replace('_', '-')}", action="store_true") # e.g. --no-timers

    args = ap.parse_args()

    # 1. Determine Global Defaults
    global_defaults = {}
    for f in features:
        # If --no-timers is passed, 'timers' = False. Otherwise True.
        arg_name = f"no_{f}"
        global_defaults[f] = not getattr(args, arg_name)

    # 2. Parse Config / Rooms
    rooms: list[Room] = []
    
    if args.config:
        cfg = load_config(args.config)
        args.key_suffix = cfg.get("key_suffix", args.key_suffix)
        args.file_suffix = cfg.get("file_suffix", args.file_suffix)
        
        # Apply config-level global overrides
        for f in features:
            if f"emit_{f}" in cfg:
                global_defaults[f] = bool(cfg[f"emit_{f}"])

        for obj in cfg.get("rooms", []):
            rooms.append(build_room(obj, args.key_suffix))
    elif args.rooms:
        for r in args.rooms:
            rooms.append(build_room(r, args.key_suffix))
    else:
        ap.error("Must provide --rooms or --config")

    # 3. Read & Unwrap Template ONCE
    raw_template = args.template.read_text(encoding="utf-8")
    base_inner = extract_inner_if_single_package(raw_template)

    if not args.out.exists():
        args.out.mkdir(parents=True, exist_ok=True)

    # 4. Generate per room
    for room in rooms:
        # A. Determine effective flags for this specific room
        # Start with global defaults -> update with room overrides
        effective_flags = global_defaults.copy()
        effective_flags.update(room.overrides)

        # B. Strip blocks from a fresh copy of the template
        current_text = base_inner
        for block, enabled in effective_flags.items():
            if not enabled:
                current_text = strip_marked_block(current_text, block)

        # C. Clean up empty sections
        for sec in ("timer", "input_datetime", "input_number", "input_boolean"):
            current_text = remove_empty_section(current_text, sec)

        # D. Replace Tokens
        current_text = apply_tokens(current_text, room)

        # E. Wrap and Write
        final_yaml = f"---\n{room.package_key}:\n{indent(current_text, 2)}\n"
        
        # Determine filename (allow room slug override in filename if needed)
        fname = f"{room.slug}{args.file_suffix}"
        out_path = args.out / fname
        out_path.write_text(final_yaml, encoding="utf-8")
        print(f"Generated {fname} [Features: {', '.join(k for k,v in effective_flags.items() if v)}]")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())