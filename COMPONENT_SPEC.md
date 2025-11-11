# Component Specification

## Purpose

This document defines the detailed requirements for all road cross-section components based on civil engineering practice. It serves as the specification for implementing the component library in the core domain model.

## Component Hierarchy

```
RoadSection
├── ControlPoint (grade point/crown)
├── TraveledWay (collection of adjacent lanes)
│   ├── TravelLane
│   ├── TurnLane
│   └── BikeLane (when in roadway)
├── Shoulder
├── Barrier
├── Curb
├── Median (special case of Buffer)
├── Buffer (separation zones)
├── PedestrianFacility (sidewalk, path)
├── BicycleFacility (when separate from roadway)
├── RetainingWall
└── Slope (cut/fill)
```

---

## Core Concepts

### Control Point (Grade Point)

**Purpose:** Reference point for all other elements in the cross-section.

**Location:**
- Usually the crown on an undivided road
- Could be other strategic locations (median centerline, edge of traveled way, etc.)
- Always present in every section

**Properties:**
```python
@dataclass
class ControlPoint:
    """Reference point for cross-section geometry"""
    x: float = 0.0              # Horizontal position
    elevation: float = 0.0       # Vertical position (datum)
    location_type: str = "crown" # "crown", "median_cl", "edge_tw", "custom"
    description: str = ""        # Optional description
```

**Key Behaviors:**
- All other components positioned relative to control point
- Defines coordinate system origin
- Elevation reference for vertical geometry

---

## Pavement Components

### Pavement Structure

**Concept:** Pavement consists of one or more layers of materials.

**Layer Types:**
- Surface course (asphalt, concrete)
- Base course (aggregate, stabilized)
- Subbase
- Geotextile/separator layers

**Key Characteristics:**
- Layers may extend beyond component width (e.g., open shoulders)
- Unconfined layers have slump angles based on material
- Confined layers (between curbs) maintain shape

```python
@dataclass
class PavementLayer:
    """Individual pavement layer"""
    material: str               # "AC", "PCC", "aggregate_base", "subbase"
    thickness: float            # meters
    extends_beyond: bool = False  # Extends beyond component width?
    slump_angle: Optional[float] = None  # For unconfined materials (degrees)

@dataclass
class PavementStructure:
    """Multi-layer pavement definition"""
    layers: List[PavementLayer]

    def get_total_thickness(self) -> float:
        return sum(layer.thickness for layer in self.layers)
```

---

## Travel Lanes

**Purpose:** Primary component for vehicle traffic.

**Requirements:**
- Section MUST have one or more travel lanes
- Each lane has direction (up/down, approach/depart)
- Lanes usually have same direction on same side (but not required)
- Multiple adjacent lanes form a "traveled way"
- Section may have multiple traveled ways (e.g., freeway with mainline + ramps)

**Properties:**
```python
@dataclass
class TravelLane(RoadComponent):
    """Standard travel lane"""
    # Geometry
    width: float = 3.6              # meters (12 ft typical)
    cross_slope: float = 0.02       # decimal (2% typical)

    # Traffic
    direction: str = "forward"      # "forward", "reverse", "reversible"
    lane_type: str = "through"      # "through", "passing", "climbing", "auxiliary"

    # Pavement
    pavement: PavementStructure = field(default_factory=lambda: PavementStructure([
        PavementLayer(material="AC", thickness=0.15),      # 6" asphalt
        PavementLayer(material="aggregate_base", thickness=0.20)  # 8" base
    ]))

    # Traveled Way membership
    traveled_way_id: Optional[str] = None  # Groups lanes into traveled ways

    # Standards
    design_speed: Optional[int] = None  # km/h
```

**Key Behaviors:**
- Part of pavement structure (inherits layers)
- Cross-slope typically 2% for drainage
- Width varies by functional classification (3.0-3.7m typical)
- Can be part of multiple traveled ways in complex sections

**Validation Rules:**
- Width >= minimum for design classification
- Cross-slope within acceptable range (1.5% - 3%)
- Adjacent lanes in same traveled way typically same direction

---

## Shoulders

**Purpose:** Paved and/or earthwork areas at edge of traveled way.

**Characteristics:**
- Pavement layers may extend to edge or set distance
- Lower layers (aggregate base) may fill between upper pavement edge and shoulder edge
- Can be paved, gravel, or turf
- Provides recovery area and emergency stopping

**Properties:**
```python
@dataclass
class Shoulder(RoadComponent):
    """Shoulder at edge of traveled way"""
    # Geometry
    width: float = 2.4              # meters (8 ft typical)
    cross_slope: float = 0.04       # decimal (4% typical for drainage)

    # Surface type
    paved: bool = True              # Fully paved?
    paved_width: Optional[float] = None  # If partially paved
    surface_material: str = "asphalt"  # "asphalt", "concrete", "gravel", "turf"

    # Pavement structure
    pavement: Optional[PavementStructure] = None  # If paved
    base_extends: bool = True       # Does base extend full width?
    base_material: str = "aggregate_base"
    base_thickness: float = 0.15    # meters if base extends

    # Function
    shoulder_type: str = "outside"  # "outside", "inside", "median"

    def get_paved_width(self) -> float:
        """Return effective paved width"""
        if self.paved:
            return self.width
        return self.paved_width if self.paved_width else 0.0
```

**Pavement Extension Rules:**
1. **Full Paved**: All layers extend to shoulder edge
2. **Partial Paved**: Upper layers stop at `paved_width`, base extends full width
3. **Unpaved**: Only base/subbase extends (possibly with slump)

**Key Behaviors:**
- Higher cross-slope than lanes (typically 4% vs 2%)
- Inside shoulders (median side) often narrower than outside
- May transition to different material at outer edge

---

## Barriers

**Purpose:** Safety devices to redirect errant vehicles or prevent falls.

**Types:**
- Metal beam guardrail (W-beam, Thrie-beam)
- Cable barrier (low-tension, high-tension)
- Concrete barrier (various profiles)

**Standard Profiles:**
- Jersey Barrier (NJ shape)
- F-shape barrier
- Single-slope barrier
- Vertical wall barrier
- Texas (T-type) barrier

**Properties:**
```python
@dataclass
class Barrier(RoadComponent):
    """Safety barrier component"""
    # Identification
    barrier_type: str = "concrete"  # "concrete", "guardrail", "cable"
    profile_name: str = "jersey"    # "jersey", "f_shape", "single_slope", etc.

    # Geometry
    width: float = 0.6              # Base width (meters)
    height: float = 0.8             # Height (meters)

    # Profile definition (for concrete barriers)
    profile_points: Optional[List[Point2D]] = None  # Custom profile

    # For metal barriers
    post_spacing: Optional[float] = None  # meters
    rail_height: Optional[float] = None   # meters

    # Placement
    offset_from_edge: float = 0.6   # Lateral offset from traveled way edge
    mounting: str = "surface"        # "surface", "buried", "bridge"

    # Standards compliance
    test_level: str = "TL-4"        # MASH/NCHRP 350 test level

    @staticmethod
    def get_standard_profile(profile_name: str) -> List[Point2D]:
        """Return standard barrier profile coordinates"""
        # Implementation returns standard shapes
        pass
```

**Standard Profiles (relative to base):**

**Jersey Barrier (NJ):**
```
      0.81m (32")
        ___
       /   \
      /     \___  0.53m (21")
     /          \
    /____________\
    0.61m (24")
```

**F-Shape Barrier:**
```
      0.81m
        _
       / \
      /   \
     /     \___  0.33m
    /          \
   /____________\
   0.61m
```

**Properties:**
```python
STANDARD_PROFILES = {
    "jersey": [
        Point2D(0, 0),           # Base left
        Point2D(0.075, 0.075),   # 3" vertical
        Point2D(0.255, 0.53),    # 21" at 55° slope
        Point2D(0.355, 0.81),    # 32" at 84° slope
        Point2D(0.61, 0),        # Base right
    ],
    "f_shape": [
        Point2D(0, 0),
        Point2D(0.075, 0.25),    # Steeper initial slope
        Point2D(0.255, 0.33),    # Break point lower
        Point2D(0.355, 0.81),
        Point2D(0.61, 0),
    ],
    # ... other standard profiles
}
```

**Placement Rules:**
- Minimum offset from edge of traveled way (function of design speed)
- Behind curb if present
- At required clear zone if slope exceeds traversable limits

---

## Curbs

**Purpose:** Vertical or sloped elements that confine pavement.

**Types:**
- **Barrier curb**: Vertical face, prevents vehicle departure (150-200mm / 6-8")
- **Mountable curb**: Sloped face, allows occasional crossing (100mm / 4")
- **Ribbon curb**: Small vertical edge (50-75mm / 2-3")
- **Curb and gutter**: Combined curb + drainage channel

**Properties:**
```python
@dataclass
class Curb(RoadComponent):
    """Curb element (usually concrete)"""
    # Type and geometry
    curb_type: str = "barrier"      # "barrier", "mountable", "ribbon", "curb_gutter"
    width: float = 0.15             # Base width (meters)
    height: float = 0.15            # Total height (meters)
    face_angle: float = 90.0        # Face angle (degrees from horizontal)

    # Material
    material: str = "concrete"      # Almost always concrete

    # Gutter (if curb_gutter type)
    gutter_width: Optional[float] = None     # meters
    gutter_cross_slope: Optional[float] = None  # decimal

    # Attachment
    attached_to: str = "lane"       # "lane", "shoulder", "buffer"
    side: str = "right"             # Which side of attached component

    # Profile definition
    profile_points: List[Point2D] = field(default_factory=list)

    @staticmethod
    def get_standard_profile(curb_type: str, height: float) -> List[Point2D]:
        """Generate standard curb profile"""
        if curb_type == "barrier":
            # Vertical face
            return [
                Point2D(0, 0),
                Point2D(0, height),
                Point2D(0.15, height),
                Point2D(0.15, 0),
            ]
        elif curb_type == "mountable":
            # 1:1 slope (45°)
            return [
                Point2D(0, 0),
                Point2D(0.1, height),
                Point2D(0.15, height),
                Point2D(0.15, 0),
            ]
        # ... other types
```

**Curb & Gutter Profile:**
```
   Curb
    |___
    |   \___  Gutter
    |       \___________
   150mm  600mm typical
   (6")   (24")
```

**Key Behaviors:**
- Almost always concrete
- Usually attached to lanes
- Provides pavement confinement and drainage
- May be combined with gutter

**Connection Rules:**
- Curb LEFT side connects to lane (RAISED connection)
- Curb RIGHT side connects to sidewalk/buffer (RAISED connection)
- Height difference must be respected in geometry

---

## Median

**Purpose:** Special buffer separating opposing traffic flows.

**Types:**
- Painted (no physical separation)
- Raised (curbed or barrier)
- Depressed (drainage channel)
- Barrier-separated

**Properties:**
```python
@dataclass
class Median(RoadComponent):
    """Median separation between traveled ways"""
    # Geometry
    width: float = 4.0              # meters (minimum)

    # Type
    median_type: str = "raised"     # "painted", "raised", "depressed", "barrier"

    # If raised
    curb_height: Optional[float] = None     # meters
    has_barrier: bool = False
    barrier: Optional[Barrier] = None

    # If depressed
    depth: Optional[float] = None           # meters below grade
    side_slopes: Optional[float] = None     # H:V ratio

    # Surface
    surface_type: str = "concrete"  # "concrete", "asphalt", "grass", "gravel"
    pavement: Optional[PavementStructure] = None

    # Drainage
    has_drainage: bool = False

    def get_minimum_width_for_barrier(self, barrier_type: str) -> float:
        """Return minimum median width for barrier type"""
        # AASHTO minimums
        if barrier_type == "concrete":
            return 1.2  # 4 feet
        elif barrier_type == "guardrail":
            return 6.0  # 20 feet (with deflection)
        elif barrier_type == "cable":
            return 9.0  # 30 feet (with deflection)
        return self.width
```

**Median Width Requirements (AASHTO):**
- Absolute minimum: 1.2m (4 ft) with concrete barrier
- Desirable minimum: 9m (30 ft) for cable barrier deflection
- Preferred: 12-18m (40-60 ft) for recovery

**Key Behaviors:**
- Separates opposing traffic
- May contain drainage
- Width affects barrier type selection
- Can contain landscape elements

---

## Buffer

**Purpose:** Separation zones between components (general case of median).

**Properties:**
```python
@dataclass
class Buffer(RoadComponent):
    """General separation zone"""
    # Geometry
    width: float = 2.0              # meters

    # Type
    buffer_type: str = "earthwork"  # "earthwork", "pavement", "landscape"

    # If paved
    pavement: Optional[PavementStructure] = None

    # If earthwork
    slope: Optional[float] = None   # H:V ratio if sloped
    material: str = "topsoil"       # "topsoil", "gravel", "mulch"

    # Purpose
    separates: tuple[str, str] = ("lane", "sidewalk")  # What it separates
```

**Common Uses:**
- Between bike lane and parking
- Between sidewalk and roadway (planting strip)
- Between traveled way and pedestrian facilities
- Utility corridor

---

## Pedestrian Facilities

**Purpose:** Facilities for pedestrian traffic.

**Types:**
- Sidewalk (most common)
- Shared use path
- Boardwalk

**Properties:**
```python
@dataclass
class Sidewalk(RoadComponent):
    """Pedestrian facility (sidewalk, path)"""
    # Geometry
    width: float = 1.5              # meters (5 ft minimum)
    cross_slope: float = 0.02       # 2% max for ADA

    # Pavement structure
    pavement: PavementStructure = field(default_factory=lambda: PavementStructure([
        PavementLayer(material="concrete", thickness=0.1),  # 4" typical
        PavementLayer(material="aggregate_base", thickness=0.1)
    ]))

    # Material
    surface_material: str = "concrete"  # "concrete", "asphalt", "paver"

    # ADA compliance
    ada_compliant: bool = True
    max_cross_slope: float = 0.02   # 2% maximum
    max_running_slope: float = 0.05  # 5% maximum (else it's a ramp)

    # Connection to roadway
    has_curb: bool = True           # Usually separated by curb
    buffer_width: Optional[float] = None  # Planting strip if present

    def validate_ada(self) -> List[str]:
        """Check ADA compliance"""
        errors = []
        if self.width < 1.5:
            errors.append(f"Width {self.width}m < 1.5m minimum")
        if self.cross_slope > 0.02:
            errors.append(f"Cross-slope {self.cross_slope} > 2% maximum")
        return errors
```

**ADA Requirements:**
- Minimum width: 1.5m (5 ft), 1.8m (6 ft) preferred
- Maximum cross-slope: 2%
- Maximum running slope: 5% (steeper = ramp with additional requirements)
- Surface must be firm, stable, slip-resistant

---

## Bicycle Facilities

**Purpose:** Facilities dedicated to bicycle traffic.

**Types:**
- Bike lane (part of roadway)
- Separated bike lane (barrier protected)
- Shared use path (bikes + pedestrians)
- Cycle track

**Properties:**
```python
@dataclass
class BikeLane(RoadComponent):
    """Bicycle facility"""
    # Geometry
    width: float = 1.5              # meters (5 ft minimum)
    cross_slope: float = 0.02       # Same as adjacent roadway typically

    # Type
    facility_type: str = "lane"     # "lane", "separated", "cycle_track", "shared_path"

    # Location
    in_roadway: bool = True         # Part of traveled way?
    direction: str = "with_traffic" # "with_traffic", "contra_flow", "bidirectional"

    # Separation
    separated: bool = False
    buffer_width: Optional[float] = None
    has_barrier: bool = False

    # Pavement
    pavement: Optional[PavementStructure] = None  # If in roadway, shares structure
    surface_material: str = "asphalt"

    # Markings
    has_markings: bool = True       # Bike lane symbols, etc.
```

**Design Requirements (AASHTO):**
- Minimum width: 1.2m (4 ft) on-road, 1.5m (5 ft) separated
- Preferred width: 1.8m (6 ft) for comfort
- Buffer if adjacent to parking: 0.5m (18") minimum
- Protected/separated: 2.4-3.0m (8-10 ft) including buffer

---

## Retaining Walls

**Purpose:** Vertical or near-vertical structures to retain earth.

**Types:**
- Gravity wall
- Cantilever wall
- MSE (Mechanically Stabilized Earth) wall
- Soldier pile wall
- Sheet pile wall

**Properties:**
```python
@dataclass
class RetainingWall(RoadComponent):
    """Retaining wall (simplified for typical sections)"""
    # Type
    wall_type: str = "mse"          # "gravity", "cantilever", "mse", "soldier_pile"

    # Geometry (simplified - not fully defined on typical sections)
    height: float = 3.0             # Exposed height (meters)
    width: float = 0.3              # Face width/thickness
    batter: float = 0.0             # Face angle from vertical (degrees)

    # Material
    facing_material: str = "concrete"  # "concrete", "modular_block", "cip"

    # Placement
    location: str = "behind_slope"  # "behind_slope", "toe_slope", "independent"

    # Note: Full structural design is separate from typical section
    notes: str = "See retaining wall details"

    def get_width(self) -> float:
        """Return width for cross-section geometry"""
        # Usually shown as simple vertical line
        return self.width
```

**Key Characteristics:**
- Usually NOT fully defined on typical sections
- Shown as vertical line or simplified face
- Actual design is in separate structural drawings
- May affect slope geometry

---

## Slopes

**Purpose:** Earthwork transitions from roadway to existing ground.

**Types:**
- Cut slope (excavation, usually steeper)
- Fill slope (embankment, usually flatter)
- Combination (cut/fill transition)

**Characteristics:**
- Dimensions depend on location and existing conditions
- Usually simple shapes defined by H:V ratio
- May have benches or terraces for stability
- Slope ratio depends on material and stability

**Properties:**
```python
@dataclass
class CutSlope(RoadComponent):
    """Cut slope (excavation)"""
    # Slope ratio
    horizontal_ratio: float = 2.0   # Horizontal component
    vertical_ratio: float = 1.0     # Vertical component (2H:1V = 2:1)

    # Vertical extent
    height: float = 3.0             # Vertical distance (meters)

    # Material
    material: str = "soil"          # "soil", "rock", "weathered_rock"

    # Rounding
    top_rounding: float = 1.0       # Radius at top (meters)
    bottom_rounding: float = 0.5    # Radius at toe

    # Benches (for high slopes)
    has_benches: bool = False
    bench_interval: Optional[float] = None  # Vertical spacing
    bench_width: Optional[float] = None

    # Traversability
    def is_traversable(self, max_ratio: float = 4.0) -> bool:
        """Check if slope is traversable (4:1 typical max)"""
        ratio = self.horizontal_ratio / self.vertical_ratio
        return ratio >= max_ratio

    def requires_barrier(self, max_ratio: float = 4.0) -> bool:
        """Check if barrier required due to steep slope"""
        return not self.is_traversable(max_ratio)

    def get_width(self) -> float:
        """Calculate horizontal extent"""
        return abs(self.height * self.horizontal_ratio / self.vertical_ratio)

@dataclass
class FillSlope(RoadComponent):
    """Fill slope (embankment)"""
    # Same structure as CutSlope
    horizontal_ratio: float = 2.0
    vertical_ratio: float = 1.0
    height: float = 3.0
    material: str = "compacted_fill"

    # Compaction
    compaction_requirement: str = "95% standard Proctor"

    # Similar methods...
```

**Typical Slope Ratios:**

| Material | Cut Slope | Fill Slope |
|----------|-----------|------------|
| Soil | 2:1 to 3:1 | 2:1 to 3:1 |
| Rock | 1:1 to 0.5:1 | N/A |
| Compacted Fill | N/A | 2:1 to 3:1 |

**Traversable Clear Zone:**
- Maximum slope: 4:1 (4H:1V) or flatter
- Steeper slopes require barrier protection

**Key Behaviors:**
- Width calculated from height and ratio
- Top/toe rounding for realistic geometry
- Traversability affects barrier requirements

---

## Component Relationships

### Geometric Connection Model

Components connect through **insertion points** and **attachment points** rather than categorical connection types. Each component:

1. Has an **insertion point** - where it connects to the previous component (snaps to previous attachment point)
2. Has an **attachment point** - where the next component connects to it (defined by geometry)

Components naturally "snap together" with geometry determining elevation changes, slopes, etc.

**See [ARCHITECTURE.md](ARCHITECTURE.md) for complete architectural specification.**

**Key Principles:**
- **Control Point**: Provides initial attachment point (usually at crown, edge of traveled way)
- **Snap-Together**: Insertion points snap to attachment points forming continuous chain
- **Natural Geometry**: Vertical offsets (curbs), slopes, and transitions emerge from component geometry
- **Rare Exceptions**: Components can offset their insertion point if needed (e.g., barrier with lateral offset)

**Example:**
```
Control Point (crown at elevation 0)
    ↓ attachment: (0, 0)
Lane 1 inserts at (0, 0)
    ↓ attachment: (3.6, -0.072) [3.6m wide, 2% cross-slope]
Lane 2 inserts at (3.6, -0.072)
    ↓ attachment: (7.2, -0.144)
Shoulder inserts at (7.2, -0.144)
    ↓ attachment: (9.6, -0.240) [2.4m wide, 4% cross-slope]
Slope inserts at toe (9.6, -0.240)
    ↓ attachment: (14.6, -3.240) [2:1 slope, 3m drop]
```

All connections are geometric - no categorical types needed!

### Typical Sequences

**Rural Highway:**
```
FillSlope → Shoulder → Lane → Lane → Shoulder → FillSlope
```

**Urban Arterial:**
```
Sidewalk → Curb → ParkingLane → Lane → Lane → Median (with barrier) → Lane → Lane → ParkingLane → Curb → Sidewalk
```

**Freeway:**
```
CutSlope → Barrier → Shoulder → Lane → Lane → Lane → Shoulder → Median → Shoulder → Lane → Lane → Lane → Shoulder → Barrier → FillSlope
```

---

## Implementation Notes

### Phase 1 Components (Core)
- TravelLane
- Shoulder
- Curb (basic)
- Simple slopes

### Phase 2 Components (Extended)
- Barrier (with standard profiles)
- Median
- Buffer
- Sidewalk

### Phase 3 Components (Advanced)
- BikeLane
- RetainingWall
- Complex curb profiles
- Benched slopes

### Component Features

Each component must implement:
1. **Geometry generation** (`to_geometry()`) - pure Python
2. **Connection interfaces** - define how it connects to neighbors
3. **Validation** - check dimensions, materials, standards
4. **Default values** - sensible defaults based on practice

### Material Library

Maintain library of materials with properties:
```python
MATERIALS = {
    "AC": {  # Asphalt concrete
        "name": "Asphalt Concrete",
        "slump_angle": 45,  # degrees
        "typical_thickness": 0.15,  # meters
        "confined": False,
    },
    "PCC": {  # Portland cement concrete
        "name": "Portland Cement Concrete",
        "slump_angle": None,  # Confined
        "typical_thickness": 0.20,
        "confined": True,
    },
    "aggregate_base": {
        "name": "Aggregate Base",
        "slump_angle": 37,  # 3:4 typical
        "typical_thickness": 0.20,
        "confined": False,
    },
    # ... more materials
}
```

---

## Standards References

### AASHTO Green Book
- Geometric design standards
- Lane widths, shoulder widths
- Clear zone requirements

### AASHTO Roadside Design Guide
- Barrier warrants
- Slope traversability
- Clear zone analysis

### MUTCD (Manual on Uniform Traffic Control Devices)
- Lane markings
- Bike lane designations

### ADA Standards
- Sidewalk requirements
- Maximum slopes
- Minimum widths

### State DOT Standards
- Jurisdiction-specific requirements
- Standard cross-sections
- Material specifications

---

## Future Enhancements

### Advanced Features
- **Pavement layer extension logic** - Complex rules for how layers extend
- **Superelevation** - Banking in curves
- **Variable width components** - Tapers and transitions
- **3D extrusion** - Along horizontal alignment
- **Quantity calculations** - Earthwork, pavement volumes

### Analysis Integration
- **Cost estimation** - Material quantities × unit prices
- **Drainage analysis** - Gutter flow, inlet spacing
- **ADA compliance** - Automated checking
- **Clear zone analysis** - Sight distance, obstacles

---

## Testing Strategy

Each component type should have:

### Unit Tests
```python
def test_travel_lane_geometry():
    """Test lane geometry generation"""
    lane = TravelLane(width=3.6, cross_slope=0.02)
    geom = lane.to_geometry(start_x=0, elevation=0)

    assert len(geom.polygons) == 1
    assert geom.polygons[0].bounds()[2] == 3.6  # Width correct

def test_curb_connection_interface():
    """Test curb provides raised connection"""
    curb = Curb(height=0.15)
    left_conn = curb.get_connection_interface(ConnectionSide.LEFT)

    assert left_conn.connection_type == ConnectionType.RAISED
    assert left_conn.elevation == 0.15

def test_slope_traversability():
    """Test slope traversability logic"""
    gentle_slope = FillSlope(h_ratio=4, v_ratio=1)
    steep_slope = FillSlope(h_ratio=2, v_ratio=1)

    assert gentle_slope.is_traversable()
    assert not steep_slope.is_traversable()
    assert steep_slope.requires_barrier()
```

### Integration Tests
```python
def test_urban_section_assembly():
    """Test complete urban section"""
    section = RoadSection()
    section.add_component(Sidewalk(width=1.8))
    section.add_component(Curb(height=0.15))
    section.add_component(ParkingLane(width=2.4))
    section.add_component(TravelLane(width=3.3))
    section.add_component(TravelLane(width=3.3))
    section.add_component(ParkingLane(width=2.4))
    section.add_component(Curb(height=0.15))
    section.add_component(Sidewalk(width=1.8))

    errors = section.validate_connections()
    assert len(errors) == 0

    geom = section.to_geometry()
    assert geom.get_total_width() == pytest.approx(17.4)
```

---

## Summary

This specification defines 11 major component types:

1. **ControlPoint** - Reference for all measurements
2. **TravelLane** - Primary traffic lanes
3. **Shoulder** - Edge of traveled way
4. **Barrier** - Safety barriers (complex profiles)
5. **Curb** - Pavement confinement
6. **Median** - Separation between opposing traffic
7. **Buffer** - General separation zones
8. **Sidewalk** - Pedestrian facilities
9. **BikeLane** - Bicycle facilities
10. **RetainingWall** - Simplified representation
11. **Slope** - Cut/fill earthwork

Each component has:
- Detailed geometric properties
- Material/structural properties
- Connection interfaces
- Validation rules
- Standard defaults

This forms the foundation for Phase 1 implementation of the core domain model.
