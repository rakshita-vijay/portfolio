#!/usr/bin/env python3
"""
generate_og_image.py

Renders assets/og-source.svg (the Open Graph / Twitter Card preview image:
blue-to-purple "RV" monogram on black) to assets/og-image.png at the
standard 1200x630 OG size.

This runs manually - not part of any build step. Both assets/og-source.svg
and assets/og-image.png are committed to the repo. If you edit
og-source.svg, re-run this script and commit the updated og-image.png.

Usage:
    python3 generate_og_image.py [path/to/assets]

Requires: rsvg-convert on PATH (Debian/Ubuntu: apt-get install librsvg2-bin).
"""

import subprocess
import sys
import shutil
from pathlib import Path

OG_WIDTH = 1200
OG_HEIGHT = 630


def main() -> int:
    assets_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "assets"
    svg_path = assets_dir / "og-source.svg"
    png_path = assets_dir / "og-image.png"

    if not svg_path.exists():
        print(f"error: {svg_path} not found", file=sys.stderr)
        return 1

    if shutil.which("rsvg-convert") is None:
        print(
            "error: rsvg-convert not found on PATH.\n"
            "Install it first, e.g.:\n"
            "  Debian/Ubuntu: apt-get install -y librsvg2-bin\n"
            "  macOS (Homebrew): brew install librsvg",
            file=sys.stderr,
        )
        return 1

    subprocess.run(
        [
            "rsvg-convert",
            "-w", str(OG_WIDTH),
            "-h", str(OG_HEIGHT),
            str(svg_path),
            "-o", str(png_path),
        ],
        check=True,
    )
    print(f"wrote {png_path} ({OG_WIDTH}x{OG_HEIGHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
