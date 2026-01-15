"""Drainage and slope symbols for cross-section annotations."""

from .library import SymbolLibrary

# Drainage arrow (smaller than traffic arrow, points downslope)
# Note: "SLOPE" text removed - add separately as TextAnnotation to avoid rotation issues
SymbolLibrary.register(
    symbol_type="drainage_arrow",
    svg_path='''
        <g>
            <path d="M -10,0 L 8,0 L 8,-5 L 15,0 L 8,5 L 8,0 Z"
                  fill="black" stroke="black" stroke-width="0.75"/>
        </g>
    ''',
    width=0.4,  # 400mm (reduced since no text)
    height=0.2,  # 200mm
    library="aashto"
)

# Drainage inlet symbol
SymbolLibrary.register(
    symbol_type="drainage_inlet",
    svg_path='''
        <g>
            <rect x="-8" y="-8" width="16" height="16"
                  fill="white" stroke="black" stroke-width="1.5"/>
            <line x1="-8" y1="-8" x2="8" y2="8" stroke="black" stroke-width="1"/>
            <line x1="-8" y1="8" x2="8" y2="-8" stroke="black" stroke-width="1"/>
        </g>
    ''',
    width=0.4,
    height=0.4,
    library="aashto"
)

# Water flow direction arrow (for ditches)
SymbolLibrary.register(
    symbol_type="flow_arrow",
    svg_path='''
        <g>
            <path d="M -12,0 L 5,0 M 0,-5 L 5,0 L 0,5"
                  fill="none" stroke="blue" stroke-width="1.5"/>
        </g>
    ''',
    width=0.4,
    height=0.25,
    library="aashto"
)
