#!/usr/bin/env python3
"""Turn a photo into ascii.svg - a portrait drawn in the ramp `: + # @`.

Run this locally whenever you change your source photo (it doesn't need to
run daily like generate_stats.py, so it isn't in the scheduled workflow -
see .github/workflows/portrait.yml, which runs on demand instead).

Usage:
  pip install pillow
  python3 scripts/generate_ascii.py assets/photo.jpg -o ascii.svg

The grid assumes JBMono's advance width of exactly 0.600 em (that's why the
font is inlined rather than left to the viewer's default monospace - a
narrower fallback font would squeeze every row and distort the portrait).
"""
import argparse
import sys

from svgkit import WIDTH, RAMP, head, wipe, write

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

FS = 6.2                # font-size per character cell
CHAR_W_RATIO = 0.600     # JBMono's pinned advance width, in em
CHAR_H_RATIO = 1.15      # approximate line-height, in em - taller than wide,
                         # which is what keeps the grid from looking squashed


def to_levels(img, cols, rows):
    """Grayscale -> per-cell brightness, darkest cell first (top-left)."""
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.resize((cols, rows), Image.LANCZOS)
    px = img.load()
    levels = []
    for y in range(rows):
        row = []
        for x in range(cols):
            v = px[x, y]                      # 0 (black) .. 255 (white)
            dark = 255 - v                     # invert: dark subject -> more ink
            idx = min(4, dark * 5 // 256)       # 0..4 -> RAMP index
            row.append(idx)
        levels.append(row)
    return levels


def build(levels, cols, rows):
    cw = FS * CHAR_W_RATIO
    lh = FS * CHAR_H_RATIO
    grid_w = cols * cw
    grid_h = rows * lh
    H = int(grid_h) + 8

    p = [head(WIDTH, H)]
    x0 = (WIDTH - grid_w) / 2   # centered in the shared column width

    clip, cursor = wipe("ap", x0, 2, grid_w, grid_h, 0.10, dur=1.60)
    p.append(clip)
    p.append('<g clip-path="url(#ap)">')
    for y, row in enumerate(levels):
        line = "".join(RAMP[idx] for idx in row)
        if not line.strip():
            continue
        safe = line.replace("&", "&amp;").replace("<", "&lt;")
        p.append(f'<text xml:space="preserve" x="{x0:.1f}" '
                  f'y="{2 + (y + 1) * lh - lh * 0.2:.1f}" class="d-f" '
                  f'font-size="{FS}">{safe}</text>')
    p.append("</g>")
    p.append(cursor)
    p.append("</svg>")
    return "".join(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="source photo (jpg/png)")
    ap.add_argument("-o", "--output", default="ascii.svg")
    ap.add_argument("--cols", type=int, default=140,
                     help="grid width in characters (default 140)")
    ap.add_argument("--aspect", type=float, default=None,
                     help="override image aspect ratio (h/w); default: "
                          "read from the image itself")
    args = ap.parse_args()

    img = Image.open(args.image)
    aspect = args.aspect or (img.height / img.width)
    # rows chosen so the grid's on-screen aspect ratio matches the photo's,
    # given each character cell is CHAR_W_RATIO wide and CHAR_H_RATIO tall
    rows = round(args.cols * aspect * (CHAR_W_RATIO / CHAR_H_RATIO))
    rows = max(rows, 1)

    levels = to_levels(img, args.cols, rows)
    svg = build(levels, args.cols, rows)
    changed = write(args.output, svg)
    print(f"{args.cols}x{rows} grid -> {args.output} "
          f"({'updated' if changed else 'unchanged'})")


if __name__ == "__main__":
    main()
