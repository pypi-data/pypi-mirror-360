import os
import subprocess
import sys
import time
import threading

from atlaz.headquarter.client import AtlazClient

def start_app_server():
    """Starts the Flask app server."""
    subprocess.run(["python", "-m", "atlaz.codeGen.backend.flask_server"])

def start_frontend_client():
    """Starts the AtlazClient."""
    client = AtlazClient()
    client.start_frontend()

def start_full_chain():
    #app_thread = threading.Thread(target=start_app_server)
    #app_thread.daemon = True
    #app_thread.start()
    #time.sleep(3)
    start_frontend_client()

def main():
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd) # Adjust this to match your actual logic
    start_full_chain()

if __name__ == "__main__":
    main()