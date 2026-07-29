#!/usr/bin/env python3
"""One-time setup: download JetBrains Mono and subset it for these graphics.

Run via .github/workflows/prepare-fonts.yml (Actions has open internet
access; your own machine or this toolkit's dev sandbox may not). Produces:

  scripts/fonts/jbmono-400.woff2   regular weight, full latin - data graphics
  scripts/fonts/jbmono-600.woff2   semibold, full latin       - data graphics
  scripts/fonts/jbmono-head.woff2  semibold, letters only      - headings

These are committed once and then reused by generate_stats.py and
generate_ascii.py every time they render an SVG - no network access needed
at render time.

Requires: fonttools (`pip install fonttools brotli`)
"""
import os
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

RELEASE = "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Everything the graphics ever draw: digits, latin letters (upper + lower for
# headings and labels), the ramp characters, and common punctuation.
TEXT_CHARS = ("0123456789abcdefghijklmnopqrstuvwxyz"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              " :+#@.,%-–—()/'&")
HEAD_CHARS = "abcdefghijlkmnopqrstuvwxyz "   # "about stack projects stats..."


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "font-prep"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def subset(src_ttf, out_woff2, chars):
    subprocess.run([
        sys.executable, "-m", "fontTools.subset", src_ttf,
        f"--text={chars}",
        f"--output-file={out_woff2}",
        "--flavor=woff2",
        "--layout-features=*",
        "--no-hinting",
    ], check=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        zpath = os.path.join(tmp, "jbm.zip")
        print("downloading JetBrains Mono...")
        download(RELEASE, zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)

        def find(weight):
            for root, _, files in os.walk(tmp):
                for fn in files:
                    if fn.lower() == f"jetbrainsmono-{weight}.ttf".lower():
                        return os.path.join(root, fn)
            raise SystemExit(f"couldn't find a {weight} ttf in the release zip")

        regular = find("regular")
        semibold = find("semibold")

        subset(regular, os.path.join(OUT_DIR, "jbmono-400.woff2"), TEXT_CHARS)
        subset(semibold, os.path.join(OUT_DIR, "jbmono-600.woff2"), TEXT_CHARS)
        subset(semibold, os.path.join(OUT_DIR, "jbmono-head.woff2"), HEAD_CHARS)

    print("done - scripts/fonts/*.woff2 written")


if __name__ == "__main__":
    main()
