"""Configurazione dell'agente. Tutti i numeri fissi stanno qui, con la loro origine."""
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
PRODOTTI = ROOT / "prodotti"

# --- Regole del gioco (decise con Lorenzo il 13/11/2026)
DATA_INIZIO = date(2026, 11, 13)
CAPITALE_INIZIALE_EUR = 100.0
GIORNO_CHECKPOINT = 14          # se cassa < soglia a questo giorno -> game over
GIORNO_FINE = 30
SOGLIA_SOPRAVVIVENZA_EUR = 100.0

# --- Modelli e prezzi (USD per milione di token, listino Anthropic ottobre 2026)
MODELLO_STRATEGICO = "claude-sonnet-5-5"   # 1 ciclo al giorno, decisioni
MODELLO_ROUTINE = "claude-haiku-5-5"       # gli altri cicli, controllo e operativita'
PREZZI_USD_MTOK = {
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.10},
    # Haiku 5.5: prezzi validi per prompt fino a 100k token; oltre si moltiplicano x5
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_write": 0.125, "cache_read": 0.01},
}
USD_EUR = float(os.getenv("USD_EUR") or "0.92")  # ipotesi di cambio, aggiornabile via variabile

# --- Limiti di spesa del cervello
CREDITO_API_EUR = float(os.getenv("CREDITO_API_EUR") or "20")   # quanto e' stato caricato in console
TETTO_CICLO_EUR = 0.60          # un singolo ciclo non puo' costare di piu'
MAX_TURNI_CICLO = {"claude-sonnet-5-5": 30, "claude-haiku-5-5": 20}
MAX_TOKENS_RISPOSTA = 4096

# Ora UTC del ciclo strategico (gli altri cicli usano il modello di routine)
ORA_CICLO_STRATEGICO_UTC = 7

# --- Etsy
ETSY_API = "https://openapi.etsy.com/v3"
ETSY_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
ETSY_AUTH_URL = "https://www.etsy.com/oauth/connect"
ETSY_SCOPES = "listings_r listings_w listings_d shops_r shops_w transactions_r profile_r"
ETSY_REDIRECT_URI = os.getenv("ETSY_REDIRECT_URI") or "https://github.com/"
# Stima commissioni Etsy su prodotti digitali venduti dall'Italia:
# 6.5% transazione + ~4% elaborazione pagamento + 0.8% regolatoria, + 0.30 EUR fisso stimato
ETSY_FEE_PCT = 0.113
ETSY_FEE_FISSA_EUR = 0.30

# --- Instagram (API con login Instagram)
IG_API = "https://graph.instagram.com/v23.0"

LABEL_AIUTO = "aiuto-umano"
