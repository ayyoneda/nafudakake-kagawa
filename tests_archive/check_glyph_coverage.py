import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
from fontTools.ttLib import TTFont
from google.oauth2 import service_account
from googleapiclient.discovery import build

font = TTFont("epgyobld.ttf")
cmap = font.getBestCmap()

creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
service = build('sheets', 'v4', credentials=creds)

res = service.spreadsheets().values().get(spreadsheetId='1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA', range='Kenshis!A4:ZZ300').execute()
rows = res.get('values', [])

missing_chars = set()
all_chars = set()

for r in rows:
    jap = r[69].strip() if len(r) > 69 else ""
    for ch in jap:
        if ch in (' ', '・', '\t', '\n', '　'):
            continue
        all_chars.add(ch)
        if ord(ch) not in cmap:
            missing_chars.add(ch)

print(f"Total unique Japanese characters in database: {len(all_chars)}")
print(f"Total missing in epgyobld.ttf: {len(missing_chars)}")
if missing_chars:
    print("Missing characters:", "".join(missing_chars))
else:
    print("ALL characters in database exist in epgyobld.ttf!")
