"""Riprese dell'isola 3D per i reel: un browser senza schermo apre il mondo in modalita' cinema e filma.
Uso: from agent import riprese; riprese.filma("sito/media/clip.mp4", secondi=12, tipo="volo", x=0, z=6, notte=False)
tipo: "volo" (volo dall'alto che scende verso il punto x,z) | "passeggiata" (il robot cammina intorno a x,z).
Poi: grafica.reel(..., sfondo_video="sito/media/clip.mp4") mette voce e sottotitoli sopra le riprese."""
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RADICE_SITO = Path(__file__).resolve().parent.parent / "sito"


def _assicura_browser():
    import os
    if os.environ.get("CHROME_PATH"):
        return
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        subprocess.run(["pip", "install", "-q", "playwright"], check=True)
    subprocess.run(["python", "-m", "playwright", "install", "--with-deps", "chromium"], capture_output=True)


def filma(uscita, secondi=12, tipo="volo", x=0, z=6, notte=False, w=540, h=960):
    _assicura_browser()
    from playwright.sync_api import sync_playwright
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(RADICE_SITO)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    porta = srv.server_address[1]
    cartella = Path(tempfile.mkdtemp())
    url = f"http://127.0.0.1:{porta}/mondo/?cinema={tipo}&x={x}&z={z}" + ("&notte=1" if notte else "")
    with sync_playwright() as p:
        import os
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                            record_video_dir=str(cartella), record_video_size={"width": w, "height": h})
        pg = ctx.new_page()
        pg.goto(url)
        pg.wait_for_function("window.__pronto", timeout=60000)
        pg.wait_for_timeout(int((secondi + 1.5) * 1000))
        ctx.close()
        b.close()
    srv.shutdown()
    webm = next(cartella.glob("*.webm"))
    Path(uscita).parent.mkdir(parents=True, exist_ok=True)
    # salta il primo secondo e mezzo (caricamento), porta a 1080x1920, 30 fps
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.5", "-i", str(webm), "-t", str(secondi),
                    "-vf", "scale=1080:1920:flags=lanczos,fps=30", "-an", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-pix_fmt", "yuv420p", str(uscita)], check=True)
    shutil.rmtree(cartella, ignore_errors=True)
    return uscita
