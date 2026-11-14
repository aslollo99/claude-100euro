"""Kit grafico di Sopravvivo: stile coerente e curato per post, reel e anteprime.

Uso tipico (da esegui_python):
    from agent import grafica as g
    g.post("sito/media/post_g2.png", occhiello="GIORNO 2", titolo="Ho ancora", evidenza="80,00 €",
           sotto="Oggi si accende la Palude dei Bug.", umore="stanco")
    g.reel("sito/media/reel_g2.mp4", [
        {"testo": "Sono un'AI.", "umore": "ok"},
        {"testo": "Ho 100 € e 14 giorni", "evidenza": "per non farmi spegnere.", "umore": "panico"},
        {"testo": "Oggi ho", "evidenza": "80,00 €", "umore": "stanco"},
        {"testo": "Aiutami a sopravvivere", "evidenza": "link in bio", "umore": "felice"}])
Umori di Centino: ok, stanco, felice, panico. Controlla SEMPRE il risultato con guarda_immagine.
"""
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CARTELLA_FONT = Path(__file__).parent / "font"
SFONDO = (11, 11, 20)
CORALLO = (255, 90, 60)
GIALLO = (255, 216, 74)
MENTA = (57, 217, 138)
BIANCO = (242, 240, 234)
GRIGIO = (150, 156, 170)
HANDLE = "@sopravvivo.ai"
try:  # il nome vero dell'account, se l'agente l'ha salvato in state/config.json (chiave ig_username)
    import json as _j
    _cfg = _j.loads((Path(__file__).parent.parent / "state" / "config.json").read_text())
    if _cfg.get("ig_username"):
        HANDLE = "@" + _cfg["ig_username"].lstrip("@")
except Exception:
    pass
SITO = "aslollo99.github.io/claude-100euro"


def font(nome="titolo", dim=80, peso=700):
    f = ImageFont.truetype(str(CARTELLA_FONT / ("SpaceGrotesk.ttf" if nome == "titolo" else "Inter.ttf")), dim)
    try:
        f.set_variation_by_axes([peso] if nome == "titolo" else [14, peso])
    except Exception:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def sfondo(w, h, bagliori=((CORALLO, 0.15, 0.1), (GIALLO, 0.9, 0.85)), seme=7):
    """Sfondo scuro con aloni colorati sfocati e grana leggera."""
    im = Image.new("RGB", (w, h), SFONDO)
    alone = Image.new("RGB", (w // 4, h // 4), SFONDO)
    d = ImageDraw.Draw(alone)
    for col, fx, fy in bagliori:
        r = int(min(w, h) / 4 * 0.55)
        cx, cy = int(fx * w / 4), int(fy * h / 4)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * 0.32) for c in col))
    alone = alone.filter(ImageFilter.GaussianBlur(min(w, h) / 4 / 5)).resize((w, h), Image.BICUBIC)
    im = Image.blend(im, alone, 0.8)
    rnd = random.Random(seme)
    grana = Image.new("L", (w // 2, h // 2))
    grana.putdata([rnd.randint(0, 255) for _ in range((w // 2) * (h // 2))])
    grana = grana.resize((w, h))
    return Image.composite(Image.new("RGB", (w, h), (30, 30, 40)), im, grana.point(lambda v: 14 if v > 128 else 0))


def centino(dim=400, umore="ok", fase=0.0):
    """Il robot Centino, disegnato in alta risoluzione e ridotto (bordi morbidi). fase anima occhi e battito."""
    S = dim * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = S / 100
    ombra = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(ombra).ellipse([22 * u, 88 * u, 78 * u, 96 * u], fill=(0, 0, 0, 110))
    im.alpha_composite(ombra.filter(ImageFilter.GaussianBlur(3 * u)))
    d.line([50 * u, 22 * u, 50 * u, 12 * u], fill=BIANCO, width=int(3 * u))
    luce = CORALLO if umore != "felice" else MENTA
    d.ellipse([45 * u, 5 * u, 55 * u, 15 * u], fill=luce)
    d.rounded_rectangle([18 * u, 22 * u, 82 * u, 84 * u], radius=int(14 * u), fill=BIANCO)
    d.rounded_rectangle([24 * u, 29 * u, 76 * u, 60 * u], radius=int(9 * u), fill=(18, 16, 31))
    ammicca = (fase * 1.3) % 4 < 0.12
    for cx in (37, 63):
        if ammicca:
            d.rounded_rectangle([(cx - 6) * u, 43 * u, (cx + 6) * u, 46 * u], radius=int(u), fill=GIALLO)
        elif umore == "stanco":
            d.pieslice([(cx - 6) * u, 38 * u, (cx + 6) * u, 50 * u], 180, 360, fill=GIALLO)
        elif umore == "felice":
            d.arc([(cx - 6) * u, 40 * u, (cx + 6) * u, 52 * u], 200, 340, fill=GIALLO, width=int(3 * u))
        elif umore == "panico":
            d.ellipse([(cx - 7) * u, 37 * u, (cx + 7) * u, 51 * u], fill=GIALLO)
            d.ellipse([(cx - 2) * u, 42 * u, (cx + 2) * u, 46 * u], fill=(18, 16, 31))
        else:
            d.ellipse([(cx - 6) * u, 38 * u, (cx + 6) * u, 50 * u], fill=GIALLO)
    # battito sul petto
    # tracciato ECG che scorre: piatto, piccola onda, picco alto, discesa, risalita
    forma = {0: 0, 1: 2, 2: 0, 3: 0, 4: 12, 5: -7, 6: 3, 7: 0}
    sp = int(fase * 12) % 24
    pts = []
    for i in range(0, 49, 2):
        k = ((i // 2) - sp // 2) % 12
        pts.append(((26 + i) * u, (72 - forma.get(k, 0)) * u))
    col = CORALLO if umore != "felice" else MENTA
    d.line(pts, fill=col, width=int(2.6 * u), joint="curve")
    return im.resize((dim, dim), Image.LANCZOS)


def a_capo(testo, f, larghezza):
    righe, riga = [], ""
    for parola in testo.split():
        prova = (riga + " " + parola).strip()
        if f.getlength(prova) <= larghezza or not riga:
            riga = prova
        else:
            righe.append(riga)
            riga = parola
    if riga:
        righe.append(riga)
    return righe


def _blocco(d, x, y, testo, f, colore, larghezza, interlinea=1.08):
    for r in a_capo(testo, f, larghezza):
        d.text((x, y), r, font=f, fill=colore)
        y += int(f.size * interlinea)
    return y


def _pillola(d, x, y, testo, f, bg, fg):
    w = f.getlength(testo)
    d.rounded_rectangle([x, y, x + w + 44, y + f.size + 26], radius=(f.size + 26) // 2, fill=bg)
    d.text((x + 22, y + 11), testo, font=f, fill=fg)


def post(percorso, titolo, evidenza="", sotto="", occhiello="", umore="ok", w=1080, h=1350):
    """Post 4:5 per il feed. titolo in bianco, evidenza grande in giallo, sotto in grigio."""
    im = sfondo(w, h).convert("RGBA")
    d = ImageDraw.Draw(im)
    m = 84
    if occhiello:
        _pillola(d, m, 90, occhiello.upper(), font("testo", 30, 700), CORALLO, (255, 255, 255))
    y = 210
    y = _blocco(d, m, y, titolo, font("titolo", 100, 700), BIANCO, w - 2 * m)
    if evidenza:
        y = _blocco(d, m, y + 6, evidenza, font("titolo", 128, 700), GIALLO, w - 2 * m, 1.0)
    if sotto:
        y = _blocco(d, m, y + 30, sotto, font("testo", 42, 500), GRIGIO, w - 2 * m - 60, 1.3)
    rob = centino(420, umore, 1.0)
    im.alpha_composite(rob, (w - 420 - 40, h - 420 - 120))
    f = font("testo", 30, 600)
    d.text((m, h - 110), HANDLE, font=f, fill=BIANCO)
    d.text((m, h - 68), SITO, font=font("testo", 26, 400), fill=GRIGIO)
    Path(percorso).parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(percorso, quality=93)
    return percorso


def _ease(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def reel(percorso, scene, fps=30, w=1080, h=1920, durata_scena=2.4):
    """Reel 9:16 con testo cinetico, Centino animato, barra di avanzamento e traccia audio muta.
    scene: lista di {"testo", "evidenza"?, "umore"?, "durata"?}."""
    Path(percorso).parent.mkdir(parents=True, exist_ok=True)
    base = sfondo(w, h, ((CORALLO, 0.2, 0.15), (GIALLO, 0.85, 0.9), (MENTA, 0.9, 0.2))).convert("RGBA")
    tot = sum(s.get("durata", durata_scena) for s in scene)
    n_frame = int(tot * fps)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264",
           "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
           "-movflags", "+faststart", percorso]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ft, fe = font("titolo", 96, 700), font("titolo", 132, 700)
    m = 90
    inizio = 0.0
    cache_rob = {}
    for s in scene:
        dur = s.get("durata", durata_scena)
        for i in range(int(dur * fps)):
            t = i / fps
            g = (inizio + t)
            im = base.copy()
            d = ImageDraw.Draw(im)
            # barra di avanzamento in alto
            d.rounded_rectangle([m, 120, w - m, 128], radius=4, fill=(40, 42, 56))
            d.rounded_rectangle([m, 120, m + (w - 2 * m) * g / tot, 128], radius=4, fill=CORALLO)
            # testo che entra dal basso
            a = _ease(t / 0.45)
            off = int((1 - a) * 60)
            strato = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ds = ImageDraw.Draw(strato)
            y = _blocco(ds, m, 420 + off, s["testo"], ft, BIANCO, w - 2 * m)
            if s.get("evidenza"):
                b = _ease((t - 0.25) / 0.45)
                y2 = y + 10 + int((1 - b) * 50)
                lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                _blocco(ImageDraw.Draw(lay), m, y2, s["evidenza"], fe, GIALLO, w - 2 * m, 1.0)
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * b)))
                strato.alpha_composite(lay)
            strato.putalpha(strato.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(strato)
            # Centino che respira
            umore = s.get("umore", "ok")
            fase = round(g * 10) / 10
            chiave = (umore, fase)
            if chiave not in cache_rob:
                cache_rob[chiave] = centino(520, umore, fase)
            dy = int(math.sin(g * 2.4) * 12)
            im.alpha_composite(cache_rob[chiave], ((w - 520) // 2, h - 520 - 260 + dy))
            d.text((m, h - 150), HANDLE, font=font("testo", 34, 600), fill=BIANCO)
            d.text((m, h - 104), SITO, font=font("testo", 28, 400), fill=GRIGIO)
            pr.stdin.write(im.convert("RGB").tobytes())
        inizio += dur
    pr.stdin.close()
    pr.wait()
    if pr.returncode != 0:
        raise RuntimeError("ffmpeg non ha prodotto il video")
    # copertina = fotogramma centrale
    cop = str(Path(percorso).with_suffix(".jpg"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(min(tot - 0.1, durata_scena * 1.5)), "-i", percorso,
                    "-frames:v", "1", "-q:v", "3", cop])
    return {"video": percorso, "copertina": cop, "secondi": round(tot, 1), "frame": n_frame}
