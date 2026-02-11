"""1D constraint solver for annotation placement.

Implements a sweep-compact algorithm (simplified VPSC) that finds
minimum-displacement positions for annotations along the X axis,
respecting minimum gap constraints and fixed barriers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SolverItem:
    """A single item to be placed by the 1D solver.

    Attributes:
        index: Original index in the annotation list (for mapping results back).
        desired_x: Where the annotation wants to be (original center X).
        half_width: Half of horizontal extent from bounds().
        fixed: If True, this item cannot move (e.g. symbols, high-priority).
        solved_x: Output — the solved X position after sweep_compact_1d.
    """

    index: int
    desired_x: float
    half_width: float
    fixed: bool = False
    solved_x: float = field(init=False)

    def __post_init__(self) -> None:
        self.solved_x = self.desired_x


def sweep_compact_1d(items: list[SolverItem], gap: float = 0.05) -> None:
    """Solve 1D placement with minimum total displacement.

    Modifies each item's ``solved_x`` in place.

    Algorithm:
      1. Sort items by desired_x.
      2. Forward sweep (left → right): push each item right if it overlaps
         its left neighbour (considering half-widths + gap). Fixed items
         never move; movable items absorb the displacement.
      3. Backward sweep (right → left): pull movable items back toward
         desired_x without violating the constraint with their right
         neighbour. This redistributes displacement symmetrically.

    Args:
        items: List of SolverItem instances. Modified in place.
        gap: Minimum gap between adjacent item edges.
    """
    if len(items) <= 1:
        return

    # Sort by desired position (stable sort preserves original order for ties)
    items.sort(key=lambda it: it.desired_x)

    # --- Forward sweep (left → right) ---
    for i in range(1, len(items)):
        prev = items[i - 1]
        curr = items[i]
        min_x = prev.solved_x + prev.half_width + gap + curr.half_width
        if curr.solved_x < min_x:
            if not curr.fixed:
                curr.solved_x = min_x
            # If curr is fixed, it stays put. The backward sweep will
            # push movable predecessors left to make room.

    # --- Backward sweep (right → left) ---
    for i in range(len(items) - 2, -1, -1):
        curr = items[i]
        right = items[i + 1]

        if curr.fixed:
            # Fixed items don't move, but ensure right neighbour respects gap
            min_right = curr.solved_x + curr.half_width + gap + right.half_width
            if right.solved_x < min_right and not right.fixed:
                right.solved_x = min_right
            continue

        # Maximum X this item can occupy without violating right constraint
        max_x = right.solved_x - right.half_width - gap - curr.half_width

        # First: clamp to respect the right constraint (may push left)
        if curr.solved_x > max_x:
            curr.solved_x = max_x

        # Second: if forward sweep pushed us right, pull back toward desired_x
        if curr.solved_x > curr.desired_x:
            curr.solved_x = max(curr.desired_x, max_x)
