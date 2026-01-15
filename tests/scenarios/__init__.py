"""Scenario builders for integration tests.

Each scenario module should provide a `build_scenario()` function that returns
a tuple of (SectionGeometry, AnnotationCollection).
"""

__all__ = [
    "crowned_road",
    "three_lane_urban",
    "ardot_undivided_highway",
    "ardot_undivided_notch_and_widen",
]
