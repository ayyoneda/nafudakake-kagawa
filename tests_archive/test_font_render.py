import os
from PySide6.QtGui import QGuiApplication, QFontDatabase, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication([])
fid = QFontDatabase.addApplicationFont('epgyobld.ttf')
fams = QFontDatabase.applicationFontFamilies(fid)
fam = fams[0]
print("Loaded family:", fam)

# Test 1: Stack with quotes and commas
svg_stack = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
<text x="10" y="50" font-size="36" font-family="'GyoshoKagawa', '{fam}', serif">洗心</text>
</svg>'''

# Test 2: Single exact family name without quotes
svg_single = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
<text x="10" y="50" font-size="36" font-family="{fam}">洗心</text>
</svg>'''

r1 = QSvgRenderer(svg_stack.encode('utf-8'))
img1 = QImage(200, 100, QImage.Format_ARGB32)
img1.fill(0xFFFFFFFF)
p1 = QPainter(img1)
r1.render(p1)
p1.end()
img1.save('test_stack.png')

r2 = QSvgRenderer(svg_single.encode('utf-8'))
img2 = QImage(200, 100, QImage.Format_ARGB32)
img2.fill(0xFFFFFFFF)
p2 = QPainter(img2)
r2.render(p2)
p2.end()
img2.save('test_single.png')

import hashlib
h1 = hashlib.md5(open('test_stack.png', 'rb').read()).hexdigest()
h2 = hashlib.md5(open('test_single.png', 'rb').read()).hexdigest()
print("Hash stack:", h1)
print("Hash single:", h2)
print("Are they different?", h1 != h2)
