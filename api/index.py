import os
from pathlib import Path

# Ensure we can import the Flask app
ROOT = Path(__file__).resolve().parents[1]
os.chdir(str(ROOT))

from app import app as app  # Vercel expects a WSGI app named "app"
