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
