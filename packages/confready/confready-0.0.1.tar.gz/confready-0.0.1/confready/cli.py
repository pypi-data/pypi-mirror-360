import subprocess
import sys
import time
import os
from pathlib import Path
import importlib.resources as pkg_resources
import confready  

CONFREADY_DIR = Path(confready.__file__).parent
FRONTEND_DIR = CONFREADY_DIR / "frontend"
BACKEND_DIR = CONFREADY_DIR / "server"

def run_backend():
    print("Starting Flask backend...")
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--port=8080"], cwd=str(BACKEND_DIR), env=env
    )
    return backend_process

def run_frontend():
    if not (FRONTEND_DIR / "package.json").exists():
        print("Error: Frontend package.json not found.")
        sys.exit(1)

    print("Installing frontend dependencies (if needed)...")
    subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)

    print("Starting React frontend...")
    frontend_process = subprocess.Popen(["npm", "start"], cwd=str(FRONTEND_DIR))
    return frontend_process

def main():
    backend_process = run_backend()
    time.sleep(3)
    frontend_process = run_frontend()
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()
