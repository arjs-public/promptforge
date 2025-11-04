#!/usr/bin/env python3
# ------------------------------------------------------------------
#  png_to_icns.py
#
#  Usage:
#     python png_to_icns.py input.png output.icns
#
#  Requires:
#     Pillow   (pip install Pillow)
#     macOS   (iconutil is built‑in)
#
#  The script:
#     1. Opens the source PNG.
#     2. Creates the temporary *.iconset* folder with the required
#        sizes (16, 32, 64, 128, 256, 512, 1024).
#     3. Calls `iconutil` to build the final *.icns* file.
# ------------------------------------------------------------------

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from PIL import Image

# -------------------------------------------------------------
# 1.  Define the icon sizes macOS expects
# -------------------------------------------------------------
ICON_SIZES = [
    (16, 16),     # 16x16 (no @2x)
    (32, 32),     # 16x16@2x
    (32, 32),     # 32x32 (no @2x)
    (64, 64),     # 32x32@2x
    (128, 128),   # 128x128 (no @2x)
    (256, 256),   # 128x128@2x
    (256, 256),   # 256x256 (no @2x)
    (512, 512),   # 256x256@2x
    (512, 512),   # 512x512 (no @2x)
    (1024, 1024), # 512x512@2x
]

# Names that iconutil expects inside the .iconset folder
ICON_NAMES = [
    "icon_16x16.png",
    "icon_16x16@2x.png",
    "icon_32x32.png",
    "icon_32x32@2x.png",
    "icon_128x128.png",
    "icon_128x128@2x.png",
    "icon_256x256.png",
    "icon_256x256@2x.png",
    "icon_512x512.png",
    "icon_512x512@2x.png",
]

assert len(ICON_SIZES) == len(ICON_NAMES), "Size/name mismatch"

# -------------------------------------------------------------
# 2.  Create the iconset folder
# -------------------------------------------------------------
def make_iconset(png_path: Path, iconset_dir: Path):
    """Populate `iconset_dir` with the required PNGs."""
    img = Image.open(png_path)
    img = img.convert("RGBA")           # Ensure 32‑bit PNG

    for (size, name) in zip(ICON_SIZES, ICON_NAMES):
        resized = img.resize(size, Image.LANCZOS)
        dest = iconset_dir / name
        resized.save(dest, "PNG")
        print(f"  → {dest.name} ({size[0]}x{size[1]})")

# -------------------------------------------------------------
# 3.  Build the .icns file
# -------------------------------------------------------------
def build_icns(iconset_dir: Path, out_path: Path):
    """Run iconutil to create the .icns file."""
    cmd = ["iconutil", "-c", "icns", str(iconset_dir)]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"iconutil failed:\n{result.stderr}")

    # iconutil writes the .icns next to the .iconset folder
    produced = iconset_dir.with_suffix(".icns")
    if not produced.exists():
        raise FileNotFoundError("iconutil did not create the .icns file.")
    shutil.move(str(produced), str(out_path))
    print(f"✅  Created {out_path}")

# -------------------------------------------------------------
# 4.  Main driver
# -------------------------------------------------------------
def main(argv):
    if len(argv) != 3:
        print(f"Usage: {argv[0]} input.png output.icns")
        sys.exit(1)

    src_png = Path(argv[1])
    out_icns = Path(argv[2])

    if not src_png.is_file():
        raise FileNotFoundError(f"{src_png} does not exist.")

    # Create a temporary directory for the iconset
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset_dir = Path(tmpdir) / f"{src_png.stem}.iconset"
        iconset_dir.mkdir()
        make_iconset(src_png, iconset_dir)
        build_icns(iconset_dir, out_icns)

if __name__ == "__main__":
    main(sys.argv)

