"""Scopre l'ID dell'account Instagram a partire dal token, provando le varie API di Meta. Non stampa il token."""
import json, os, sys
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import config as C

T = os.environ.get("IG_TOKEN", "")
if not T:
    sys.exit("IG_TOKEN mancante")
FB, IG = "https://graph.facebook.com/v23.0", "https://graph.instagram.com/v23.0"
trovati = []

def get(url, **p):
    p["access_token"] = T
    try:
        r = requests.get(url, params=p, timeout=30); j = r.json()
    except Exception as e:
        j = {"eccezione": str(e)}
    print(url.replace(T, "***"), p.get("fields", ""), "->", json.dumps(j)[:400])
    return j

j = get(f"{IG}/me", fields="id,user_id,username")
if j.get("user_id") or (j.get("id") and j.get("username")):
    trovati.append((j.get("user_id") or j["id"], j.get("username")))
dbg = get(f"{FB}/debug_token", input_token=T)
for g in dbg.get("data", {}).get("granular_scopes", []):
    for tid in g.get("target_ids", []):
        x = get(f"{FB}/{tid}", fields="id,username")
        if x.get("username"):
            trovati.append((x["id"], x["username"]))
me = get(f"{FB}/me", fields="id,name")
for x in get(f"{FB}/me/accounts", fields="instagram_business_account{id,username}").get("data", []):
    if x.get("instagram_business_account"):
        trovati.append((x["instagram_business_account"]["id"], x["instagram_business_account"].get("username")))
for b in get(f"{FB}/me/businesses", fields="id,name").get("data", []):
    for edge in ("owned_instagram_accounts", "instagram_accounts", "instagram_business_accounts"):
        for x in get(f"{FB}/{b['id']}/{edge}", fields="id,username").get("data", []):
            trovati.append((x["id"], x.get("username")))
if me.get("id"):
    for edge in ("instagram_accounts", "assigned_instagram_accounts"):
        for x in get(f"{FB}/{me['id']}/{edge}", fields="id,username").get("data", []):
            trovati.append((x["id"], x.get("username")))

print("TROVATI:", trovati)
if trovati:
    p = C.STATE / "config.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    d["ig_user_id"] = str(trovati[0][0]); d["ig_username"] = trovati[0][1]
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print("Salvato in state/config.json:", d)
