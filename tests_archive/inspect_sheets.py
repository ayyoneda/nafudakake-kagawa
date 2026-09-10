from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)
meta = service.spreadsheets().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA').execute()
print('Spreadsheet Title:', meta.get('properties', {}).get('title'))
print('Sheets in spreadsheet:')
for s in meta.get('sheets', []):
    p = s.get('properties', {})
    print(f"  - Title: {p.get('title')}, SheetId (gid): {p.get('sheetId')}, rowCount: {p.get('gridProperties', {}).get('rowCount')}, colCount: {p.get('gridProperties', {}).get('columnCount')}")
