"""Traffic symbols for cross-section annotations."""

from .library import SymbolLibrary

# Traffic arrow (default pointing up, rotate 180 for down)
SymbolLibrary.register(
    symbol_type="traffic_arrow",
    svg_path='''
        <g>
            <path d="M -5,-15 L 5,-15 L 5,0 L 9,0 L 0,15 L -9,0 L -5,0 Z"
                  fill="black" stroke="black" stroke-width="1"/>
        </g>
    ''',
    width=0.36,  # Path spans -9 to 9 = 18 units; 18/50 = 0.36m
    height=0.60,  # Path spans -15 to 15 = 30 units; 30/50 = 0.60m
    library="aashto"
)

# Lane designation marker (circle with number)
# Note: Number should be added via text annotation
SymbolLibrary.register(
    symbol_type="lane_marker",
    svg_path='''
        <g>
            <circle cx="0" cy="0" r="12" fill="white" stroke="black" stroke-width="2"/>
        </g>
    ''',
    width=0.5,
    height=0.5,
    library="aashto"
)
