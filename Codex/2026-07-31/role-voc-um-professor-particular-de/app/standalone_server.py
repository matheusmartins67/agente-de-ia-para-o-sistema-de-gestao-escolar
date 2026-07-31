"""Dependency-free local HTTP server for Windows installations without Docker."""

import argparse
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app.tutor import TutorService

WEB_FILE = Path(__file__).parent / "web" / "index.html"


def load_local_env() -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_local_env()
tutor = TutorService(os.getenv("LLM_PROVIDER", "mock"))


class TutorHandler(BaseHTTPRequestHandler):
    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/v1/health":
            self._json(HTTPStatus.OK, {"status": "ok", "service": "school-management-assistant", "provider": tutor.provider})
        elif path == "/":
            content = WEB_FILE.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/v1/chat":
            self._json(HTTPStatus.NOT_FOUND, {"detail": "Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(size)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except UnicodeDecodeError:
                # Windows PowerShell 5.1 can send JSON as Windows-1252.
                payload = json.loads(raw_body.decode("cp1252"))
            message, level = payload.get("message"), payload.get("student_level")
            if not isinstance(message, str) or not message.strip() or len(message) > 12_000:
                raise ValueError("message must be a non-empty string up to 12000 characters")
            if level is not None and (not isinstance(level, int) or level not in (1, 2, 3)):
                raise ValueError("student_level must be 1, 2, or 3")
            self._json(HTTPStatus.OK, {"reply": tutor.reply(message, level), "conversation_id": payload.get("conversation_id"), "provider": tutor.provider})
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": str(exc)})
        except RuntimeError as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"detail": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8017)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), TutorHandler)
    print(f"Tutor Agent listening at http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
