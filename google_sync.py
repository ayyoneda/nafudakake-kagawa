"""
Módulo de Integração com Google Cloud (Google Sheets e Google Drive)
Associação Kagawa de Kendo - 洗心香武館

Lê dados diretamente da aba mestre 'Kenshis' do Google Sheets para Kendo e Iaido,
aplica hierarquia oficial de Dans, Shogo e antiguidade, e publica os arquivos
vetoriais e rasterizados diretamente no Google Drive do dojo.
"""

import os
import sys
import csv
import io
import re
import json
import urllib.request
from typing import List, Dict, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SPREADSHEET_ID_DEFAULT = "1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA"
SHEET_GID_DEFAULT = "1448812233"
DRIVE_FOLDER_ID_DEFAULT = "1gbzJWLZWGbTqYXSX419Lsuzbe6TTASC_"
CREDENTIALS_FILE_DEFAULT = "credentials.json"
LOCAL_CSV_DEFAULT = "Cadastro - Atletas Kagawa (respostas) - Nafudakake.csv"

# Meses abreviados para ordenação de datas de exames
MONTHS_MAP = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

DAN_RANK_ORDER = {
    "8o dan": 80, "8º dan": 80,
    "7o dan": 70, "7º dan": 70,
    "6o dan": 60, "6º dan": 60,
    "5o dan": 50, "5º dan": 50,
    "4o dan": 40, "4º dan": 40,
    "3o dan": 30, "3º dan": 30,
    "2o dan": 20, "2º dan": 20,
    "1o dan": 10, "1º dan": 10, "shodan": 10,
    "ikkyu": 1, "1º kyu": 1, "1o kyu": 1,
    "sem graduação": 0, "sem graduacao": 0, "iniciante": 0
}


def parse_date_sort_key(date_str: str) -> Tuple[int, int, int]:
    """Converte qualquer string de data da planilha em uma tupla ordenável (ano, mês, dia)."""
    if not date_str or date_str in ('?', '-', 'None', '#N/A', ''):
        return (9999, 12, 31)

    s = str(date_str).strip().lower()

    # Formato ISO: YYYY-MM-DD
    m_iso = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m_iso:
        return (int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))

    # Formato BR: DD/MM/YYYY
    m_br = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m_br:
        return (int(m_br.group(3)), int(m_br.group(2)), int(m_br.group(1)))

    # Formato mês/ano abreviado (ex: jul./01, jan./85, set./25)
    m_abr = re.match(r'^([a-z]{3})\.?/(\d{2,4})', s)
    if m_abr:
        mon = MONTHS_MAP.get(m_abr.group(1), 6)
        yr_val = int(m_abr.group(2))
        yr = (1900 + yr_val) if yr_val >= 30 else (2000 + yr_val) if yr_val < 100 else yr_val
        return (yr, mon, 1)

    # Apenas 4 dígitos de ano (ex: 2018)
    m_yr = re.match(r'^(\d{4})', s)
    if m_yr:
        return (int(m_yr.group(1)), 6, 1)

    return (9999, 12, 31)


def parse_graduacao_info(grad_raw: str) -> Tuple[int, int, Optional[str]]:
    """
    Retorna (base_weight, total_weight, shogo_str).
    Exemplos:
      '7o Dan Kyoshi' -> (70, 72, '教士')
      '7o Dan Renshi' -> (70, 71, '錬士')
      '5o Dan'        -> (50, 50, None)
    """
    g_clean = grad_raw.strip().lower()
    shogo_bonus = 0
    shogo_name = None
    if "hanshi" in g_clean or "範士" in grad_raw:
        shogo_bonus = 3
        shogo_name = "範士"
    elif "kyoshi" in g_clean or "教士" in grad_raw:
        shogo_bonus = 2
        shogo_name = "教士"
    elif "renshi" in g_clean or "錬士" in grad_raw:
        shogo_bonus = 1
        shogo_name = "錬士"

    base_weight = 0
    for k, w in DAN_RANK_ORDER.items():
        if k in g_clean:
            base_weight = w
            break

    total_weight = (base_weight + shogo_bonus) if base_weight >= 50 else base_weight
    return base_weight, total_weight, shogo_name


def get_credentials_path() -> Optional[str]:
    """Retorna o caminho do arquivo de credenciais se existir."""
    env_file = os.getenv("GOOGLE_CREDENTIALS_FILE", CREDENTIALS_FILE_DEFAULT)
    if os.path.isfile(env_file):
        return env_file
    if os.path.isfile(CREDENTIALS_FILE_DEFAULT):
        return CREDENTIALS_FILE_DEFAULT
    return None


def fetch_from_kenshis_sheet(
    creds_path: str,
    modalidade: str = "kendo",
    spreadsheet_id: str = SPREADSHEET_ID_DEFAULT
) -> List[Dict[str, str]]:
    """
    Lê DIRETAMENTE a aba mestra 'Kenshis' do Google Sheets, sem intermediários.
    Filtra os membros ativos e ordena por hierarquia de graduação e antiguidade.
    """
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)

    res = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Kenshis!A3:ZZ400"
    ).execute()

    rows = res.get("values", [])
    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    mod = modalidade.lower()
    grad_col = 12 if mod == "kendo" else 15

    raw_items = []
    for r in rows[1:]:
        if len(r) <= grad_col:
            continue

        inativo = r[0].strip().upper() if len(r) > 0 else "FALSE"
        if inativo == "TRUE":
            continue

        grad = r[grad_col].strip()
        if not grad or grad.lower() in ("não pratica", "nao pratica", "-", "none", "false"):
            continue

        nome_completo = r[2].strip() if len(r) > 2 else ""
        data_nasc = r[3].strip() if len(r) > 3 else ""
        idade_str = r[9].strip() if len(r) > 9 else ""
        nome_abrev = r[68].strip() if (len(r) > 68 and r[68].strip()) else nome_completo
        jap = r[69].strip() if len(r) > 69 else ""

        base_w, total_w, shogo = parse_graduacao_info(grad)

        # Buscar data do Dan atual para critério de desempate
        exam_date = ""
        dan_search = f"{base_w // 10}o dan {mod}" if base_w >= 10 else f"ikkyu {mod}"
        for c_idx, h_name in enumerate(headers):
            if dan_search in h_name.lower():
                if c_idx < len(r) and r[c_idx].strip() not in ('?', '-', '', 'None'):
                    exam_date = r[c_idx].strip()
                break

        raw_items.append({
            "Nome abreviado": nome_abrev,
            "Nome completo": nome_completo,
            "Japonês": jap,
            "Graduação": grad,
            "Peso": str(total_w),
            "base_weight": base_w,
            "total_weight": total_w,
            "Shogo": shogo or "",
            "Data Graduação": exam_date,
            "Data Nascimento": data_nasc,
            "Idade": idade_str
        })

    # Ordenação estrita tradicional do Dojo:
    # 1º: Peso total decrescente (Dan + Shogo)
    # 2º: Data de exame mais antiga primeiro (antiguidade no Dan)
    # 3º: Data de nascimento mais antiga primeiro (maior idade tem precedência na mesma data)
    # 4º: Ordem alfabética pelo nome abreviado
    raw_items.sort(key=lambda x: (
        -x["total_weight"],
        parse_date_sort_key(x["Data Graduação"]),
        parse_date_sort_key(x["Data Nascimento"]),
        x["Nome abreviado"]
    ))

    # Atribuir o número de ordem e formatar o dicionário padronizado
    formatted_members = []
    for idx, item in enumerate(raw_items):
        item["Ordem"] = str(idx + 1)
        formatted_members.append(item)

    # Salvar snapshot local em cache JSON para contingência offline
    try:
        cache_file = f"cache_{mod}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(formatted_members, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return formatted_members


def fetch_members_from_local_csv(csv_path: str = LOCAL_CSV_DEFAULT) -> List[Dict[str, str]]:
    """Lê membros a partir do arquivo CSV local de fallback."""
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Arquivo CSV local não encontrado: {csv_path}")

    members = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            members.append(dict(row))
    return members


def fetch_members_from_local_cache(modalidade: str = "kendo") -> List[Dict[str, str]]:
    """Lê o cache JSON local da modalidade se disponível."""
    cache_file = f"cache_{modalidade.lower()}.json"
    if os.path.isfile(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def get_members_data(modalidade: str = "kendo") -> Tuple[List[Dict[str, str]], str]:
    """
    Obtém os membros com estratégia de leitura inteligente:
    1. Leitura direta da aba mestre 'Kenshis' via Service Account (tempo real).
    2. Cache JSON local da modalidade.
    3. Arquivo CSV local (contingência garantida).
    """
    mod = modalidade.lower()
    creds_file = get_credentials_path()

    if creds_file:
        try:
            members = fetch_from_kenshis_sheet(creds_file, modalidade=mod)
            if members:
                mod_name = "Kendo" if mod == "kendo" else "Iaido"
                return members, f"Google Sheets (Aba Kenshis - {mod_name} em Tempo Real)"
        except Exception as e:
            print(f"[Aviso] Falha ao ler aba Kenshis via Service Account: {e}")

    # Fallback para cache local da modalidade
    cached = fetch_members_from_local_cache(mod)
    if cached:
        return cached, f"Cache Local ({mod.upper()})"

    # Fallback para CSV local (apenas para Kendo)
    if mod == "kendo":
        try:
            members = fetch_members_from_local_csv()
            return members, f"Arquivo Local ({os.path.basename(LOCAL_CSV_DEFAULT)})"
        except Exception:
            pass

    return [], "Nenhum dado encontrado"


def upload_to_google_drive(
    file_path: str,
    folder_id: str = DRIVE_FOLDER_ID_DEFAULT,
    mime_type: Optional[str] = None
) -> Dict[str, str]:
    """
    Faz upload ou atualiza um arquivo na pasta especificada do Google Drive.
    Requer arquivo credentials.json com permissão de Drive.
    """
    creds_file = get_credentials_path()
    if not creds_file:
        raise RuntimeError("Arquivo 'credentials.json' não encontrado para upload no Google Drive.")

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    scopes = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(creds_file, scopes=scopes)
    service = build("drive", "v3", credentials=creds)

    filename = os.path.basename(file_path)
    if mime_type is None:
        if filename.endswith(".svg"):
            mime_type = "image/svg+xml"
        elif filename.endswith(".png"):
            mime_type = "image/png"
        else:
            mime_type = "application/octet-stream"

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        # Procurar por arquivos existentes (aceita nome exato ou variantes de nomes)
        # ex: Nafudakake_Kendo.svg ou Nafudakake_Kagawa.svg ou Nafudakake_Realista.svg
        possible_names = [filename]
        if "Kendo" in filename:
            possible_names.append(filename.replace("Kendo", "Kagawa"))
            possible_names.append(filename.replace("Kendo", "Realista"))
        elif "Realista" in filename:
            possible_names.append(filename.replace("Realista", "Kagawa"))
            possible_names.append(filename.replace("Realista", "Kendo"))

        names_query = " or ".join([f"name = '{n}'" for n in possible_names])
        query = f"'{folder_id}' in parents and ({names_query}) and trashed = false"

        response = service.files().list(q=query, spaces="drive", fields="files(id, name, webViewLink)").execute()
        files = response.get("files", [])

        if files:
            file_id = files[0]["id"]
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields="id, name, webViewLink"
            ).execute()
            return {
                "status": "updated",
                "file_id": updated_file.get("id"),
                "file_name": files[0]["name"],
                "webViewLink": updated_file.get("webViewLink", "")
            }
        else:
            file_metadata = {
                "name": filename,
                "parents": [folder_id]
            }
            try:
                created_file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, name, webViewLink"
                ).execute()
                return {
                    "status": "created",
                    "file_id": created_file.get("id"),
                    "file_name": filename,
                    "webViewLink": created_file.get("webViewLink", "")
                }
            except Exception as create_err:
                err_str = str(create_err)
                if "storage quota" in err_str or "storageQuotaExceeded" in err_str:
                    raise PermissionError(
                        f"O Google Drive bloqueou a criação de um arquivo NOVO ('{filename}') pela Conta de Serviço "
                        f"porque robôs não possuem cota de armazenamento própria em contas pessoais do Gmail.\n\n"
                        f"👉 SOLUÇÃO SIMPLES (1 minuto):\n"
                        f"Abra a pasta do Nafudakake no Google Drive e faça o upload inicial do arquivo '{filename}' "
                        f"(ou baixe pelo botão 'Exportar Imagem PNG' e arraste para a pasta).\n"
                        f"Assim que o arquivo existir lá com você como dono, o botão 'Publicar no Google Drive' "
                        f"conseguirá atualizá-lo automaticamente todas as vezes!"
                    )
                raise create_err
    except Exception as e:
        err_str = str(e)
        if "File not found" in err_str or "notFound" in err_str:
            sa_email = "sua conta de serviço"
            try:
                with open(creds_file, "r", encoding="utf-8") as f:
                    sa_email = json.load(f).get("client_email", sa_email)
            except Exception:
                pass
            raise PermissionError(
                f"A pasta de destino no Google Drive não está compartilhada com a Conta de Serviço. "
                f"Por favor, abra a pasta no Google Drive, clique em Compartilhar e adicione o e-mail '{sa_email}' com permissão de Editor."
            )
        raise e


if __name__ == "__main__":
    print("--- Testando Leitura Direta de Kenshis ---")
    data_kendo, src_kendo = get_members_data("kendo")
    print(f"Kendo ({src_kendo}): {len(data_kendo)} atletas")
    if data_kendo:
        print("  1º Kendo:", data_kendo[0]["Nome abreviado"], data_kendo[0]["Graduação"])

    data_iaido, src_iaido = get_members_data("iaido")
    print(f"Iaido ({src_iaido}): {len(data_iaido)} atletas")
    if data_iaido:
        print("  1º Iaido:", data_iaido[0]["Nome abreviado"], data_iaido[0]["Graduação"])
