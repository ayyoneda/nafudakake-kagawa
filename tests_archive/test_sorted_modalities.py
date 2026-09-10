import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
from test_kenshis_extraction import extract_modality, rows, headers
from test_date_parser import parse_date_sort_key

k_list = extract_modality(rows, headers, 'kendo')
k_list.sort(key=lambda x: (-x['peso'], parse_date_sort_key(x['exam_date']), x['nome']))

print("Top 10 Kendo with date sorting:")
for idx, k in enumerate(k_list[:10]):
    print(f"{idx+1}: {k['peso']} | {k['graduacao']} | {k['exam_date']} | {k['nome']} ({k['jap']})")

i_list = extract_modality(rows, headers, 'iaido')
i_list.sort(key=lambda x: (-x['peso'], parse_date_sort_key(x['exam_date']), x['nome']))

print("\nTop 10 Iaido with date sorting:")
for idx, i in enumerate(i_list[:10]):
    print(f"{idx+1}: {i['peso']} | {i['graduacao']} | {i['exam_date']} | {i['nome']} ({i['jap']})")
