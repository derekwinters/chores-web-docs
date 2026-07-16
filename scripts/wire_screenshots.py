#!/usr/bin/env python3
"""Wire captured screenshots into the documentation pages.

Each target doc page (see the "wiring" section of screenshots.config.json)
carries a marker block:

    <!-- screenshots:auto:START -->
    <!-- screenshots:auto:END -->

This script replaces whatever is between those markers with Markdown image
references — but ONLY for screenshots whose PNG actually exists on disk. That
guarantees `mkdocs build --strict` never sees a reference to a missing file:

* Before the pipeline has ever run, the marker block is empty and no images
  are referenced, so strict passes.
* After capture_screenshots.mjs writes the PNGs, running this script fills the
  block in, and strict passes because the files now exist.

The operation is idempotent: it always rewrites the block from scratch based on
the current config + which PNGs exist, so re-running produces identical output.

Usage:
    python wire_screenshots.py [--check]

    --check   Exit non-zero if any page would change (CI drift guard), without
              writing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

START = "<!-- screenshots:auto:START -->"
END = "<!-- screenshots:auto:END -->"

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "screenshots.config.json"


def _rel_image_path(doc_page: Path, png_path: Path) -> str:
    """POSIX relative path from the doc page's directory to the PNG."""
    rel = os.path.relpath(png_path, doc_page.parent)
    return Path(rel).as_posix()


def build_block(page_rel: str, screenshot_names: list[str], config: dict) -> str:
    """Build the Markdown that goes between the markers for one page."""
    doc_page = REPO_ROOT / page_rel
    output_dir = REPO_ROOT / config["outputDir"]
    captures = {c["name"]: c for c in config["captures"]}

    lines: list[str] = [START]
    for name in screenshot_names:
        capture = captures.get(name)
        if capture is None:
            print(f"  ! unknown screenshot '{name}' in config", file=sys.stderr)
            continue
        png_path = output_dir / f"{name}.png"
        if not png_path.exists():
            # PNG not generated yet — skip so strict stays green.
            print(f"  - {name}: PNG not present, skipping reference")
            continue
        rel = _rel_image_path(doc_page, png_path)
        lines.append("")
        lines.append(f"![{capture['title']}]({rel})")
    lines.append(END)
    return "\n".join(lines)


def rewrite_page(page_rel: str, screenshot_names: list[str], config: dict, check: bool) -> bool:
    """Rewrite one page's marker block. Returns True if the file changed."""
    doc_page = REPO_ROOT / page_rel
    text = doc_page.read_text()

    if START not in text or END not in text:
        print(f"  ! {page_rel}: marker block not found, skipping", file=sys.stderr)
        return False

    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)

    new_block = build_block(page_rel, screenshot_names, config)
    new_text = before + new_block + after

    if new_text == text:
        return False

    if not check:
        doc_page.write_text(new_text)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift, do not write")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text())

    changed_any = False
    for entry in config["wiring"]:
        print(f"Wiring {entry['page']} ...")
        changed = rewrite_page(entry["page"], entry["screenshots"], config, args.check)
        changed_any = changed_any or changed
        if changed:
            print(f"  {'would change' if args.check else 'updated'}")
        else:
            print("  up to date")

    if args.check and changed_any:
        print("Doc screenshot references are out of date. Run wire_screenshots.py.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
