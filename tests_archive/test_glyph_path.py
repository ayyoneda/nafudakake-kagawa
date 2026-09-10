import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

font = TTFont("epgyobld.ttf")
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()
units_per_em = font['head'].unitsPerEm

def text_to_paths(text: str, font_size: float = 36.0, x: float = 0, y: float = 0, vertical: bool = True):
    scale = font_size / units_per_em
    paths = []
    current_x = x
    current_y = y
    
    for ch in text:
        code = ord(ch)
        gname = cmap.get(code)
        if not gname:
            continue
        pen = SVGPathPen(glyph_set)
        glyph = glyph_set[gname]
        glyph.draw(pen)
        d = pen.getCommands()
        if d:
            # TTF glyph coordinates have Y pointing up. SVG Y points down.
            # So transform is translate(current_x, current_y), scale(scale, -scale)
            # and adjust vertical offset
            transform = f"translate({current_x:.2f}, {current_y:.2f}) scale({scale:.5f}, {-scale:.5f})"
            paths.append(f'<path d="{d}" transform="{transform}" fill="#111"/>')
        
        if vertical:
            current_y += font_size * 1.15
        else:
            current_x += font_size * 1.05
            
    return "\n".join(paths)

svg_body = text_to_paths("洗心香武館", font_size=40, x=100, y=60, vertical=True)
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300">
<rect width="200" height="300" fill="#fdf6e7"/>
{svg_body}
</svg>"""

with open("test_glyph.svg", "w", encoding="utf-8") as f:
    f.write(svg)

app = QGuiApplication([])
r = QSvgRenderer("test_glyph.svg")
img = QImage(200, 300, QImage.Format_ARGB32)
img.fill(0xFFFFFFFF)
p = QPainter(img)
r.render(p)
p.end()
img.save("test_glyph.png")
print("SUCCESS: test_glyph.svg and test_glyph.png generated without any external font dependency!")
