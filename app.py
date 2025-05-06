import os
import sys
import time
import socket
import webview
import random
import string
import tempfile
import threading
import django
import traceback
from django.core.management import execute_from_command_line

# Handle PyInstaller _MEIPASS directory
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.join(BASE_DIR, "eballot_api")

# Ensure Django project is in path
sys.path.append(BASE_DIR)
sys.path.append(PROJECT_DIR)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eballot_api.settings")

# Generate secret key and store it
def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

key_dir = os.path.join(tempfile.gettempdir(), 'eballot_app')
os.makedirs(key_dir, exist_ok=True)
secret_key_file = os.path.join(key_dir, 'secret_key.txt')

if not os.path.exists(secret_key_file):
    secret_key = generate_secret_key()
    with open(secret_key_file, 'w') as f:
        f.write(secret_key)
else:
    with open(secret_key_file, 'r') as f:
        secret_key = f.read().strip()

print("SECRET_KEY loaded from file.")

# Setup Django
os.environ["EBALLOT_SECRET_KEY"] = secret_key
django.setup()

# Utility to find a free port
def find_free_port(start=8000, end=9000):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free ports available.")

def start_gui(port):
    """Run the GUI in the main thread."""
    # Wait a few seconds for the server to start
    time.sleep(3)
    webview.create_window("Ballot Query", f"http://127.0.0.1:{port}/ballotquery/", width=1024, height=768)
    webview.start()

if __name__ == "__main__":
    try:
        port = find_free_port()

        # Start Django in a background thread
        def run_django_server():
            sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload', '--nothreading']
            execute_from_command_line(sys.argv)

        django_thread = threading.Thread(target=run_django_server, daemon=True)
        django_thread.start()

        # Run the GUI in the main thread (which is required by pywebview)
        start_gui(port)

    except Exception as e:
        print("Fatal error:", e)
        traceback.print_exc()
