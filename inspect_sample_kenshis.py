import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)

res = service.spreadsheets().values().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA', range='Kenshis!A3:BR30').execute()
rows = res.get('values', [])
header = rows[0]

target_names = ['Tadao Ebihara', 'Adrian Yoneda', 'Setsuo Fukamizu', 'Eduardo Muzzette', 'Aurea Kojima']

for r in rows[1:]:
    nome = r[2] if len(r) > 2 else ''
    if any(t.lower() in nome.lower() for t in target_names):
        print(f"\nNome: {nome} (Inativo: {r[0] if len(r)>0 else ''})")
        print(f"  Nome abrev: {r[68] if len(r)>68 else ''} | Japonês: {r[69] if len(r)>69 else ''}")
        print(f"  Grad Kendo (Col 13): {r[12] if len(r)>12 else ''}")
        print(f"  Grad Iaido (Col 16): {r[15] if len(r)>15 else ''}")
        print(f"  Datas Kendo:")
        for idx in range(18, 30):
            if idx < len(r) and r[idx]:
                print(f"    {header[idx]}: {r[idx]}")
        print(f"  Datas Iaido:")
        for idx in range(30, 42):
            if idx < len(r) and r[idx]:
                print(f"    {header[idx]}: {r[idx]}")
