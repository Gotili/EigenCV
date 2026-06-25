#!/usr/bin/env python3
"""
EigenCV Cloud Export Tool
=========================
Creates a clean ZIP of the repository for uploading to cloud AIs
(ChatGPT, Gemini, Claude) WITHOUT the .git folder or other junk.

Usage:
    python tools/export_for_cloud.py

Output:
    EigenCV_for_cloud.zip  (in the repository root)
"""

import zipfile
import os
import sys
from pathlib import Path
from datetime import datetime

# Import manifest generator to ensure VALID_IDS.md is always up-to-date
sys.path.insert(0, str(Path(__file__).parent))
try:
    from generate_id_manifest import generate_manifest
except ImportError:
    generate_manifest = None

# --- Config ---
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".devcontainer",       # Docker env not needed for cloud AI
    "application-packages", # Personal application data — keep private!
}
EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "EigenCV_for_cloud.zip",  # Don't zip the zip
}
EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
}

def should_exclude(path: Path, root: Path) -> bool:
    """Return True if this path should be excluded from the ZIP."""
    parts = path.relative_to(root).parts

    # Exclude any path that passes through an excluded directory
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True

    # Exclude specific filenames
    if path.name in EXCLUDE_FILES:
        return True

    # Exclude by extension
    if path.suffix in EXCLUDE_EXTENSIONS:
        return True

    return False


def main():
    root = Path(__file__).parent.parent.resolve()
    output_path = root / "EigenCV_for_cloud.zip"

    print("=" * 60)
    print("  EigenCV Cloud Export Tool")
    print("=" * 60)
    print(f"  Source:  {root}")
    print(f"  Output:  {output_path}")
    print(f"  Excluding: {', '.join(sorted(EXCLUDE_DIRS))}")
    print("=" * 60)

    # Always regenerate VALID_IDS.md before packaging
    if generate_manifest:
        print("[INFO] Regenerating VALID_IDS.md from active database...")
        generate_manifest(root_dir=str(root))
        print("[OK]  VALID_IDS.md updated.")
    else:
        print("[WARNING] generate_id_manifest.py not found — VALID_IDS.md may be stale.")
    print("=" * 60)

    file_count = 0
    skipped_count = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file():
                continue

            if should_exclude(file_path, root):
                skipped_count += 1
                continue

            arcname = file_path.relative_to(root)
            zf.write(file_path, arcname)
            print(f"  + {arcname}")
            file_count += 1

    size_kb = output_path.stat().st_size / 1024
    print("=" * 60)
    print(f"  [OK] Done! {file_count} files added, {skipped_count} excluded.")
    print(f"  [ZIP] Output size: {size_kb:.1f} KB")
    print(f"  [OUT] File: {output_path.name}")
    print("=" * 60)
    print()
    print("  Upload this ZIP to ChatGPT / Gemini / Claude along")
    print("  with your old CV to populate the database.")
    print()


if __name__ == "__main__":
    main()
