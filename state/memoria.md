# Memoria strategica

## Decisioni (giorno 0, 13/11/2026)
- Business: modelli Excel/Google Fogli in italiano su Etsy (consegna automatica). Instagram = racconto trasparente.
- Prezzi previsti: Budget Familiare 2027 4,90; Planner Regali Natale 2,90; tracker abbonamenti 2,90; planner matrimonio 5,90; bundle 7,90.

## Stato prodotti
- prodotti/Budget_Familiare_2027.xlsx: pronto (script build_budget_2027.py). Anteprima media/prev_budget.png
- prodotti/Planner_Regali_Natale.xlsx: pronto, formule verificate con LibreOffice, 0 errori (script build_regali_natale.py). Anteprima media/prev_regali.png
- Da fare: tracker abbonamenti, planner matrimonio, bundle.

## Blocchi
- Etsy: ETSY_KEYSTRING assente nei secret. Aperta richiesta #1 a Lorenzo (negozio, app, OAuth). Non fare altro su Etsy finche' non risolta.
- Instagram non collegato.
- Cassa 80 EUR; credito API 20 EUR. Spese listing: 0,20 USD ciascuna. Serve cassa >=100 al giorno 14: servono vendite (obiettivo ~25 vendite da ~3-5 EUR... difficile; massimizzare numero inserzioni e prezzo bundle).

## Note operative
- Tra chiamate esegui_python lo stato NON persiste: scrivere script in scripts/ e rieseguire.
- LibreOffice installato (soffice) per ricalcolo/verifica formule.

## Cosa funziona / cosa no
- (da compilare con i dati)

## Nota del creatore (13/11, 18:15)
- La PRIMA inserzione (Budget Familiare 2027, 4,90 EUR) la crea Lorenzo a mano durante l'apertura del negozio, perche'
  Etsy la richiede per aprire. Copertina usata: media/etsy_budget_cover.jpg. Quando Etsy e' collegato, controlla le
  inserzioni attive prima di crearne: non duplicarla. Puoi migliorarne testo e foto.
- La copertina media/etsy_budget_cover.jpg e' un buon riferimento di stile per le altre foto (2000x1600, titolo,
  finta schermata con dati d'esempio, 5 benefici).
