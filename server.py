"""
Servidor Local do Nafudakake Digital (洗心香武館)
Fornece interface web interativa, API REST para sincronização,
exportação gráfica e upload no Google Drive.
"""

import os
import sys
import json
from flask import Flask, request, jsonify, send_file, Response

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import Nafudakake
import google_sync

app = Flask(__name__, static_folder=".", static_url_path="")


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/status", methods=["GET"])
def api_status():
    """Retorna o status atual da base de dados e credenciais."""
    creds_path = google_sync.get_credentials_path()
    has_creds = bool(creds_path and os.path.isfile(creds_path))

    return jsonify({
        "status": "online",
        "has_credentials": has_creds,
        "credentials_file": os.path.basename(creds_path) if creds_path else None,
        "spreadsheet_id": google_sync.SPREADSHEET_ID_DEFAULT,
        "drive_folder_id": google_sync.DRIVE_FOLDER_ID_DEFAULT,
        "svg_exists": os.path.isfile("Nafudakake_Realista.svg"),
        "png_exists": os.path.isfile("Nafudakake_Realista.png"),
    })


@app.route("/api/members", methods=["GET"])
def api_members():
    """Retorna a lista processada de kenshis para busca e estatísticas no frontend."""
    try:
        modalidade = request.args.get("modalidade", "kendo").lower()
        raw_members, source = google_sync.get_members_data(modalidade=modalidade)
        processed = Nafudakake.process_members(raw_members)
        return jsonify({
            "modalidade": modalidade,
            "source": source,
            "total": len(processed),
            "members": processed
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/nafudakake.svg", methods=["GET"])
def api_svg():
    """Gera ou serve o SVG do Nafudakake com parâmetros customizados."""
    try:
        modalidade = request.args.get("modalidade", "kendo").lower()
        placas_por_linha = int(request.args.get("placas_por_linha", 18))
        show_romaji = request.args.get("show_romaji", "true").lower() == "true"
        force_regen = request.args.get("refresh", "false").lower() == "true"

        svg_path = f"Nafudakake_{modalidade.capitalize()}.svg"

        if force_regen or not os.path.isfile(svg_path):
            Nafudakake.build_nafudakake(
                modalidade=modalidade,
                output_svg=svg_path,
                output_png=None,
                placas_por_linha=placas_por_linha,
                show_romaji=show_romaji
            )

        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        return Response(svg_content, mimetype="image/svg+xml")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sync", methods=["POST"])
def api_sync():
    """Aciona a sincronização com o Google Sheets / CSV local e reconstrói SVG e PNG para ambas as modalidades."""
    try:
        data = request.get_json(silent=True) or {}
        placas_por_linha = int(data.get("placas_por_linha", 18))
        show_romaji = bool(data.get("show_romaji", True))

        # Gera Kendo
        k_svg, k_png, k_total = Nafudakake.build_nafudakake(
            modalidade="kendo",
            output_svg="Nafudakake_Kendo.svg",
            output_png="Nafudakake_Kendo.png",
            placas_por_linha=placas_por_linha,
            show_romaji=show_romaji
        )
        import shutil
        shutil.copy("Nafudakake_Kendo.svg", "Nafudakake_Realista.svg")
        if os.path.isfile("Nafudakake_Kendo.png"):
            shutil.copy("Nafudakake_Kendo.png", "Nafudakake_Realista.png")

        # Gera Iaido
        i_svg, i_png, i_total = Nafudakake.build_nafudakake(
            modalidade="iaido",
            output_svg="Nafudakake_Iaido.svg",
            output_png="Nafudakake_Iaido.png",
            placas_por_linha=placas_por_linha,
            show_romaji=show_romaji
        )

        _, source_k = google_sync.get_members_data("kendo")

        return jsonify({
            "success": True,
            "source": source_k,
            "total_kendo": k_total,
            "total_iaido": i_total,
            "message": f"Nafudakake sincronizado com sucesso! (Kendo: {k_total} praticantes | Iaido: {i_total} praticantes)"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export-png", methods=["GET", "POST"])
def api_export_png():
    """Gera e faz download do PNG rasterizado em altíssima resolução para a modalidade solicitada."""
    try:
        modalidade = request.args.get("modalidade", "kendo").lower()
        scale = float(request.args.get("scale", 2.0))
        png_path = f"Nafudakake_{modalidade.capitalize()}.png"
        svg_path = f"Nafudakake_{modalidade.capitalize()}.svg"

        if not os.path.isfile(svg_path):
            Nafudakake.build_nafudakake(modalidade=modalidade, output_svg=svg_path, output_png=None)

        success = Nafudakake.export_svg_to_png(svg_path=svg_path, png_path=png_path, scale_factor=scale)
        if not success or not os.path.isfile(png_path):
            return jsonify({"error": "Falha na geração do arquivo PNG"}), 500

        download_filename = f"Nafudakake_{modalidade.capitalize()}_SenshinKabukan.png"
        return send_file(png_path, mimetype="image/png", as_attachment=True, download_name=download_filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload-drive", methods=["POST"])
def api_upload_drive():
    """Dispara o upload do PNG e SVG para a pasta do Google Drive."""
    try:
        results = {}
        files_to_upload = [
            ("Nafudakake_Kendo.svg", "Nafudakake_Kendo.png"),
            ("Nafudakake_Iaido.svg", "Nafudakake_Iaido.png"),
            ("Nafudakake_Realista.svg", "Nafudakake_Realista.png")
        ]

        if not os.path.isfile("Nafudakake_Kendo.svg"):
            Nafudakake.build_nafudakake(modalidade="kendo", output_svg="Nafudakake_Kendo.svg", output_png="Nafudakake_Kendo.png")
        if not os.path.isfile("Nafudakake_Iaido.svg"):
            Nafudakake.build_nafudakake(modalidade="iaido", output_svg="Nafudakake_Iaido.svg", output_png="Nafudakake_Iaido.png")

        for svg_f, png_f in files_to_upload:
            if os.path.isfile(svg_f):
                try:
                    results[svg_f] = google_sync.upload_to_google_drive(svg_f)
                except Exception as ex:
                    results[f"{svg_f}_error"] = str(ex)
            if os.path.isfile(png_f):
                try:
                    results[png_f] = google_sync.upload_to_google_drive(png_f)
                except Exception as ex:
                    results[f"{png_f}_error"] = str(ex)

        return jsonify({
            "success": True,
            "message": "Arquivos sincronizados com o Google Drive para Kendo e Iaido!",
            "results": results
        })
    except Exception as e:
        err_msg = str(e)
        if "File not found" in err_msg or "notFound" in err_msg:
            sa_email = "sua conta de serviço"
            try:
                creds_path = google_sync.get_credentials_path()
                if creds_path:
                    with open(creds_path, "r", encoding="utf-8") as f:
                        sa_email = json.load(f).get("client_email", sa_email)
            except Exception:
                pass
            err_msg = (
                f"A pasta de destino no Google Drive (ID: {google_sync.DRIVE_FOLDER_ID_DEFAULT}) "
                f"não está compartilhada com a sua Conta de Serviço. "
                f"Por favor, abra a pasta no Google Drive, clique em Compartilhar e adicione o e-mail '{sa_email}' com permissão de Editor."
            )
        return jsonify({"success": False, "error": err_msg}), 500


@app.route("/api/test-sheets", methods=["GET"])
def api_test_sheets():
    """Diagnóstico detalhado da conexão com o Google Sheets e Google Drive."""
    import urllib.request
    creds_path = google_sync.get_credentials_path()
    has_creds = bool(creds_path and os.path.isfile(creds_path))
    service_email = None

    if has_creds:
        try:
            with open(creds_path, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                service_email = cdata.get("client_email")
        except Exception:
            pass

    # Teste de URL direta
    public_ok = False
    public_msg = ""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{google_sync.SPREADSHEET_ID_DEFAULT}/export?format=csv&gid={google_sync.SHEET_GID_DEFAULT}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                public_ok = True
                public_msg = "Acesso online direto liberado (Qualquer pessoa com o link)"
    except Exception as e:
        public_msg = str(e)

    # Teste de Service Account (Google Sheets)
    sa_ok = False
    sa_msg = ""
    if has_creds:
        try:
            m = google_sync.fetch_members_via_service_account(creds_path)
            if m:
                sa_ok = True
                sa_msg = f"Autenticado com sucesso via Service Account ({len(m)} praticantes lidos da aba 'Nafudakake')"
        except Exception as e:
            sa_msg = str(e)

    # Teste de Pasta do Google Drive
    drive_ok = False
    drive_msg = ""
    if has_creds:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            drive_creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=["https://www.googleapis.com/auth/drive"]
            )
            drive_service = build("drive", "v3", credentials=drive_creds)
            folder_info = drive_service.files().get(
                fileId=google_sync.DRIVE_FOLDER_ID_DEFAULT,
                fields="id, name, capabilities"
            ).execute()
            can_add_children = folder_info.get("capabilities", {}).get("canAddChildren", False)
            if can_add_children:
                drive_ok = True
                drive_msg = f"Acesso confirmado à pasta '{folder_info.get('name')}' como Editor."
            else:
                drive_msg = f"Pasta encontrada ('{folder_info.get('name')}'), mas sem permissão de escrita/Editor."
        except Exception as e:
            err_str = str(e)
            if "File not found" in err_str or "notFound" in err_str:
                drive_msg = (
                    f"A pasta '{google_sync.DRIVE_FOLDER_ID_DEFAULT}' ainda NÃO foi compartilhada com a Conta de Serviço "
                    f"({service_email}). No Google Drive, o Google oculta pastas não compartilhadas retornando 'File not found'."
                )
            else:
                drive_msg = str(e)

    _, active_source = google_sync.get_members_data()

    return jsonify({
        "spreadsheet_id": google_sync.SPREADSHEET_ID_DEFAULT,
        "sheet_gid": google_sync.SHEET_GID_DEFAULT,
        "public_url_ok": public_ok,
        "public_url_msg": public_msg,
        "service_account_configured": has_creds,
        "service_account_email": service_email,
        "service_account_ok": sa_ok,
        "service_account_msg": sa_msg,
        "drive_folder_id": google_sync.DRIVE_FOLDER_ID_DEFAULT,
        "drive_folder_ok": drive_ok,
        "drive_folder_msg": drive_msg,
        "active_source": active_source
    })


@app.route("/api/upload-credentials", methods=["POST"])
def api_upload_credentials():
    """Recebe e valida o arquivo credentials.json da Service Account."""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "Nenhum arquivo enviado."}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "Nome de arquivo inválido."}), 400

        content = file.read().decode("utf-8")
        parsed = json.loads(content)
        if "type" not in parsed or parsed["type"] != "service_account":
            return jsonify({"success": False, "error": "O arquivo JSON enviado não é uma chave válida de 'service_account'."}), 400

        target_path = "credentials.json"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        client_email = parsed.get("client_email", "desconhecido")
        return jsonify({
            "success": True,
            "message": f"Credenciais salvas com sucesso! E-mail da Conta de Serviço: {client_email}",
            "client_email": client_email
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Falha ao processar credenciais: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"=====================================================")
    print(f"   NAFUDAKAKE DIGITAL - ASSOCIAÇÃO KAGAWA DE KENDO   ")
    print(f"   Servidor iniciado em: http://localhost:{port}     ")
    print(f"=====================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
