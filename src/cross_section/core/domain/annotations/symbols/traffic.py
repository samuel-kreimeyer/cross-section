"""Traffic symbols for cross-section annotations."""

from .library import SymbolLibrary

# Traffic arrow (default pointing right, rotate 180 for left)
SymbolLibrary.register(
    symbol_type="traffic_arrow",
    svg_path='''
        <g>
            <path d="M -15,0 L 10,0 L 10,-8 L 20,0 L 10,8 L 10,0 Z"
                  fill="black" stroke="black" stroke-width="1"/>
        </g>
    ''',
    width=0.7,  # 700mm
    height=0.4,  # 400mm
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
