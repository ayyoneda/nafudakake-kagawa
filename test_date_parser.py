import re
from datetime import datetime

MONTHS = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def parse_date_sort_key(date_str: str):
    if not date_str or date_str in ('?', '-', 'None', '#N/A'):
        return (9999, 12, 31)
    
    date_str = str(date_str).strip().lower()
    
    # Formato ISO: YYYY-MM-DD
    m_iso = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if m_iso:
        return (int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))
        
    # Formato BR: DD/MM/YYYY
    m_br = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if m_br:
        return (int(m_br.group(3)), int(m_br.group(2)), int(m_br.group(1)))
        
    # Formato mês/ano abreviado: jul./01 ou jan./85 ou set./26
    m_abr = re.match(r'([a-z]{3})\.?/(\d{2,4})', date_str)
    if m_abr:
        mon = MONTHS.get(m_abr.group(1), 6)
        yr_val = int(m_abr.group(2))
        # Ajuste de 2 dígitos de ano
        if yr_val < 100:
            # Anos 30-99 -> 1930-1999; Anos 00-29 -> 2000-2029
            yr = 1900 + yr_val if yr_val >= 30 else 2000 + yr_val
        else:
            yr = yr_val
        return (yr, mon, 1)
        
    # Apenas 4 dígitos de ano: 2018
    m_yr = re.match(r'(\d{4})', date_str)
    if m_yr:
        return (int(m_yr.group(1)), 6, 1)
        
    return (9999, 12, 31)

test_dates = ['jul./01', 'jan./85', '2025-09-06', '2018-03-03', 'nov./17', '?', '2006-07-01']
for td in test_dates:
    print(f"{td} -> {parse_date_sort_key(td)}")
