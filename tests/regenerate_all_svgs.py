#!/usr/bin/env python
"""Runner script to regenerate all SVG outputs.

This script runs all generator scripts in tests/generators/ to regenerate
all SVG cross-section diagrams in tests/output/.
"""

import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Get the absolute path to the project root (parent of tests/)
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

# Add src to path for imports
sys.path.insert(0, str(SRC_DIR))

# Set PYTHONPATH environment variable for subprocess calls
os.environ["PYTHONPATH"] = str(SRC_DIR)

# Configure logging for annotation debugging
logging.basicConfig(
    level=logging.WARNING,
    format="%(name)s - %(levelname)s - %(message)s"
)


def run_generator_scripts():
    """Run all generator scripts in tests/generators/.

    Returns:
        Tuple of (generated_files, skipped_scripts, failed_scripts)
    """
    generators_dir = SCRIPT_DIR / "generators"
    generator_scripts = sorted(generators_dir.glob("*.py"))
    output_dir = SCRIPT_DIR / "output"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Running Generator Scripts")
    print("=" * 70)

    generated_files: dict[str, str] = {}  # filename -> generator script
    skipped_scripts: list[str] = []  # scripts that don't generate SVGs
    failed_scripts: list[tuple[str, str]] = []  # (script, error message)
    warned_scripts: list[tuple[str, str]] = []  # (script, warning message)

    for script in generator_scripts:
        # Skip README and __init__ files
        if script.name.startswith("_") or script.name == "README.md":
            continue

        print(f"\n{script.name}...")

        # Record time before running script
        run_start = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                failed_scripts.append((script.name, result.stderr[:200] if result.stderr else "Unknown error"))
                print(f"  ✗ Failed (exit code {result.returncode})")
                continue

            # Capture collision warnings from stderr
            warnings = result.stderr.strip() if result.stderr else ""

            # Check which SVG files were created/updated by this script
            # A file is considered generated if its mtime is >= when we started running the script
            files_from_this_script = []
            for svg in output_dir.glob("*.svg"):
                if svg.stat().st_mtime >= run_start:
                    # This file was created or updated during this script run
                    if svg.name not in generated_files:
                        files_from_this_script.append(svg.name)
                        generated_files[svg.name] = script.name

            if files_from_this_script:
                for svg_name in files_from_this_script:
                    svg_path = output_dir / svg_name
                    size_kb = svg_path.stat().st_size / 1024
                    png_path = svg_path.with_suffix(".png")
                    png_note = ""
                    if png_path.exists() and png_path.stat().st_mtime >= run_start:
                        png_kb = png_path.stat().st_size / 1024
                        png_note = f" + PNG ({png_kb:.1f} KB)"
                    if warnings:
                        print(f"  ⚠ {svg_name} ({size_kb:.1f} KB){png_note} — {warnings}")
                        warned_scripts.append((script.name, warnings))
                    else:
                        print(f"  ✓ {svg_name} ({size_kb:.1f} KB){png_note}")
            else:
                skipped_scripts.append(script.name)
                print(f"  - No SVG output")

        except subprocess.TimeoutExpired:
            failed_scripts.append((script.name, "Timed out"))
            print(f"  ✗ Timed out")
        except Exception as e:
            failed_scripts.append((script.name, str(e)))
            print(f"  ✗ {e}")

    return generated_files, skipped_scripts, failed_scripts, warned_scripts


def main():
    """Main runner function."""
    print("\nCross-Section SVG Regeneration Tool")
    print("=" * 70)

    start_time = datetime.now()

    # Run generator scripts
    generated_files, skipped_scripts, failed_scripts, warned_scripts = run_generator_scripts()

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    output_dir = SCRIPT_DIR / "output"
    all_svg_files = sorted(output_dir.glob("*.svg"))

    # Show generated files
    if generated_files:
        print(f"\nGenerated {len(generated_files)} SVG files:")
        for svg_name in sorted(generated_files.keys()):
            generator = generated_files[svg_name]
            svg_path = output_dir / svg_name
            size_kb = svg_path.stat().st_size / 1024
            print(f"  ✓ {svg_name} ({size_kb:.1f} KB) ← {generator}")

    # Show skipped scripts (no SVG output)
    if skipped_scripts:
        print(f"\nScripts with no SVG output ({len(skipped_scripts)}):")
        for script in skipped_scripts:
            print(f"  - {script}")

    # Show scripts with collision warnings
    if warned_scripts:
        print(f"\nCollision warnings ({len(warned_scripts)}):")
        for script, warning in warned_scripts:
            print(f"  ⚠ {script}: {warning}")

    # Show failed scripts
    if failed_scripts:
        print(f"\nFailed scripts ({len(failed_scripts)}):")
        for script, error in failed_scripts:
            print(f"  ✗ {script}: {error}")

    # Show pre-existing files that weren't regenerated
    pre_existing = [f.name for f in all_svg_files if f.name not in generated_files]
    if pre_existing:
        print(f"\nPre-existing files not updated ({len(pre_existing)}):")
        for filename in sorted(pre_existing):
            svg_path = output_dir / filename
            size_kb = svg_path.stat().st_size / 1024
            mtime = datetime.fromtimestamp(svg_path.stat().st_mtime)
            print(f"  - {filename} ({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")

    elapsed = datetime.now() - start_time
    print(f"\nCompleted in {elapsed.total_seconds():.1f}s")


if __name__ == "__main__":
    main()
