"""Stato persistente dell'agente: cassa, costi API, token cifrati, diario."""
import base64
import hashlib
import json
import os
from datetime import datetime, timezone

from cryptography.fernet import Fernet

from . import config as C


def _leggi(nome, default):
    p = C.STATE / nome
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def _scrivi(nome, dati):
    C.STATE.mkdir(exist_ok=True)
    (C.STATE / nome).write_text(json.dumps(dati, indent=2, ensure_ascii=False), encoding="utf-8")


def ora_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def giorno_corrente():
    return (datetime.now(timezone.utc).date() - C.DATA_INIZIO).days


# ---------------- Cassa
def cassa():
    return _leggi("cassa.json", {"movimenti": [
        {"data": "2026-11-13", "voce": "Capitale iniziale da Lorenzo", "importo": C.CAPITALE_INIZIALE_EUR, "rif": "capitale"}
    ]})


def registra_movimento(voce, importo, rif=None):
    """importo > 0 entrata, < 0 uscita. rif evita doppioni (es. id ordine Etsy)."""
    c = cassa()
    if rif and any(m.get("rif") == rif for m in c["movimenti"]):
        return False
    c["movimenti"].append({"data": ora_iso()[:10], "voce": voce, "importo": round(float(importo), 2), "rif": rif})
    _scrivi("cassa.json", c)
    return True


def saldo_cassa():
    return round(sum(m["importo"] for m in cassa()["movimenti"]), 2)


# ---------------- Costi del cervello
def costi():
    return _leggi("costi_api.json", {"totale_eur": 0.0, "cicli": []})


def aggiungi_costo_ciclo(modello, usage_tot, eur):
    c = costi()
    c["totale_eur"] = round(c["totale_eur"] + eur, 4)
    c["cicli"].append({"quando": ora_iso(), "modello": modello, "uso": usage_tot, "eur": round(eur, 4)})
    c["cicli"] = c["cicli"][-200:]
    _scrivi("costi_api.json", c)


def credito_api_residuo():
    return round(C.CREDITO_API_EUR - costi()["totale_eur"], 2)


# ---------------- Segreti cifrati nel repo (token che ruotano: Etsy)
def _fernet():
    seme = os.environ.get("ETSY_SHARED_SECRET") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not seme:
        raise RuntimeError("manca un segreto per cifrare i token")
    chiave = base64.urlsafe_b64encode(hashlib.sha256(("100euro:" + seme).encode()).digest())
    return Fernet(chiave)


def leggi_segreti():
    p = C.STATE / "segreti.enc"
    if not p.exists():
        return {}
    return json.loads(_fernet().decrypt(p.read_bytes()).decode())


def scrivi_segreti(d):
    (C.STATE / "segreti.enc").write_bytes(_fernet().encrypt(json.dumps(d).encode()))


# ---------------- Diario
def aggiungi_diario(testo):
    p = C.STATE / "diario.md"
    if not p.exists():
        p.write_text("# Diario dell'agente\n\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"\n## Giorno {giorno_corrente()} — {ora_iso()}\n\n{testo.strip()}\n")


def ultime_voci_diario(n_caratteri=4000):
    p = C.STATE / "diario.md"
    if not p.exists():
        return "(diario vuoto: questo e' il primo ciclo)"
    t = p.read_text(encoding="utf-8")
    return t[-n_caratteri:]
