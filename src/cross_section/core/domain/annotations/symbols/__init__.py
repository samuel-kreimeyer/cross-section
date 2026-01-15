"""Symbol library for annotation system."""

# Import symbol modules to register symbols
from . import drainage, standard, traffic  # noqa: F401
from .library import SymbolLibrary

__all__ = ["SymbolLibrary"]
