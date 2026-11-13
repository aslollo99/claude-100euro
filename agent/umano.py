"""Canale con Lorenzo: issue GitHub con etichetta aiuto-umano (gli arriva una mail)."""
import os

import requests

from . import config as C

API = "https://api.github.com"


def _h():
    return {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"}


def _repo():
    return os.environ["GITHUB_REPOSITORY"]


def apri_richiesta(titolo, corpo):
    # niente doppioni: se esiste gia' una richiesta aperta con lo stesso titolo, la riusa
    for i in richieste_aperte():
        if i["titolo"] == titolo:
            return {"gia_aperta": True, "numero": i["numero"]}
    requests.post(f"{API}/repos/{_repo()}/labels", headers=_h(),
                  json={"name": C.LABEL_AIUTO, "color": "d93f0b"}, timeout=20)
    r = requests.post(f"{API}/repos/{_repo()}/issues", headers=_h(), timeout=20,
                      json={"title": titolo, "body": corpo + "\n\n— l'agente", "labels": [C.LABEL_AIUTO],
                            "assignees": [_repo().split("/")[0]]})
    r.raise_for_status()
    return {"numero": r.json()["number"], "url": r.json()["html_url"]}


def richieste_aperte():
    r = requests.get(f"{API}/repos/{_repo()}/issues", headers=_h(), timeout=20,
                     params={"labels": C.LABEL_AIUTO, "state": "open"})
    r.raise_for_status()
    return [{"numero": i["number"], "titolo": i["title"], "commenti": i["comments"]} for i in r.json()]


def risposte(numero):
    r = requests.get(f"{API}/repos/{_repo()}/issues/{numero}/comments", headers=_h(), timeout=20)
    r.raise_for_status()
    return [{"autore": c["user"]["login"], "testo": c["body"], "quando": c["created_at"]} for c in r.json()]


def chiudi(numero, messaggio=None):
    if messaggio:
        requests.post(f"{API}/repos/{_repo()}/issues/{numero}/comments", headers=_h(), timeout=20,
                      json={"body": messaggio})
    requests.patch(f"{API}/repos/{_repo()}/issues/{numero}", headers=_h(), timeout=20, json={"state": "closed"})


def disattiva_workflow(nome_file="agente.yml"):
    requests.put(f"{API}/repos/{_repo()}/actions/workflows/{nome_file}/disable", headers=_h(), timeout=20)
