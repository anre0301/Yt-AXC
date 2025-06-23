from flask import Flask, render_template, request, Response, send_file
import os
import yt_dlp
import uuid
import tempfile
import subprocess
import requests

app = Flask(__name__)

@app.route("/", endpoint="index_audio")
def index_audio():
    return render_template("index.html", modo="audio")

@app.route("/mp4", endpoint="index_video")
def index_video():
    return render_template("index.html", modo="video")

@app.route("/all", endpoint="index_all")
def index_all():
    return render_template("index.html", modo="all")

@app.route("/procesar", methods=["POST"])
def procesar():
    url = request.form["url"]
    modo = request.form.get("modo", "all")

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return f"Error: {str(e)}"

    formatos = info.get("formats", [])

    # Filtrar por modo
    if modo == "audio":
        formatos = [f for f in formatos if f.get("vcodec") == "none"]
    elif modo == "video":
        formatos = [f for f in formatos if f.get("vcodec") != "none"]

    # Solo formatos con tamaño válido
    formatos = [f for f in formatos if f.get("filesize") and f["filesize"] > 0]

    # Ordenar por calidad
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
    from flask import send_file
    import subprocess

    url = request.form["stream_url"]
    filename = request.form["filename"].rsplit(".", 1)[0]
    ffmpeg_path = r"C:\Users\yosel\Downloads\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

    if not os.path.isfile(ffmpeg_path):
        return "Error: ffmpeg.exe no encontrado. Verifica la ruta en el código."

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_audio = os.path.join(tmpdir, f"{uuid.uuid4()}.webm")
            salida_mp3 = os.path.join(tmpdir, f"{filename}.mp3")

            print(f"🔽 Descargando: {url}")
            r = requests.get(url, stream=True, timeout=30)
            with open(temp_audio, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
                return "Error: el archivo de audio no se descargó correctamente o está vacío."

            print("🎧 Ejecutando FFmpeg...")
            result = subprocess.run([
                ffmpeg_path,
                "-i", temp_audio,
                "-vn",
                "-ab", "192k",
                "-ar", "44100",
                "-y", salida_mp3
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"❌ FFmpeg ERROR:\n{result.stderr}")
                return f"<pre>FFmpeg ERROR:\n{result.stderr}</pre>"

            if not os.path.exists(salida_mp3):
                return "Error: El archivo MP3 no fue generado."

            print(f"✅ MP3 generado: {salida_mp3} ({os.path.getsize(salida_mp3)} bytes)")
            return send_file(salida_mp3, as_attachment=True, download_name=f"{filename}.mp3")

    except Exception as e:
        return f"<pre>ERROR GENERAL: {str(e)}</pre>"


if __name__ == "__main__":
    app.run(debug=True)
