import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess

# ✅ Configurar Chrome sin interfaz (modo headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("🌐 Abriendo YouTube para extraer cookies...")
driver.get("https://www.youtube.com")

time.sleep(5)  # Espera a que cargue la página completamente

cookies = driver.get_cookies()

with open("cookies.txt", "w", encoding="utf-8") as f:
    for cookie in cookies:
        line = f"{cookie['name']}\t{cookie['value']}\n"
        f.write(line)

driver.quit()
print("✅ cookies.txt generado")

# 📤 Subir cookies.txt a GitHub
print("📤 Subiendo cookies.txt a GitHub...")

try:
    subprocess.run(["git", "config", "--global", "user.email", "axc983744@gmail.com"], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "aysAYS0301@"], check=True)
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "add", "cookies.txt"], check=True)
    subprocess.run(["git", "commit", "-m", "🔄 Update cookies"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Push exitoso")
except subprocess.CalledProcessError as e:
    print(f"❌ Error subiendo a GitHub: {e}")
