#!/usr/bin/env python
"""Runner script to regenerate all SVG outputs.

This script runs all generator scripts and scenario builders to regenerate
all SVG cross-section diagrams in tests/output/.
"""

import io
import os
import subprocess
import sys
from pathlib import Path

# Get the absolute path to the project root (parent of tests/)
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

# Add src to path for imports
sys.path.insert(0, str(SRC_DIR))

# Set PYTHONPATH environment variable for subprocess calls
os.environ["PYTHONPATH"] = str(SRC_DIR)

from cross_section.export import AnnotatedSVGExporter


def run_generator_scripts():
    """Run all generator scripts in tests/generators/."""
    generators_dir = SCRIPT_DIR / "generators"
    generator_scripts = sorted(generators_dir.glob("*.py"))

    print("=" * 70)
    print("Running Generator Scripts")
    print("=" * 70)

    for script in generator_scripts:
        print(f"\nRunning {script.name}...")
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"  ✓ {script.name} completed successfully")
            else:
                print(f"  ✗ {script.name} failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"  ✗ {script.name} timed out")
        except Exception as e:
            print(f"  ✗ {script.name} failed: {e}")


def run_scenario_builders():
    """Run all scenario builders to generate annotated SVGs."""
    print("\n" + "=" * 70)
    print("Running Scenario Builders")
    print("=" * 70)

    # Add tests directory to path for importing scenarios
    sys.path.insert(0, str(SCRIPT_DIR))

    # Import scenario builders
    from scenarios.crowned_road import build_scenario as build_crowned_road
    from scenarios.three_lane_urban import build_scenario as build_3lane_urban
    from scenarios.ardot_undivided_highway import build_scenario as build_ardot_highway
    from scenarios.ardot_undivided_notch_and_widen import build_scenario as build_ardot_notch

    scenarios = [
        ("crowned_road.svg", build_crowned_road),
        ("3lane_urban.svg", build_3lane_urban),
        ("ardot_undivided_highway.svg", build_ardot_highway),
        ("ardot_undivided_notch_and_widen.svg", build_ardot_notch),
    ]

    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    exporter = AnnotatedSVGExporter(scale=30.48)

    for filename, builder in scenarios:
        print(f"\nGenerating {filename}...")
        try:
            geometry, annotations = builder()

            # Export to SVG
            svg_path = output_dir / filename
            with open(svg_path, 'w') as f:
                output_buffer = io.StringIO()
                exporter.export_with_annotations(geometry, annotations, output_buffer)
                f.write(output_buffer.getvalue())

            print(f"  ✓ {filename} generated successfully")
            print(f"    Components: {len(geometry.components)}, Annotations: {len(annotations.annotations)}")
        except Exception as e:
            print(f"  ✗ {filename} failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main runner function."""
    print("\nCross-Section SVG Regeneration Tool")
    print("=" * 70)

    # Run generator scripts
    run_generator_scripts()

    # Run scenario builders
    run_scenario_builders()

    # Summary
    print("\n" + "=" * 70)
    print("Regeneration Complete")
    print("=" * 70)

    output_dir = SCRIPT_DIR / "output"
    svg_files = sorted(output_dir.glob("*.svg"))
    print(f"\nTotal SVG files in {output_dir}: {len(svg_files)}")

    if svg_files:
        print("\nGenerated files:")
        for svg_file in svg_files:
            size_kb = svg_file.stat().st_size / 1024
            print(f"  - {svg_file.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
