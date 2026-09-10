from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
res_kenshis = sheet.values().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA', range='Kenshis!A1:BR2').execute()
headers = res_kenshis.get('values', [])[0]
print(f"Total columns in Kenshis: {len(headers)}")
for i, h in enumerate(headers):
    if any(term in h.lower() for term in ['iaido', 'kendo', 'jodo', 'gradua', 'dan', 'nome', 'japon', 'shogo', 'status', 'ativo', 'modalidade']):
        print(f"Col {i+1} ({chr(65 + i % 26)}): {h}")
