import os
import sys
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor, QFontDatabase
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication.instance() or QGuiApplication([])
fid = QFontDatabase.addApplicationFont("epgyobld.ttf")
fams = QFontDatabase.applicationFontFamilies(fid)
print("Qt loaded families:", fams)
fam_name = fams[0] if fams else "serif"

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
<rect width="400" height="300" fill="#fdf6e7"/>
<g font-size="36" font-family="{fam_name}" fill="#111" text-anchor="middle">
  <text x="200" y="80">洗心香武館</text>
  <text x="200" y="160">海老原忠雄</text>
  <text x="200" y="240">米田裕</text>
</g>
</svg>"""

with open("test_gyosho.svg", "w", encoding="utf-8") as f:
    f.write(svg)

r = QSvgRenderer("test_gyosho.svg")
img = QImage(400, 300, QImage.Format.Format_ARGB32)
img.fill(QColor(255, 255, 255))
p = QPainter(img)
r.render(p)
p.end()
img.save("test_gyosho.png", "PNG")
print("test_gyosho.png saved successfully!")
