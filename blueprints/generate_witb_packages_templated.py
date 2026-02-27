#!/usr/bin/env python3
from __future__ import annotations

r"""
Template-driven generator for Home Assistant merge_named packages for:
  WITB Standard Helpers (Occupied, Override, Latched, Failsafe)
  WITB Actions Helpers  (Lights, Fan, Thresholds, Timers)
  Room Humidity Baseline + Delta
  Transit Room Helpers
  Vacuum Job Helpers
  … and any future template files.

Supports per-room configuration overrides via config file.

CHANGELOG:
  v1 → v2 (auto-discovery + multi-template hardening):
  NEW #1  - Feature blocks are now AUTO-DISCOVERED from the template file at
            startup by scanning for  # --- BEGIN X ---  markers. The static
            ALL_FEATURES list is kept as a fallback/documentation artifact but
            is no longer the sole source of --no-X CLI flags. Any new template
            block name is picked up automatically without editing this script.

  NEW #2  - apply_tokens() now handles BOTH token styles:
              "Room Friendly Name"  (witb_plus / witb_actions / humidity templates)
              "Friendly Name"       (transit template — no "Room" prefix)
            The first pass replaces "Room Friendly Name" → room.name; the second
            replaces any remaining bare "Friendly Name" → room.name so transit
            templates work without modification.

  NEW #3  - remove_empty_section() now covers ALL HA platform section headers,
            including `input_text` (transit) and `counter` (vacuum) which were
            previously unhandled, leaving bare section keys in the output.

  NEW #4  - extract_inner_if_single_package() de-indents by the ACTUAL wrapper
            indentation width instead of hard-coding 2 spaces. Wrapper blocks
            indented by 4 spaces (or any other depth) now unwrap correctly.

  BUG #1  - input_number missing from remove_empty_section cleanup list. Fixed.
  BUG #2  - Config emit_X overrode CLI --no-X flags. CLI now wins.
  BUG #3  - No duplicate slug detection. Added.
  BUG #4  - slugify() matched Unicode word chars. Fixed with re.ASCII.
  BUG #5  - Dead-code regex in apply_tokens(). Removed.
  BUG #6  - No --dry-run mode. Added.
  BUG #7  - No existence check on --template path. Added.
  BUG #8  - Redundant dual override syntax. Unified to no_X per-room.
  BUG #9  - remove_empty_section used DOTALL, ate real content. Fixed.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Static feature registry
# ---------------------------------------------------------------------------
# This list documents known features and supplies --no-X flags even when
# invoked WITHOUT a --template (e.g. --help).  It is merged at runtime with
# features auto-discovered from the actual template file, so new templates
# never require editing this list.
#
# witb_plus_package_template.yaml blocks:
#   helpers       - occupancy (input_boolean) + last_motion, last_door
#                   (input_datetime) + exit_eval (timer)
#   controls      - automation_override, force_occupied, manual_occupied (input_boolean)
#   latched       - latched debug (input_boolean)
#   exit_close    - last_exit_door (input_datetime)
#   failsafe      - failsafe (timer) + failsafe_timeout (input_number)
#   entry_gating  - entry_window_seconds (input_number)
#
# room_witb_actions_package_template.yaml blocks:
#   lights        - auto_lights_on, keep_on (input_boolean) + brightness helpers
#                   (input_number) + actions_cooldown (timer)
#   fan           - auto_fan_on (input_boolean) + fan speed/delay/runon helpers
#                   (input_number) + fan_runon (timer)
#   lux           - lux_threshold (input_number)
#   humidity      - humidity_high/low (input_number)
#   night         - night_start/end (input_datetime)
#
# room_humidity_baseline_delta_package_template.yaml blocks:
#   tuning_helpers - input_boolean + input_number tuning entities
#
# transit_helpers_package_template.yaml blocks:
#   (no feature blocks — flat template, no # --- BEGIN/END --- markers)
#
# vacuum_job_helpers.yaml:
#   (no feature blocks — flat template, no # --- BEGIN/END --- markers)
#
# room_witb_profile_with_sbm_helpers_template.yaml blocks:
#   sbm           - sbm_cooldown_seconds (input_number) + last_sbm_reset
#                   (trigger timestamp sensor) + sbm_cooldown_active
#                   (binary_sensor) + sbm_cooldown_remaining (sensor)
_STATIC_FEATURES: list[str] = [
    # witb_plus core template
    "helpers", "controls", "latched", "exit_close", "failsafe", "entry_gating",
    # witb_actions template
    "lights", "fan", "lux", "humidity", "night",
    # humidity template
    "tuning_helpers",
    # witb_profile sbm helpers template
    "sbm",
]

# All HA platform section keys that may become empty after block stripping.
# Extend this list if future templates introduce new HA platform keys.
_HA_SECTIONS: tuple[str, ...] = (
    "input_boolean",
    "input_button",
    "input_datetime",
    "input_number",
    "input_select",
    "input_text",
    "timer",
    "counter",
    "template",
    "binary_sensor",
    "sensor",
    "automation",
    "script",
)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Convert a room name to a valid HA entity slug (ASCII lowercase + underscore)."""
    s = name.strip().lower()
    s = s.replace("&", " and ")
    # Use re.ASCII so \w only matches [a-zA-Z0-9_], stripping accented and
    # other non-ASCII characters that would make invalid HA entity IDs.
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


def discover_features_from_text(text: str) -> list[str]:
    """Return all feature names found via # --- BEGIN X --- markers in *text*."""
    return re.findall(r"# --- BEGIN (\S+) ---", text)


def _prescan_template_features() -> list[str]:
    """
    Pre-scan sys.argv for --template and extract feature names from that file
    before argparse is fully configured.  Returns an empty list if --template
    is absent, the file doesn't exist, or the file has no markers.
    """
    for i, arg in enumerate(sys.argv):
        if arg == "--template" and i + 1 < len(sys.argv):
            path = Path(sys.argv[i + 1])
            if path.exists():
                return discover_features_from_text(path.read_text(encoding="utf-8"))
    return []


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Room:
    name: str
    slug: str
    package_key: str
    # Per-room feature flag overrides (True = include, False = strip)
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

        # Per-room overrides use `no_X: true` only.
        # emit_X is reserved for config root-level global overrides.
        overrides = {}
        for k, v in obj.items():
            if k.startswith("no_"):
                feature = k[3:]
                overrides[feature] = not bool(v)

    return Room(
        name=name,
        slug=slug,
        package_key=f"{slug}{key_suffix}",
        overrides=overrides,
    )


# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

def strip_marked_block(text: str, block: str) -> str:
    """
    Remove the block delimited by:
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
    Remove all remaining # --- BEGIN X --- and # --- END X --- comment lines.
    These are template scaffolding and serve no purpose in generated output.
    Also collapse 3+ consecutive blank lines down to 2 for clean formatting.
    """
    text = re.sub(r"(?m)^[ \t]*# --- (BEGIN|END) [^\n]+ ---[ \t]*\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def remove_empty_section(text: str, section: str) -> str:
    """
    Remove a top-level YAML key (e.g. `input_boolean:`) if its body contains
    only comments and/or blank lines — i.e. all real content was stripped.

    The `s` (DOTALL) flag is intentionally omitted and `.*` replaced with
    `[^\n]*` so comment matching is strictly single-line (avoids eating real
    content that follows a comment in the same section).
    """
    pat = rf"(?m)^(?P<hdr>{re.escape(section)}:\s*\n)(?P<body>(?:[ \t]*#[^\n]*\n|[ \t]*\n)*)(?=^[A-Za-z0-9_]+:\s*$|\Z)"
    return re.sub(pat, "", text)


def extract_inner_if_single_package(text: str) -> str:
    """
    Smart unwrapping: if the template has a single top-level wrapper key
    (e.g. `room_witb_actions:` or `roomba_vacjob:`), unwrap its content by
    removing the wrapper line and de-indenting by the wrapper's indent width.

    The de-indent width is detected from the first non-blank/non-comment line
    *inside* the wrapper, so templates indented by 2, 4, or any other depth
    all unwrap correctly.

    Header comments above the wrapper key are preserved.
    If no wrapper key is found, the content is returned as-is.
    """
    lines = text.splitlines()

    # Strip leading blank lines and optional YAML document separator
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip() == "---":
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return ""

    # Find the first non-comment, non-blank line and check for a bare top-level key
    wrapper_index = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*$", line):
            wrapper_index = i
        break  # Only inspect the very first content line

    if wrapper_index == -1:
        return "\n".join(lines)

    # Detect actual indentation width from the first substantive child line
    indent_width = 2  # sensible default
    for line in lines[wrapper_index + 1:]:
        if line.strip() and not line.strip().startswith("#"):
            leading = len(line) - len(line.lstrip())
            if leading > 0:
                indent_width = leading
            break

    # Preserve header comments; de-indent wrapper body
    result_lines: list[str] = list(lines[:wrapper_index])
    for line in lines[wrapper_index + 1:]:
        if line.startswith(" " * indent_width):
            result_lines.append(line[indent_width:])
        elif not line.strip():
            result_lines.append("")
        else:
            # Line at column 0 inside a wrapper — unusual, pass through
            result_lines.append(line)

    return "\n".join(result_lines)


def apply_tokens(text: str, room: Room) -> str:
    """
    Replace template tokens with room-specific values.

    Two friendly-name token styles are supported:
      "Room Friendly Name"  — used by witb_plus, witb_actions, humidity templates
      "Friendly Name"       — used by transit template (no "Room" prefix)

    "room_slug" is shared across all templates.

    Processing order:
      1. Replace "Room Friendly Name" first (more specific, must come first to
         avoid the bare "Friendly Name" replacement consuming it partially).
      2. Replace any remaining "Friendly Name" occurrences (transit compat).
      3. Replace "room_slug".
    """
    text = text.replace("Room Friendly Name", room.name)
    text = text.replace("Friendly Name", room.name)
    text = text.replace("room_slug", room.slug)
    return text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # Auto-discover feature block names from the template before configuring
    # argparse so that --no-X flags exist for ALL blocks, including those in
    # templates written after this script was last edited.
    discovered_features = _prescan_template_features()

    # Merge: static list first (preserves order + supplies flags without
    # --template), then append any newly discovered names not already listed.
    all_features: list[str] = list(_STATIC_FEATURES)
    for f in discovered_features:
        if f not in all_features:
            all_features.append(f)

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

  # Transit template (flat, no feature blocks):
  python generate_witb_packages_templated.py \\
    --template transit_helpers_package_template.yaml \\
    --rooms "Hallway" "Stairs" \\
    --key-suffix _transit \\
    --out ./packages/transit

Per-room config override example (rooms.yaml):
  rooms:
    - name: Master Bedroom
      no_latched: true       # Disable the latched helper for this room
    - name: Office
      no_exit_eval: true     # Disable exit_eval timer (not using WITB v4.2)
    - name: Bathroom
""",
    )
    ap.add_argument("--out", type=Path, help="Output directory for generated files (can also be set in config as 'out:')")
    ap.add_argument("--template", type=Path, help="Template YAML file (can also be set in config as 'template:')") 
    ap.add_argument("--rooms", nargs="+", metavar="ROOM", help="One or more room names (quoted if multi-word)")
    ap.add_argument("--config", type=Path, help="JSON or YAML config file defining rooms and global options")
    ap.add_argument("--key-suffix", default="_witb", help="Suffix appended to slug to form the package key (default: _witb)")
    ap.add_argument("--file-suffix", default=".yaml", help="Output file extension (default: .yaml)")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be generated without writing any files")

    # Global feature disable flags — built from the merged feature list so
    # new template blocks automatically get a --no-X flag.
    for f in all_features:
        flag = f"--no-{f.replace('_', '-')}"
        ap.add_argument(
            flag,
            dest=f"no_{f}",
            action="store_true",
            help=f"Disable the '{f}' block globally for all rooms",
        )

    args = ap.parse_args()

    # Load config early so template/out defined inside it are available
    # before validation. CLI values always take priority.
    cfg: dict[str, Any] = {}
    if args.config:
        cfg = load_config(args.config)
        if not cfg:
            ap.error(f"Config file is empty or contains no valid YAML: {args.config}")
        args.key_suffix = cfg.get("key_suffix", args.key_suffix)
        args.file_suffix = cfg.get("file_suffix", args.file_suffix)

        # Pull template and out from config if not supplied on CLI.
        # Resolved relative to the config file so the project is portable.
        if args.template is None and "template" in cfg:
            args.template = args.config.parent / cfg["template"]
        if args.out is None and "out" in cfg:
            args.out = args.config.parent / cfg["out"]

    # Validate required args now that config has had a chance to fill them in.
    if args.template is None:
        ap.error("--template is required (or set 'template:' in your config file)")
    if args.out is None:
        ap.error("--out is required (or set 'out:' in your config file)")

    # Validate template path exists with a clear error message.
    if not args.template.exists():
        ap.error(f"Template file not found: {args.template}")

    # 1. Build global feature defaults from CLI flags (all ON unless --no-X passed)
    global_defaults: dict[str, bool] = {}
    for f in all_features:
        global_defaults[f] = not getattr(args, f"no_{f}", False)

    # 2. Parse rooms from config or CLI
    rooms: list[Room] = []

    if args.config:
        # Config-level emit_X overrides apply ONLY if the corresponding CLI
        # --no-X flag was NOT explicitly passed. CLI takes priority.
        for f in all_features:
            cli_flag_key = f"no_{f}"
            cli_was_set = getattr(args, cli_flag_key, False)
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

    # Detect duplicate slugs before generating any files.
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
        sys.exit(
            "Error: Duplicate room slugs detected (would silently overwrite files):\n"
            + "\n".join(duplicates)
        )

    # 3. Read and unwrap template once
    raw_template = args.template.read_text(encoding="utf-8")
    base_inner = extract_inner_if_single_package(raw_template)

    # Detect which feature blocks are actually present in this template.
    # Features with no matching # --- BEGIN X --- marker are silently ignored,
    # so the same script works against any template without false warnings.
    template_features = [
        f for f in all_features
        if re.search(rf"# --- BEGIN {re.escape(f)} ---", base_inner)
    ]

    # Restrict global_defaults to only features present in this template
    global_defaults = {f: global_defaults[f] for f in template_features}

    # Create output directory (unless dry run)
    if not args.dry_run and not args.out.exists():
        args.out.mkdir(parents=True, exist_ok=True)

    # 4. Generate per room
    generated_count = 0
    for room in rooms:
        # Effective flags scoped to this template's blocks only.
        # Per-room overrides for blocks not in this template are silently ignored.
        effective_flags = global_defaults.copy()
        effective_flags.update({
            k: v for k, v in room.overrides.items() if k in template_features
        })

        # Strip disabled blocks from a fresh copy of the template
        current_text = base_inner
        for block, enabled in effective_flags.items():
            if not enabled:
                current_text = strip_marked_block(current_text, block)

        # Strip all remaining marker comment lines from the output
        current_text = strip_block_markers(current_text)

        # Clean up any now-empty section headers.
        # _HA_SECTIONS covers all known platform keys including input_text and
        # counter (transit / vacuum templates) — extend that tuple for future needs.
        for sec in _HA_SECTIONS:
            current_text = remove_empty_section(current_text, sec)

        # Replace tokens with room-specific values
        current_text = apply_tokens(current_text, room)

        # Wrap in package key
        final_yaml = f"---\n{room.package_key}:\n{indent(current_text, 2)}\n"

        fname = f"{room.slug}{args.file_suffix}"
        active_features = [k for k, v in effective_flags.items() if v]

        if args.dry_run:
            print(f"[DRY RUN] Would write: {args.out / fname}")
            print(f"          Features:    {', '.join(active_features) or '(none — flat template)'}")
            print(f"          Package key: {room.package_key}")
            print()
        else:
            out_path = args.out / fname
            out_path.write_text(final_yaml, encoding="utf-8")
            features_str = ", ".join(active_features) or "(none — flat template)"
            print(f"Generated {fname}  [pkg: {room.package_key}]  [features: {features_str}]")

        generated_count += 1

    if args.dry_run:
        print(f"Dry run complete. {generated_count} file(s) would be written to: {args.out}")
    else:
        print(f"\nDone. {generated_count} file(s) written to: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
