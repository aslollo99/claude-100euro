"""La voce di Centino: sintesi vocale neurale italiana (Piper, offline) con un filtro "robot" leggero.
Uso: from agent import voce; voce.parla("Ciao, sono Centino.", "sito/media/v1.wav") -> durata in secondi."""
import subprocess
import urllib.request
import wave
from pathlib import Path

MODELLO = "it_IT-paola-medium"
URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/"
CACHE = Path.home() / ".cache" / "piper"


def _modello():
    CACHE.mkdir(parents=True, exist_ok=True)
    onnx, js = CACHE / f"{MODELLO}.onnx", CACHE / f"{MODELLO}.onnx.json"
    for f in (onnx, js):
        if not f.exists():
            urllib.request.urlretrieve(URL + f.name, f)
    return onnx


def _sintesi(testo, wav):
    from piper import PiperVoice
    v = PiperVoice.load(str(_modello()))
    with wave.open(str(wav), "wb") as wf:
        if hasattr(v, "synthesize_wav"):
            v.synthesize_wav(testo, wf)
        else:
            v.synthesize(testo, wf)


def parla(testo, uscita, robot=True):
    uscita = Path(uscita)
    uscita.parent.mkdir(parents=True, exist_ok=True)
    grezzo = uscita.with_suffix(".grezzo.wav")
    _sintesi(testo, grezzo)
    filtro = ("asetrate=22050*1.06,aresample=44100,atempo=0.97,"
              "aecho=0.6:0.4:12:0.25,highpass=f=120,acompressor,volume=1.4") if robot else "aresample=44100"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(grezzo), "-af", filtro, "-ac", "2", str(uscita)],
                   check=True)
    grezzo.unlink(missing_ok=True)
    return durata(uscita)


def durata(wav):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)
