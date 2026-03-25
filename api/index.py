from backend.main import app as fastapi_app
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import your REAL backend app

# The Ultimate Vercel Fix:
# Intercept the raw request, strip the "/api" part from the URL,
# and pass it to your app. This preserves your CORS settings!


async def app(scope, receive, send):
    if scope.get("type") in ["http", "websocket"]:
        path = scope.get("path", "")
        if path.startswith("/api"):
            # Strip the first 4 characters ("/api")
            scope["path"] = path[4:] or "/"

    await fastapi_app(scope, receive, send)
