import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()

    _import_error = f"{type(e).__name__}: {e}"

    @app.get("/{path:path}")
    def fallback(path: str = ""):
        return {"error": "import_failed", "detail": _import_error}
