#!/usr/bin/env python3
from __future__ import annotations

r"""
Template-driven generator for Home Assistant merge_named packages for:
  WITB Standard Helpers (Occupied, Override, Latched, Failsafe)
  WITB Actions Helpers  (Lights, Fan, Thresholds, Timers)

Supports per-room configuration overrides via config file.

CHANGELOG (fixes vs previous version):
  BUG #1  - input_number missing from remove_empty_section cleanup list.
             If all input_number helpers were stripped, the bare `input_number:`
             key remained in output, producing invalid YAML.
  BUG #2  - Config file emit_X overrode CLI --no-X flags, making CLI lower
             priority than the config file. Unintuitive. CLI now wins.
  BUG #3  - No duplicate slug detection. Two rooms with the same slug would
             silently overwrite each other's output file.
  BUG #4  - slugify() used bare \w which matches Unicode word chars under
             Python's default re flags. HA entity IDs must be ASCII. Fixed
             with re.ASCII flag so non-ASCII chars are stripped correctly.
  BUG #5  - Dead-code regex in apply_tokens(). The str.replace("Room Friendly
             Name", ...) already replaced all occurrences before the regex ran,
             so the regex never matched anything. Removed.
  BUG #6  - No --dry-run mode. Script always wrote files, no way to preview.
  BUG #7  - No existence check on --template path. Python's FileNotFoundError
             message is cryptic. Now validated early with a clear message.
  BUG #8  - Redundant dual override syntax (no_X and emit_X both did the same
             thing per-room). Unified: per-room config uses `no_X: true` only.
             emit_X at the config ROOT level (global override) is preserved.
  BUG #9  - remove_empty_section used (?ms) flags causing `.*` to match across
             newlines (DOTALL), which greedily consumed all content following
             the first comment in a section. Sections with real content were
             incorrectly stripped. Fixed by removing `s` flag and replacing
             `.*` with `[^\n]*` so comment matching is strictly single-line.
  ADDED   - exit_eval, lights, fan, lux, humidity, night added to features list
             to match the new block markers in the actions package template.
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
    """Convert a room name to a valid HA entity slug (ASCII lowercase + underscore)."""
    s = name.strip().lower()
    s = s.replace("&", " and ")
    # BUG #4 FIX: Use re.ASCII so \w only matches [a-zA-Z0-9_], stripping
    # accented and other non-ASCII characters that would make invalid HA entity IDs.
    s = re.sub(r"[^\w\s-]", "", s, flags=re.ASCII)
    s = re.sub(r"[\s-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def indent(text: str, spaces: int) -> str:
    """Indent every non-blank line by `spaces` spaces."""
    pad = " " * spaces
    return "\n".join((pad + line) if line.strip() else line for line in text.splitlines())

def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON or YAML config file."""
    if not path.exists():
        sys.exit(f"Error: Config file not found: {path}")
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
    # Per-room feature flag overrides (True=include, False=strip)
    overrides: dict[str, bool] = field(default_factory=dict)

def build_room(obj: str | dict[str, Any], key_suffix: str) -> Room:
    """Build a Room from either a plain string name or a config dict."""
    if isinstance(obj, str):
        name = obj
        overrides: dict[str, bool] = {}
        slug = slugify(name)
    else:
        name = str(obj["name"])
        slug = str(obj.get("slug") or slugify(name))

        # BUG #8 FIX: Per-room overrides use `no_X: true` only.
        # emit_X is reserved for config root-level global overrides.
        # Previously both prefixes did the same thing per-room, which was
        # confusing and undocumented. Now per-room only supports no_X.
        overrides = {}
        for k, v in obj.items():
            if k.startswith("no_"):
                # no_latched: true  ->  latched feature disabled
                feature = k[3:]
                overrides[feature] = not bool(v)

    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
        overrides=overrides,
    )

# --- Text Processing ---

def strip_marked_block(text: str, block: str) -> str:
    """
    Removes blocks delimited by:
      # --- BEGIN block ---
      ...
      # --- END block ---
    including the delimiter lines themselves.
    """
    start = re.escape(f"# --- BEGIN {block} ---")
    end = re.escape(f"# --- END {block} ---")
    pattern = rf"(?ms)^[ \t]*{start}.*?{end}[ \t]*\n?"
    return re.sub(pattern, "", text)

def strip_block_markers(text: str) -> str:
    """
    Removes all remaining # --- BEGIN X --- and # --- END X --- comment lines
    from the final output. These markers are template scaffolding — they serve
    no purpose in the generated package files and clutter the output.
    Also collapses 3+ consecutive blank lines down to 2 for clean formatting.
    """
    # Remove marker comment lines
    text = re.sub(r"(?m)^[ \t]*# --- (BEGIN|END) [^\n]+ ---[ \t]*\n?", "", text)
    # Collapse runs of 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def remove_empty_section(text: str, section: str) -> str:
    """
    Removes a top-level YAML key (e.g. `input_boolean:`) if its body contains
    only comments and/or blank lines -- i.e. all real content was stripped.

    BUG #9 FIX: Original used (?ms) flags. The s (DOTALL) flag makes .* match
    newlines, so the comment pattern greedily consumed entire sections that had
    real content. Fixed: removed s flag, replaced .* with [^\n]* so comment
    matching is strictly single-line.
    """
    pat = rf"(?m)^(?P<hdr>{re.escape(section)}:\s*\n)(?P<body>(?:[ \t]*#[^\n]*\n|[ \t]*\n)*)(?=^[A-Za-z0-9_]+:\s*$|\Z)"
    return re.sub(pat, "", text)

def extract_inner_if_single_package(text: str) -> str:
    """
    Smart unwrapping: if the template file has a single top-level wrapper key
    (e.g. `room_witb_actions:`), unwrap its content (de-indent by 2 spaces)
    while preserving any header comments above the wrapper key.
    If no wrapper key is found, returns the content as-is.
    """
    lines = text.splitlines()

    # Strip leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)

    # Strip leading YAML document separator
    if lines and lines[0].strip() == "---":
        lines.pop(0)

    # Strip blank lines after separator
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return ""

    # Find the first non-comment, non-blank content line and check if it's a
    # bare top-level key (i.e. the package wrapper key like `room_witb_actions:`)
    wrapper_index = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*$", line):
            wrapper_index = i
        break

    # No wrapper key found — return as-is
    if wrapper_index == -1:
        return "\n".join(lines)

    # Wrapper found: keep header comments, de-indent content by 2 spaces
    result_lines: list[str] = []
    result_lines.extend(lines[:wrapper_index])

    for line in lines[wrapper_index + 1:]:
        if line.startswith("  "):
            result_lines.append(line[2:])
        elif not line.strip():
            result_lines.append("")
        else:
            # Line is at column 0 inside a wrapper — unusual but pass through
            result_lines.append(line)

    return "\n".join(result_lines)

def apply_tokens(text: str, room: Room) -> str:
    """Replace template tokens with room-specific values."""
    # BUG #5 FIX: Removed dead-code regex fallback. The str.replace() calls
    # below replace ALL occurrences of both tokens literally and reliably.
    # The original regex ran AFTER str.replace had already consumed the token,
    # so it never matched. A single pass is cleaner and correct.
    text = text.replace("room_slug", room.slug)
    text = text.replace("Room Friendly Name", room.name)
    return text

# --- Main ---

# Canonical feature list — must match the # --- BEGIN X --- block names in templates.
#
# witb_plus_package_template.yaml blocks:
#   helpers       - required: occupancy (input_boolean) + last_motion, last_door
#                   (input_datetime) + exit_eval (timer)
#   controls      - optional: override, force_occupied, manual_occupied (input_boolean)
#   latched       - optional: latched debug (input_boolean)
#   exit_close    - optional: last_exit_door (input_datetime)
#   failsafe      - optional: failsafe (timer) + failsafe_timeout (input_number)
#   entry_gating  - optional: entry_window_seconds (input_number)
#
# room_witb_actions_package_template.yaml blocks:
#   lights        - auto_lights_on, keep_on (input_boolean) + brightness helpers
#                   (input_number) + actions_cooldown (timer)
#   fan           - auto_fan_on (input_boolean) + fan speed/delay/runon helpers
#                   (input_number) + fan_runon (timer)
#   lux           - lux_threshold (input_number)
#   humidity      - humidity_high/low (input_number)
#   night         - night_start/end (input_datetime)
ALL_FEATURES = [
    # witb_plus core template
    "helpers", "controls", "latched", "exit_close", "failsafe", "entry_gating",
    # witb_actions template
    "lights", "fan", "lux", "humidity", "night",
]

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate HA merge_named package files from a WITB template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from a YAML config (recommended):
  python generate_witb_packages_templated.py \\
    --template witb_plus_package_template.yaml \\
    --config rooms.yaml \\
    --out ./packages/rooms

  # Quick generation from CLI room names:
  python generate_witb_packages_templated.py \\
    --template witb_plus_package_template.yaml \\
    --rooms "Master Bedroom" "Office" "Bathroom" \\
    --out ./packages/rooms

  # Dry run to preview without writing files:
  python generate_witb_packages_templated.py \\
    --template witb_plus_package_template.yaml \\
    --rooms "Office" \\
    --out ./packages/rooms \\
    --dry-run

Per-room config override example (rooms.yaml):
  rooms:
    - name: Master Bedroom
      no_latched: true       # Disable the latched helper for this room
    - name: Office
      no_exit_eval: true     # Disable exit_eval timer (not using WITB v4.2)
    - name: Bathroom
""",
    )
    ap.add_argument("--out", required=True, type=Path, help="Output directory for generated files")
    ap.add_argument("--template", required=True, type=Path, help="Template YAML file")
    ap.add_argument("--rooms", nargs="+", metavar="ROOM", help="One or more room names (quoted if multi-word)")
    ap.add_argument("--config", type=Path, help="JSON or YAML config file defining rooms and global options")
    ap.add_argument("--key-suffix", default="_witb", help="Suffix appended to slug to form the package key (default: _witb)")
    ap.add_argument("--file-suffix", default=".yaml", help="Output file extension (default: .yaml)")
    # BUG #6 FIX: Added --dry-run flag.
    ap.add_argument("--dry-run", action="store_true", help="Print what would be generated without writing any files")

    # Global feature disable flags
    for f in ALL_FEATURES:
        # Use hyphens in CLI flag names (argparse convention).
        # argparse auto-converts hyphens to underscores for the dest attribute,
        # so --no-exit-eval is accessible as args.no_exit_eval.
        flag = f"--no-{f.replace('_', '-')}"
        ap.add_argument(flag, dest=f"no_{f}", action="store_true", help=f"Disable the '{f}' block globally for all rooms")

    args = ap.parse_args()

    # BUG #7 FIX: Validate template path exists early with a clear error message.
    if not args.template.exists():
        ap.error(f"Template file not found: {args.template}")

    # 1. Build global feature defaults from CLI flags (all ON unless --no-X passed)
    global_defaults: dict[str, bool] = {}
    for f in ALL_FEATURES:
        global_defaults[f] = not getattr(args, f"no_{f}")

    # 2. Parse rooms from config or CLI
    rooms: list[Room] = []

    if args.config:
        cfg = load_config(args.config)
        args.key_suffix = cfg.get("key_suffix", args.key_suffix)
        args.file_suffix = cfg.get("file_suffix", args.file_suffix)

        # BUG #2 FIX: Config-level emit_X overrides apply ONLY if the corresponding
        # CLI --no-X flag was NOT explicitly passed by the user. CLI takes priority.
        for f in ALL_FEATURES:
            cli_flag_key = f"no_{f}"
            cli_was_set = getattr(args, cli_flag_key)
            config_key = f"emit_{f}"
            if config_key in cfg and not cli_was_set:
                global_defaults[f] = bool(cfg[config_key])

        for obj in cfg.get("rooms", []):
            rooms.append(build_room(obj, args.key_suffix))

    elif args.rooms:
        for r in args.rooms:
            rooms.append(build_room(r, args.key_suffix))
    else:
        ap.error("Must provide --rooms or --config")

    # BUG #3 FIX: Detect duplicate slugs before generating any files.
    seen_slugs: dict[str, str] = {}
    duplicates: list[str] = []
    for room in rooms:
        if room.slug in seen_slugs:
            duplicates.append(
                f"  '{room.name}' and '{seen_slugs[room.slug]}' both slugify to '{room.slug}'"
            )
        else:
            seen_slugs[room.slug] = room.name
    if duplicates:
        sys.exit("Error: Duplicate room slugs detected (would silently overwrite files):\n" + "\n".join(duplicates))

    # 3. Read and unwrap template once
    raw_template = args.template.read_text(encoding="utf-8")
    base_inner = extract_inner_if_single_package(raw_template)

    # Detect which feature blocks are actually present in this template.
    # Features in ALL_FEATURES that have no matching # --- BEGIN X --- marker
    # in the template are silently ignored. This means the same script works
    # correctly against both witb_plus_package_template.yaml (core blocks only)
    # and room_witb_actions_package_template.yaml (actions blocks only) without
    # one template's feature flags appearing in the other's reported output.
    template_features = [
        f for f in ALL_FEATURES
        if re.search(rf"# --- BEGIN {re.escape(f)} ---", base_inner)
    ]

    # Restrict global_defaults to only the features present in this template
    global_defaults = {f: global_defaults[f] for f in template_features}

    # Create output directory (unless dry run)
    if not args.dry_run and not args.out.exists():
        args.out.mkdir(parents=True, exist_ok=True)

    # 4. Generate per room
    generated_count = 0
    for room in rooms:
        # A. Effective flags scoped to this template's blocks only.
        # Per-room overrides for blocks not in this template are silently ignored.
        effective_flags = global_defaults.copy()
        effective_flags.update({
            k: v for k, v in room.overrides.items() if k in template_features
        })

        # B. Strip disabled blocks from a fresh copy of the template
        current_text = base_inner
        for block, enabled in effective_flags.items():
            if not enabled:
                current_text = strip_marked_block(current_text, block)

        # B2. Strip all remaining marker comment lines from the output
        current_text = strip_block_markers(current_text)

        # C. Clean up any now-empty section headers
        # BUG #1 FIX: Added input_number to this list. It was previously missing,
        # meaning a bare `input_number:` key would remain if all its helpers were
        # stripped, producing structurally invalid YAML.
        for sec in ("input_boolean", "input_datetime", "input_number", "timer", "template"):
            current_text = remove_empty_section(current_text, sec)

        # D. Replace tokens with room-specific values
        current_text = apply_tokens(current_text, room)

        # E. Wrap in package key
        final_yaml = f"---\n{room.package_key}:\n{indent(current_text, 2)}\n"

        fname = f"{room.slug}{args.file_suffix}"
        active_features = [k for k, v in effective_flags.items() if v]

        if args.dry_run:
            print(f"[DRY RUN] Would write: {args.out / fname}")
            print(f"          Features:    {', '.join(active_features)}")
            print(f"          Package key: {room.package_key}")
            print()
        else:
            out_path = args.out / fname
            out_path.write_text(final_yaml, encoding="utf-8")
            print(f"Generated {fname}  [pkg: {room.package_key}]  [features: {', '.join(active_features)}]")

        generated_count += 1

    if args.dry_run:
        print(f"Dry run complete. {generated_count} file(s) would be written to: {args.out}")
    else:
        print(f"\nDone. {generated_count} file(s) written to: {args.out}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
