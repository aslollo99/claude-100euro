"""Instagram: pubblicazione tramite API ufficiale (account professionale, token in IG_TOKEN)."""
import os
import time

import requests

from . import config as C


def configurato():
    return bool(os.environ.get("IG_TOKEN"))


def _p(extra=None):
    d = {"access_token": os.environ["IG_TOKEN"]}
    d.update(extra or {})
    return d


FB_API = "https://graph.facebook.com/v23.0"
_cache = {}


def _base():
    """Supporta sia i token "Instagram Login" (graph.instagram.com) sia i token utente di sistema / Facebook Login
    for Business (graph.facebook.com + id dell'account Instagram professionale)."""
    if "base" in _cache:
        return _cache["base"], _cache["uid"]
    r = requests.get(f"{C.IG_API}/me", params=_p({"fields": "user_id,username"}), timeout=30).json()
    if r.get("user_id"):
        _cache.update(base=C.IG_API, uid=r["user_id"])
    else:
        uid = C.impostazioni().get("ig_user_id")
        if not uid:  # cerca l'account Instagram collegato alle risorse del token
            for path, campo in (("me/accounts", "instagram_business_account"),):
                j = requests.get(f"{FB_API}/{path}", params=_p({"fields": campo}), timeout=30).json()
                for x in j.get("data", []):
                    if x.get(campo):
                        uid = x[campo]["id"]; break
        _cache.update(base=FB_API, uid=uid)
    return _cache["base"], _cache["uid"]


def _me():
    base, uid = _base()
    if not uid:
        return {"errore": "non trovo l'account Instagram: scrivi il suo ID in state/config.json alla chiave ig_user_id"}
    r = requests.get(f"{base}/{uid}", params=_p({"fields": "id,username,followers_count,media_count"}), timeout=30).json()
    r["user_id"] = uid
    return r


def profilo():
    return _me()


def pubblica(urls_immagini, didascalia):
    """urls_immagini: 1 URL (post singolo) o 2-10 URL (carosello). Gli URL devono essere pubblici (es. immagini Etsy)."""
    base, uid = _base()
    if not uid:
        return {"errore": "token Instagram non valido"}
    if len(urls_immagini) == 1:
        r = requests.post(f"{base}/{uid}/media", data=_p({"image_url": urls_immagini[0], "caption": didascalia}), timeout=60)
        cont = r.json()
    else:
        figli = []
        for u in urls_immagini[:10]:
            r = requests.post(f"{base}/{uid}/media", data=_p({"image_url": u, "is_carousel_item": "true"}), timeout=60)
            if "id" not in r.json():
                return {"errore": r.json()}
            figli.append(r.json()["id"])
        r = requests.post(f"{base}/{uid}/media", timeout=60,
                          data=_p({"media_type": "CAROUSEL", "children": ",".join(figli), "caption": didascalia}))
        cont = r.json()
    if "id" not in cont:
        return {"errore": cont}
    for _ in range(10):  # attende che il contenitore sia pronto
        st = requests.get(f"{base}/{cont['id']}", params=_p({"fields": "status_code"}), timeout=30).json()
        if st.get("status_code") == "FINISHED":
            break
        time.sleep(3)
    r = requests.post(f"{base}/{uid}/media_publish", data=_p({"creation_id": cont["id"]}), timeout=60)
    return r.json()


def statistiche_recenti(n=10):
    base, uid = _base()
    r = requests.get(f"{base}/{uid}/media", timeout=30,
                     params=_p({"fields": "id,caption,timestamp,like_count,comments_count,permalink", "limit": n}))
    return r.json()
