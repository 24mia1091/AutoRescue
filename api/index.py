import os
from vercel_wsgi import handle

# Ensure we can import the Flask app
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(str(ROOT))

# Import Flask app
from app import app as flask_app

# Vercel handler
def handler(environ, start_response):
    return handle(environ, start_response, flask_app)
