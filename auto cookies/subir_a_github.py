import os
import subprocess
import datetime

REPO_PATH = r"C:\Users\yosel\OneDrive\Desktop\YT1D\YOUTUBE-DOWNLOADER"
COMMIT_MSG = f"Auto update cookies - {datetime.datetime.now().isoformat()}"

os.chdir(REPO_PATH)

print("📦 Subiendo cookies.txt a GitHub...")
subprocess.run(["git", "add", "cookies.txt"])
subprocess.run(["git", "commit", "-m", COMMIT_MSG])
subprocess.run(["git", "push", "origin", "main"])  # o usa "master" si tu rama se llama así

print("✅ Push completado.")
