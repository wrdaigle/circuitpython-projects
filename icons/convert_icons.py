#!/usr/bin/env python3
"""
Convert BMP weather icons to CircuitPython .mpy modules.

Downloads the Adafruit mpy-cross binary for CircuitPython 9.1.4 (arm64) on
first run and caches it in icons/tools/. Subsequent runs skip the download.

Run this on your desktop after any icon changes, then rsync to the board.

Requirements: pip install pillow

Usage: python convert_icons.py
"""

from PIL import Image
import os
import stat
import subprocess
import urllib.request

SRC_DIR = os.path.join("icons", "weather", "icons_80x80")
DEST_DIR = os.path.join("qtpy_esp32_s2", "weatherStation", "icons_80x80")
TOOLS_DIR = os.path.join("icons", "tools")
MPY_CROSS = os.path.join(TOOLS_DIR, "mpy-cross")
MPY_CROSS_URL = (
    "https://adafruit-circuit-python.s3.amazonaws.com/"
    "bin/mpy-cross/macos/mpy-cross-macos-9.1.4-arm64"
)
MAX_COLORS = 64  # Enough for weather icons; keeps memory usage low on device


def ensure_mpy_cross():
    if os.path.exists(MPY_CROSS):
        return
    os.makedirs(TOOLS_DIR, exist_ok=True)
    print("Downloading Adafruit mpy-cross for CircuitPython 9.1.4 (arm64)...")
    urllib.request.urlretrieve(MPY_CROSS_URL, MPY_CROSS)
    os.chmod(MPY_CROSS, os.stat(MPY_CROSS).st_mode | stat.S_IEXEC)
    print(f"  Saved to {MPY_CROSS}")


def bmp_to_py(bmp_path, py_path, max_colors=MAX_COLORS):
    img = Image.open(bmp_path).convert("RGB")
    img_indexed = img.quantize(colors=max_colors, dither=0)

    pixels = img_indexed.tobytes()
    n_colors = max(pixels) + 1
    palette_raw = img_indexed.getpalette()          # flat [R,G,B, ...] * 256
    palette_bytes = bytes(palette_raw[: n_colors * 3])

    with open(py_path, "w") as f:
        f.write(f"# Auto-generated from {os.path.basename(bmp_path)} — do not edit\n")
        f.write(f"W={img_indexed.width}\n")
        f.write(f"H={img_indexed.height}\n")
        f.write(f"C={n_colors}\n")
        f.write(f"P={palette_bytes!r}\n")
        f.write(f"B={pixels!r}\n")


ensure_mpy_cross()
os.makedirs(DEST_DIR, exist_ok=True)

converted = 0
for fname in sorted(os.listdir(SRC_DIR)):
    if not fname.endswith(".bmp"):
        continue
    name = fname[:-4]
    bmp_path = os.path.join(SRC_DIR, fname)
    py_path = os.path.join(DEST_DIR, f"i_{name}.py")
    mpy_path = os.path.join(DEST_DIR, f"i_{name}.mpy")

    bmp_to_py(bmp_path, py_path)
    subprocess.run([MPY_CROSS, py_path], check=True)
    os.remove(py_path)
    print(f"  {fname} -> {mpy_path}")
    converted += 1

# Create package __init__.py so icons_80x80 is importable as a package
init_path = os.path.join(DEST_DIR, "__init__.py")
with open(init_path, "w") as f:
    pass

print(f"\nConverted {converted} icons.")
print(f"\nNext: rsync to board")
