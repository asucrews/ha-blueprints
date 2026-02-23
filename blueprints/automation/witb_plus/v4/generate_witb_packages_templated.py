#!/usr/bin/env python3
from __future__ import annotations

"""
Template-driven generator for Home Assistant merge_named packages for:
  WITB Standard Helpers (Occupied, Override, Latched, Failsafe)

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
    # Per-room overrides for feature flags
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
                # "no_controls": true  ->  "controls": False
                feature = k[3:]
                overrides[feature] = not bool(v)
            elif k.startswith("emit_"):
                # "emit_controls": false -> "controls": False
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
    """
    Removes blocks marked with:
      # --- BEGIN block ---
      ...
      # --- END block ---
    """
    start = re.escape(f"# --- BEGIN {block} ---")
    end = re.escape(f"# --- END {block} ---")
    # Matches the block and the newline following it
    pattern = rf"(?ms)^[ \t]*{start}.*?{end}[ \t]*\n?"
    return re.sub(pattern, "", text)

def remove_empty_section(text: str, section: str) -> str:
    """Removes a top-level key (e.g. input_boolean:) if it only contains comments/whitespace."""
    pat = rf"(?ms)^(?P<hdr>{re.escape(section)}:\s*\n)(?P<body>(?:[ \t]*#.*\n|[ \t]*\n)*)(?=^[A-Za-z0-9_]+:\s*$|\Z)"
    return re.sub(pat, "", text)

def extract_inner_if_single_package(text: str) -> str:
    """
    Smart unwrapping:
    1. Ignores leading '---'
    2. Checks if the first non-comment content line is a Wrapper Key.
    3. If yes, unwraps inner content while preserving header comments.
    4. If no, returns content as-is.
    """
    lines = text.splitlines()

    # 1. Strip leading blank lines (start of file)
    while lines and not lines[0].strip():
        lines.pop(0)
    
    # 2. Strip leading '---' (document separator)
    if lines and lines[0].strip() == "---":
        lines.pop(0)
        
    # 3. Strip leading blanks again (post-separator)
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return ""

    # 4. Detect Wrapper Key (Ignore comments)
    wrapper_index = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if not s: continue        # Skip blanks
        if s.startswith("#"): continue  # Skip comments
        
        # Found first content line - is it a key?
        if re.match(r"^[A-Za-z0-9_]+:\s*$", line):
            wrapper_index = i
        break
    
    # Case A: No wrapper key found (or file is just comments). Return as-is.
    if wrapper_index == -1:
        return "\n".join(lines)

    # Case B: Wrapper key found. Unwrap it.
    result_lines = []
    
    # 1. Keep the comments ABOVE the wrapper (Header)
    result_lines.extend(lines[:wrapper_index])
    
    # 2. Unwrap the content BELOW the wrapper
    content_lines = lines[wrapper_index+1:]
    for line in content_lines:
        if line.startswith("  "):
            result_lines.append(line[2:]) # De-indent
        elif not line.strip():
            result_lines.append("")       # Preserve spacing
        else:
            result_lines.append(line)     # Fallback (weird formatting)
            
    return "\n".join(result_lines)

def apply_tokens(text: str, room: Room) -> str:
    # Standard Tokens
    text = text.replace("room_slug", room.slug)
    text = text.replace("Room Friendly Name", room.name)
    
    # Legacy quoted replacement (handles name: "Room Friendly Name ...")
    # Only acts if the token logic above didn't catch it because of quotes/formatting
    text = re.sub(
        r'(?m)^(?P<prefix>\s*name:\s*")Room(?P<rest>\s[^"]*)"$',
        lambda m: f'{m.group("prefix")}{room.name}{m.group("rest")}"',
        text,
    )
    return text

# --- Main ---

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate HA merge_named packages for WITB helpers (Optimized)")
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    ap.add_argument("--template", required=True, type=Path, help="Template file")
    ap.add_argument("--rooms", nargs="+", help="Room names")
    ap.add_argument("--config", type=Path, help="JSON/YAML config file")
    
    ap.add_argument("--key-suffix", default="_witb")
    ap.add_argument("--file-suffix", default=".yaml")
    
    # Feature flags (match the template block names)
    # Defaults: helpers=True, templates=True, controls=True, latched=True, failsafe=True
    features = ["helpers", "templates", "controls", "latched", "failsafe"]
    
    for f in features:
        ap.add_argument(f"--no-{f}", action="store_true") # e.g. --no-latched

    args = ap.parse_args()

    # 1. Determine Global Defaults (ALL ON unless flag provided)
    global_defaults = {}
    for f in features:
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
        effective_flags = global_defaults.copy()
        effective_flags.update(room.overrides)

        # B. Strip blocks from a fresh copy of the template
        current_text = base_inner
        for block, enabled in effective_flags.items():
            if not enabled:
                current_text = strip_marked_block(current_text, block)

        # C. Clean up empty sections
        for sec in ("input_boolean", "input_datetime", "timer", "template"):
            current_text = remove_empty_section(current_text, sec)

        # D. Replace Tokens
        current_text = apply_tokens(current_text, room)

        # E. Wrap and Write
        final_yaml = f"---\n{room.package_key}:\n{indent(current_text, 2)}\n"
        
        fname = f"{room.slug}{args.file_suffix}"
        out_path = args.out / fname
        out_path.write_text(final_yaml, encoding="utf-8")
        print(f"Generated {fname} [Features: {', '.join(k for k,v in effective_flags.items() if v)}]")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())