"""Helper to convert SVG files to PNG via Inkscape CLI."""

import shutil
import subprocess
import sys
from pathlib import Path


def svg_to_png(svg_path: Path, png_path: Path | None = None, dpi: int = 150) -> Path:
    """Convert an SVG file to PNG using Inkscape.

    Args:
        svg_path: Path to the input SVG file.
        png_path: Path for the output PNG. Defaults to svg_path with .png suffix.
        dpi: Resolution in dots per inch.

    Returns:
        The PNG output path (even if conversion was skipped).
    """
    if png_path is None:
        png_path = svg_path.with_suffix(".png")

    inkscape = shutil.which("inkscape")
    if inkscape is None:
        print("Warning: inkscape not found, skipping PNG export", file=sys.stderr)
        return png_path

    subprocess.run(
        [
            inkscape,
            f"--export-type=png",
            f"--export-dpi={dpi}",
            f"--export-filename={png_path}",
            str(svg_path),
        ],
        capture_output=True,
    )
    return png_path
