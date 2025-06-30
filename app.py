from flask import Flask, render_template, request, Response, send_file, redirect, url_for
import os
import yt_dlp
import uuid
import tempfile
import subprocess
import requests
import urllib.request

app = Flask(__name__)

# 📥 Descargar automáticamente cookies desde GitHub (si estás en Render o local)
COOKIES_URL = "https://raw.githubusercontent.com/anre0301/Yt-AXC/main/cookies.txt"
cookies_path = os.path.join(os.getcwd(), "cookies.txt")

try:
    urllib.request.urlretrieve(COOKIES_URL, cookies_path)
    print("✅ cookies.txt descargado desde GitHub")
except Exception as e:
    print(f"⚠️ No se pudo descargar cookies.txt: {e}")

# 🏠 Página principal para modo audio
@app.route("/", endpoint="index_audio")
def index_audio():
    return render_template("index.html", modo="audio")

# 📹 Modo video
@app.route("/mp4", endpoint="index_video")
def index_video():
    return render_template("index.html", modo="video")

# 📁 Modo todos los formatos
@app.route("/all", endpoint="index_all")
def index_all():
    return render_template("index.html", modo="all")

# 🔄 Procesar URL
@app.route("/procesar", methods=["GET", "POST"])
def procesar():
    if request.method == "GET":
        return redirect(url_for("index_all"))

    url = request.form["url"]
    modo = request.form.get("modo", "all")

    # Configuración yt-dlp con o sin cookies
    if os.path.isfile(cookies_path):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'cookiefile': cookies_path
        }
    else:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        if "Sign in to confirm" in str(e):
            return f"""
<pre>
⚠️ Este video requiere iniciar sesión para confirmar que no eres un bot.

🔐 El sistema necesita cookies de autenticación.

✅ Solución:
1. Exporta tus cookies desde Chrome o Edge.
2. Sube el archivo `cookies.txt` a tu repositorio:
   https://github.com/anre0301/Yt-AXC

📘 Guía:
https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

🔍 Detalles técnicos:
{str(e)}
</pre>
"""
        return f"<pre>Error al procesar el enlace:\n{str(e)}</pre>"

    formatos = info.get("formats", [])

    # Filtrar por tipo
    if modo == "audio":
        formatos = [f for f in formatos if f.get("vcodec") == "none"]
    elif modo == "video":
        formatos = [f for f in formatos if f.get("vcodec") != "none"]

    # Limpiar y ordenar formatos
    formatos = [f for f in formatos if f.get("filesize") and f["filesize"] > 0]
    formatos.sort(key=lambda x: x.get("height", 0) if x.get("vcodec") != "none" else x["filesize"], reverse=True)

    # Datos para mostrar
    thumb = info.get("thumbnail") or info.get("thumbnails", [{}])[-1].get("url")
    titulo = info.get("title", "video")

    return render_template("formatos.html", formatos=formatos, titulo=titulo, thumb=thumb, modo=modo)

# 📥 Descargar archivo directo
@app.route("/descargar_stream", methods=["POST"])
def descargar_stream():
    stream_url = request.form["stream_url"]
    filename = request.form["filename"]

    try:
        response = requests.get(stream_url, stream=True)
        return Response(
            response.iter_content(chunk_size=8192),
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
            content_type="application/octet-stream"
        )
    except Exception as e:
        return f"Error al descargar: {str(e)}"

# 🎵 Convertir a MP3 (localmente)
@app.route("/descargar_mp3", methods=["POST"])
def descargar_mp3():
    url = request.form["stream_url"]
    filename = request.form["filename"].rsplit(".", 1)[0]

    # Cambiar la ruta de ffmpeg si estás en Render
    ffmpeg_path = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")  # Compatible con Render
    if not os.path.isfile(ffmpeg_path):
        return "❌ Error: ffmpeg no encontrado. Verifica la ruta o instala ffmpeg."

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_audio = os.path.join(tmpdir, f"{uuid.uuid4()}.webm")
            salida_mp3 = os.path.join(tmpdir, f"{filename}.mp3")

            r = requests.get(url, stream=True, timeout=30)
            with open(temp_audio, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
                return "❌ Error: el archivo descargado está vacío o falló."

            result = subprocess.run([
                ffmpeg_path,
                "-i", temp_audio,
                "-vn",
                "-ab", "192k",
                "-ar", "44100",
                "-y", salida_mp3
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                return f"<pre>FFmpeg ERROR:\n{result.stderr}</pre>"

            return send_file(salida_mp3, as_attachment=True, download_name=f"{filename}.mp3")

    except Exception as e:
        return f"<pre>ERROR GENERAL: {str(e)}</pre>"

# 🔧 Ejecutar en local (Render usará WSGI por defecto)
if __name__ == "__main__":
    app.run(debug=True)
