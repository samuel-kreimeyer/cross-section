"""Tests for the 1D sweep-compact constraint solver."""

import pytest

from cross_section.core.domain.annotations.solver import SolverItem, sweep_compact_1d


class TestSweepCompact1D:
    """Tests for sweep_compact_1d algorithm."""

    def test_no_items(self):
        """Empty list is a no-op."""
        items: list[SolverItem] = []
        sweep_compact_1d(items)
        assert items == []

    def test_single_item(self):
        """Single item stays at desired position."""
        item = SolverItem(index=0, desired_x=5.0, half_width=0.5)
        sweep_compact_1d([item])
        assert item.solved_x == pytest.approx(5.0)

    def test_non_overlapping_items_unchanged(self):
        """Items that don't overlap stay at desired positions."""
        items = [
            SolverItem(index=0, desired_x=0.0, half_width=0.2),
            SolverItem(index=1, desired_x=2.0, half_width=0.2),
            SolverItem(index=2, desired_x=4.0, half_width=0.2),
        ]
        sweep_compact_1d(items, gap=0.05)
        assert items[0].solved_x == pytest.approx(0.0)
        assert items[1].solved_x == pytest.approx(2.0)
        assert items[2].solved_x == pytest.approx(4.0)

    def test_two_overlapping_items_separated(self):
        """Two overlapping items are pushed apart."""
        items = [
            SolverItem(index=0, desired_x=1.0, half_width=0.3),
            SolverItem(index=1, desired_x=1.1, half_width=0.3),
        ]
        sweep_compact_1d(items, gap=0.05)

        # After solving, gap between edges should be >= 0.05
        edge_gap = (items[1].solved_x - items[1].half_width) - (items[0].solved_x + items[0].half_width)
        assert edge_gap >= 0.05 - 1e-9

    def test_overlapping_items_minimum_displacement(self):
        """Solver minimises total displacement via backward sweep."""
        items = [
            SolverItem(index=0, desired_x=1.0, half_width=0.3),
            SolverItem(index=1, desired_x=1.1, half_width=0.3),
        ]
        sweep_compact_1d(items, gap=0.05)

        # The backward sweep should pull the left item back toward its
        # desired position, so displacement is shared rather than all on item 1
        disp0 = abs(items[0].solved_x - items[0].desired_x)
        disp1 = abs(items[1].solved_x - items[1].desired_x)
        total = disp0 + disp1
        # Total displacement should be roughly the overlap amount
        # Overlap = (0.3 + 0.05 + 0.3) - (1.1 - 1.0) = 0.55
        assert total < 0.60

    def test_three_items_at_same_position(self):
        """Three items at same X get spread with minimum rightward displacement."""
        items = [
            SolverItem(index=0, desired_x=5.0, half_width=0.2),
            SolverItem(index=1, desired_x=5.0, half_width=0.2),
            SolverItem(index=2, desired_x=5.0, half_width=0.2),
        ]
        sweep_compact_1d(items, gap=0.05)

        # All gaps should be respected
        for i in range(len(items) - 1):
            edge_gap = (items[i + 1].solved_x - items[i + 1].half_width) - (items[i].solved_x + items[i].half_width)
            assert edge_gap >= 0.05 - 1e-9, f"Gap between item {i} and {i+1} is {edge_gap}"

        # Leftmost item stays at desired (backward sweep pulls back to desired)
        assert items[0].solved_x == pytest.approx(5.0)

    def test_fixed_item_does_not_move(self):
        """Fixed items remain at their desired position."""
        items = [
            SolverItem(index=0, desired_x=1.0, half_width=0.3),
            SolverItem(index=1, desired_x=1.2, half_width=0.3, fixed=True),
        ]
        sweep_compact_1d(items, gap=0.05)

        assert items[1].solved_x == pytest.approx(1.2)

    def test_movable_items_flow_around_fixed_barrier(self):
        """Movable items adjust around a fixed barrier in the middle."""
        items = [
            SolverItem(index=0, desired_x=4.8, half_width=0.2),
            SolverItem(index=1, desired_x=5.0, half_width=0.2, fixed=True),
            SolverItem(index=2, desired_x=5.2, half_width=0.2),
        ]
        sweep_compact_1d(items, gap=0.05)

        # Fixed item stays put
        assert items[1].solved_x == pytest.approx(5.0)

        # Movable items must respect gap with fixed item
        left_gap = (items[1].solved_x - items[1].half_width) - (items[0].solved_x + items[0].half_width)
        right_gap = (items[2].solved_x - items[2].half_width) - (items[1].solved_x + items[1].half_width)
        assert left_gap >= 0.05 - 1e-9
        assert right_gap >= 0.05 - 1e-9

    def test_unsorted_input_handled(self):
        """Items provided in non-sorted order are handled correctly."""
        items = [
            SolverItem(index=0, desired_x=3.0, half_width=0.2),
            SolverItem(index=1, desired_x=1.0, half_width=0.2),
            SolverItem(index=2, desired_x=2.0, half_width=0.2),
        ]
        sweep_compact_1d(items, gap=0.05)

        # After solving, items should be sorted by solved_x
        solved_xs = [it.solved_x for it in items]
        assert solved_xs == sorted(solved_xs)

    def test_large_gap_forces_wide_spread(self):
        """Large gap parameter forces items further apart."""
        items = [
            SolverItem(index=0, desired_x=0.0, half_width=0.1),
            SolverItem(index=1, desired_x=0.0, half_width=0.1),
        ]
        sweep_compact_1d(items, gap=1.0)

        edge_gap = (items[1].solved_x - items[1].half_width) - (items[0].solved_x + items[0].half_width)
        assert edge_gap >= 1.0 - 1e-9

    def test_zero_gap(self):
        """Zero gap means items can be touching but not overlapping."""
        items = [
            SolverItem(index=0, desired_x=0.0, half_width=0.5),
            SolverItem(index=1, desired_x=0.5, half_width=0.5),
        ]
        sweep_compact_1d(items, gap=0.0)

        edge_gap = (items[1].solved_x - items[1].half_width) - (items[0].solved_x + items[0].half_width)
        assert edge_gap >= -1e-9  # non-negative

    def test_already_separated_items_not_moved(self):
        """Items that already satisfy constraints are not displaced."""
        items = [
            SolverItem(index=0, desired_x=0.0, half_width=0.1),
            SolverItem(index=1, desired_x=1.0, half_width=0.1),
        ]
        sweep_compact_1d(items, gap=0.05)

        assert items[0].solved_x == pytest.approx(0.0)
        assert items[1].solved_x == pytest.approx(1.0)

    def test_two_fixed_items_overlapping(self):
        """Two fixed overlapping items — neither moves (degenerate case)."""
        items = [
            SolverItem(index=0, desired_x=1.0, half_width=0.3, fixed=True),
            SolverItem(index=1, desired_x=1.1, half_width=0.3, fixed=True),
        ]
        sweep_compact_1d(items, gap=0.05)

        # Both stay at desired (solver can't resolve fixed-fixed overlap)
        assert items[0].solved_x == pytest.approx(1.0)
        assert items[1].solved_x == pytest.approx(1.1)

    def test_varying_half_widths(self):
        """Items with different widths are separated correctly."""
        items = [
            SolverItem(index=0, desired_x=0.0, half_width=0.5),  # wide
            SolverItem(index=1, desired_x=0.5, half_width=0.1),  # narrow
        ]
        sweep_compact_1d(items, gap=0.05)

        edge_gap = (items[1].solved_x - items[1].half_width) - (items[0].solved_x + items[0].half_width)
        assert edge_gap >= 0.05 - 1e-9

    def test_index_preserved_after_sort(self):
        """Original index values are preserved even after internal sorting."""
        items = [
            SolverItem(index=42, desired_x=3.0, half_width=0.1),
            SolverItem(index=7, desired_x=1.0, half_width=0.1),
            SolverItem(index=99, desired_x=2.0, half_width=0.1),
        ]
        sweep_compact_1d(items, gap=0.05)

        indices = {it.index for it in items}
        assert indices == {42, 7, 99}


class TestSolverItem:
    """Tests for SolverItem dataclass."""

    def test_solved_x_defaults_to_desired(self):
        """solved_x should initialise to desired_x."""
        item = SolverItem(index=0, desired_x=3.14, half_width=0.5)
        assert item.solved_x == pytest.approx(3.14)

    def test_fixed_defaults_to_false(self):
        """fixed should default to False."""
        item = SolverItem(index=0, desired_x=0.0, half_width=0.1)
        assert item.fixed is False
