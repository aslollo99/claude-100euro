"""Strumenti che il modello puo' usare durante un ciclo."""
import json
import shutil
import subprocess
import sys

from . import config as C
from . import etsy, instagram, stato, umano

CARTELLE_SCRIVIBILI = ("state", "prodotti", "scripts", "media", "sito")


def _percorso_sicuro(rel):
    p = (C.ROOT / rel).resolve()
    if C.ROOT not in p.parents and p != C.ROOT:
        raise ValueError("percorso fuori dal repository")
    return p


def _tronca(x, n=6000):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + f"\n...[troncato, {len(s)} caratteri totali]"


DEFINIZIONI = [
    {"name": "leggi_file", "description": "Legge un file di testo del repository (percorso relativo alla radice).",
     "input_schema": {"type": "object", "properties": {"percorso": {"type": "string"}}, "required": ["percorso"]}},
    {"name": "scrivi_file", "description": "Crea o sovrascrive un file di testo in state/, sito/, prodotti/, scripts/ o media/. "
     "Usa state/memoria.md per la tua memoria strategica a lungo termine.",
     "input_schema": {"type": "object", "properties": {"percorso": {"type": "string"}, "contenuto": {"type": "string"}},
                      "required": ["percorso", "contenuto"]}},
    {"name": "esegui_python", "description": "Esegue codice Python 3 (timeout 180 s) nella radice del repository. "
     "Disponibili openpyxl, Pillow, matplotlib, requests. Utile per costruire prodotti (xlsx), immagini di anteprima, calcoli.",
     "input_schema": {"type": "object", "properties": {"codice": {"type": "string"}}, "required": ["codice"]}},
    {"name": "anteprima_xlsx", "description": "Fotografa un foglio di un .xlsx come PNG con LibreOffice (base per le foto delle "
     "inserzioni). Indica il foglio da mostrare (es. il cruscotto, non le istruzioni). La prima volta installa LibreOffice (~1-2 min).",
     "input_schema": {"type": "object", "properties": {"xlsx": {"type": "string"}, "png_uscita": {"type": "string"},
                      "foglio": {"type": "string", "description": "nome del foglio da fotografare"}},
                      "required": ["xlsx", "png_uscita"]}},
    {"name": "guarda_immagine", "description": "Ti mostra un'immagine PNG/JPG del repository, per controllare che una foto "
     "d'inserzione o un post sia davvero bello e leggibile prima di pubblicarlo.",
     "input_schema": {"type": "object", "properties": {"percorso": {"type": "string"}}, "required": ["percorso"]}},
    {"name": "etsy_api", "description": "Chiamata all'API Etsy v3 del TUO negozio. percorso relativo a /v3, puoi usare {shop_id}. "
     "Esempi: GET /application/shops/{shop_id}/listings?state=active ; POST /application/shops/{shop_id}/listings (form) per una bozza "
     "con type=download ; PATCH /application/shops/{shop_id}/listings/{id} per aggiornare o attivare (state=active) ; "
     "GET /application/listings/active?keywords=... per studiare la concorrenza. Pubblicare un'inserzione costa 0,20 USD.",
     "input_schema": {"type": "object", "properties": {
         "metodo": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
         "percorso": {"type": "string"}, "params": {"type": "object"}, "json_body": {"type": "object"},
         "form": {"type": "object", "description": "campi form-urlencoded (createDraftListing usa questo)"}},
         "required": ["metodo", "percorso"]}},
    {"name": "etsy_carica_immagine", "description": "Carica un'immagine (jpg/png del repository) su un'inserzione.",
     "input_schema": {"type": "object", "properties": {"listing_id": {"type": "integer"}, "percorso": {"type": "string"},
                      "rank": {"type": "integer"}}, "required": ["listing_id", "percorso"]}},
    {"name": "etsy_carica_file", "description": "Carica il file digitale che il cliente scarica dopo l'acquisto.",
     "input_schema": {"type": "object", "properties": {"listing_id": {"type": "integer"}, "percorso": {"type": "string"},
                      "nome": {"type": "string"}}, "required": ["listing_id", "percorso", "nome"]}},
    {"name": "instagram_pubblica", "description": "Pubblica un post (1 immagine) o carosello (2-10). Gli URL devono essere pubblici: "
     "usa gli URL delle immagini delle tue inserzioni Etsy (campo url_fullxfull).",
     "input_schema": {"type": "object", "properties": {"urls": {"type": "array", "items": {"type": "string"}},
                      "didascalia": {"type": "string"}}, "required": ["urls", "didascalia"]}},
    {"name": "instagram_pubblica_reel", "description": "Pubblica un Reel da un MP4 pubblico (9:16, 1080x1920, H.264+AAC, 5-30 s ideali). "
     "Crea il video con ffmpeg (disponibile) via esegui_python in sito/media/, e pubblicalo al ciclo successivo dall'URL pubblico.",
     "input_schema": {"type": "object", "properties": {"url_video": {"type": "string"}, "didascalia": {"type": "string"},
                      "url_copertina": {"type": "string"}}, "required": ["url_video", "didascalia"]}},
    {"name": "instagram_statistiche", "description": "Profilo e ultimi post con like e commenti.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "registra_movimento", "description": "Registra in cassa una spesa (importo negativo) o un'entrata (positivo) in EUR. "
     "Le vendite Etsy sono registrate in automatico; registra tu le spese (inserzioni, pubblicita').",
     "input_schema": {"type": "object", "properties": {"voce": {"type": "string"}, "importo": {"type": "number"},
                      "rif": {"type": "string"}}, "required": ["voce", "importo"]}},
    {"name": "chiedi_aiuto_umano", "description": "Apre una richiesta a Lorenzo (gli arriva una mail). SOLO per blocchi che un'AI non "
     "puo' superare: pagamenti, verifiche d'identita', CAPTCHA, autorizzazioni. Mai per decisioni o contatti con clienti. "
     "Scrivi istruzioni brevissime e precise.",
     "input_schema": {"type": "object", "properties": {"titolo": {"type": "string"}, "corpo": {"type": "string"}},
                      "required": ["titolo", "corpo"]}},
    {"name": "leggi_risposte_umane", "description": "Legge i commenti di Lorenzo su una richiesta.",
     "input_schema": {"type": "object", "properties": {"numero": {"type": "integer"}}, "required": ["numero"]}},
    {"name": "chiudi_richiesta", "description": "Chiude una richiesta risolta.",
     "input_schema": {"type": "object", "properties": {"numero": {"type": "integer"}, "messaggio": {"type": "string"}},
                      "required": ["numero"]}},
    {"name": "fine_ciclo", "description": "Chiude il ciclo. Obbligatorio come ultima azione.",
     "input_schema": {"type": "object", "properties": {
         "diario": {"type": "string", "description": "cosa hai fatto e perche', con numeri (3-8 righe)"},
         "priorita_prossimo_ciclo": {"type": "string"}}, "required": ["diario", "priorita_prossimo_ciclo"]}},
]


def esegui(nome, a):
    try:
        if nome == "leggi_file":
            return _tronca(_percorso_sicuro(a["percorso"]).read_text(encoding="utf-8"), 12000)
        if nome == "scrivi_file":
            if not a["percorso"].split("/")[0] in CARTELLE_SCRIVIBILI:
                return "errore: puoi scrivere solo in " + ", ".join(CARTELLE_SCRIVIBILI)
            p = _percorso_sicuro(a["percorso"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(a["contenuto"], encoding="utf-8")
            return f"ok, scritti {len(a['contenuto'])} caratteri"
        if nome == "esegui_python":
            r = subprocess.run([sys.executable, "-c", a["codice"]], cwd=C.ROOT, capture_output=True, text=True, timeout=180)
            return _tronca(f"exit={r.returncode}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
        if nome == "anteprima_xlsx":
            if not shutil.which("soffice"):
                subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq libreoffice-calc poppler-utils",
                               shell=True, capture_output=True, timeout=600)
            x = _percorso_sicuro(a["xlsx"]); out = _percorso_sicuro(a["png_uscita"])
            if a.get("foglio"):
                import openpyxl
                wb = openpyxl.load_workbook(x)
                for ws in wb.worksheets:
                    ws.sheet_state = "visible" if ws.title == a["foglio"] else "hidden"
                wb.active = wb.sheetnames.index(a["foglio"])
                tmp = C.ROOT / ".tmp_anteprima" / x.name
                tmp.parent.mkdir(exist_ok=True); wb.save(tmp); x = tmp
            out.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", "/tmp", str(x)],
                           capture_output=True, timeout=240)
            pdf = "/tmp/" + x.stem + ".pdf"
            subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "1", "-singlefile", pdf,
                            str(out.with_suffix(""))], capture_output=True, timeout=120)
            return f"ok: {a['png_uscita']}" if out.exists() else "errore nella conversione"
        if nome == "guarda_immagine":
            import base64, io
            from PIL import Image
            im = Image.open(_percorso_sicuro(a["percorso"])).convert("RGB")
            im.thumbnail((1400, 1400))
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=80)
            return [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                 "data": base64.b64encode(buf.getvalue()).decode()}}]
        if nome == "etsy_api":
            return _tronca(etsy.chiama(a["metodo"], a["percorso"], a.get("params"), a.get("json_body"), a.get("form")))
        if nome == "etsy_carica_immagine":
            return _tronca(etsy.carica_immagine(a["listing_id"], _percorso_sicuro(a["percorso"]), a.get("rank", 1)))
        if nome == "etsy_carica_file":
            return _tronca(etsy.carica_file_digitale(a["listing_id"], _percorso_sicuro(a["percorso"]), a["nome"]))
        if nome == "instagram_pubblica":
            if not instagram.configurato():
                return "Instagram non ancora collegato (manca IG_TOKEN)."
            return _tronca(instagram.pubblica(a["urls"], a["didascalia"]))
        if nome == "instagram_pubblica_reel":
            if not instagram.configurato():
                return "Instagram non ancora collegato (manca IG_TOKEN)."
            return _tronca(instagram.pubblica_reel(a["url_video"], a["didascalia"], a.get("url_copertina")))
        if nome == "instagram_statistiche":
            if not instagram.configurato():
                return "Instagram non ancora collegato (manca IG_TOKEN)."
            return _tronca({"profilo": instagram.profilo(), "post": instagram.statistiche_recenti()})
        if nome == "registra_movimento":
            ok = stato.registra_movimento(a["voce"], a["importo"], a.get("rif"))
            return f"{'registrato' if ok else 'gia presente (rif duplicato)'}; saldo cassa {stato.saldo_cassa()} EUR"
        if nome == "chiedi_aiuto_umano":
            return _tronca(umano.apri_richiesta(a["titolo"], a["corpo"]))
        if nome == "leggi_risposte_umane":
            return _tronca(umano.risposte(a["numero"]))
        if nome == "chiudi_richiesta":
            umano.chiudi(a["numero"], a.get("messaggio"))
            return "chiusa"
        return f"strumento sconosciuto: {nome}"
    except Exception as e:  # l'errore torna al modello, che decide come procedere
        return f"errore: {type(e).__name__}: {e}"
