from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/script.projects.readonly']
)
try:
    service = build('drive', 'v3', credentials=creds)
    res = service.files().list(q="mimeType = 'application/vnd.google-apps.script'", fields='files(id, name, parents)').execute()
    print('Scripts found in Drive:', res.get('files', []))
except Exception as e:
    print('Drive search error:', e)
