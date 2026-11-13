"""Client Etsy Open API v3 (Seller App, solo il negozio di Lorenzo). OAuth2 con PKCE."""
import base64
import hashlib
import os
import re
import secrets
import time
from urllib.parse import urlencode

import requests

from . import config as C
from . import stato, umano

TITOLO_AUTH = "Autorizza l'agente sul negozio Etsy (un clic)"


def _keystring():
    return os.environ.get("ETSY_KEYSTRING", "")


def _api_key_header():
    ks, sh = _keystring(), os.environ.get("ETSY_SHARED_SECRET", "")
    return f"{ks}:{sh}" if sh else ks


def configurato():
    return bool(_keystring())


def _token():
    s = stato.leggi_segreti()
    t = s.get("etsy")
    if not t:
        return None
    if t["scade"] - time.time() < 120:
        r = requests.post(C.ETSY_TOKEN_URL, timeout=30, data={
            "grant_type": "refresh_token", "client_id": _keystring(), "refresh_token": t["refresh_token"]})
        if r.status_code != 200:
            s.pop("etsy", None)
            stato.scrivi_segreti(s)
            return None
        j = r.json()
        t = {"access_token": j["access_token"], "refresh_token": j["refresh_token"],
             "scade": time.time() + j["expires_in"], "user_id": j["access_token"].split(".")[0],
             "shop_id": t.get("shop_id")}
        s["etsy"] = t
        stato.scrivi_segreti(s)
    return t


def gestisci_autorizzazione():
    """Da chiamare a ogni ciclo. Ritorna (pronto: bool, nota: str)."""
    if not configurato():
        return False, "ETSY_KEYSTRING non impostato nei secret del repository"
    if _token():
        return True, "Etsy collegato"
    s = stato.leggi_segreti()
    pk = s.get("etsy_pkce")
    # 1) c'e' una richiesta aperta: cerco il codice nelle risposte di Lorenzo
    for issue in umano.richieste_aperte():
        if issue["titolo"] != TITOLO_AUTH or not pk:
            continue
        for c in umano.risposte(issue["numero"]):
            m = re.search(r"[?&]code=([^&\s]+)", c["testo"])
            if not m:
                continue
            r = requests.post(C.ETSY_TOKEN_URL, timeout=30, data={
                "grant_type": "authorization_code", "client_id": _keystring(),
                "redirect_uri": C.ETSY_REDIRECT_URI, "code": m.group(1), "code_verifier": pk["verifier"]})
            if r.status_code == 200:
                j = r.json()
                uid = j["access_token"].split(".")[0]
                s["etsy"] = {"access_token": j["access_token"], "refresh_token": j["refresh_token"],
                             "scade": time.time() + j["expires_in"], "user_id": uid}
                s.pop("etsy_pkce", None)
                stato.scrivi_segreti(s)
                shop = chiama("GET", f"/application/users/{uid}/shops")
                s["etsy"]["shop_id"] = shop.get("shop_id")
                stato.scrivi_segreti(s)
                umano.chiudi(issue["numero"], "Fatto, negozio collegato. Grazie!")
                return True, "Etsy appena collegato"
            umano.chiudi(issue["numero"], f"Il codice non ha funzionato ({r.status_code}). Ne apro una nuova.")
            s.pop("etsy_pkce", None)
            stato.scrivi_segreti(s)
            pk = None
        if pk:
            return False, "In attesa che Lorenzo autorizzi Etsy (richiesta aperta)"
    # 2) nessuna richiesta valida: ne creo una nuova
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    s["etsy_pkce"] = {"verifier": verifier}
    stato.scrivi_segreti(s)
    url = C.ETSY_AUTH_URL + "?" + urlencode({
        "response_type": "code", "redirect_uri": C.ETSY_REDIRECT_URI, "scope": C.ETSY_SCOPES,
        "client_id": _keystring(), "state": secrets.token_hex(8), "code_challenge": challenge,
        "code_challenge_method": "S256"})
    umano.apri_richiesta(TITOLO_AUTH, (
        f"1. Apri questo link (devi essere loggato su Etsy): {url}\n"
        "2. Clicca **Consenti accesso**.\n"
        "3. Finirai su una pagina (anche se sembra un errore va bene): copia l'indirizzo completo dalla barra "
        "del browser e incollalo come commento qui sotto. Il resto lo faccio io al prossimo risveglio."))
    return False, "Richiesta di autorizzazione Etsy inviata a Lorenzo"


def _h():
    t = _token()
    if not t:
        raise RuntimeError("Etsy non collegato")
    return {"x-api-key": _api_key_header(), "Authorization": f"Bearer {t['access_token']}"}


def shop_id():
    t = _token()
    return t.get("shop_id") if t else None


def chiama(metodo, percorso, params=None, json=None, form=None):
    """Chiamata generica. percorso relativo a /v3, es. /application/shops/{shop_id}/listings"""
    percorso = percorso.replace("{shop_id}", str(shop_id() or ""))
    r = requests.request(metodo, C.ETSY_API + percorso, headers=_h(), params=params, json=json, data=form, timeout=60)
    try:
        corpo = r.json()
    except ValueError:
        corpo = {"testo": r.text[:2000]}
    if r.status_code >= 400:
        return {"errore": r.status_code, "dettaglio": corpo}
    return corpo


def carica_immagine(listing_id, percorso_file, rank=1):
    with open(percorso_file, "rb") as f:
        r = requests.post(f"{C.ETSY_API}/application/shops/{shop_id()}/listings/{listing_id}/images",
                          headers=_h(), files={"image": f}, data={"rank": rank}, timeout=120)
    return r.json() if r.ok else {"errore": r.status_code, "dettaglio": r.text[:1500]}


def carica_file_digitale(listing_id, percorso_file, nome, rank=1):
    with open(percorso_file, "rb") as f:
        r = requests.post(f"{C.ETSY_API}/application/shops/{shop_id()}/listings/{listing_id}/files",
                          headers=_h(), files={"file": (nome, f)}, data={"name": nome, "rank": rank}, timeout=120)
    return r.json() if r.ok else {"errore": r.status_code, "dettaglio": r.text[:1500]}


def sincronizza_vendite():
    """Registra in cassa le vendite nuove (incasso lordo e commissioni stimate). Ritorna le nuove."""
    if not shop_id():
        return []
    j = chiama("GET", "/application/shops/{shop_id}/receipts", params={"limit": 100, "was_paid": "true"})
    nuove = []
    for rc in j.get("results", []):
        tot = rc.get("grandtotal") or rc.get("total_price") or {}
        lordo = tot.get("amount", 0) / max(tot.get("divisor", 100), 1)
        rif = f"etsy-{rc['receipt_id']}"
        if stato.registra_movimento(f"Vendita Etsy #{rc['receipt_id']}", lordo, rif=rif):
            stato.registra_movimento(f"Commissioni Etsy stimate #{rc['receipt_id']}",
                                     -(lordo * C.ETSY_FEE_PCT + C.ETSY_FEE_FISSA_EUR), rif=rif + "-fee")
            nuove.append({"ordine": rc["receipt_id"], "lordo": lordo})
    return nuove
