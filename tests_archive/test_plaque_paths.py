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

    def get_glyph_path(self, char: str):
        # Mapear chōonpu horizontal para vertical se necessário
        if char in ('ー', '―', '-'):
            char = '︱'
            
        if char in self._path_cache:
            return self._path_cache[char]
            
        code = ord(char)
        gname = self.cmap.get(code)
        if not gname:
            # Fallback para chōonpu padrão se ︱ não estiver no cmap
            if char == '︱' and ord('ー') in self.cmap:
                gname = self.cmap[ord('ー')]
            else:
                return None
                
        pen = SVGPathPen(self.glyph_set)
        glyph = self.glyph_set[gname]
        glyph.draw(pen)
        d = pen.getCommands()
        adv_width, lsb = self.hmetrics.get(gname, (self.units_per_em, 0))
        res = (d, adv_width)
        self._path_cache[char] = res
        return res

    def render_vertical_text(self, text: str, cx: float, start_y: float, font_size: float, fill: str = "#141414"):
        scale = font_size / self.units_per_em
        paths = []
        current_y = start_y
        step_y = font_size * 1.15
        
        for ch in text:
            if ch in (' ', '　', '\t'):
                current_y += step_y * 0.6
                continue
            if ch == '・':
                # Ponto médio
                paths.append(f'<circle cx="{cx:.2f}" cy="{current_y - font_size*0.4:.2f}" r="{font_size*0.1:.2f}" fill="{fill}"/>')
                current_y += step_y * 0.5
                continue
                
            info = self.get_glyph_path(ch)
            if not info or not info[0]:
                continue
            d, adv_width = info
            
            # Centralização horizontal: glifo tem largura adv_width no espaço do EM.
            # O centro do glifo em coordenadas de fonte é adv_width / 2.
            # No SVG queremos que fique centrado em cx.
            gx = cx - (adv_width * 0.5 * scale)
            gy = current_y
            
            transform = f"translate({gx:.2f}, {gy:.2f}) scale({scale:.5f}, {-scale:.5f})"
            paths.append(f'<path d="{d}" transform="{transform}" fill="{fill}"/>')
            current_y += step_y
            
        return "".join(paths), current_y

v = GlyphVectorizer("epgyobld.ttf")
paths, end_y = v.render_vertical_text("米田裕", 100, 50, 30)
print(f"Rendered paths length: {len(paths)}, end_y: {end_y}")
