"""
Processa as texturas fotográficas reais de Hinoki e Cedro para o Nafudakake.
Gera variações procedurais de corte, enquadramento e tonalidade sutil (tonalidades naturais da madeira)
e exporta como base64 otimizado para inclusão direta no SVG vetorial.
"""

import os
import io
import base64
from PIL import Image, ImageEnhance

TEXTURES_DIR = "textures"
os.makedirs(TEXTURES_DIR, exist_ok=True)

def generate_plaque_variations(num_variations=10):
    """
    Gera fatias verticais proporcionais a plaquetas (48x175) em resolução 2x (96x350).
    Utiliza madeira de Hinoki maciça com fibra vertical contínua, eliminando quaisquer
    emendas, linhas de colagem ou transições artificiais.
    """
    master_path = os.path.join(TEXTURES_DIR, "hinoki_solid_master.jpg")
    if not os.path.isfile(master_path):
        # Fallback se necessário
        master_img = Image.open(os.path.join(TEXTURES_DIR, "hinoki_1.jpg")).convert("RGB")
    else:
        master_img = Image.open(master_path).convert("RGB")

    mw, mh = master_img.size
    target_w, target_h = 96, 350
    encoded_textures = []

    # Altura de corte abrangendo quase toda a extensão vertical do tronco (fibra contínua)
    crop_h = int(mh * 0.96)
    crop_w = int(crop_h * (target_w / target_h))
    max_x = max(0, mw - crop_w)

    # 10 Variações naturais por deslocamento horizontal ao longo dos veios do Hinoki
    # e ajustes sutis de luminosidade e calor (mantendo a família nobre do Hinoki)
    var_params = [
        (0.05, 1.02, 1.01, 0.99),  # Hinoki claro suave
        (0.15, 1.00, 1.03, 1.00),  # Fibra reta clássica
        (0.25, 0.98, 1.04, 1.02),  # Mel suave
        (0.35, 1.03, 1.00, 0.98),  # Blond puro
        (0.45, 0.97, 1.05, 1.03),  # Âmbar nobre
        (0.55, 1.01, 1.02, 1.01),  # Veio vertical denso
        (0.65, 0.99, 1.03, 1.02),  # Tonalidade natural equilibrada
        (0.75, 1.02, 1.01, 0.99),  # Claro acetinado
        (0.85, 0.96, 1.04, 1.04),  # Dourado quente
        (0.95, 1.00, 1.02, 1.00),  # Fibra reta fina
    ]

    for i, (x_pct, bright, cont, warm) in enumerate(var_params[:num_variations]):
        left = int(max_x * x_pct)
        top = int((mh - crop_h) * 0.5)
        right = left + crop_w
        bottom = top + crop_h

        cropped = master_img.crop((left, top, right, bottom))
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Ajuste fino de tonalidade
        if bright != 1.0:
            resized = ImageEnhance.Brightness(resized).enhance(bright)
        if cont != 1.0:
            resized = ImageEnhance.Contrast(resized).enhance(cont)
        if warm != 1.0:
            resized = ImageEnhance.Color(resized).enhance(warm)

        # Salva em arquivo JPEG e codifica em base64
        save_path = os.path.join(TEXTURES_DIR, f"hinoki_plaque_{i}.jpg")
        resized.save(save_path, "JPEG", quality=90, optimize=True)

        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=90, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        encoded_textures.append(b64)
        print(f"Plaqueta {i}: {os.path.getsize(save_path)} bytes")

    # Processa o fundo de cedro escuro
    wall_img = Image.open(os.path.join(TEXTURES_DIR, "wall_dark.jpg")).convert("RGB")
    wall_resized = wall_img.resize((600, 600), Image.Resampling.LANCZOS)
    wall_path = os.path.join(TEXTURES_DIR, "wall_dark_tile.jpg")
    wall_resized.save(wall_path, "JPEG", quality=85, optimize=True)
    buf_wall = io.BytesIO()
    wall_resized.save(buf_wall, format="JPEG", quality=85, optimize=True)
    wall_b64 = base64.b64encode(buf_wall.getvalue()).decode("utf-8")
    print(f"Fundo Parede: {os.path.getsize(wall_path)} bytes")

    # Placa do topo (Gaku)
    gaku_crop = master_img.crop((30, 80, mw - 30, 280)).resize((600, 90), Image.Resampling.LANCZOS)
    buf_gaku = io.BytesIO()
    gaku_crop.save(buf_gaku, format="JPEG", quality=88, optimize=True)
    gaku_b64 = base64.b64encode(buf_gaku.getvalue()).decode("utf-8")

    return encoded_textures, wall_b64, gaku_b64

if __name__ == "__main__":
    generate_plaque_variations()
    print("Processamento de texturas concluído com sucesso!")
