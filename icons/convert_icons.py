#!/usr/bin/env python3
"""
Convert BMP weather icons to CircuitPython-importable Python modules.

Run this on your desktop after any icon changes, then copy the generated
.py files and __init__.py to CIRCUITPY/icons_80x80/.

Requirements: pip install pillow

Usage: python convert_icons.py
"""

from PIL import Image
import os

ICONS_DIR = os.path.join("qtpy_esp32_s2", "weatherStation", "icons_80x80")
MAX_COLORS = 64  # Enough for weather icons; keeps memory usage low on device


def bmp_to_py(bmp_path, py_path, max_colors=MAX_COLORS):
    img = Image.open(bmp_path).convert("RGB")
    img_indexed = img.quantize(colors=max_colors, dither=0)

    pixels = bytes(img_indexed.getdata())
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


converted = 0
for fname in sorted(os.listdir(ICONS_DIR)):
    if not fname.endswith(".bmp"):
        continue
    name = fname[:-4]
    bmp_path = os.path.join(ICONS_DIR, fname)
    py_path = os.path.join(ICONS_DIR, f"i_{name}.py")
    bmp_to_py(bmp_path, py_path)
    print(f"  {fname} -> i_{name}.py")
    converted += 1

# Create package __init__.py so icons_80x80 is importable as a package
init_path = os.path.join(ICONS_DIR, "__init__.py")
with open(init_path, "w") as f:
    pass

print(f"\nConverted {converted} icons.")
print(f"Created {init_path}")
print("\nNext: copy all .py files from icons_80x80/ to CIRCUITPY/icons_80x80/")
