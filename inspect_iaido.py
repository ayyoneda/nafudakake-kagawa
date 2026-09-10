from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)

res = service.spreadsheets().values().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA', range='Kenshis!A3:ZZ300').execute()
rows = res.get('values', [])
if not rows:
    print("No rows found")
    exit()

header = rows[0]
iaido_members = []
for r in rows[1:]:
    if len(r) > 15:
        inativo = r[0].strip().upper() if len(r) > 0 else 'FALSE'
        nome = r[2] if len(r) > 2 else ''
        kendo_grad = r[12] if len(r) > 12 else ''
        iaido_grad = r[15] if len(r) > 15 else ''
        nome_abrev = r[68] if len(r) > 68 else nome
        jap = r[69] if len(r) > 69 else ''
        
        # Filtrar se pratica Iaido
        if iaido_grad and iaido_grad.strip().lower() not in ('não pratica', 'nao pratica', '-', '', 'none', 'false'):
            iaido_members.append({
                'inativo': inativo,
                'nome': nome,
                'nome_abrev': nome_abrev,
                'jap': jap,
                'kendo': kendo_grad,
                'iaido': iaido_grad
            })

print(f"Total que praticam Iaido na base: {len(iaido_members)}")
for m in iaido_members:
    print(f"  {m['nome_abrev']} - Iaido: {m['iaido']} | Kendo: {m['kendo']} | Inativo: {m['inativo']}")
