# Migration Notes (Draft)

## Stable API Surface
Use the stable API re-exports:

```python
from cross_section import RoadSection, ControlPoint, TravelLane
```

or

```python
from cross_section.api import RoadSection, ControlPoint, TravelLane
```

## Planned Deprecations
- Deep imports (e.g., `cross_section.core.domain.section`) will remain for now.
- Once the API is stabilized, deprecation notices will be added for legacy paths.

## Action Items
- Update internal examples and scenarios to use the stable API.
- Publish a short migration guide when deprecations are introduced.
