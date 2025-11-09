# VIKTOR Vendoring Strategy

## The Problem

VIKTOR projects have a unique constraint: **code cannot import modules from parent folders**. This means a VIKTOR app at `src/cross_section/interfaces/viktor/app.py` cannot use standard Python imports like:

```python
# ❌ This DOES NOT work in VIKTOR
from cross_section.core.domain.components import TravelLane
```

VIKTOR can only import from:
1. Its own folder and subfolders
2. Installed packages (via `requirements.txt`)
3. VIKTOR SDK modules

## The Solution: Vendoring

**Vendoring** means copying the core logic into the VIKTOR project folder. This allows VIKTOR to import the code locally while CLI/Web interfaces use the original source.

### Architecture Overview

```
src/cross_section/
├── core/                          # ← Source of truth (pure Python)
│   ├── geometry/
│   ├── domain/
│   └── validation/
│
└── interfaces/viktor/
    ├── app.py                     # VIKTOR app
    ├── viktor_adapter.py          # Core → VIKTOR geometry
    │
    └── vendor/                    # ← COPY of core/
        └── cross_section_core/    # Copied from ../../../core/
            ├── geometry/
            ├── domain/
            └── validation/
```

### Import Patterns

**In CLI/Web code:**
```python
# Import from original source
from cross_section.core.domain.components import TravelLane, Shoulder
from cross_section.core.domain.section import RoadSection
```

**In VIKTOR code:**
```python
# Import from vendored copy
from .vendor.cross_section_core.domain.components import TravelLane, Shoulder
from .vendor.cross_section_core.domain.section import RoadSection
```

## Why Pure Python Core?

The vendoring strategy **requires** the core to be pure Python with no external dependencies:

### ✅ What Can Go in Core

- Standard library imports (`math`, `dataclasses`, `typing`, `abc`, `enum`)
- Pure Python logic (calculations, validation, transformations)
- Data structures (Point2D, Polygon, ComponentGeometry)
- Business logic (road components, connection rules)

### ❌ What Cannot Go in Core

- External libraries (CadQuery, Shapely, NumPy, etc.)
- File I/O operations (handled by exporters)
- Library-specific geometry types
- Heavy dependencies

**Why?** If core had dependencies, we'd have to:
1. Install them in VIKTOR project (messy)
2. Vendor those libraries too (maintenance nightmare)
3. Deal with version conflicts

By keeping core pure Python, we can copy it anywhere without dependency issues.

## Sync Strategy

### Option 1: Manual Sync Script

```python
# scripts/sync_to_viktor.py
"""Sync core module to VIKTOR vendor folder"""
import shutil
from pathlib import Path

def sync_core_to_viktor():
    source = Path("src/cross_section/core")
    destination = Path("src/cross_section/interfaces/viktor/vendor/cross_section_core")

    # Remove old vendored copy
    if destination.exists():
        shutil.rmtree(destination)

    # Copy fresh core
    shutil.copytree(source, destination)

    print(f"✓ Synced {source} → {destination}")

if __name__ == "__main__":
    sync_core_to_viktor()
```

**Usage:**
```bash
python scripts/sync_to_viktor.py
```

### Option 2: Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Auto-sync core to VIKTOR vendor before every commit

python scripts/sync_to_viktor.py
git add src/cross_section/interfaces/viktor/vendor/
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

**Benefit:** Never forget to sync. Vendor is always up to date.

### Option 3: CI/CD Validation

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check VIKTOR vendor sync
        run: |
          python scripts/sync_to_viktor.py
          git diff --exit-code src/cross_section/interfaces/viktor/vendor/ || \
            (echo "❌ VIKTOR vendor out of sync. Run: python scripts/sync_to_viktor.py" && exit 1)

      - name: Run tests
        run: pytest
```

**Benefit:** CI fails if vendor is out of sync, preventing bugs.

## Development Workflow

### Typical Development Cycle

1. **Make changes to core:**
   ```bash
   vim src/cross_section/core/domain/components/lanes.py
   ```

2. **Sync to VIKTOR:**
   ```bash
   python scripts/sync_to_viktor.py
   ```

3. **Test changes:**
   ```bash
   # Test core directly
   pytest tests/unit/test_components.py

   # Test in VIKTOR (if VIKTOR installed)
   cd src/cross_section/interfaces/viktor
   viktor-cli start
   ```

4. **Commit both:**
   ```bash
   git add src/cross_section/core/
   git add src/cross_section/interfaces/viktor/vendor/
   git commit -m "Update lane component"
   ```

### With Pre-commit Hook

1. **Make changes:**
   ```bash
   vim src/cross_section/core/domain/components/lanes.py
   ```

2. **Commit (sync happens automatically):**
   ```bash
   git add src/cross_section/core/
   git commit -m "Update lane component"
   # Hook runs: sync_to_viktor.py
   # Hook auto-adds: vendor/ changes
   ```

3. **Push:**
   ```bash
   git push
   ```

## Version Control Considerations

### Should vendor/ be committed to git?

**✅ YES - Commit the vendored copy**

**Reasons:**
1. **Clarity:** Shows exactly what VIKTOR sees
2. **History:** Track changes to vendored code over time
3. **Deployment:** VIKTOR deployment gets correct version
4. **Review:** PRs show both source and vendored changes
5. **Safety:** No risk of source/vendor mismatch in production

**Trade-off:** Slight repo size increase, but worth it for correctness.

### .gitignore Considerations

```gitignore
# Don't ignore vendor folder (we want to track it)
# src/cross_section/interfaces/viktor/vendor/  # ← DO NOT ADD THIS

# Ignore Python cache in vendor
src/cross_section/interfaces/viktor/vendor/**/__pycache__/
src/cross_section/interfaces/viktor/vendor/**/*.pyc
```

## Testing Strategy

### Test Both Versions

```python
# tests/unit/test_core_import.py
"""Test that core can be imported both ways"""

def test_import_from_source():
    """Test importing from source (CLI/Web path)"""
    from cross_section.core.domain.components import TravelLane
    lane = TravelLane(width=3.6)
    assert lane.get_width() == 3.6

def test_import_from_vendor():
    """Test importing from vendor (VIKTOR path)"""
    from cross_section.interfaces.viktor.vendor.cross_section_core.domain.components import TravelLane
    lane = TravelLane(width=3.6)
    assert lane.get_width() == 3.6

def test_vendor_sync():
    """Test that vendor is in sync with source"""
    import filecmp
    from pathlib import Path

    source = Path("src/cross_section/core")
    vendor = Path("src/cross_section/interfaces/viktor/vendor/cross_section_core")

    # Compare directory trees
    comparison = filecmp.dircmp(source, vendor)

    assert len(comparison.left_only) == 0, f"Files in source but not vendor: {comparison.left_only}"
    assert len(comparison.right_only) == 0, f"Files in vendor but not source: {comparison.right_only}"
    assert len(comparison.diff_files) == 0, f"Files differ: {comparison.diff_files}"
```

### Integration Test

```python
# tests/integration/test_viktor_vendor.py
"""Test VIKTOR can use vendored core"""

def test_viktor_section_creation():
    """Test creating section using VIKTOR imports"""
    from cross_section.interfaces.viktor.vendor.cross_section_core.domain.components import TravelLane, Shoulder
    from cross_section.interfaces.viktor.vendor.cross_section_core.domain.section import RoadSection

    section = (RoadSection(name="Test")
        .add_component(Shoulder(width=2.4))
        .add_component(TravelLane(width=3.6))
        .add_component(Shoulder(width=2.4)))

    assert section.get_total_width() == 8.4

def test_viktor_adapter():
    """Test VIKTOR adapter works with vendored geometry"""
    from cross_section.interfaces.viktor.vendor.cross_section_core.domain.components import TravelLane
    from cross_section.interfaces.viktor.viktor_adapter import ViktorAdapter

    lane = TravelLane(width=3.6)
    geom = lane.to_geometry(start_x=0, elevation=0)

    # Convert to VIKTOR (adapter imports viktor module)
    viktor_polygons = ViktorAdapter.component_to_viktor(geom)

    assert len(viktor_polygons) > 0
```

## Troubleshooting

### Problem: Vendor out of sync

**Symptoms:**
- VIKTOR shows old behavior
- Tests pass but VIKTOR fails
- Git shows unexpected vendor changes

**Solution:**
```bash
python scripts/sync_to_viktor.py
git diff src/cross_section/interfaces/viktor/vendor/
# Review changes, then commit
```

### Problem: Import errors in VIKTOR

**Symptoms:**
```
ImportError: cannot import name 'TravelLane'
```

**Causes:**
1. Forgot to sync after core changes
2. Wrong import path (using source path instead of vendor)
3. Circular import

**Solution:**
```python
# ❌ Wrong (source path)
from cross_section.core.domain.components import TravelLane

# ✅ Correct (vendor path)
from .vendor.cross_section_core.domain.components import TravelLane
```

### Problem: Core has dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'shapely'
```

**Cause:** Accidentally added library import to core

**Solution:** Move library-dependent code to adapter:

```python
# ❌ In core/ - DON'T DO THIS
from shapely.geometry import Polygon

def validate_overlap(poly1, poly2):
    return poly1.intersects(poly2)

# ✅ In adapters/shapely_adapter.py - DO THIS
from shapely.geometry import Polygon as ShapelyPolygon
from ..core.geometry.primitives import Polygon

class ShapelyAdapter:
    @staticmethod
    def check_overlap(poly1: Polygon, poly2: Polygon) -> bool:
        sp1 = ShapelyAdapter.to_shapely(poly1)
        sp2 = ShapelyAdapter.to_shapely(poly2)
        return sp1.intersects(sp2)
```

## Benefits of This Approach

### ✅ Advantages

1. **VIKTOR Compatible:** Works within VIKTOR's constraints
2. **No Dependency Hell:** Core is pure Python, copies cleanly
3. **Version Control:** Vendor changes tracked in git
4. **Easy Testing:** Can test both import paths
5. **Clear Separation:** Core vs. library-specific code
6. **Portable:** Core can be used anywhere (CLI, Web, VIKTOR, future tools)
7. **Simple Sync:** One script keeps everything in sync

### ⚠️ Trade-offs

1. **Code Duplication:** Core exists in two places
2. **Sync Required:** Must remember to sync (mitigated by automation)
3. **Repo Size:** Slightly larger git repo
4. **Discipline Required:** Must keep core dependency-free

## Future Improvements

### Option: Python Package

If VIKTOR ever supports it, could publish core as separate package:

```toml
# pyproject.toml
[project]
name = "cross-section-core"
version = "0.1.0"
dependencies = []  # None! Pure Python
```

Then VIKTOR could install it:
```txt
# requirements.txt
cross-section-core==0.1.0
```

But for now, vendoring is the reliable approach.

### Option: Submodule

Could use git submodule for vendor/, but adds complexity:
- Harder to review in PRs
- Another git concept to learn
- Submodule pointer can get out of sync

Simple copy is better for this use case.

## Summary

**The vendoring strategy allows cross-section to:**
- Support VIKTOR's folder constraints
- Keep core logic dependency-free and portable
- Maintain a single source of truth (core/)
- Test both CLI/Web and VIKTOR paths
- Track vendor changes in version control

**Key principle:** Core is pure Python, adapters handle libraries. This makes vendoring trivial and reliable.
