import os
import time
import pickle
import requests
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

print("🚀 Ejecutando automatización completa...")

# Configurar Chrome en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0")

# Iniciar navegador
try:
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
except Exception as e:
    print(f"❌ Error al iniciar Chrome: {e}")
    exit()

driver.get("https://www.youtube.com")
time.sleep(5)

# Guardar cookies
cookies_path = "cookies.txt"
with open(cookies_path, "w", encoding="utf-8") as f:
    for cookie in driver.get_cookies():
        line = f"{cookie['name']}\t{cookie.get('domain', '')}\t{cookie.get('path', '/')}\t{'TRUE' if cookie.get('secure', False) else 'FALSE'}\t0\t{cookie['value']}\n"
        f.write(line)

driver.quit()
print("✅ Cookies extraídas correctamente")

# Subir a GitHub
print("📦 Subiendo cookies.txt a GitHub...")
fecha = datetime.utcnow().isoformat()

try:
    subprocess.run("git add cookies.txt", shell=True, check=True)
    subprocess.run(f'git commit -m "Auto update cookies - {fecha}"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("✅ Push completado.")
except subprocess.CalledProcessError as e:
    print(f"❌ Error al hacer git push: {e}")

print("✅ Todo completado correctamente.")
