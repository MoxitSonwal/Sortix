"""Dependency-free local HTTP server."""

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from backend.duplicates.finder import find_duplicates
from backend.history import store
from backend.history.undo import undo
from backend.scanner.scanner import scan
from backend.sorter.engine import execute, preview


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class SortixHandler(BaseHTTPRequestHandler):
    server_version = "Sortix/1.0"

    def log_message(self, format, *args):
        return

    def _send(self, status: int, body, content_type: str = "application/json"):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._send(200, {"ok": True, "product": "Sortix"})
        if parsed.path == "/api/history":
            return self._send(200, {"history": store.list_history()})
        if parsed.path.startswith("/api/"):
            return self._send(404, {"error": "That Sortix endpoint does not exist."})
        self._serve_frontend(parsed.path)

    def _serve_frontend(self, path: str):
        relative = path.lstrip("/") or "index.html"
        candidate = (FRONTEND / relative).resolve()
        if not str(candidate).startswith(str(FRONTEND.resolve())) or not candidate.is_file():
            candidate = FRONTEND / "index.html"
        try:
            body = candidate.read_bytes()
            content_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
            self._send(200, body, content_type)
        except OSError:
            self._send(404, {"error": "Sortix could not load that resource."})

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._payload()
            if parsed.path == "/api/scan":
                return self._send(200, scan(payload["path"], bool(payload.get("include_hidden"))))
            if parsed.path == "/api/preview":
                return self._send(200, preview(payload["root"], payload.get("records", []), payload.get("rules")))
            if parsed.path == "/api/sort":
                result = execute(payload)
                item = store.append(result)
                return self._send(200, item)
            if parsed.path == "/api/undo":
                history = next((item for item in store.list_history() if item.get("operation_id") == payload.get("operation_id")), None)
                if not history:
                    return self._send(404, {"error": "Sortix could not find that operation in history."})
                result = undo(history)
                store.update(payload["operation_id"], {"undo": result, "status": "undone" if not result["errors"] else "partially-undone"})
                return self._send(200, result)
            if parsed.path == "/api/duplicates":
                result = scan(payload["path"], bool(payload.get("include_hidden")))
                return self._send(200, find_duplicates(result["files"]))
            return self._send(404, {"error": "That Sortix action does not exist."})
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            return self._send(400, {"error": str(exc) or "Sortix could not understand that request."})
        except OSError:
            return self._send(403, {"error": "Sortix could not access that folder. Check permissions and try again."})


def run(host: str = "127.0.0.1", port: int = 8765):
    server = ThreadingHTTPServer((host, port), SortixHandler)
    print(f"Sortix is running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()