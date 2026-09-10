"""
Teste de visualização hiper-realista da madeira e caligrafia Gyosho.
Gera uma amostra de alta definição com moldura, cantoneiras em latão (kanagu),
placa do dojo e plaquetas individuais em madeira Hinoki texturizada.
"""

import os
import sys
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor, QFontDatabase
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication.instance() or QGuiApplication([])
fid = QFontDatabase.addApplicationFont("epgyobld.ttf")
fams = QFontDatabase.applicationFontFamilies(fid)
qt_font_name = fams[0] if fams else "serif"
print("Qt Font Family Name:", qt_font_name)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480">
<defs>
  <!-- Sombras Suaves 3D -->
  <filter id="shadow-deep" x="-10%" y="-10%" width="120%" height="125%">
    <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#0a0502" flood-opacity="0.75"/>
  </filter>
  <filter id="plaque-shadow" x="-20%" y="-10%" width="140%" height="125%">
    <feDropShadow dx="2" dy="5" stdDeviation="3.5" flood-color="#120904" flood-opacity="0.55"/>
  </filter>
  <filter id="metal-emboss" x="-10%" y="-10%" width="120%" height="120%">
    <feDropShadow dx="1" dy="1" stdDeviation="0.8" flood-color="#fff8d0" flood-opacity="0.8" result="hi"/>
    <feDropShadow dx="-1" dy="-1" stdDeviation="0.8" flood-color="#2a1a08" flood-opacity="0.9"/>
  </filter>

  <!-- Padrão Textural de Madeira Hinoki (Cipreste Japonês) -->
  <linearGradient id="hinoki-base" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#dfbe96"/>
    <stop offset="6%" stop-color="#edd5b6"/>
    <stop offset="25%" stop-color="#f8e7d2"/>
    <stop offset="50%" stop-color="#fff4e3"/>
    <stop offset="75%" stop-color="#f6e4ce"/>
    <stop offset="94%" stop-color="#e8cfad"/>
    <stop offset="100%" stop-color="#d4b084"/>
  </linearGradient>

  <!-- Fibras orgânicas verticais da madeira Hinoki -->
  <pattern id="hinoki-grain" width="48" height="120" patternUnits="userSpaceOnUse">
    <path d="M 3 0 Q 3.5 60 2.5 120" stroke="#cfa878" stroke-width="0.75" opacity="0.35" fill="none"/>
    <path d="M 7 0 Q 6.5 60 7 120" stroke="#e8c99e" stroke-width="0.5" opacity="0.4" fill="none"/>
    <path d="M 14 0 Q 15 60 13.5 120" stroke="#b88f5c" stroke-width="0.8" opacity="0.28" fill="none"/>
    <path d="M 21 0 Q 20.5 60 21.5 120" stroke="#dfbc8f" stroke-width="0.6" opacity="0.35" fill="none"/>
    <path d="M 28 0 Q 29 60 27.5 120" stroke="#caa272" stroke-width="0.75" opacity="0.3" fill="none"/>
    <path d="M 35 0 Q 34.5 60 35 120" stroke="#b08652" stroke-width="0.7" opacity="0.26" fill="none"/>
    <path d="M 42 0 Q 42.5 60 41.5 120" stroke="#d5af82" stroke-width="0.65" opacity="0.32" fill="none"/>
    <path d="M 46 0 Q 45.5 60 46 120" stroke="#c09663" stroke-width="0.5" opacity="0.25" fill="none"/>
  </pattern>

  <!-- Padrão de Tábuas de Madeira Nobre para o Fundo (Cedro Escuro / Nogueira) -->
  <linearGradient id="wall-wood" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#362012"/>
    <stop offset="50%" stop-color="#2a170c"/>
    <stop offset="100%" stop-color="#1e0f06"/>
  </linearGradient>

  <pattern id="wall-planks" width="900" height="40" patternUnits="userSpaceOnUse">
    <rect width="900" height="39" fill="none"/>
    <!-- Linha de junção entre tábuas horizontais -->
    <line x1="0" y1="39.5" x2="900" y2="39.5" stroke="#120803" stroke-width="1.5"/>
    <line x1="0" y1="40" x2="900" y2="40" stroke="#482d1b" stroke-width="0.6" opacity="0.5"/>
    <!-- Fibras longitudinais sutis -->
    <line x1="0" y1="10" x2="900" y2="10" stroke="#3d2616" stroke-width="0.5" opacity="0.4"/>
    <line x1="0" y1="24" x2="900" y2="24" stroke="#452a17" stroke-width="0.6" opacity="0.3"/>
  </pattern>

  <!-- Madeira Escura dos Cabeçalhos de Dan (Madeira Envelhecida) -->
  <linearGradient id="dan-wood" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#2e190d"/>
    <stop offset="15%" stop-color="#462916"/>
    <stop offset="50%" stop-color="#55331c"/>
    <stop offset="85%" stop-color="#422614"/>
    <stop offset="100%" stop-color="#2a160b"/>
  </linearGradient>

  <!-- Latão Dourado Envelhecido (Shinchu / Kanagu) -->
  <linearGradient id="brass-grad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#e9cc88"/>
    <stop offset="25%" stop-color="#c49b4c"/>
    <stop offset="50%" stop-color="#ffd980"/>
    <stop offset="75%" stop-color="#aa7e35"/>
    <stop offset="100%" stop-color="#80591f"/>
  </linearGradient>

  <!-- Trilho de Apoio com Perfil Físico Chanfrado -->
  <linearGradient id="rail-profile" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#91613c"/>
    <stop offset="15%" stop-color="#6e4526"/>
    <stop offset="60%" stop-color="#4e2e17"/>
    <stop offset="85%" stop-color="#381e0c"/>
    <stop offset="100%" stop-color="#211005"/>
  </linearGradient>
</defs>

<!-- 1. Fundo do Painel com Textura de Madeira Real -->
<rect width="900" height="480" fill="url(#wall-wood)"/>
<rect width="900" height="480" fill="url(#wall-planks)"/>

<!-- Moldura Externa Maciça com Chanfros e Brilhos Naturais -->
<rect x="12" y="12" width="876" height="456" fill="none" stroke="#160b05" stroke-width="16" rx="4"/>
<rect x="20" y="20" width="860" height="440" fill="none" stroke="#5d3921" stroke-width="2.5" opacity="0.75"/>
<rect x="22" y="22" width="856" height="436" fill="none" stroke="#8d5b38" stroke-width="0.8" opacity="0.5"/>

<!-- Cantoneiras Tradicionais de Latão (Kanagu - 金具) nos 4 Cantos -->
<!-- Canto Superior Esquerdo -->
<g filter="url(#metal-emboss)">
  <path d="M 12 12 L 54 12 L 54 28 L 28 28 L 28 54 L 12 54 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="20" cy="20" r="2.5" fill="#302008"/>
  <circle cx="42" cy="20" r="2" fill="#302008"/>
  <circle cx="20" cy="42" r="2" fill="#302008"/>
</g>
<!-- Canto Superior Direito -->
<g filter="url(#metal-emboss)">
  <path d="M 888 12 L 846 12 L 846 28 L 872 28 L 872 54 L 888 54 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="880" cy="20" r="2.5" fill="#302008"/>
  <circle cx="858" cy="20" r="2" fill="#302008"/>
  <circle cx="880" cy="42" r="2" fill="#302008"/>
</g>
<!-- Canto Inferior Esquerdo -->
<g filter="url(#metal-emboss)">
  <path d="M 12 468 L 54 468 L 54 452 L 28 452 L 28 426 L 12 426 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="20" cy="460" r="2.5" fill="#302008"/>
  <circle cx="42" cy="460" r="2" fill="#302008"/>
  <circle cx="20" cy="438" r="2" fill="#302008"/>
</g>
<!-- Canto Inferior Direito -->
<g filter="url(#metal-emboss)">
  <path d="M 888 468 L 846 468 L 846 452 L 872 452 L 872 426 L 888 426 Z" fill="url(#brass-grad)" stroke="#523912" stroke-width="0.8"/>
  <circle cx="880" cy="460" r="2.5" fill="#302008"/>
  <circle cx="858" cy="460" r="2" fill="#302008"/>
  <circle cx="880" cy="438" r="2" fill="#302008"/>
</g>

<!-- 2. Placa Superior do Dojo (Gaku - 額) -->
<g filter="url(#shadow-deep)">
  <!-- Moldura de Madeira Nobre com Canto em Bisel -->
  <rect x="220" y="28" width="460" height="84" rx="4" fill="url(#dan-wood)" stroke="#5d3921" stroke-width="3"/>
  <!-- Filete de Madeira Clara com Ranhura Dourada -->
  <rect x="230" y="37" width="440" height="66" rx="2" fill="url(#hinoki-base)"/>
  <rect x="230" y="37" width="440" height="66" rx="2" fill="url(#hinoki-grain)"/>
  <rect x="234" y="41" width="432" height="58" fill="none" stroke="#b38448" stroke-width="1.2" opacity="0.8"/>
  
  <!-- Caligrafia em Gyosho Autêntico -->
  <text x="450" y="76" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="34" font-weight="bold" fill="#140f09" letter-spacing="10" text-anchor="middle">洗心香武館</text>
  <text x="450" y="93" font-family="'Cinzel', 'Trajan Pro', Georgia, serif" font-size="10" font-weight="bold" fill="#885b28" letter-spacing="4" text-anchor="middle">ASSOCIAÇÃO KAGAWA DE KENDO</text>
</g>

<!-- 3. Trilho de Encaixe com Sulco Realista -->
<g filter="url(#shadow-deep)">
  <!-- Corpo da barra de madeira -->
  <rect x="36" y="325" width="828" height="22" rx="2" fill="url(#rail-profile)"/>
  <!-- Linha de luz no chanfro superior -->
  <line x1="36" y1="326" x2="864" y2="326" stroke="#b68255" stroke-width="1.2" opacity="0.75"/>
  <!-- Sulco escuro onde as plaquetas se encaixam -->
  <rect x="42" y="328" width="816" height="4" rx="1" fill="#150a04"/>
  <!-- Linha de sombra inferior -->
  <line x1="36" y1="347" x2="864" y2="347" stroke="#120803" stroke-width="1.5"/>
</g>

<!-- 4. Demonstração de Plaquetas com Textura Hinoki Realista -->
<!-- Plaqueta de Dan: 七段 (7º Dan) -->
<g filter="url(#plaque-shadow)">
  <rect x="60" y="155" width="48" height="175" rx="3" fill="url(#dan-wood)" stroke="#87582b" stroke-width="1.5"/>
  <rect x="62.5" y="157.5" width="43" height="170" rx="2" fill="none" stroke="#d4af37" stroke-width="1.2" opacity="0.85"/>
  <text x="84" y="225" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="30" font-weight="bold" fill="#f8d692" text-anchor="middle">七</text>
  <text x="84" y="265" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="30" font-weight="bold" fill="#f8d692" text-anchor="middle">段</text>
  <text x="84" y="315" font-family="Arial, sans-serif" font-size="7.5" font-weight="bold" fill="#e8c17b" letter-spacing="1" text-anchor="middle">7º DAN</text>
</g>

<!-- Plaqueta 1: 海老原 忠雄 (7º Dan Kyoshi) -->
<g filter="url(#plaque-shadow)">
  <rect x="120" y="155" width="48" height="175" rx="3" fill="url(#hinoki-base)"/>
  <rect x="120" y="155" width="48" height="175" rx="3" fill="url(#hinoki-grain)"/>
  <!-- Chanfros de iluminação da madeira (luz vindo do topo-esquerda) -->
  <line x1="121" y1="156" x2="167" y2="156" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <line x1="121" y1="156" x2="121" y2="329" stroke="#ffffff" stroke-width="0.8" opacity="0.4"/>
  <line x1="167" y1="156" x2="167" y2="329" stroke="#b0885a" stroke-width="1" opacity="0.6"/>
  <line x1="121" y1="329" x2="167" y2="329" stroke="#946d42" stroke-width="1.2" opacity="0.8"/>
  <rect x="121.5" y="156.5" width="45" height="172" rx="2" fill="none" stroke="#d5b58d" stroke-width="0.8" opacity="0.7"/>

  <!-- Shogo Badge: 教士 -->
  <rect x="126" y="162" width="36" height="16" rx="2" fill="#fff5e5" stroke="#9e1e1e" stroke-width="0.8"/>
  <text x="144" y="174" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="11" font-weight="bold" fill="#9e1e1e" letter-spacing="1" text-anchor="middle">教士</text>

  <!-- Nome Kanji em Gyosho -->
  <text x="144" y="200" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="20" fill="#141414" text-anchor="middle">海</text>
  <text x="144" y="225" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="20" fill="#141414" text-anchor="middle">老</text>
  <text x="144" y="250" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="20" fill="#141414" text-anchor="middle">原</text>
  <text x="144" y="275" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="20" fill="#141414" text-anchor="middle">忠</text>
  <text x="144" y="300" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="20" fill="#141414" text-anchor="middle">雄</text>

  <!-- Romaji -->
  <text x="144" y="320" font-family="'Segoe UI', Roboto, sans-serif" font-size="7.5" font-weight="600" fill="#2d2218" text-anchor="middle">T. Ebihara</text>
</g>

<!-- Plaqueta 2: 米田 裕 (7º Dan Renshi) -->
<g filter="url(#plaque-shadow)">
  <rect x="180" y="155" width="48" height="175" rx="3" fill="url(#hinoki-base)"/>
  <rect x="180" y="155" width="48" height="175" rx="3" fill="url(#hinoki-grain)"/>
  <line x1="181" y1="156" x2="227" y2="156" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <line x1="181" y1="156" x2="181" y2="329" stroke="#ffffff" stroke-width="0.8" opacity="0.4"/>
  <line x1="227" y1="156" x2="227" y2="329" stroke="#b0885a" stroke-width="1" opacity="0.6"/>
  <line x1="181" y1="329" x2="227" y2="329" stroke="#946d42" stroke-width="1.2" opacity="0.8"/>
  <rect x="181.5" y="156.5" width="45" height="172" rx="2" fill="none" stroke="#d5b58d" stroke-width="0.8" opacity="0.7"/>

  <!-- Shogo Badge: 錬士 -->
  <rect x="186" y="162" width="36" height="16" rx="2" fill="#fff5e5" stroke="#9e1e1e" stroke-width="0.8"/>
  <text x="204" y="174" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="11" font-weight="bold" fill="#9e1e1e" letter-spacing="1" text-anchor="middle">錬士</text>

  <!-- Nome Kanji em Gyosho -->
  <text x="204" y="206" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="22" fill="#141414" text-anchor="middle">米</text>
  <text x="204" y="238" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="22" fill="#141414" text-anchor="middle">田</text>
  <text x="204" y="274" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="22" fill="#141414" text-anchor="middle">裕</text>

  <!-- Romaji -->
  <text x="204" y="320" font-family="'Segoe UI', Roboto, sans-serif" font-size="7.5" font-weight="600" fill="#2d2218" text-anchor="middle">Y. Yoneda</text>
</g>

<!-- Plaqueta 3: ギレルメ (Katakana com traço vertical) -->
<g filter="url(#plaque-shadow)">
  <rect x="240" y="155" width="48" height="175" rx="3" fill="url(#hinoki-base)"/>
  <rect x="240" y="155" width="48" height="175" rx="3" fill="url(#hinoki-grain)"/>
  <line x1="241" y1="156" x2="287" y2="156" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <line x1="241" y1="156" x2="241" y2="329" stroke="#ffffff" stroke-width="0.8" opacity="0.4"/>
  <line x1="287" y1="156" x2="287" y2="329" stroke="#b0885a" stroke-width="1" opacity="0.6"/>
  <line x1="241" y1="329" x2="287" y2="329" stroke="#946d42" stroke-width="1.2" opacity="0.8"/>
  <rect x="241.5" y="156.5" width="45" height="172" rx="2" fill="none" stroke="#d5b58d" stroke-width="0.8" opacity="0.7"/>

  <!-- Nome Katakana com traço vertical -->
  <text x="264" y="184" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="18" fill="#141414" text-anchor="middle">ギ</text>
  <text x="264" y="206" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="18" fill="#141414" text-anchor="middle">レ</text>
  <text x="264" y="228" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="18" fill="#141414" text-anchor="middle">ル</text>
  <text x="264" y="250" font-family="{qt_font_name}, 'EPSON 行書体', serif" font-size="18" fill="#141414" text-anchor="middle">メ</text>

  <!-- Romaji -->
  <text x="264" y="320" font-family="'Segoe UI', Roboto, sans-serif" font-size="7.5" font-weight="600" fill="#2d2218" text-anchor="middle">Guilherme</text>
</g>
</svg>"""

with open("test_realistic.svg", "w", encoding="utf-8") as f:
    f.write(svg)

renderer = QSvgRenderer("test_realistic.svg")
print("Renderer valid:", renderer.isValid())

scale = 2.0
img = QImage(int(900 * scale), int(480 * scale), QImage.Format.Format_ARGB32)
img.fill(QColor(0, 0, 0, 0))
p = QPainter(img)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
renderer.render(p)
p.end()

img.save("test_realistic.png", "PNG")
print("Amosstra salva em test_realistic.png!")
