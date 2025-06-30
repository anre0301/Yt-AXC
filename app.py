from flask import Flask, render_template, request, Response, send_file, redirect, url_for
import os
import yt_dlp
import uuid
import tempfile
import subprocess
import requests
import urllib.request

app = Flask(__name__)

# 🔄 Descargar cookies actualizadas desde GitHub al iniciar
COOKIES_URL = "https://raw.githubusercontent.com/anre0301/Yt-AXC/main/cookies.txt"
cookies_path = os.path.join(os.getcwd(), "cookies.txt")

try:
    urllib.request.urlretrieve(COOKIES_URL, cookies_path)
    print("✅ cookies.txt actualizado desde GitHub")
except Exception as e:
    print(f"⚠️ No se pudo descargar cookies.txt automáticamente: {e}")

@app.route("/", endpoint="index_audio")
def index_audio():
    return render_template("index.html", modo="audio")

@app.route("/mp4", endpoint="index_video")
def index_video():
    return render_template("index.html", modo="video")

@app.route("/all", endpoint="index_all")
def index_all():
    return render_template("index.html", modo="all")

@app.route("/procesar", methods=["GET", "POST"])
def procesar():
    if request.method == "GET":
        return redirect(url_for("index_all"))

    url = request.form["url"]
    modo = request.form.get("modo", "all")

    if os.path.isfile(cookies_path):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'cookiefile': cookies_path
        }
    else:
        print("⚠️ No se encontraron cookies. Intentando sin autenticación.")
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

    if modo == "audio":
        formatos = [f for f in formatos if f.get("vcodec") == "none"]
    elif modo == "video":
        formatos = [f for f in formatos if f.get("vcodec") != "none"]

    formatos = [f for f in formatos if f.get("filesize") and f["filesize"] > 0]
    formatos.sort(key=lambda x: x.get("height", 0) if x.get("vcodec") != "none" else x["filesize"], reverse=True)

    thumb = info.get("thumbnail") or info.get("thumbnails", [{}])[-1].get("url")
    titulo = info.get("title", "video")

    return render_template("formatos.html", formatos=formatos, titulo=titulo, thumb=thumb, modo=modo)

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

@app.route("/descargar_mp3", methods=["POST"])
def descargar_mp3():
    url = request.form["stream_url"]
    filename = request.form["filename"].rsplit(".", 1)[0]
    ffmpeg_path = "/usr/bin/ffmpeg"  # Ruta típica en Render (Linux)

    if not os.path.isfile(ffmpeg_path):
        return "Error: ffmpeg no encontrado. Verifica la ruta en el código."

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
                return "Error: el archivo de audio no se descargó correctamente o está vacío."

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

            if not os.path.exists(salida_mp3):
                return "Error: El archivo MP3 no fue generado."

            return send_file(salida_mp3, as_attachment=True, download_name=f"{filename}.mp3")

    except Exception as e:
        return f"<pre>ERROR GENERAL: {str(e)}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
