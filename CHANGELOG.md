# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PNG output alongside SVG from all generator scripts via Inkscape CLI helper (`tests/generators/_svg_to_png.py`)
- Shapely validation with geometry clipping and gap checks
- Barrier and wall components with dimensionally accurate profiles
- Shoulder attachment point fixes for fully_paved mode
- Comprehensive type annotations and mypy checking
- README sections: Purpose, Status, Quick Start, Project Structure, License
- Changelog file
- Type guard assertions with proper documentation
- Stable public API module (`cross_section.api`) with package re-exports
- Core components: `SurfaceProfile`, `Buffer`, `Gutter`, `Sidewalk`, `TurnLane`, `TraveledWay`
- Geometry invariants reference documentation
- Migration notes for the stable API surface
- Tests for new components and traveled way helpers
- Guide-based annotation planner with component registry and profiles
- Cross-slope annotation options and crown-dimension enforcement
- Cross-slope warning for opposing left/right pavement slopes
- SVG margin system to reserve space for legend, scale, and keyed notes

### Changed
- Updated development dependencies to include types-shapely
- Configured mypy to handle optional shapely dependency
- Improved type safety across component modules
- Scenario builders for crowned road and three-lane urban now use the domain API
- Scenario validation enforces shapely checks in tests
- Leader annotations keep anchor points fixed during repositioning

### Fixed
- Zone-aware collision resolver: annotations in different zones no longer treated as colliding, allowing labels, symbols, and dimensions to coexist inside dimension brackets
- Dimension bounding box false positives: `_annotation_has_collision` no longer uses generic `bounds().intersects()` against dimension annotations (whose bounds span the entire bracket area)
- Extension line collision exemption: `detect_line_text` and `detect_symbol_dimension` skip extension line checks for annotations horizontally inside the dimension span
- Traffic arrow geometry collision: traffic arrows now marked `allow_geometry_overlap` since they intentionally straddle the road surface
- Paired annotation collision: same-layer annotations at the same X position (e.g., drainage arrow + slope text) skip collision detection
- Slope text offset adjusted (0.55 -> 0.69) to clear rotation-inflated drainage arrow bounding boxes
- Type errors in slopes, shoulders, curbs, barriers, and section modules
- Added proper type guards for union types
- Resolved variable naming conflicts in shoulder layer processing
- Suppressed false-positive security warnings for type guard assertions
- Test imports for annotated export scenario generation

## [0.1.0] - Initial Development

### Added
- Core component system for road cross-section assembly
- Domain models for lanes, shoulders, slopes, curbs, and barriers
- Pavement layer definitions (asphalt, concrete, crushed rock)
- Geometric primitives and validation framework
- Section assembly and coordination system
- Export modules for CAD and SVG formats
- Comprehensive documentation and examples
- Test suite with pytest and hypothesis

[Unreleased]: https://github.com/samuel-kreimeyer/cross-section/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/samuel-kreimeyer/cross-section/releases/tag/v0.1.0
