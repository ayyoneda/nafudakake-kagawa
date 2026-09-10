"""
Gerador do Nafudakake Digital (洗心香武館 - Associação Kagawa de Kendo)
Renderizador vetorial hiper-realista com caligrafia Gyosho autêntica (epgyobld.ttf)
convertida em curvas vetoriais puras (<path d="...">), texturas orgânicas de madeira Hinoki,
brasão oficial AKK, fundo de cedro escuro, hierarquia completa de Dans (八段 a 無段)
e suporte multi-modalidade (Kendo, Iaido e Jodo).
"""

import os
import sys
import json
import base64
import html
from typing import List, Dict, Tuple, Optional
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google_sync import get_members_data, DAN_RANK_ORDER

DAN_METADATA = {
    80: {"kanji": "八段", "romaji": "8º DAN", "shogo_allowed": True},
    70: {"kanji": "七段", "romaji": "7º DAN", "shogo_allowed": True},
    60: {"kanji": "六段", "romaji": "6º DAN", "shogo_allowed": True},
    50: {"kanji": "五段", "romaji": "5º DAN", "shogo_allowed": True},
    40: {"kanji": "四段", "romaji": "4º DAN", "shogo_allowed": False},
    30: {"kanji": "三段", "romaji": "3º DAN", "shogo_allowed": False},
    20: {"kanji": "二段", "romaji": "2º DAN", "shogo_allowed": False},
    10: {"kanji": "初段", "romaji": "1º DAN", "shogo_allowed": False},
    1:  {"kanji": "一級", "romaji": "IKKYU", "shogo_allowed": False},
    0:  {"kanji": "無段", "romaji": "INICIANTES", "shogo_allowed": False},
}


class GlyphVectorizer:
    """
    Extrai as curvas de Bézier da fonte TrueType (epgyobld.ttf) e converte
    cada caractere japonês em elementos vetoriais puros (<path d="...">).
    Garante renderização 100% universal e independente de fontes externas.
    """
    def __init__(self, font_path: str = "epgyobld.ttf"):
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"Arquivo de fonte tipográfica não encontrado: {font_path}")
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
        adv_width, _ = self.hmetrics.get(gname, (self.units_per_em, 0))
        res = (d, adv_width)
        self._path_cache[char] = res
        return res

    def render_horizontal_text(
        self, text: str, cx: float, cy: float, font_size: float,
        fill: str = "#141414", letter_spacing: float = 0.0
    ) -> str:
        """Renderiza texto horizontal centrado em (cx, cy)."""
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

    def render_vertical_text(
        self, text: str, cx: float, start_y: float, step_y: float,
        font_size: float, fill: str = "#141414"
    ) -> str:
        """
        Renderiza texto vertical tradicional centrado horizontalmente em cx.
        Trata o traço de prolongamento do Katakana (chōonpu) rotacionando-o verticalmente.
        """
        scale = font_size / self.units_per_em
        paths = []
        current_y = start_y

        for ch in text:
            if ch in (' ', '　', '\t'):
                current_y += step_y * 0.5
                continue
            if ch == '・':
                paths.append(
                    f'<circle cx="{cx:.2f}" cy="{current_y - (font_size * 0.35):.2f}" '
                    f'r="{font_size * 0.12:.2f}" fill="{fill}"/>'
                )
                current_y += step_y * 0.5
                continue

            is_choonpu = (ch in ('ー', '―', '-', '︱'))
            lookup_char = 'ー' if is_choonpu else ch

            info = self.get_glyph_info(lookup_char)
            if not info or not info[0]:
                continue
            d, adv_width = info

            if is_choonpu:
                mid_x = adv_width * 0.5
                mid_y = self.units_per_em * 0.35
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


# Instância global do vetorizador de glifos
_VECTORIZER: Optional[GlyphVectorizer] = None

def get_glyph_vectorizer() -> GlyphVectorizer:
    global _VECTORIZER
    if _VECTORIZER is None:
        _VECTORIZER = GlyphVectorizer("epgyobld.ttf")
    return _VECTORIZER


def load_logo_base64(logo_path: str = "AKK_colorido.png") -> str:
    """Carrega o brasão oficial do dojo e converte para Base64."""
    if os.path.isfile(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def parse_graduacao_and_shogo(grad_raw: str) -> Tuple[int, Optional[str], str]:
    """Analisa a string de graduação para extrair peso, shogo e kanji do Dan."""
    grad_clean = grad_raw.strip().lower()

    shogo = None
    if "hanshi" in grad_clean or "範士" in grad_raw:
        shogo = "範士"
    elif "kyoshi" in grad_clean or "教士" in grad_raw:
        shogo = "教士"
    elif "renshi" in grad_clean or "錬士" in grad_raw:
        shogo = "錬士"

    dan_weight = 0
    for key, weight in DAN_RANK_ORDER.items():
        if key in grad_clean:
            dan_weight = weight
            break

    kanji_dan = DAN_METADATA.get(dan_weight, {}).get("kanji", "無段")
    return dan_weight, shogo, kanji_dan


def process_members(raw_data: List[Dict]) -> List[Dict]:
    """Padroniza e enriquece os registros lidos da base de dados."""
    processed = []
    for item in raw_data:
        nome_completo = item.get("Nome completo", item.get("Nome abreviado", "")).strip()
        nome_abreviado = item.get("Nome abreviado", "").strip() or nome_completo
        jap = item.get("Japonês", "").strip()
        grad_raw = item.get("Graduação", "").strip()

        dan_weight, shogo, kanji_dan = parse_graduacao_and_shogo(grad_raw)

        # Tratar peso explícito da planilha se presente
        peso_raw = item.get("Peso", "")
        try:
            peso_final = int(peso_raw) if peso_raw else dan_weight
        except ValueError:
            peso_final = dan_weight

        processed.append({
            "ordem": item.get("Ordem", ""),
            "nome_completo": nome_completo,
            "nome_abreviado": nome_abreviado,
            "jap": jap,
            "graduacao": grad_raw,
            "dan_weight": dan_weight,
            "peso": peso_final,
            "shogo": shogo or item.get("Shogo", None),
            "kanji_dan": kanji_dan,
            "data_grad": item.get("Data Graduação", "")
        })

    return processed


def group_plaques_with_headers(members: List[Dict]) -> List[Dict]:
    """
    Agrupa os praticantes inserindo plaquetas de cabeçalho (Dan Headers)
    apenas para graduações que possuam ao menos um atleta.
    """
    dans_presentes = set(m["dan_weight"] for m in members)
    sorted_dans = sorted(dans_presentes, reverse=True)

    items = []
    for dan in sorted_dans:
        meta = DAN_METADATA.get(dan, {"kanji": f"{dan//10}段", "romaji": f"{dan//10}º DAN"})
        items.append({
            "type": "dan_header",
            "dan_weight": dan,
            "jap": meta["kanji"],
            "romaji": meta["romaji"],
            "shogo": None
        })

        group = [m for m in members if m["dan_weight"] == dan]
        for kenshi in group:
            items.append({
                "type": "kenshi",
                "dan_weight": dan,
                "ordem": kenshi["ordem"],
                "nome_completo": kenshi["nome_completo"],
                "nome_abreviado": kenshi["nome_abreviado"],
                "romaji": kenshi["nome_abreviado"],
                "jap": kenshi["jap"],
                "graduacao": kenshi["graduacao"],
                "shogo": kenshi["shogo"]
            })

    return items


def calc_typography(text: str, has_shogo: bool = False) -> Tuple[float, float, float]:
    """
    Calcula dinamicamente tamanho de fonte, espaçamento vertical e posição inicial Y,
    garantindo que o último ideograma termine confortavelmente antes de Y=144px.
    """
    length = max(1, len(text))
    start_y = 36.0 if has_shogo else 20.0
    max_bottom_y = 144.0
    avail_height = max_bottom_y - start_y

    if length == 1:
        return 23.0, 0.0, (70.0 if has_shogo else 60.0)

    ideal_step = avail_height / (length - 1)

    if length <= 3:
        step_y = min(ideal_step, 30.0)
        font_size = 22.0
        start_y = 48.0 if has_shogo else 36.0
    elif length <= 4:
        step_y = min(ideal_step, 25.5)
        font_size = 20.0
        start_y = 42.0 if has_shogo else 28.0
    elif length <= 6:
        step_y = min(ideal_step, 19.5)
        font_size = 17.0
        start_y = 38.0 if has_shogo else 24.0
    elif length <= 8:
        step_y = min(ideal_step, 15.5)
        font_size = 14.0
        start_y = 36.0 if has_shogo else 22.0
    elif length <= 10:
        step_y = min(ideal_step, 12.8)
        font_size = 11.8
        start_y = 36.0 if has_shogo else 20.0
    else:
        step_y = min(ideal_step, 10.8)
        font_size = 10.2
        start_y = 35.0 if has_shogo else 19.0

    return font_size, step_y, start_y


def format_romaji_display(nome: str, max_width_chars: int = 11) -> Tuple[str, float]:
    """Formata o nome ocidental para a base da plaqueta (48px)."""
    nome_clean = nome.strip()
    if not nome_clean:
        return "", 8.0

    parts = nome_clean.split()
    if len(nome_clean) > max_width_chars and len(parts) >= 2:
        nome_display = f"{parts[0][0]}. {' '.join(parts[1:])}"
    else:
        nome_display = nome_clean

    length = len(nome_display)
    if length <= 8:
        font_size = 8.0
    elif length <= 11:
        font_size = 7.0
    elif length <= 14:
        font_size = 6.2
    else:
        font_size = 5.5

    return nome_display, font_size


def generate_nafudakake_svg(
    items: List[Dict],
    modalidade: str = "kendo",
    placas_por_linha: int = 18,
    largura_placa: int = 48,
    altura_placa: int = 175,
    espaco_x: int = 11,
    espaco_y: int = 36,
    margem_x: int = 48,
    margem_topo: int = 135,
    margem_base: int = 50,
    show_romaji: bool = True,
) -> str:
    """
    Gera o SVG hiper-realista completo com ideogramas vetorizados (curvas puras),
    texturas orgânicas de Hinoki, moldura nobre, cantoneiras de latão e brasão oficial AKK.
    """
    vectorizer = get_glyph_vectorizer()
    logo_b64 = load_logo_base64("AKK_colorido.png")

    total_itens = len(items)
    num_linhas = (total_itens + placas_por_linha - 1) // placas_por_linha
    if num_linhas < 1:
        num_linhas = 1

    largura_util = (placas_por_linha * largura_placa) + ((placas_por_linha - 1) * espaco_x)
    largura_total = margem_x * 2 + largura_util
    altura_total = margem_topo + margem_base + (num_linhas * altura_placa) + ((num_linhas - 1) * espaco_y)

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura_total} {altura_total}" '
        f'width="{largura_total}" height="{altura_total}" id="nafudakake-svg">'
    )

    # Geração/Carregamento das Texturas Fotográficas Reais de Madeira
    import process_wood_textures
    encoded_plaques, wall_b64, gaku_b64 = process_wood_textures.generate_plaque_variations(10)

    # Definições de Estilos, Texturas e Filtros 3D
    svg.append(f"""
<defs>
  <style>
    .gaku-subtitle {{
      font-family: 'Cinzel', 'Trajan Pro', 'Georgia', serif;
      font-size: 11px;
      font-weight: bold;
      fill: #8d5e2a;
      letter-spacing: 4px;
      text-anchor: middle;
    }}
    .dan-header-sub {{
      font-family: 'Arial', sans-serif;
      font-size: 7.5px;
      font-weight: bold;
      fill: #dfb26b;
      letter-spacing: 1px;
      text-anchor: middle;
    }}
    .romaji-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      font-size: 8.5px;
      font-weight: 600;
      fill: #2d2319;
      letter-spacing: 0.3px;
      text-anchor: middle;
    }}
    .kenshi-plaque {{
      cursor: pointer;
      transition: transform 0.2s ease, filter 0.2s ease;
    }}
    .kenshi-plaque:hover {{
      filter: drop-shadow(0 0 10px rgba(245, 195, 100, 0.85));
    }}
  </style>

  <!-- Filtros 3D de Sombras Profundas -->
  <filter id="placa-shadow" x="-20%" y="-10%" width="140%" height="125%">
    <feDropShadow dx="2" dy="5" stdDeviation="3.5" flood-color="#120904" flood-opacity="0.55"/>
  </filter>

  <filter id="trilho-shadow" x="-3%" y="-15%" width="106%" height="160%">
    <feDropShadow dx="0" dy="7" stdDeviation="5" flood-color="#0c0704" flood-opacity="0.75"/>
  </filter>

  <filter id="gaku-shadow" x="-5%" y="-10%" width="110%" height="135%">
    <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#0a0502" flood-opacity="0.75"/>
  </filter>

  <filter id="metal-emboss" x="-10%" y="-10%" width="120%" height="120%">
    <feDropShadow dx="1" dy="1" stdDeviation="0.8" flood-color="#fff8d0" flood-opacity="0.7" result="hi"/>
    <feDropShadow dx="-1" dy="-1" stdDeviation="0.8" flood-color="#2a1a08" flood-opacity="0.8"/>
  </filter>

  <!-- Textura Fotográfica do Fundo de Cedro Escuro -->
  <pattern id="wall-real-wood" width="300" height="300" patternUnits="userSpaceOnUse">
    <image href="data:image/jpeg;base64,{wall_b64}" width="300" height="300"/>
  </pattern>

  <!-- Textura da Placa Superior (Gaku) -->
  <pattern id="gaku-real-wood" width="600" height="90" patternUnits="userSpaceOnUse">
    <image href="data:image/jpeg;base64,{gaku_b64}" width="600" height="90" preserveAspectRatio="none"/>
  </pattern>
  <!-- Máscara com cantos arredondados de 3px para as plaquetas de Hinoki maciço -->
  <clipPath id="plaque-rounded-clip">
    <rect width="{largura_placa}" height="{altura_placa}" rx="3"/>
  </clipPath>

  <!-- Madeira dos Trilhos Chanfrados -->
  <linearGradient id="rail-profile" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#91613c"/>
    <stop offset="15%" stop-color="#6e4526"/>
    <stop offset="60%" stop-color="#4e2e17"/>
    <stop offset="85%" stop-color="#381e0c"/>
    <stop offset="100%" stop-color="#211005"/>
  </linearGradient>

  <!-- Plaqueta de Cabeçalho de Dan (Madeira Envelhecida Nobre) -->
  <linearGradient id="dan-header-wood" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#25140b"/>
    <stop offset="15%" stop-color="#3b2212"/>
    <stop offset="50%" stop-color="#4a2c18"/>
    <stop offset="85%" stop-color="#381f10"/>
    <stop offset="100%" stop-color="#221208"/>
  </linearGradient>

  <!-- Latão Dourado Tradicional (Shinchu Kanagu - 金具) -->
  <linearGradient id="brass-grad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#e9cc88"/>
    <stop offset="25%" stop-color="#c49b4c"/>
    <stop offset="50%" stop-color="#ffd980"/>
    <stop offset="75%" stop-color="#aa7e35"/>
    <stop offset="100%" stop-color="#80591f"/>
  </linearGradient>

  <!-- Placa Superior do Dojo (Gaku) -->
  <linearGradient id="gaku-wood" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#3a2213"/>
    <stop offset="50%" stop-color="#2b180c"/>
    <stop offset="100%" stop-color="#1b0e06"/>
  </linearGradient>
</defs>
""")

    # 1. Parede e Moldura Externa do Dojo
    svg.append(f'<rect width="{largura_total}" height="{altura_total}" fill="url(#wall-real-wood)" id="dojo-wall"/>')
    svg.append(
        f'<rect width="{largura_total}" height="{altura_total}" '
        f'fill="black" opacity="0.15" style="mix-blend-mode: multiply;"/>'
    )
    svg.append(
        f'<rect x="12" y="12" width="{largura_total - 24}" height="{altura_total - 24}" '
        f'fill="none" stroke="#160b05" stroke-width="16" rx="4"/>'
    )
    svg.append(
        f'<rect x="20" y="20" width="{largura_total - 40}" height="{altura_total - 40}" '
        f'fill="none" stroke="#5d3921" stroke-width="2.5" opacity="0.75"/>'
    )
    svg.append(
        f'<rect x="22" y="22" width="{largura_total - 44}" height="{altura_total - 44}" '
        f'fill="none" stroke="#8d5b38" stroke-width="0.8" opacity="0.5"/>'
    )

    # Cantoneiras Tradicionais de Latão (Kanagu) nos 4 Cantos
    svg.append(f"""
<g filter="url(#metal-emboss)">
  <path d="M 12 12 L 54 12 L 54 28 L 28 28 L 28 54 L 12 54 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="20" cy="20" r="2.5" fill="#302008"/>
  <circle cx="42" cy="20" r="2" fill="#302008"/>
  <circle cx="20" cy="42" r="2" fill="#302008"/>
</g>
<g filter="url(#metal-emboss)">
  <path d="M {largura_total - 12} 12 L {largura_total - 54} 12 L {largura_total - 54} 28 L {largura_total - 28} 28 L {largura_total - 28} 54 L {largura_total - 12} 54 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="{largura_total - 20}" cy="20" r="2.5" fill="#302008"/>
  <circle cx="{largura_total - 42}" cy="20" r="2" fill="#302008"/>
  <circle cx="{largura_total - 20}" cy="42" r="2" fill="#302008"/>
</g>
<g filter="url(#metal-emboss)">
  <path d="M 12 {altura_total - 12} L 54 {altura_total - 12} L 54 {altura_total - 28} L 28 {altura_total - 28} L 28 {altura_total - 54} L 12 {altura_total - 54} Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="20" cy="{altura_total - 20}" r="2.5" fill="#302008"/>
  <circle cx="42" cy="{altura_total - 20}" r="2" fill="#302008"/>
  <circle cx="20" cy="{altura_total - 42}" r="2" fill="#302008"/>
</g>
<g filter="url(#metal-emboss)">
  <path d="M {largura_total - 12} {altura_total - 12} L {largura_total - 54} {altura_total - 12} L {largura_total - 54} {altura_total - 28} L {largura_total - 28} {altura_total - 28} L {largura_total - 28} {altura_total - 54} L {largura_total - 12} {altura_total - 54} Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="{largura_total - 20}" cy="{altura_total - 20}" r="2.5" fill="#302008"/>
  <circle cx="{largura_total - 42}" cy="{altura_total - 20}" r="2" fill="#302008"/>
  <circle cx="{largura_total - 20}" cy="{altura_total - 42}" r="2" fill="#302008"/>
</g>
""")

    # 2. Placa Superior do Dojo (Kamiza / Gaku - 額)
    gaku_largura = min(720, largura_util)
    gaku_altura = 88
    gaku_x = (largura_total - gaku_largura) / 2
    gaku_y = 26

    svg.append(f'<g filter="url(#gaku-shadow)" id="dojo-gaku">')
    # Moldura de Madeira Nobre
    svg.append(
        f'  <rect x="{gaku_x}" y="{gaku_y}" width="{gaku_largura}" height="{gaku_altura}" '
        f'rx="5" fill="url(#gaku-wood)" stroke="#5d3921" stroke-width="3.5"/>'
    )
    # Fundo de Madeira Hinoki Clara
    svg.append(
        f'  <rect x="{gaku_x + 9}" y="{gaku_y + 8}" width="{gaku_largura - 18}" height="{gaku_altura - 16}" '
        f'rx="3" fill="url(#gaku-real-wood)"/>'
    )
    # Borda sutil interna dourada
    svg.append(
        f'  <rect x="{gaku_x + 13}" y="{gaku_y + 11}" width="{gaku_largura - 26}" height="{gaku_altura - 22}" '
        f'fill="none" stroke="#b38448" stroke-width="1.2" opacity="0.8"/>'
    )

    # Brasão Oficial AKK (Logo circular colorido embutido em alta resolução)
    logo_size = 60
    logo_x = gaku_x + 22
    logo_y = gaku_y + (gaku_altura - logo_size) / 2
    if logo_b64:
        svg.append(
            f'  <image href="data:image/png;base64,{logo_b64}" x="{logo_x}" y="{logo_y}" '
            f'width="{logo_size}" height="{logo_size}" preserveAspectRatio="xMidYMid meet"/>'
        )

    # Insígnia da Modalidade no lado direito (劍道 / 居合道 / 杖道)
    badge_size = 56
    badge_x = gaku_x + gaku_largura - 22 - badge_size
    badge_y = gaku_y + (gaku_altura - badge_size) / 2
    badge_cx = badge_x + (badge_size / 2)
    badge_cy = badge_y + (badge_size / 2)

    svg.append(f"""
  <!-- Selo Nobre da Modalidade -->
  <circle cx="{badge_cx}" cy="{badge_cy}" r="{badge_size / 2}" fill="url(#gaku-wood)" stroke="#d4af37" stroke-width="1.6"/>
  <circle cx="{badge_cx}" cy="{badge_cy}" r="{(badge_size / 2) - 3}" fill="none" stroke="#87582b" stroke-width="0.8"/>
""")

    # Inscrição do Selo perfeitamente centrada na vertical
    if modalidade.lower() == "kendo":
        mod_kanji = "劍道"
        mod_font_size = 17.5
        mod_step_y = 19.0
    else:
        mod_kanji = "居合道"
        mod_font_size = 14.5
        mod_step_y = 15.5

    n_chars = len(mod_kanji)
    mod_start_y = badge_cy - ((n_chars - 1) * mod_step_y / 2.0) + (mod_font_size * 0.38)

    mod_badge_paths = vectorizer.render_vertical_text(
        mod_kanji, cx=badge_cx, start_y=mod_start_y, step_y=mod_step_y, font_size=mod_font_size, fill="#f8d692"
    )
    svg.append(f'  {mod_badge_paths}')

    # Caligrafia Principal Vetorizada (Curvas Puras): 洗心香武館
    center_x = largura_total / 2.0
    gaku_paths = vectorizer.render_horizontal_text(
        "洗心香武館", cx=center_x, cy=gaku_y + 49, font_size=36.0, fill="#161009", letter_spacing=10.0
    )
    svg.append(f'  {gaku_paths}')

    # Subtítulo Oficial Imutável: ASSOCIAÇÃO KAGAWA DE KENDO
    svg.append(
        f'  <text x="{center_x}" y="{gaku_y + 68}" class="gaku-subtitle">ASSOCIAÇÃO KAGAWA DE KENDO</text>'
    )
    svg.append('</g>')

    # 3. Trilhos Horizontais de Sustentação
    for row in range(num_linhas):
        rail_y = margem_topo + (row * (altura_placa + espaco_y)) + altura_placa - 5
        rail_width = largura_util + 30
        rail_x = margem_x - 15

        svg.append(f'<g filter="url(#trilho-shadow)">')
        svg.append(
            f'  <rect x="{rail_x}" y="{rail_y}" width="{rail_width}" height="20" rx="2" fill="url(#rail-profile)"/>'
        )
        svg.append(
            f'  <line x1="{rail_x}" y1="{rail_y + 1}" x2="{rail_x + rail_width}" y2="{rail_y + 1}" stroke="#b68255" stroke-width="1.2" opacity="0.8"/>'
        )
        svg.append(
            f'  <rect x="{rail_x + 4}" y="{rail_y + 3}" width="{rail_width - 8}" height="4" rx="1" fill="#150a04"/>'
        )
        svg.append(
            f'  <line x1="{rail_x}" y1="{rail_y + 20}" x2="{rail_x + rail_width}" y2="{rail_y + 20}" stroke="#100702" stroke-width="1.5"/>'
        )
        svg.append('</g>')

    # 4. Renderização das Plaquetas Individuais e Cabeçalhos
    for idx, item in enumerate(items):
        row = idx // placas_por_linha
        col = idx % placas_por_linha

        x = margem_x + col * (largura_placa + espaco_x)
        y = margem_topo + row * (altura_placa + espaco_y)

        is_header = (item.get("type") == "dan_header")
        nome_jp = item.get("jap", "")
        nome_romaji = item.get("romaji", "")
        shogo = item.get("shogo")

        # Variação randômica consistente de textura de Hinoki
        wood_seed = f"{item.get('jap', '')}_{item.get('romaji', '')}_{item.get('ordem', idx)}"
        wood_idx = abs(hash(wood_seed)) % len(encoded_plaques)
        x_center = x + (largura_placa / 2.0)

        if is_header:
            # Plaqueta de Cabeçalho de Dan (七段, 五段, etc.)
            header_text = item.get("jap", "")
            dan_header_paths = vectorizer.render_vertical_text(
                header_text, cx=x_center, start_y=y + 40, step_y=36.0, font_size=27.0, fill="#f8d692"
            )

            svg.append(f'<g filter="url(#placa-shadow)" class="dan-header-plaque" id="header-{item.get("dan_weight")}">' )
            svg.append(
                f'  <rect x="{x}" y="{y}" width="{largura_placa}" height="{altura_placa}" rx="3" '
                f'fill="url(#dan-header-wood)" stroke="#87582b" stroke-width="1.5"/>'
            )
            svg.append(
                f'  <rect x="{x + 2.5}" y="{y + 2.5}" width="{largura_placa - 5}" height="{altura_placa - 5}" '
                f'rx="2" fill="none" stroke="#d4af37" stroke-width="1.2" opacity="0.85"/>'
            )
            svg.append(f'  {dan_header_paths}')

            if show_romaji:
                svg.append(
                    f'  <text x="{x_center}" y="{y + altura_placa - 16}" class="dan-header-sub">{nome_romaji}</text>'
                )
            svg.append('</g>')

        else:
            # Plaqueta Individual de Praticante (Nafuda)
            kenshi_id = f"kenshi-{item.get('ordem', idx)}"
            has_shogo = bool(shogo)
            raw_jap_name = item.get("jap", "")
            font_size, step_y, text_start_y = calc_typography(raw_jap_name, has_shogo)

            kanji_paths = vectorizer.render_vertical_text(
                raw_jap_name, cx=x_center, start_y=y + text_start_y, step_y=step_y, font_size=font_size, fill="#141414"
            )

            svg.append(
                f'<g filter="url(#placa-shadow)" class="kenshi-plaque" id="{kenshi_id}" '
                f'data-nome="{html.escape(nome_romaji)}" data-kanji="{html.escape(nome_jp)}" data-dan="{item.get("dan_weight")}">'
            )
            svg.append(
                f'  <g transform="translate({x}, {y})" clip-path="url(#plaque-rounded-clip)">\n'
                f'    <image href="data:image/jpeg;base64,{encoded_plaques[wood_idx]}" width="{largura_placa}" height="{altura_placa}" preserveAspectRatio="none"/>\n'
                f'  </g>'
            )
            # Chanfros e iluminação 3D
            svg.append(
                f'  <line x1="{x + 1}" y1="{y + 1}" x2="{x + largura_placa - 1}" y2="{y + 1}" stroke="#ffffff" stroke-width="1" opacity="0.65"/>'
            )
            svg.append(
                f'  <line x1="{x + 1}" y1="{y + 1}" x2="{x + 1}" y2="{y + altura_placa - 1}" stroke="#ffffff" stroke-width="0.8" opacity="0.45"/>'
            )
            svg.append(
                f'  <line x1="{x + largura_placa - 1}" y1="{y + 1}" x2="{x + largura_placa - 1}" y2="{y + altura_placa - 1}" stroke="#b0885a" stroke-width="1" opacity="0.6"/>'
            )
            svg.append(
                f'  <line x1="{x + 1}" y1="{y + altura_placa - 1}" x2="{x + largura_placa - 1}" y2="{y + altura_placa - 1}" stroke="#946d42" stroke-width="1.2" opacity="0.8"/>'
            )
            svg.append(
                f'  <rect x="{x + 1.5}" y="{y + 1.5}" width="{largura_placa - 3}" height="{altura_placa - 3}" '
                f'rx="2" fill="none" stroke="#d5b48e" stroke-width="0.8" opacity="0.7"/>'
            )

            # Insígnia de Mestre (Shogo)
            if has_shogo:
                svg.append(
                    f'  <rect x="{x + 6}" y="{y + 7}" width="{largura_placa - 12}" height="16" rx="2" '
                    f'fill="#fff5e5" stroke="#9e1e1e" stroke-width="0.8"/>'
                )
                shogo_paths = vectorizer.render_horizontal_text(
                    shogo, cx=x_center, cy=y + 19, font_size=11.0, fill="#9e1e1e", letter_spacing=2.0
                )
                svg.append(f'  {shogo_paths}')

            # Curvas Vetoriais da Caligrafia Japonesa (100% livre de fontes externas)
            svg.append(f'  {kanji_paths}')

            # Nome Ocidental na base
            if show_romaji and nome_romaji:
                romaji_display, romaji_font_size = format_romaji_display(nome_romaji)
                svg.append(
                    f'  <text x="{x_center}" y="{y + altura_placa - 16}" class="romaji-text" '
                    f'style="font-size: {romaji_font_size:.1f}px;">{html.escape(romaji_display)}</text>'
                )

            svg.append('</g>')

    svg.append('</svg>')
    return '\n'.join(svg)


def export_svg_to_png(svg_path: str, png_path: str, scale_factor: float = 2.0) -> bool:
    """
    Renderiza o SVG para PNG de altíssima definição utilizando PySide6.
    Como todos os ideogramas são curvas vetoriais puras (<path>),
    a renderização é 100% idêntica e perfeita sem dependência de fontes do sistema.
    """
    try:
        from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor
        from PySide6.QtSvg import QSvgRenderer

        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv if hasattr(sys, "argv") else [])

        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            print(f"[Erro] Arquivo SVG inválido para renderização: {svg_path}")
            return False

        default_size = renderer.defaultSize()
        target_width = int(default_size.width() * scale_factor)
        target_height = int(default_size.height() * scale_factor)

        image = QImage(target_width, target_height, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()

        success = image.save(png_path, "PNG")
        if success:
            print(f"PNG gerado com sucesso: {png_path} ({target_width}x{target_height}px)")
        return success
    except Exception as e:
        print(f"[Aviso] Falha ao renderizar PNG via PySide6: {e}")
        return False


def build_nafudakake(
    modalidade: str = "kendo",
    output_svg: Optional[str] = None,
    output_png: Optional[str] = None,
    placas_por_linha: int = 18,
    show_romaji: bool = True
) -> Tuple[str, str, int]:
    """Fluxo completo de geração dos artefatos gráficos para a modalidade especificada."""
    mod = modalidade.lower()
    if output_svg is None:
        output_svg = f"Nafudakake_{mod.capitalize()}.svg"
    if output_png is None:
        output_png = f"Nafudakake_{mod.capitalize()}.png"

    raw_members, source = get_members_data(modalidade=mod)
    processed_members = process_members(raw_data=raw_members)
    items = group_plaques_with_headers(members=processed_members)

    svg_content = generate_nafudakake_svg(
        items=items,
        modalidade=mod,
        placas_por_linha=placas_por_linha,
        show_romaji=show_romaji
    )

    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Salva cache processado para o visualizador estático do GitHub Pages
    cache_json_file = f"cache_{mod}.json"
    try:
        with open(cache_json_file, "w", encoding="utf-8") as f:
            json.dump(processed_members, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Aviso] Falha ao salvar {cache_json_file}: {e}")

    print(f"SVG salvo: {output_svg} ({len(processed_members)} atletas de {mod.upper()}, {len(items)} plaquetas)")

    if output_png:
        export_svg_to_png(svg_path=output_svg, png_path=output_png, scale_factor=2.0)

    return output_svg, output_png if output_png else "", len(processed_members)


if __name__ == "__main__":
    print("Gerando Nafudakake para Kendo...")
    build_nafudakake(modalidade="kendo", output_svg="Nafudakake_Kendo.svg", output_png="Nafudakake_Kendo.png")
    # Manter cópias com o nome legado para compatibilidade com a pasta do Drive
    import shutil
    shutil.copy("Nafudakake_Kendo.svg", "Nafudakake_Realista.svg")
    if os.path.isfile("Nafudakake_Kendo.png"):
        shutil.copy("Nafudakake_Kendo.png", "Nafudakake_Realista.png")

    print("\nGerando Nafudakake para Iaido...")
    build_nafudakake(modalidade="iaido", output_svg="Nafudakake_Iaido.svg", output_png="Nafudakake_Iaido.png")
    print("\nTodos os artefatos gerados com sucesso!")