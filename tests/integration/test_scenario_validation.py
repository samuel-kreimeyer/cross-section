"""Integration tests for scenario validation.

Tests construct sections from scenario descriptions, generate annotations,
validate geometry, and export to SVG. Each scenario should pass validation
checks, but human evaluation is needed to judge quality of output.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cross_section.export import AnnotatedSVGExporter
from cross_section.core.geometry.validate import validate_section_geometry

# Import scenario builders
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scenarios"))

from crowned_road import build_scenario as build_crowned_road
from three_lane_urban import build_scenario as build_three_lane_urban
from ardot_undivided_highway import build_scenario as build_ardot_undivided_highway
from ardot_undivided_notch_and_widen import build_scenario as build_ardot_undivided_notch_and_widen


# Test output directory
TEST_OUTPUT_DIR = Path(__file__).parent.parent / "output"
TEST_OUTPUT_DIR.mkdir(exist_ok=True)


class TestScenarioValidation:
    """Tests for scenario validation workflow."""

    @pytest.fixture
    def exporter(self):
        """Create SVG exporter for tests."""
        return AnnotatedSVGExporter(
            scale=100.0,
            vertical_exaggeration=1.0,
            units="imperial"
        )

    def _validate_section_geometry(self, section):
        """Validate section geometry using shapely if available."""
        # Run shapely validation (expects list of components)
        validate_section_geometry(section.components)

        # Basic validation (no shapely required)
        assert len(section.components) > 0, "Section must have at least one component"
        assert section.metadata is not None, "Section must have metadata"

        # Check that all components have valid geometry
        for component in section.components:
            assert (
                len(component.polygons) > 0 or len(component.polylines) > 0
            ), "Component must have polygons or polylines"

    def _validate_svg_output(self, svg_content: str, scenario_name: str):
        """Validate SVG output is well-formed XML with expected content."""
        # Parse as XML to verify well-formedness
        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError as e:
            pytest.fail(f"SVG is not well-formed XML for {scenario_name}: {e}")

        # Check SVG namespace
        assert root.tag.endswith('svg'), f"Root element should be <svg> for {scenario_name}"

        # Check for geometry (polygons or polylines)
        has_geometry = (
            len(root.findall('.//{http://www.w3.org/2000/svg}polygon')) > 0 or
            len(root.findall('.//{http://www.w3.org/2000/svg}polyline')) > 0 or
            len(root.findall('.//{http://www.w3.org/2000/svg}path')) > 0
        )
        assert has_geometry, f"SVG should contain geometry elements for {scenario_name}"

        # Check for annotation layer (if annotations present)
        # Look for annotation elements (text, dimension markers, leaders)
        texts = root.findall('.//{http://www.w3.org/2000/svg}text')

        # Most scenarios should have text annotations
        if 'dimension' in svg_content.lower() or 'leader' in svg_content.lower():
            assert len(texts) > 0, f"SVG should contain text elements for annotations in {scenario_name}"

    def _export_and_validate(self, scenario_name: str, build_func, exporter):
        """Build scenario, export to SVG, and validate."""
        # Build scenario
        section, annotations = build_func()

        # Validate geometry
        self._validate_section_geometry(section)

        # Validate annotations
        assert annotations.count() > 0, f"{scenario_name} should have annotations"

        # Export to SVG
        output_path = TEST_OUTPUT_DIR / f"{scenario_name}.svg"
        with open(output_path, 'w') as f:
            exporter.export_with_annotations(section, annotations, f)

        # Verify file was created
        assert output_path.exists(), f"SVG file should be created for {scenario_name}"

        # Read and validate SVG content
        with open(output_path, 'r') as f:
            svg_content = f.read()

        assert len(svg_content) > 0, f"SVG file should not be empty for {scenario_name}"
        self._validate_svg_output(svg_content, scenario_name)

        return section, annotations, svg_content

    def test_crowned_road_scenario(self, exporter):
        """Test crowned road scenario."""
        section, annotations, svg_content = self._export_and_validate(
            "crowned_road_annotated",
            build_crowned_road,
            exporter
        )

        # Specific validation for crowned road
        assert len(section.components) == 6, "Crowned road should have 6 components"
        assert section.metadata["name"] == "Crowned Road with Ditches"

        # Check for expected dimensions
        assert "12'-0\"" in svg_content, "Should have 12-ft lane dimensions"
        assert "8'-0\"" in svg_content, "Should have 8-ft shoulder dimensions"
        assert "40'-0\"" in svg_content, "Should have overall 40-ft dimension"
        assert "Crown" in svg_content, "Should have Crown leader"

    def test_three_lane_urban_scenario(self, exporter):
        """Test 3-lane urban section scenario."""
        section, annotations, svg_content = self._export_and_validate(
            "3lane_urban_annotated",
            build_three_lane_urban,
            exporter
        )

        # Specific validation for 3-lane urban
        assert len(section.components) > 10, "3-lane urban should have many components"
        assert section.metadata["name"] == "3-Lane Urban Section with Turn Lane"

        # Check for expected dimensions and annotations
        assert "10'-0\"" in svg_content, "Should have 10-ft lane dimensions"
        assert "12'-0\"" in svg_content, "Should have 12-ft turn lane dimension"
        assert "5'-0\"" in svg_content, "Should have 5-ft sidewalk dimensions"
        assert "Surface Course" in svg_content, "Should have layer annotations"
        assert "Concrete Sidewalk" in svg_content, "Should have sidewalk annotations"

    def test_ardot_undivided_highway_scenario(self, exporter):
        """Test ARDOT undivided highway scenario."""
        section, annotations, svg_content = self._export_and_validate(
            "ardot_undivided_highway",
            build_ardot_undivided_highway,
            exporter
        )

        # Specific validation
        assert section.metadata["name"] == "ARDOT Undivided Highway"
        assert section.metadata["standard"] == "ARDOT"

        # Check for expected dimensions
        assert "11'-0\"" in svg_content, "Should have 11-ft lane dimensions"
        assert "4'-0\"" in svg_content, "Should have 4-ft shoulder dimensions"
        assert "30'-0\"" in svg_content, "Should have overall 30-ft dimension"

        # Check for pavement layer annotations
        assert "Surface Course" in svg_content, "Should have surface course annotation"
        assert "Binder Course" in svg_content, "Should have binder course annotation"
        assert "Aggregate Base" in svg_content, "Should have base course annotation"

    def test_ardot_undivided_notch_and_widen_scenario(self, exporter):
        """Test ARDOT undivided notch and widen scenario."""
        section, annotations, svg_content = self._export_and_validate(
            "ardot_undivided_notch_and_widen",
            build_ardot_undivided_notch_and_widen,
            exporter
        )

        # Specific validation
        assert section.metadata["name"] == "ARDOT Undivided Notch and Widen"
        assert section.metadata["standard"] == "ARDOT"

        # Check for expected dimensions
        assert "11'-0\"" in svg_content, "Should have 11-ft lane dimensions"
        assert "4'-0\"" in svg_content, "Should have 4-ft shoulder dimensions"
        assert "30'-0\"" in svg_content, "Should have overall 30-ft dimension"

        # Check for specific annotations
        assert "Overlay" in svg_content, "Should have overlay annotation"
        assert "Widening" in svg_content, "Should have widening annotation"
        assert "Notch" in svg_content, "Should have notch annotation"

    def test_all_scenarios_pass_shapely_validation(self, exporter):
        """Test that all scenarios pass shapely geometric validation."""
        scenarios = [
            ("crowned_road", build_crowned_road),
            ("three_lane_urban", build_three_lane_urban),
            ("ardot_undivided_highway", build_ardot_undivided_highway),
            ("ardot_undivided_notch_and_widen", build_ardot_undivided_notch_and_widen),
        ]

        for scenario_name, build_func in scenarios:
            section, annotations = build_func()

            # This should not raise any validation errors
            validate_section_geometry(section.components)

    def test_all_scenarios_have_annotations(self):
        """Test that all scenarios generate annotations."""
        scenarios = [
            build_crowned_road,
            build_three_lane_urban,
            build_ardot_undivided_highway,
            build_ardot_undivided_notch_and_widen,
        ]

        for build_func in scenarios:
            section, annotations = build_func()
            assert annotations.count() > 0, f"{build_func.__name__} should generate annotations"

    def test_output_directory_contains_svgs(self):
        """Verify that output directory contains generated SVG files."""
        # After running other tests, output directory should have SVG files
        expected_files = [
            "crowned_road_annotated.svg",
            "3lane_urban_annotated.svg",
            "ardot_undivided_highway.svg",
            "ardot_undivided_notch_and_widen.svg",
        ]

        for filename in expected_files:
            # File may not exist until specific test runs, so we just check format
            filepath = TEST_OUTPUT_DIR / filename
            if filepath.exists():
                # Verify it's valid XML
                with open(filepath, 'r') as f:
                    try:
                        ET.parse(f)
                    except ET.ParseError as e:
                        pytest.fail(f"{filename} is not valid XML: {e}")


class TestScenarioBuilderInterface:
    """Test that all scenario builders follow the expected interface."""

    def test_scenario_builders_return_tuple(self):
        """Test that all scenario builders return (SectionGeometry, AnnotationCollection)."""
        scenarios = [
            build_crowned_road,
            build_three_lane_urban,
            build_ardot_undivided_highway,
            build_ardot_undivided_notch_and_widen,
        ]

        for build_func in scenarios:
            result = build_func()
            assert isinstance(result, tuple), f"{build_func.__name__} should return tuple"
            assert len(result) == 2, f"{build_func.__name__} should return 2-tuple"

            section, annotations = result
            assert hasattr(section, 'components'), "First element should be SectionGeometry"
            assert hasattr(annotations, 'count'), "Second element should be AnnotationCollection"

    def test_scenario_builders_have_docstrings(self):
        """Test that all scenario builders are documented."""
        scenarios = [
            build_crowned_road,
            build_three_lane_urban,
            build_ardot_undivided_highway,
            build_ardot_undivided_notch_and_widen,
        ]

        for build_func in scenarios:
            assert build_func.__doc__ is not None, f"{build_func.__name__} should have docstring"
            assert len(build_func.__doc__.strip()) > 0, f"{build_func.__name__} docstring should not be empty"
