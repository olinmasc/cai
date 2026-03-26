import sys
import os

# Add backend/ directly to path so "from database import ..." works inside main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app  # noqa: F401 — Vercel picks up `app` automatically
