# Cross-Section Generator Scripts

This directory contains example generator scripts that create various cross-section SVG diagrams.

## Usage

### Run All Generators

To regenerate all SVG outputs, run from any directory:

```bash
# From project root
python tests/regenerate_all_svgs.py

# From tests directory
cd tests
python regenerate_all_svgs.py

# From anywhere (using absolute path)
python /path/to/cross-section/tests/regenerate_all_svgs.py
```

This will:
1. Run all generator scripts in this directory
2. Run all generator scripts
3. Output SVG files to `tests/output/`

The script automatically handles Python paths and can be run from any directory.

### Run Individual Generator

```bash
# From project root
PYTHONPATH=src python tests/generators/<script_name>.py

# Or from tests/generators directory
cd tests/generators
PYTHONPATH=../../src python <script_name>.py
```

## Generator Scripts

Generator scripts in this directory generate SVG output:

- **three_lane_urban.py** - Three-lane urban section with annotations
- **crowned_road.py** - Crowned road with annotations
- **ardot_undivided_highway.py** - ARDOT undivided highway section
- **ardot_undivided_notch_and_widen.py** - ARDOT notch and widen section
- **asymmetric_cut_fill.py** - Asymmetric cut and fill slopes
- **basic_section.py** - Simple two-lane road section
- **curb_and_gutter.py** - Curb and gutter detail
- **cut_and_fill.py** - Symmetric cut and fill
- **layered_pavement.py** - Detailed pavement layer structure (flexible vs. rigid)
- **road_with_shoulders.py** - Road with paved and unpaved shoulders
- **roadside_ditch.py** - Roadside drainage ditch
- **shoring_example.py** - Temporary shoring system
- **slumped_shoulder.py** - Slumped shoulder detail
- **symmetric_section.py** - Four-lane divided highway (symmetric)

## Output Location

All generator scripts output to: `tests/output/`

## Related

- Reusable scenario builders: `tests/generators/` via `build_scenario()`
- Runner script: `tests/regenerate_all_svgs.py`
