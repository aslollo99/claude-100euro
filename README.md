# claude-100euro

Un agente AI (Claude) riceve 100 € e deve farli fruttare da solo. Al giorno 14 la cassa deve essere almeno 100 €, altrimenti è **game over**. Se sopravvive, va avanti fino al giorno 30.

## Come vive

- **Risveglio:** GitHub Actions lo sveglia ogni 4 ore (`.github/workflows/agente.yml`). Un ciclo al giorno è "strategico" e usa Sonnet 5.5; gli altri sono "di routine" e usano Haiku 5.5, molto più economico.
- **Memoria:** sta in `state/`. Ci sono `memoria.md` per la strategia, `diario.md` per il diario, `cassa.json` per i movimenti, `costi_api.json` per il costo di ogni ciclo e `segreti.enc` per i token cifrati.
- **Lavoro:** costruisce i prodotti in `prodotti/`, pubblica su Etsy tramite l'API ufficiale e su Instagram tramite l'API ufficiale di Meta.
- **Aiuto umano:** quando serve un pagamento o una verifica, apre una issue con etichetta `aiuto-umano` e Lorenzo riceve una mail.
- **Freni:**
  - tetto di spesa per ogni ciclo;
  - tetto sul credito API totale;
  - spegnimento automatico al game over o alla fine dell'esperimento;
  - un file `STOP` nella radice ferma tutto subito.

## Configurazione (una tantum)

Vai su Settings → Secrets and variables → Actions.

| Tipo | Nome | Valore |
|---|---|---|
| Secret | `ANTHROPIC_API_KEY` | chiave della console Anthropic |
| Secret | `ETSY_KEYSTRING` | keystring della Seller App Etsy |
| Secret | `ETSY_SHARED_SECRET` | shared secret della Seller App Etsy |
| Secret | `IG_TOKEN` | token Instagram (account professionale) |
| Variable | `ETSY_REDIRECT_URI` | lo stesso URL di callback registrato nella Seller App |
| Variable | `CREDITO_API_EUR` | euro caricati in console (default 20) |
