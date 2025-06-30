from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

CHROMEDRIVER_PATH = r"C:\Users\yosel\OneDrive\Desktop\YT1D\YOUTUBE-DOWNLOADER\auto cookies\chromedriver.exe"
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

print("✅ Abriendo YouTube...")
driver.get("https://www.youtube.com")
time.sleep(10)
driver.quit()

