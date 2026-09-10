import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

def parse_weight_and_shogo(grad_raw: str):
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

    # Peso final: ex: 7o Dan Kyoshi = 72; 7o Dan Renshi = 71; 7o Dan = 70
    total_weight = base_weight + shogo_bonus if base_weight >= 50 else base_weight
    return base_weight, total_weight, shogo_name

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)
res = service.spreadsheets().values().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA', range='Kenshis!A3:ZZ400').execute()
rows = res.get('values', [])
headers = rows[0]

def extract_modality(rows, headers, modality='kendo'):
    grad_col = 12 if modality == 'kendo' else 15
    results = []
    
    for r in rows[1:]:
        if len(r) <= grad_col:
            continue
        inativo = r[0].strip().upper() if len(r) > 0 else 'FALSE'
        if inativo == 'TRUE':
            continue
            
        grad = r[grad_col].strip()
        if not grad or grad.lower() in ('não pratica', 'nao pratica', '-', 'none', 'false'):
            continue
            
        nome_completo = r[2].strip() if len(r) > 2 else ''
        nome_abrev = r[68].strip() if len(r) > 68 and r[68].strip() else nome_completo
        jap = r[69].strip() if len(r) > 69 else ''
        
        base_w, total_w, shogo = parse_weight_and_shogo(grad)
        
        # Obter data de graduação correspondente ao Dan atual
        # Procurar na linha pelas colunas de datas
        exam_date = ""
        # Mapeamento do nome da coluna de Dan
        dan_search_str = f"{base_w // 10}o dan {modality}" if base_w >= 10 else f"ikkyu {modality}"
        for c_idx, h_name in enumerate(headers):
            if dan_search_str in h_name.lower():
                if c_idx < len(r) and r[c_idx].strip() not in ('?', '-', '', 'None'):
                    exam_date = r[c_idx].strip()
                break

        results.append({
            'nome': nome_abrev,
            'nome_completo': nome_completo,
            'jap': jap,
            'graduacao': grad,
            'base_weight': base_w,
            'peso': total_w,
            'shogo': shogo,
            'exam_date': exam_date
        })
        
    # Ordenar por: peso decrescente, depois data (se disponível)
    results.sort(key=lambda x: x['peso'], reverse=True)
    return results

kendo_list = extract_modality(rows, headers, 'kendo')
iaido_list = extract_modality(rows, headers, 'iaido')

print(f"Kendo atletas ativos encontrados: {len(kendo_list)}")
print(f"Iaido atletas ativos encontrados: {len(iaido_list)}")

print("\nTop 10 Kendo:")
for k in kendo_list[:10]:
    print(f"  {k['peso']} | {k['graduacao']} | {k['nome']} ({k['jap']})")

print("\nTop 10 Iaido:")
for i in iaido_list[:10]:
    print(f"  {i['peso']} | {i['graduacao']} | {i['nome']} ({i['jap']})")
