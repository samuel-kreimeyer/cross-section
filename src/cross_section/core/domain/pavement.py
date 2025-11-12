"""Pavement layer components."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AsphaltLayer:
    """Asphalt concrete pavement layer.

    Attributes:
        thickness: Layer thickness in meters
        aggregate_size: Maximum aggregate size in mm
        binder_type: Type of asphalt binder (e.g., 'PG 64-22', 'PG 70-28')
        binder_percentage: Binder content as percentage by weight
        density: Compacted density in kg/m³
    """
    thickness: float
    aggregate_size: float  # mm
    binder_type: str
    binder_percentage: float  # percentage (e.g., 5.5 for 5.5%)
    density: float  # kg/m³

    def validate(self) -> list[str]:
        """Validate asphalt layer parameters."""
        errors = []

        if self.thickness <= 0:
            errors.append(f"Asphalt layer thickness must be positive (got {self.thickness}m)")
        elif self.thickness < 0.04:
            errors.append(f"Asphalt layer thickness {self.thickness}m is very thin - typical minimum is 40mm")
        elif self.thickness > 0.15:
            errors.append(f"Asphalt layer thickness {self.thickness}m exceeds typical single lift maximum (150mm)")

        if self.aggregate_size <= 0:
            errors.append(f"Aggregate size must be positive (got {self.aggregate_size}mm)")
        elif self.aggregate_size > 37.5:
            errors.append(f"Aggregate size {self.aggregate_size}mm exceeds typical maximum (37.5mm)")

        if self.binder_percentage < 4.0 or self.binder_percentage > 7.0:
            errors.append(f"Binder percentage {self.binder_percentage}% outside typical range (4-7%)")

        if self.density < 2200 or self.density > 2500:
            errors.append(f"Density {self.density} kg/m³ outside typical range (2200-2500 kg/m³)")

        return errors


@dataclass
class ConcreteLayer:
    """Portland cement concrete pavement layer.

    Attributes:
        thickness: Layer thickness in meters
        compressive_strength: 28-day compressive strength in MPa
        reinforced: Whether the layer contains steel reinforcement
        steel_per_cy: Pounds of steel per cubic yard (only if reinforced)
    """
    thickness: float
    compressive_strength: float  # MPa
    reinforced: bool = False
    steel_per_cy: Optional[float] = None  # lbs/cy³

    def validate(self) -> list[str]:
        """Validate concrete layer parameters."""
        errors = []

        if self.thickness <= 0:
            errors.append(f"Concrete layer thickness must be positive (got {self.thickness}m)")
        elif self.thickness < 0.15:
            errors.append(f"Concrete layer thickness {self.thickness}m below typical minimum (150mm)")
        elif self.thickness > 0.40:
            errors.append(f"Concrete layer thickness {self.thickness}m exceeds typical maximum (400mm)")

        if self.compressive_strength < 20:
            errors.append(f"Compressive strength {self.compressive_strength} MPa below minimum for pavement (20 MPa)")
        elif self.compressive_strength > 50:
            errors.append(f"Compressive strength {self.compressive_strength} MPa is unusually high - verify design")

        if self.reinforced and self.steel_per_cy is None:
            errors.append("Reinforced concrete must specify steel_per_cy")
        elif self.reinforced and self.steel_per_cy is not None:
            if self.steel_per_cy < 20 or self.steel_per_cy > 100:
                errors.append(f"Steel reinforcement {self.steel_per_cy} lbs/cy³ outside typical range (20-100 lbs/cy³)")
        elif not self.reinforced and self.steel_per_cy is not None:
            errors.append("steel_per_cy should only be specified for reinforced concrete")

        return errors


@dataclass
class CrushedRockLayer:
    """Crushed rock base or subbase layer.

    Attributes:
        thickness: Layer thickness in meters
        aggregate_size: Maximum aggregate size in mm
        density: Compacted density in kg/m³
        material_type: Type of material (e.g., 'crushed_stone', 'recycled_concrete')
    """
    thickness: float
    aggregate_size: float  # mm
    density: float  # kg/m³
    material_type: str = 'crushed_stone'

    def validate(self) -> list[str]:
        """Validate crushed rock layer parameters."""
        errors = []

        if self.thickness <= 0:
            errors.append(f"Crushed rock layer thickness must be positive (got {self.thickness}m)")
        elif self.thickness < 0.10:
            errors.append(f"Crushed rock layer thickness {self.thickness}m below typical minimum (100mm)")
        elif self.thickness > 0.60:
            errors.append(f"Crushed rock layer thickness {self.thickness}m exceeds typical maximum (600mm)")

        if self.aggregate_size <= 0:
            errors.append(f"Aggregate size must be positive (got {self.aggregate_size}mm)")
        elif self.aggregate_size < 19:
            errors.append(f"Aggregate size {self.aggregate_size}mm is small for base course (typical min 19mm)")
        elif self.aggregate_size > 63:
            errors.append(f"Aggregate size {self.aggregate_size}mm exceeds typical maximum (63mm)")

        if self.density < 1800 or self.density > 2400:
            errors.append(f"Density {self.density} kg/m³ outside typical range (1800-2400 kg/m³)")

        return errors


# Type alias for any pavement layer
PavementLayer = AsphaltLayer | ConcreteLayer | CrushedRockLayer
