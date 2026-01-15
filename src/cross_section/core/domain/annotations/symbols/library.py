"""Symbol library registry for annotation symbols."""

from typing import Any


class SymbolLibrary:
    """Registry of SVG symbol definitions.

    Symbols are referenced by type string (e.g., "traffic_arrow", "drainage_arrow").
    Each symbol has an SVG path definition, width, and height.
    """

    _symbols: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        symbol_type: str,
        svg_path: str,
        width: float,
        height: float,
        library: str = "default"
    ) -> None:
        """Register a symbol in the library.

        Args:
            symbol_type: Unique identifier for this symbol
            svg_path: SVG path or group element definition
            width: Symbol width in meters (for bounding box)
            height: Symbol height in meters
            library: Library name (e.g., "aashto", "caltrans")
        """
        cls._symbols[symbol_type] = {
            "svg_path": svg_path,
            "width": width,
            "height": height,
            "library": library,
        }

    @classmethod
    def get(cls, symbol_type: str) -> dict[str, Any]:
        """Get symbol definition by type.

        Args:
            symbol_type: Symbol type identifier

        Returns:
            Symbol definition dictionary

        Raises:
            KeyError: If symbol type not found
        """
        if symbol_type not in cls._symbols:
            raise KeyError(f"Symbol type '{symbol_type}' not found in library")

        return cls._symbols[symbol_type]

    @classmethod
    def list_symbols(cls, library: str | None = None) -> list[str]:
        """List all registered symbol types.

        Args:
            library: Optional library name to filter by

        Returns:
            List of symbol type identifiers
        """
        if library is None:
            return list(cls._symbols.keys())

        return [
            symbol_type
            for symbol_type, definition in cls._symbols.items()
            if definition.get("library") == library
        ]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered symbols.

        Useful for testing.
        """
        cls._symbols.clear()


# Register a simple test symbol for development
SymbolLibrary.register(
    symbol_type="test_circle",
    svg_path='<circle cx="0" cy="0" r="10" fill="blue" stroke="black"/>',
    width=0.5,
    height=0.5,
    library="test"
)
