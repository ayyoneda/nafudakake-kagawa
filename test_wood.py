import os
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication([])
svg = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
<defs>
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.05 0.005" numOctaves="3" result="noise"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.9  0 0 0 0 0.8  0 0 0 0 0.7  0 0 0 1 0"/>
  </filter>
  <linearGradient id="placa-grad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#dfc49f"/>
    <stop offset="15%" stop-color="#f5e1c8"/>
    <stop offset="50%" stop-color="#fff2df"/>
    <stop offset="85%" stop-color="#f2dcbf"/>
    <stop offset="100%" stop-color="#d6b992"/>
  </linearGradient>
  <!-- Textura procedural vetorial com linhas de veios de madeira -->
  <pattern id="wood-stripes" width="48" height="60" patternUnits="userSpaceOnUse">
    <line x1="4" y1="0" x2="5" y2="60" stroke="#c49a6c" stroke-width="0.75" opacity="0.35"/>
    <line x1="12" y1="0" x2="11" y2="60" stroke="#d8b284" stroke-width="0.5" opacity="0.4"/>
    <line x1="22" y1="0" x2="23" y2="60" stroke="#b88b58" stroke-width="0.8" opacity="0.3"/>
    <line x1="33" y1="0" x2="32" y2="60" stroke="#cfa777" stroke-width="0.6" opacity="0.35"/>
    <line x1="42" y1="0" x2="43" y2="60" stroke="#b08350" stroke-width="0.7" opacity="0.25"/>
  </pattern>
</defs>
<rect width="200" height="200" fill="url(#placa-grad)"/>
<rect width="200" height="200" fill="url(#wood-stripes)"/>
</svg>"""

with open("test_wood.svg", "w", encoding="utf-8") as f:
    f.write(svg)

r = QSvgRenderer("test_wood.svg")
print("Renderer valid:", r.isValid())
img = QImage(200, 200, QImage.Format.Format_ARGB32)
img.fill(QColor(255, 255, 255))
p = QPainter(img)
r.render(p)
p.end()
img.save("test_wood.png")
print("Saved test_wood.png")
