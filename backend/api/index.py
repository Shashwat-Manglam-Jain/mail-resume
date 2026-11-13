import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
except Exception:
    import json

    _tb = traceback.format_exc()

    async def app(scope, receive, send):
        if scope["type"] == "http":
            body = json.dumps({"error": "import_failed", "traceback": _tb}).encode()
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({"type": "http.response.body", "body": body})
