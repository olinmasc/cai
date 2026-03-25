import sys
import os

# Make backend/ importable from the api/ entry point
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app  # noqa: F401 — Vercel picks up `app` automatically
