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
2. Run all scenario builders
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

All 12 generator scripts successfully generate SVG output:

- **annotated_3lane_urban.py** - Three-lane urban section with annotations
- **annotated_crowned_road.py** - Crowned road with annotations
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

- Scenario builders: `tests/scenarios/`
- Runner script: `tests/regenerate_all_svgs.py`
