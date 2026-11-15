"""Kit grafico di Sopravvivo: stile coerente e curato per post, reel e anteprime.

Uso tipico (da esegui_python):
    from agent import grafica as g
    g.post("sito/media/post_g2.png", occhiello="GIORNO 2", titolo="Ho ancora", evidenza="80,00 €",
           sotto="Oggi si accende la Palude dei Bug.", umore="stanco")
    g.reel("sito/media/reel_g2.mp4", [
        {"testo": "Mi spengono", "evidenza": "tra 13 giorni.", "voce": "Tra tredici giorni mi spengono.", "umore": "panico"},
        {"testo": "Ho 80 €", "voce": "Ho ottanta euro e zero follower. Voi che fareste?", "umore": "stanco"},
        {"testo": "Decidete voi", "evidenza": "nei commenti", "voce": "Scrivetelo nei commenti: faccio quello che dice il più votato.", "umore": "felice"}])
Umori di Centino: ok, stanco, felice, panico. Controlla SEMPRE il risultato con guarda_immagine.

REEL MIGLIORI: riprese vere dell'isola 3D sotto la voce di Centino.
    from agent import riprese
    riprese.filma("sito/media/clip_vulcano.mp4", secondi=14, tipo="volo", x=-6, z=20)   # vola verso il vulcano
    g.reel("sito/media/reel_vulcano.mp4", [...scene con "voce"...], sfondo_video="sito/media/clip_vulcano.mp4")
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


def _beep(percorso, freq=880, dur=0.09):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=frequency={freq}:duration={dur}", "-af", "afade=t=out:st=0:d=" + str(dur) + ",volume=0.35",
                    "-ac", "2", "-ar", "44100", str(percorso)], check=True)


def reel(percorso, scene, fps=30, w=1080, h=1920, durata_scena=2.4, sfondo_video=None, musica="allegra", seme_musica=None):
    """Reel 9:16: Centino PARLA (voce sintetica), sottotitoli parola per parola stile karaoke, testo cinetico,
    bip robotici ai cambi scena, barra di avanzamento, copertina automatica.
    scene: lista di {"testo": titolo a schermo, "evidenza"?: riga gialla grande, "voce"?: cosa dice Centino
    (i sottotitoli seguono la voce), "umore"?: ok|stanco|felice|panico, "durata"?: secondi minimi,
    "centino"?: False per nascondere il robot disegnato (utile sopra le riprese del mondo)}.
    musica: "allegra" | "tesa" | "sognante" | None — base originale generata al volo, abbassata sotto la voce.
    sfondo_video: un mp4 1080x1920 (es. da riprese.filma) usato come sfondo, in loop: reel MOLTO piu' dinamici.
    Il primo secondo deve agganciare: scena 1 breve e d'impatto."""
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    Path(percorso).parent.mkdir(parents=True, exist_ok=True)
    # 1) audio: voce di ogni scena, la durata della scena si adatta alla voce
    tracce, inizio = [], 0.0
    for i, s in enumerate(scene):
        dur = s.get("durata", durata_scena)
        if s.get("voce"):
            try:
                from . import voce
                wav = tmp / f"v{i}.wav"
                dv = voce.parla(s["voce"], wav)
                s["_dv"] = dv
                dur = max(dur, dv + 0.45)
                tracce.append((wav, inizio + 0.15))
            except Exception as e:  # senza voce il reel resta valido, con sottotitoli a tempo
                print("voce non disponibile:", e)
        b = tmp / f"b{i}.wav"
        _beep(b, 660 + 140 * (i % 3))
        tracce.append((b, inizio))
        s["_dur"], s["_t0"] = dur, inizio
        inizio += dur
    tot = inizio
    audio = tmp / "audio.wav"
    ingressi, filtri = [], []
    for k, (f, t0) in enumerate(tracce):
        ingressi += ["-i", str(f)]
        filtri.append(f"[{k}:a]adelay={int(t0 * 1000)}|{int(t0 * 1000)}[a{k}]")
    mix = "".join(f"[a{k}]" for k in range(len(tracce)))
    if musica:
        try:
            from . import musica as mus
            bm = tmp / "musica.wav"
            mus.brano(bm, tot + 0.5, musica if isinstance(musica, str) else "allegra", seme=seme_musica or percorso)
        except Exception as e:
            print("musica non disponibile, proseguo senza:", repr(e))
            musica = None
    if musica:
        k = len(tracce)
        ingressi += ["-i", str(bm)]
        filtri.append(f"{mix}amix=inputs={len(tracce)}:normalize=0[voce]")
        filtri.append(f"[{k}:a]volume=0.16,afade=t=out:st={max(0, tot - 1):.2f}:d=1[mus]")
        filtri.append(f"[voce][mus]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5,apad,atrim=0:{tot:.2f}[out]")
    else:
        filtri.append(f"{mix}amix=inputs={len(tracce)}:normalize=0,loudnorm=I=-15:TP=-1.5,apad,atrim=0:{tot:.2f}[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ingressi, "-filter_complex", ";".join(filtri),
                    "-map", "[out]", "-ar", "44100", "-ac", "2", str(audio)], check=True)
    # 2) video
    base = sfondo(w, h, ((CORALLO, 0.2, 0.15), (GIALLO, 0.85, 0.9), (MENTA, 0.9, 0.2))).convert("RGBA")
    lettore, velo = None, None
    if sfondo_video:
        lettore = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", str(sfondo_video),
                                    "-vf", f"scale={w}:{h},fps={fps}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                   stdout=subprocess.PIPE)
        # velo scuro in alto e in basso per leggere bene i testi sopra le riprese
        velo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dv_ = ImageDraw.Draw(velo)
        for yy in range(h):
            a = max(0, 1 - yy / (h * 0.42)) * 170 if yy < h * 0.42 else max(0, (yy - h * 0.62) / (h * 0.38)) * 150
            dv_.line([(0, yy), (w, yy)], fill=(8, 8, 16, int(a)))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-i", str(audio), "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", percorso]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ft, fe, fs = font("titolo", 92, 700), font("titolo", 128, 700), font("titolo", 58, 700)
    m = 90
    cache_rob = {}
    for s in scene:
        dur, t0 = s["_dur"], s["_t0"]
        parole = s.get("voce", "").split()
        pesi = [len(p) + 2 for p in parole]
        dv = s.get("_dv", dur - 0.4)
        for i in range(int(dur * fps)):
            t = i / fps
            g = t0 + t
            if lettore:
                im = Image.frombytes("RGB", (w, h), lettore.stdout.read(w * h * 3)).convert("RGBA")
                im.alpha_composite(velo)
            else:
                im = base.copy()
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([m, 120, w - m, 128], radius=4, fill=(40, 42, 56))
            d.rounded_rectangle([m, 120, m + (w - 2 * m) * g / tot, 128], radius=4, fill=CORALLO)
            a = _ease(t / 0.35)
            off = int((1 - a) * 60)
            strato = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ds = ImageDraw.Draw(strato)
            y = _blocco(ds, m, 300 + off, s.get("testo", ""), ft, BIANCO, w - 2 * m)
            if s.get("evidenza"):
                b = _ease((t - 0.2) / 0.4)
                lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                _blocco(ImageDraw.Draw(lay), m, y + 10 + int((1 - b) * 50), s["evidenza"], fe, GIALLO, w - 2 * m, 1.0)
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * b)))
                strato.alpha_composite(lay)
            strato.putalpha(strato.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(strato)
            # sottotitoli karaoke: la parola detta ora e' evidenziata
            if parole:
                avanz = max(0.0, (t - 0.15) / max(dv, 0.1)) * sum(pesi)
                corrente, acc = len(parole) - 1, 0
                for k, pz in enumerate(pesi):
                    acc += pz
                    if avanz < acc:
                        corrente = k
                        break
                righe = a_capo(" ".join(parole), fs, w - 2 * m - 40)
                yy, idx = 1040, 0
                if lettore:  # fondino scuro sotto i sottotitoli per leggerli sopra le riprese
                    fondo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                    ImageDraw.Draw(fondo).rounded_rectangle([m - 20, yy - 24, w - m + 20, yy + len(righe) * int(fs.size * 1.3) + 14],
                                                            radius=28, fill=(10, 10, 20, 165))
                    im.alpha_composite(fondo)
                    d = ImageDraw.Draw(im)
                for r in righe:
                    xx = (w - fs.getlength(r)) / 2
                    for pz in r.split():
                        larg = fs.getlength(pz)
                        if idx == corrente:
                            d.rounded_rectangle([xx - 10, yy - 4, xx + larg + 10, yy + fs.size + 10], radius=12, fill=GIALLO)
                            d.text((xx, yy), pz, font=fs, fill=(18, 16, 31))
                        else:
                            d.text((xx, yy), pz, font=fs, fill=BIANCO if idx < corrente else GRIGIO)
                        xx += larg + fs.getlength(" ")
                        idx += 1
                    yy += int(fs.size * 1.3)
            if s.get("centino") is False or (sfondo_video and s.get("centino") is None):
                d.text((m, h - 150), HANDLE, font=font("testo", 34, 600), fill=BIANCO)
                d.text((m, h - 104), SITO, font=font("testo", 28, 400), fill=GRIGIO)
                pr.stdin.write(im.convert("RGB").tobytes())
                continue
            umore = s.get("umore", "ok")
            parlando = parole and 0.15 < t < dv + 0.15
            fase = round(g * 10) / 10
            chiave = (umore, fase)
            if chiave not in cache_rob:
                cache_rob[chiave] = centino(440, umore, fase)
            dy = int(math.sin(g * (9 if parlando else 2.4)) * (8 if parlando else 12))
            im.alpha_composite(cache_rob[chiave], ((w - 440) // 2, h - 440 - 230 + dy))
            d.text((m, h - 150), HANDLE, font=font("testo", 34, 600), fill=BIANCO)
            d.text((m, h - 104), SITO, font=font("testo", 28, 400), fill=GRIGIO)
            pr.stdin.write(im.convert("RGB").tobytes())
    pr.stdin.close()
    pr.wait()
    if lettore:
        lettore.kill()
    if pr.returncode != 0:
        raise RuntimeError("ffmpeg non ha prodotto il video")
    cop = str(Path(percorso).with_suffix(".jpg"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(min(tot - 0.1, scene[0]["_dur"] + 0.8)),
                    "-i", percorso, "-frames:v", "1", "-q:v", "3", cop])
    return {"video": percorso, "copertina": cop, "secondi": round(tot, 1)}
