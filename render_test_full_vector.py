from test_full_vectorizer import GlyphVectorizer
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

v = GlyphVectorizer("epgyobld.ttf")
h_paths = v.render_horizontal_text("洗心香武館", 200, 60, 38, "#161009", letter_spacing=12)
v_paths1 = v.render_vertical_text("蛯原忠雄", 70, 130, 30, 24, "#141414")
v_paths2 = v.render_vertical_text("米田裕", 150, 130, 32, 24, "#141414")
v_paths3 = v.render_vertical_text("ムゼッティ・エドゥアルド", 260, 115, 18, 15, "#141414")
shogo_paths = v.render_horizontal_text("教士", 70, 110, 12, "#9e1e1e", letter_spacing=2)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="320" viewBox="0 0 400 320">
<rect width="400" height="320" fill="#fdf6e7"/>
{h_paths}
{v_paths1}
{v_paths2}
{v_paths3}
{shogo_paths}
</svg>"""

with open("test_full_vector.svg", "w", encoding="utf-8") as f:
    f.write(svg)

app = QGuiApplication([])
r = QSvgRenderer("test_full_vector.svg")
img = QImage(400, 320, QImage.Format_ARGB32)
img.fill(0xFFFFFFFF)
p = QPainter(img)
r.render(p)
p.end()
img.save("test_full_vector.png")
print("Rendered test_full_vector.png successfully!")
