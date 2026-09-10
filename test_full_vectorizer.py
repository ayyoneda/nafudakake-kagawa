import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

class GlyphVectorizer:
    def __init__(self, font_path: str = "epgyobld.ttf"):
        self.font = TTFont(font_path)
        self.glyph_set = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.units_per_em = self.font['head'].unitsPerEm
        self.hmetrics = self.font['hmtx'].metrics
        self._path_cache = {}

    def get_glyph_info(self, char: str):
        if char in self._path_cache:
            return self._path_cache[char]
            
        code = ord(char)
        gname = self.cmap.get(code)
        if not gname:
            return None
                
        pen = SVGPathPen(self.glyph_set)
        glyph = self.glyph_set[gname]
        glyph.draw(pen)
        d = pen.getCommands()
        adv_width, lsb = self.hmetrics.get(gname, (self.units_per_em, 0))
        res = (d, adv_width)
        self._path_cache[char] = res
        return res

    def render_horizontal_text(self, text: str, cx: float, cy: float, font_size: float, fill: str = "#141414", letter_spacing: float = 0.0) -> str:
        scale = font_size / self.units_per_em
        char_infos = []
        total_width = 0.0
        
        for ch in text:
            info = self.get_glyph_info(ch)
            if info:
                d, adv = info
                w = adv * scale
                char_infos.append((d, w, ch))
                total_width += w
            elif ch in (' ', '　'):
                w = font_size * 0.5
                char_infos.append((None, w, ch))
                total_width += w

        if not char_infos:
            return ""

        total_width += max(0, len(char_infos) - 1) * letter_spacing
        cur_x = cx - (total_width / 2.0)
        paths = []
        
        for d, w, ch in char_infos:
            if d:
                transform = f"translate({cur_x:.2f}, {cy:.2f}) scale({scale:.5f}, {-scale:.5f})"
                paths.append(f'<path d="{d}" transform="{transform}" fill="{fill}"/>')
            cur_x += w + letter_spacing
            
        return "".join(paths)

    def render_vertical_text(self, text: str, cx: float, start_y: float, step_y: float, font_size: float, fill: str = "#141414") -> str:
        scale = font_size / self.units_per_em
        paths = []
        current_y = start_y
        
        for ch in text:
            if ch in (' ', '　', '\t'):
                current_y += step_y * 0.5
                continue
            if ch == '・':
                # Ponto médio estilizado
                paths.append(f'<circle cx="{cx:.2f}" cy="{current_y - (font_size * 0.35):.2f}" r="{font_size * 0.12:.2f}" fill="{fill}"/>')
                current_y += step_y * 0.5
                continue
                
            is_choonpu = (ch in ('ー', '―', '-'))
            lookup_char = 'ー' if is_choonpu else ch
            
            info = self.get_glyph_info(lookup_char)
            if not info or not info[0]:
                continue
            d, adv_width = info
            
            if is_choonpu:
                # Rotacionar o traço horizontal 90 graus no centro do glifo
                # Centro do glifo no espaço de coordenadas da fonte (unidades por em):
                mid_x = adv_width * 0.5
                mid_y = self.units_per_em * 0.35
                # No SVG:
                # 1. translada para (cx, current_y - font_size*0.35)
                # 2. rotaciona 90 graus
                # 3. escala (scale, -scale)
                # 4. translada (-mid_x, -mid_y)
                transform = (
                    f"translate({cx:.2f}, {current_y - font_size*0.35:.2f}) "
                    f"rotate(90) scale({scale:.5f}, {-scale:.5f}) "
                    f"translate({-mid_x:.1f}, {-mid_y:.1f})"
                )
            else:
                gx = cx - (adv_width * 0.5 * scale)
                gy = current_y
                transform = f"translate({gx:.2f}, {gy:.2f}) scale({scale:.5f}, {-scale:.5f})"
                
            paths.append(f'<path d="{d}" transform="{transform}" fill="{fill}"/>')
            current_y += step_y
            
        return "".join(paths)

v = GlyphVectorizer("epgyobld.ttf")
h_res = v.render_horizontal_text("洗心香武館", 200, 50, 38, "#161009", letter_spacing=12)
v_res = v.render_vertical_text("ムゼッティ・エドゥアルド", 100, 30, 15, 14, "#141414")
print("Horizontal rendered chars successfully. Length:", len(h_res))
print("Vertical rendered chars with choonpu successfully. Length:", len(v_res))
