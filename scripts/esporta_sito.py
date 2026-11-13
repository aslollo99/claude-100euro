"""Copia i numeri veri dell'agente dentro sito/data, cosi' la pagina li mostra."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import config as C, stato, donazioni

dati = {
    "giorno": max(stato.giorno_corrente(), 0), "checkpoint": C.GIORNO_CHECKPOINT, "fine": C.GIORNO_FINE,
    "cassa": stato.saldo_cassa(), "soglia": C.SOGLIA_SOPRAVVIVENZA_EUR,
    "speso_api": stato.costi()["totale_eur"], "donazioni": donazioni.totale_donazioni(),
    "link_donazioni": os.environ.get("LINK_DONAZIONI", ""),
    "stato": "spento" if (C.ROOT / "STOP").exists() else "in vita",
    "repo": "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "aslollo99/claude-100euro"),
    "aggiornato": stato.ora_iso(),
}
out = C.ROOT / "sito" / "data"; out.mkdir(parents=True, exist_ok=True)
(out / "stato.json").write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")
if (C.STATE / "diario.md").exists():
    shutil.copy(C.STATE / "diario.md", out / "diario.md")
print(dati)
