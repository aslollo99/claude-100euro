"""Donazioni tramite Buy Me a Coffee (API ufficiale, token in BMC_TOKEN). Registra in cassa le nuove."""
import os

import requests

from . import stato

COMMISSIONE_STIMATA = 0.10  # 5% Buy Me a Coffee + ~5% elaborazione pagamento (stima)


def configurato():
    return bool(os.environ.get("BMC_TOKEN"))


def sincronizza():
    if not configurato():
        return []
    nuove, url = [], "https://developers.buymeacoffee.com/api/v1/supporters"
    for _ in range(5):
        r = requests.get(url, headers={"Authorization": f"Bearer {os.environ['BMC_TOKEN']}"}, timeout=30)
        if r.status_code != 200:
            break
        j = r.json()
        for s in j.get("data", []):
            lordo = float(s.get("support_coffee_price", 0)) * int(s.get("support_coffees", 1))
            rif = f"bmc-{s['support_id']}"
            nome = s.get("supporter_name") or "anonimo"
            if stato.registra_movimento(f"Donazione di {nome}", lordo, rif=rif):
                stato.registra_movimento("Commissioni donazione (stima)", -lordo * COMMISSIONE_STIMATA, rif=rif + "-fee")
                nuove.append({"da": nome, "euro": lordo, "messaggio": (s.get("support_note") or "")[:300]})
        url = j.get("next_page_url")
        if not url:
            break
    return nuove


def totale_donazioni():
    return round(sum(m["importo"] for m in stato.cassa()["movimenti"]
                     if (m.get("rif") or "").startswith("bmc-") and not m["rif"].endswith("-fee")), 2)
