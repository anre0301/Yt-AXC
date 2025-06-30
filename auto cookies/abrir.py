from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

service = Service("chromedriver.exe")  # o ruta completa
options = Options()
# No pongas headless ni perfiles para probar
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")
input("Presiona ENTER para cerrar...")
driver.quit()
