# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

### Changed
- Updated development dependencies to include types-shapely
- Configured mypy to handle optional shapely dependency
- Improved type safety across component modules
- Scenario builders for crowned road and three-lane urban now use the domain API
- Scenario validation enforces shapely checks in tests

### Fixed
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
