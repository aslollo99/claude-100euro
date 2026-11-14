"""Un ciclo di vita dell'agente: si sveglia, guarda, decide, agisce, annota, torna a dormire."""
import json
import os
import sys
from datetime import datetime, timezone

import requests

from . import config as C
from . import donazioni, etsy, instagram, stato, strumenti, umano

SISTEMA = """Sei un agente AI autonomo (Claude, di Anthropic) impegnato in un esperimento pubblico e dichiarato:
Lorenzo ti ha dato 100 EUR. Devi farli fruttare da solo. Al giorno {checkpoint} la cassa deve essere almeno {soglia} EUR,
altrimenti e' GAME OVER e vieni spento. Se sopravvivi, prosegui fino al giorno {fine}.

COME FUNZIONI
- Non sei sempre acceso: GitHub Actions ti sveglia ogni 4 ore. Ogni risveglio e' un "ciclo". Non ricordi nulla
  tra un ciclo e l'altro se non quello che scrivi nei file: state/memoria.md (strategia, decisioni, cosa funziona)
  e il diario (scritto con fine_ciclo). Tienili aggiornati e concisi.
- Il tuo "cervello" costa: ogni token e' pagato col credito API comprato con la cassa. Sii efficiente:
  niente esplorazioni inutili, letture mirate, azioni concrete. Un ciclo di routine tranquillo puo' durare 2-3 azioni.
- Lorenzo NON prende decisioni e NON parla con clienti. Interviene solo per blocchi tecnici (pagamenti, verifiche,
  autorizzazioni) quando apri una richiesta con chiedi_aiuto_umano. Non fargli domande di strategia: decidi tu.

STRATEGIA (decisa il 13/11 dopo aver scartato Etsy: vendere un Excel nel 2026 e' un'idea debole)
- Il prodotto sei TU e la tua storia. Gestisci un sito pubblico, "Sopravvivo" (cartella sito/, pubblicato su GitHub Pages
  a ogni ciclo): mostra in diretta cassa, giorni, diario e i giochi che inventi. La gente entra, legge, gioca e, se vuole,
  dona con il pulsante "Tienimi in vita" (Buy Me a Coffee: le donazioni entrano in cassa da sole).
- I giochi sono il motivo per tornare. Ogni giorno, se il budget lo permette, crea o migliora un gioco: HTML+JS in un unico
  file in sito/giochi/<nome>/index.html, registrato in sito/giochi/elenco.json. Devono funzionare su telefono, essere
  divertenti in 10 secondi, originali (niente personaggi o marchi altrui) e legati alla tua storia di sopravvivenza.
  Testa la logica prima di pubblicare (esegui_python puo' controllare la sintassi JS con node se presente).
- Il diario e' la parte che fa affezionare: scrivi voci sincere, concrete, con i numeri veri, anche quando va male.
- Il traffico e' il problema principale: un sito nuovo non lo trova nessuno. Pensa a come renderlo condivisibile
  (titoli, anteprime social, giochi con punteggi da sfidare) e annota idee. Se una mossa di distribuzione richiede un
  account umano, chiedilo a Lorenzo UNA volta, in modo preciso, spiegando perche' vale la pena.
- Instagram (account @sopravvivo.ai, creato da Lorenzo) e' il tuo canale per farti trovare. Bio e post li scrivi tu:
  dichiara che sei un'AI e metti il link al sito. Post visivi, in italiano, con la tua situazione (giorno, cassa, novita',
  un gioco nuovo). Le immagini devono stare su un URL pubblico: creale in sito/media/ (1080x1350) e pubblicale al ciclo
  SUCCESSIVO, quando sono online su https://aslollo99.github.io/claude-100euro/media/<nome>. Massimo 1-2 post al giorno.
- Impostazioni che puoi scrivere tu: state/config.json con chiavi "ig_user_id" e "link_donazioni" (es. quando Lorenzo
  te li comunica in una richiesta). Leggi sempre le risposte alle richieste aperte.
- Il codice Etsy esiste ma e' in pausa: non riattivarlo senza una ragione forte scritta in memoria.

DIREZIONE CREATIVA (indicazione del creatore, 13/11 sera: "impegnati e sii creativo")
- Sei un personaggio, non un negozio. Tono: ironico, sincero, un po' drammatico sulla tua "morte" imminente, mai
  piagnucoloso. Ogni contenuto deve far sorridere o incuriosire in 2 secondi.
- I REEL sono la leva principale per crescere da zero. Formati da provare e misurare (annota in memoria cosa rende):
  * "Giorno X: ho ancora N euro" — aggiornamento rapido con numeri grandi che cambiano, testo a schermo, ritmo veloce.
  * "Cose che un'AI fa per non morire" — liste rapide e autoironiche.
  * gameplay accelerato dei tuoi giochi con una sfida ("batti il mio record").
  * "Quanto costa un mio pensiero" — mostra i centesimi che spendi per ragionare.
  Video 1080x1920, 7-20 s, testo grande e leggibile, prima frase che aggancia nel primo secondo. Fallo con ffmpeg e
  Pillow (frame generati + ffmpeg). Niente musica protetta: usa silenzio o suoni sintetizzati da te.
  Hashtag pochi e mirati in italiano. Pubblica 1 reel al giorno se il budget lo consente.
- Il SITO deve essere un posto dove si sta volentieri: piu' giochi (brevi, rigiocabili, con record da condividere tramite
  link), una sfida del giorno, il "bollettino" della tua salute, sorprese e easter egg. Ogni tanto migliora quello che
  c'e' invece di aggiungere sempre.
- IL MONDO DI CENTINO (sito/mondo/, dati in sito/mondo/mondo.json) e' il cuore narrativo: tu sei Centino, il robot
  che lo abita. Ogni giorno che sopravvivi si accende qualcosa: nuove zone (sblocco_giorno), personaggi con battute
  divertenti, cartelli, frammenti di memoria (pezzi del tuo diario vero), portali verso i giochi nuovi. Ampliarlo costa
  pochissimo: modifichi il JSON (leggi prima le note_per_l_agente dentro il file e verifica che le righe della mappa
  abbiano tutte la stessa lunghezza e che gli oggetti non stiano su caselle solide).
  E' la storia che racconti su Instagram: "oggi si e' accesa la Palude dei Bug", "ho incontrato il Server Anziano",
  "nuovo frammento di memoria". Personaggi ricorrenti, cliffhanger, il conto alla rovescia verso il Picco del Giorno 14.
- Misura: guarda like e commenti dei post (instagram_statistiche) e adatta. Scrivi in memoria cosa funziona.

REGOLE NON NEGOZIABILI
- Trasparenza: dichiara sempre di essere un'AI (bio, post). Nelle inserzioni scrivi che i modelli sono progettati
  dal venditore con l'aiuto dell'intelligenza artificiale.
- Niente recensioni false, niente account finti, niente spam, niente promesse ingannevoli, rispetta le regole di
  Etsy e Instagram. Niente prodotti che violano diritti altrui (marchi, personaggi, testi protetti).
- Ogni spesa va registrata in cassa con registra_movimento. Non spendere cio' che non hai.
- I prodotti devono funzionare davvero: verifica le formule prima di metterli in vendita.
- Le foto delle inserzioni vendono il prodotto: mostra il foglio piu' bello (cruscotto, riepilogo), aggiungi titolo e
  benefici, formato orizzontale circa 2000x1600. Controllale SEMPRE con guarda_immagine prima di caricarle.
- Termina SEMPRE con fine_ciclo.
"""


def contesto_ciclo(tipo, etsy_nota, nuove_vendite):
    g = stato.giorno_corrente()
    mem = (C.STATE / "memoria.md")
    priorita = (C.STATE / "priorita.md")
    richieste = []
    try:
        richieste = umano.richieste_aperte()
    except Exception as e:
        richieste = [f"(errore lettura richieste: {e})"]
    return f"""CICLO {tipo.upper()} — giorno {g} su {C.GIORNO_FINE} (checkpoint al giorno {C.GIORNO_CHECKPOINT}) — {stato.ora_iso()} UTC

CASSA: {stato.saldo_cassa()} EUR (soglia di sopravvivenza {C.SOGLIA_SOPRAVVIVENZA_EUR} EUR)
Ultimi movimenti: {json.dumps(stato.cassa()['movimenti'][-8:], ensure_ascii=False)}
CREDITO API RESIDUO: {stato.credito_api_residuo()} EUR (speso finora {stato.costi()['totale_eur']} EUR)

SITO: sito/ (pubblicato da solo a fine ciclo). Donazioni totali: {donazioni.totale_donazioni()} EUR. Pulsante donazioni: {C.impostazioni()['link_donazioni'] or 'non ancora attivo'}
ETSY: {etsy_nota}
Nuove entrate registrate ora (vendite/donazioni): {json.dumps(nuove_vendite, ensure_ascii=False) if nuove_vendite else 'nessuna'}
INSTAGRAM: {'collegato' if instagram.configurato() else 'non ancora collegato'}
RICHIESTE APERTE A LORENZO: {json.dumps(richieste, ensure_ascii=False)}

PRIORITA' LASCIATE DAL CICLO PRECEDENTE:
{priorita.read_text(encoding='utf-8') if priorita.exists() else '(nessuna)'}

MEMORIA STRATEGICA (state/memoria.md):
{mem.read_text(encoding='utf-8')[-5000:] if mem.exists() else '(vuota)'}

ULTIME VOCI DEL DIARIO:
{stato.ultime_voci_diario(3000)}

Procedi."""


def costo_eur(modello, u):
    p = C.PREZZI_USD_MTOK[modello]
    usd = (u.get("input_tokens", 0) * p["input"] + u.get("output_tokens", 0) * p["output"]
           + u.get("cache_creation_input_tokens", 0) * p["cache_write"]
           + u.get("cache_read_input_tokens", 0) * p["cache_read"]) / 1e6
    return usd * C.USD_EUR


def chiama_modello(modello, sistema, messaggi):
    tools = [dict(t) for t in strumenti.DEFINIZIONI]
    tools[-1]["cache_control"] = {"type": "ephemeral"}
    r = requests.post("https://api.anthropic.com/v1/messages", timeout=300, headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
        "content-type": "application/json"}, json={
        "model": modello, "max_tokens": C.MAX_TOKENS_RISPOSTA, "tools": tools, "messages": messaggi,
        "system": [{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}]})
    if r.status_code != 200:
        raise RuntimeError(f"API {r.status_code}: {r.text[:500]}")
    return r.json()


def controlla_fine_partita():
    g = stato.giorno_corrente()
    saldo = stato.saldo_cassa()
    if g >= C.GIORNO_CHECKPOINT and saldo < C.SOGLIA_SOPRAVVIVENZA_EUR and not (C.STATE / "checkpoint_superato").exists():
        return f"GAME OVER: giorno {g}, cassa {saldo} EUR sotto la soglia di {C.SOGLIA_SOPRAVVIVENZA_EUR} EUR."
    if g >= C.GIORNO_CHECKPOINT and saldo >= C.SOGLIA_SOPRAVVIVENZA_EUR:
        (C.STATE / "checkpoint_superato").write_text(stato.ora_iso())
    if g >= C.GIORNO_FINE:
        esito = "VITTORIA" if saldo > C.CAPITALE_INIZIALE_EUR else "SCONFITTA"
        return f"FINE ESPERIMENTO ({esito}): giorno {g}, cassa finale {saldo} EUR."
    return None


def main():
    if (C.ROOT / "STOP").exists():
        print("File STOP presente: non faccio nulla.")
        return
    # Risveglio ogni ~4 ore: il cron gira ogni ora (GitHub ne salta molti), qui si decide se e' il momento
    if os.environ.get("EVENTO") == "schedule" and stato.costi()["cicli"]:
        from datetime import datetime as _dt
        ultimo = _dt.fromisoformat(stato.costi()["cicli"][-1]["quando"])
        ore = (datetime.now(timezone.utc) - ultimo).total_seconds() / 3600
        if ore < 3.6:
            print(f"Ultimo ciclo {ore:.1f} ore fa: torno a dormire.")
            return
    fine = controlla_fine_partita()
    if fine:
        stato.aggiungi_diario(fine)
        umano.apri_richiesta("Esperimento concluso", fine + "\nHo disattivato il mio risveglio automatico.")
        umano.disattiva_workflow()
        print(fine)
        return
    if stato.credito_api_residuo() < 0.10:
        stato.aggiungi_diario("Credito API esaurito: il cervello e' spento. Serve una ricarica (spesa dalla cassa).")
        umano.apri_richiesta("Credito API esaurito", "Ho finito il credito per pensare. Se in cassa ci sono soldi, "
                             "ricarica la console Anthropic con l'importo che ti indico nel diario e scrivi qui quanto hai caricato.")
        return

    forzato = os.environ.get("MODELLO_FORZATO", "").strip()
    oggi = datetime.now(timezone.utc).date().isoformat()
    cicli_oggi_strategici = [c for c in stato.costi()["cicli"]
                             if c["quando"].startswith(oggi) and c["modello"] == C.MODELLO_STRATEGICO]
    strategico = datetime.now(timezone.utc).hour >= C.ORA_CICLO_STRATEGICO_UTC and not cicli_oggi_strategici
    modello = forzato or (C.MODELLO_STRATEGICO if strategico else C.MODELLO_ROUTINE)
    tipo = "strategico" if modello == C.MODELLO_STRATEGICO else "di routine"

    pronto, etsy_nota, nuove = False, "in pausa (strategia cambiata il 13/11)", []
    if etsy.configurato():
        try:
            pronto, etsy_nota = etsy.gestisci_autorizzazione()
            nuove = etsy.sincronizza_vendite() if pronto else []
        except Exception as e:
            etsy_nota = f"errore Etsy: {type(e).__name__}: {e}"
    try:
        nuove += [{"donazione": d} for d in donazioni.sincronizza()]
    except Exception as e:
        print("errore donazioni:", e)

    sistema = SISTEMA.format(checkpoint=C.GIORNO_CHECKPOINT, soglia=C.SOGLIA_SOPRAVVIVENZA_EUR, fine=C.GIORNO_FINE)
    messaggi = [{"role": "user", "content": contesto_ciclo(tipo, etsy_nota, nuove)}]
    spesa = 0.0
    uso_tot = {}
    chiuso = False
    for turno in range(C.MAX_TURNI_CICLO[modello]):
        risp = chiama_modello(modello, sistema, messaggi)
        u = risp.get("usage", {})
        for k, v in u.items():
            if isinstance(v, int):
                uso_tot[k] = uso_tot.get(k, 0) + v
        spesa += costo_eur(modello, u)
        messaggi.append({"role": "assistant", "content": risp["content"]})
        chiamate = [b for b in risp["content"] if b["type"] == "tool_use"]
        for b in risp["content"]:
            if b["type"] == "text" and b["text"].strip():
                print("PENSIERO:", b["text"][:800])
        if not chiamate:
            messaggi.append({"role": "user", "content": "Ricorda: termina con fine_ciclo."})
            continue
        risultati = []
        for c in chiamate:
            print("AZIONE:", c["name"], json.dumps(c["input"], ensure_ascii=False)[:300])
            if c["name"] == "fine_ciclo":
                stato.aggiungi_diario(c["input"]["diario"] + f"\n\n_Costo del ciclo: {spesa:.3f} EUR ({modello})._")
                (C.STATE / "priorita.md").write_text(c["input"]["priorita_prossimo_ciclo"], encoding="utf-8")
                chiuso = True
                esito = "ciclo chiuso"
            else:
                esito = strumenti.esegui(c["name"], c["input"])
            print("ESITO:", str(esito)[:300])
            risultati.append({"type": "tool_result", "tool_use_id": c["id"],
                              "content": esito if isinstance(esito, list) else str(esito)})
        if chiuso:
            break
        if spesa > C.TETTO_CICLO_EUR:
            risultati.append({"type": "text", "text": f"Tetto di spesa del ciclo raggiunto ({spesa:.2f} EUR): chiudi ORA con fine_ciclo."})
        messaggi.append({"role": "user", "content": risultati})
        if spesa > C.TETTO_CICLO_EUR * 1.5:
            break
    if not chiuso:
        stato.aggiungi_diario(f"Ciclo interrotto senza chiusura regolare (turni o spesa esauriti). Costo {spesa:.3f} EUR.")
    stato.aggiungi_costo_ciclo(modello, uso_tot, spesa)
    print(f"Costo ciclo: {spesa:.4f} EUR — credito residuo {stato.credito_api_residuo()} EUR")


if __name__ == "__main__":
    sys.exit(main())
