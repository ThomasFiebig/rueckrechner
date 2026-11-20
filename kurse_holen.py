# Holt Gold- und Silberkurs in Euro je Unze von goldprice.dev und schreibt kurse.json
import json, os, urllib.request

KEY = os.environ.get('GOLDPRICE_KEY', '')

def preis(symbol):
    req = urllib.request.Request('https://api.goldprice.dev/v1/prices?symbol=' + symbol,
                                 headers={'X-API-Key': KEY} if KEY else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        daten = json.load(r)['symbols']
    return (float(daten[0]['price']), daten[0]['computed_at']) if daten else (None, None)

gold, stand = preis('XAU-EUR-SPOT')
silber, _ = preis('XAG-EUR-SPOT')
if silber is None:
    # Silber in Euro über das Gold-Silber-Verhältnis in Dollar
    xag, _ = preis('XAG-USD-SPOT')
    xau, _ = preis('XAU-USD-SPOT')
    silber = xag * gold / xau
assert 500 < gold < 20000 and 5 < silber < 500, (gold, silber)

json.dump({'gold': round(gold, 2), 'silber': round(silber, 2), 'stand': stand, 'quelle': 'goldprice.dev'},
          open('kurse.json', 'w'), indent=1)
print('Gold', round(gold, 2), 'Silber', round(silber, 2), 'Stand', stand)

# Jahreswerte für das Gold-Quiz (quiz/index.html): Der Kurs des laufenden Jahres wird bei jedem Lauf überschrieben,
# der letzte Lauf im Dezember bleibt als Jahresschlusskurs stehen. Dazu Inflation Deutschland ab 2026 von Eurostat
# (HVPI, nur als Ersatz für Jahre, die in der Destatis-Tabelle im Quiz noch fehlen). Fehler hier stoppen nie die Kurse.
try:
    import datetime
    try:
        jw = json.load(open('jahreswerte.json'))
    except Exception:
        jw = {}
    jw.setdefault('gold', {})[str(datetime.date.fromisoformat(stand[:10]).year if stand else datetime.date.today().year)] = round(gold, 2)
    try:
        url = ('https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind'
               '?format=JSON&geo=DE&coicop=CP00&unit=RCH_A_AVG&sinceTimePeriod=2026')
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.load(r)
        werte = d.get('value', {})
        for jahr, i in d['dimension']['time']['category']['index'].items():
            v = werte.get(str(i))
            if v is not None and -5 < v < 30:
                jw.setdefault('inflation', {})[jahr] = v
    except Exception as e:
        print('Inflation nicht abrufbar:', e)
    jw['hinweis'] = 'Automatisch von kurse_holen.py gepflegt. gold = Euro je Unze, letzter Stand des Jahres; inflation = HVPI Deutschland in %.'
    json.dump(jw, open('jahreswerte.json', 'w'), indent=1, sort_keys=True)
    print('Jahreswerte', jw.get('gold'), jw.get('inflation'))
except Exception as e:
    print('Jahreswerte nicht geschrieben:', e)
