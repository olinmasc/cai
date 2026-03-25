from backend.main import app as backend_app
import sys
import os
from fastapi import FastAPI

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 1. Import your actual backend application and rename it to avoid confusion

# 2. Create a new, blank FastAPI app just for Vercel
app = FastAPI()

# 3. Mount your backend to the /api path.
# This catches /api/auth/signup, strips the "/api", and sends exactly "/auth/signup" to your code!
app.mount("/api", backend_app)
