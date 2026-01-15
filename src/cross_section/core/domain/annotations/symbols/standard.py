"""Standard geometric marks for cross-section annotations."""

from .library import SymbolLibrary

# Centerpoint mark (circle with crosshairs)
SymbolLibrary.register(
    symbol_type="centerpoint",
    svg_path='''
        <g>
            <circle cx="0" cy="0" r="8" fill="none" stroke="black" stroke-width="1.5"/>
            <line x1="-12" y1="0" x2="12" y2="0" stroke="black" stroke-width="1"/>
            <line x1="0" y1="-12" x2="0" y2="12" stroke="black" stroke-width="1"/>
        </g>
    ''',
    width=0.3,
    height=0.3,
    library="aashto"
)

# Grade point / control point mark
SymbolLibrary.register(
    symbol_type="grade_point",
    svg_path='''
        <g>
            <circle cx="0" cy="0" r="6" fill="black" stroke="black" stroke-width="1"/>
            <circle cx="0" cy="0" r="10" fill="none" stroke="black" stroke-width="1.5"/>
        </g>
    ''',
    width=0.25,
    height=0.25,
    library="aashto"
)

# Station mark (for offset stations)
SymbolLibrary.register(
    symbol_type="station_mark",
    svg_path='''
        <g>
            <line x1="0" y1="-15" x2="0" y2="15" stroke="black" stroke-width="2"/>
            <line x1="-8" y1="-10" x2="8" y2="-10" stroke="black" stroke-width="1.5"/>
            <line x1="-8" y1="10" x2="8" y2="10" stroke="black" stroke-width="1.5"/>
        </g>
    ''',
    width=0.2,
    height=0.6,
    library="aashto"
)

# Elevation mark (benchmark)
SymbolLibrary.register(
    symbol_type="elevation_mark",
    svg_path='''
        <g>
            <path d="M -10,10 L 0,-10 L 10,10 Z"
                  fill="none" stroke="black" stroke-width="2"/>
            <line x1="-12" y1="10" x2="12" y2="10" stroke="black" stroke-width="2"/>
        </g>
    ''',
    width=0.3,
    height=0.4,
    library="aashto"
)

# Section cut mark
SymbolLibrary.register(
    symbol_type="section_cut",
    svg_path='''
        <g>
            <line x1="-15" y1="0" x2="15" y2="0" stroke="black" stroke-width="2.5"/>
            <path d="M 15,-6 L 15,6 L 22,0 Z" fill="black"/>
            <path d="M -15,-6 L -15,6 L -22,0 Z" fill="black"/>
        </g>
    ''',
    width=0.9,
    height=0.3,
    library="aashto"
)
