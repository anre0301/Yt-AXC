import os
import subprocess
import shutil

# Ruta donde Chrome guarda el archivo exportado por la extensión
descargas = os.path.expanduser("~/Downloads/cookies.txt")
destino = os.path.join(os.getcwd(), "cookies.txt")

if os.path.exists(descargas):
    shutil.copy(descargas, destino)
    print("✅ cookies.txt copiado al proyecto")

    try:
        subprocess.run(["git", "add", "cookies.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "✅ Cookies actualizadas"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Cookies subidas a GitHub correctamente.")
    except subprocess.CalledProcessError as e:
        print("❌ Error al ejecutar comando git:", e)
else:
    print("❌ No se encontró cookies.txt en Descargas.")
