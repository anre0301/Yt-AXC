import browser_cookie3
import http.cookiejar
import os
import subprocess

# Ruta donde se guardará cookies.txt
cookies_file = "cookies.txt"

# Extraer cookies de YouTube desde Chrome
cj = browser_cookie3.chrome(domain_name=".youtube.com")

# Guardar en formato Netscape
cj.clear_expired_cookies()
cj.save(cookies_file, ignore_discard=True, ignore_expires=True)

print("✅ cookies.txt exportado desde el navegador.")

# Subir a GitHub
try:
    subprocess.run(["git", "add", "cookies.txt"], check=True)
    subprocess.run(["git", "commit", "-m", "🆕 Actualización automática de cookies"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 cookies.txt subido a GitHub.")
except subprocess.CalledProcessError as e:
    print(f"❌ Error al subir a GitHub: {e}")
