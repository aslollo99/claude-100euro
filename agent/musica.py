"""Musica originale per i reel, generata al volo (niente diritti d'autore): chiptune leggera con basso, arpeggio
e cassa. Ogni seme da' un brano diverso. Uso interno di grafica.reel (parametro musica=True, default)."""
import random
import wave

import numpy as np

SR = 44100
SCALE = {"allegra": [0, 2, 4, 7, 9], "tesa": [0, 1, 5, 7, 8], "sognante": [0, 2, 4, 7, 11]}
GIRI = {"allegra": [0, 5, 3, 4], "tesa": [0, 0, 5, 4], "sognante": [0, 3, 5, 4]}


def _nota(f, dur, forma="quadra", vol=0.2):
    t = np.arange(int(SR * dur)) / SR
    if forma == "quadra":
        o = np.sign(np.sin(2 * np.pi * f * t)) * 0.6
    elif forma == "triangolo":
        o = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
    else:
        o = np.sin(2 * np.pi * f * t)
    inv = np.minimum(1, np.minimum(t / 0.005, (dur - t) / 0.03).clip(0))
    return o * inv * np.exp(-t * 3) * vol


def brano(uscita, secondi, umore="allegra", bpm=118, seme=None):
    r = random.Random(seme)
    scala, giro = SCALE.get(umore, SCALE["allegra"]), GIRI.get(umore, GIRI["allegra"])
    radice = 220 * 2 ** (r.choice([-5, -3, 0, 2]) / 12)
    beat = 60 / bpm
    out = np.zeros(int(SR * (secondi + 8 * 60 / bpm + 1)))  # margine per l'ultima battuta
    battuta = 0
    t = 0.0
    while t < secondi:
        accordo = giro[battuta % len(giro)]
        base = radice * 2 ** (accordo / 12)
        for b in range(4):
            i0 = int((t + b * beat) * SR)
            # basso
            s = _nota(base / 2, beat * 0.9, "triangolo", 0.28)
            out[i0:i0 + len(s)] += s[:len(out) - i0]
            # cassa
            k = np.arange(int(SR * 0.12)) / SR
            cassa = np.sin(2 * np.pi * (110 * np.exp(-k * 30) + 45) * k) * np.exp(-k * 25) * 0.5
            out[i0:i0 + len(cassa)] += cassa[:len(out) - i0]
            # arpeggio in sedicesimi
            for q in range(4):
                gr = scala[(r.randrange(len(scala)) if r.random() < 0.35 else (b + q) % len(scala))]
                f = base * 2 ** ((gr + 12 * r.choice([0, 0, 1])) / 12)
                j0 = int((t + b * beat + q * beat / 4) * SR)
                s = _nota(f, beat / 4 * 0.9, "quadra", 0.07)
                out[j0:j0 + len(s)] += s[:len(out) - j0]
        t += 4 * beat
        battuta += 1
    out = out[:int(SR * secondi)]
    out /= max(1e-6, np.abs(out).max()) / 0.8
    dati = (np.repeat(out[:, None], 2, axis=1) * 32767).astype(np.int16)
    with wave.open(str(uscita), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dati.tobytes())
    return uscita
