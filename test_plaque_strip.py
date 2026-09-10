import os
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor, QFontDatabase
from PySide6.QtSvg import QSvgRenderer
import process_wood_textures

app = QGuiApplication.instance() or QGuiApplication([])
fid = QFontDatabase.addApplicationFont("epgyobld.ttf")
fams = QFontDatabase.applicationFontFamilies(fid)
qt_font_name = fams[0] if fams else "serif"

encoded_plaques, wall_b64, gaku_b64 = process_wood_textures.generate_plaque_variations(10)

svg_parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="240" viewBox="0 0 620 240">',
    '<defs>',
    f'<pattern id="wall-pat" width="200" height="200" patternUnits="userSpaceOnUse"><image href="data:image/jpeg;base64,{wall_b64}" width="200" height="200"/></pattern>'
]

for i, b64 in enumerate(encoded_plaques):
    svg_parts.append(
        f'<pattern id="wood-p-{i}" width="48" height="175" patternUnits="userSpaceOnUse">'
        f'<image href="data:image/jpeg;base64,{b64}" width="48" height="175" preserveAspectRatio="none"/>'
        f'</pattern>'
    )

svg_parts.append('</defs>')
svg_parts.append('<rect width="620" height="240" fill="url(#wall-pat)"/>')

# Desenha 10 plaquetas lado a lado
names = ["米田裕", "海老原", "深水", "石田", "小島", "丸井", "島田", "相子", "高山", "菅武朗"]
for i in range(10):
    x = 20 + i * (48 + 10)
    y = 30
    svg_parts.append(f'<g transform="translate({x}, {y})">')
    svg_parts.append(f'  <rect width="48" height="175" rx="3" fill="url(#wood-p-{i})"/>')
    # Chanfros sutis
    svg_parts.append(f'  <line x1="1" y1="1" x2="47" y2="1" stroke="#ffffff" stroke-width="1" opacity="0.6"/>')
    svg_parts.append(f'  <line x1="1" y1="1" x2="1" y2="174" stroke="#ffffff" stroke-width="0.8" opacity="0.4"/>')
    svg_parts.append(f'  <line x1="47" y1="1" x2="47" y2="174" stroke="#8b5e34" stroke-width="1" opacity="0.6"/>')
    svg_parts.append(f'  <line x1="1" y1="174" x2="47" y2="174" stroke="#684220" stroke-width="1.2" opacity="0.7"/>')
    # Kanji
    name = names[i % len(names)]
    for j, ch in enumerate(name):
        cy = 50 + j * 32
        svg_parts.append(f'  <text x="24" y="{cy}" font-family="{qt_font_name}, \'EPSON 行書体\', serif" font-size="20" fill="#15120e" font-weight="bold" text-anchor="middle">{ch}</text>')
    svg_parts.append('</g>')

svg_parts.append('</svg>')

with open("test_strip.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg_parts))

r = QSvgRenderer("test_strip.svg")
img = QImage(1240, 480, QImage.Format.Format_ARGB32)
img.fill(QColor(0, 0, 0, 0))
p = QPainter(img)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
r.render(p)
p.end()
img.save("test_strip.png", "PNG")
print("Saved test_strip.png successfully!")
