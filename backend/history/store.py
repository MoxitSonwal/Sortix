"""Small JSON history store kept outside the user's selected directory."""

import json
from datetime import datetime, timezone
from pathlib import Path


def _history_path() -> Path:
    path = Path.home() / ".sortix"
    path.mkdir(parents=True, exist_ok=True)
    return path / "history.json"


def list_history() -> list[dict]:
    try:
        return json.loads(_history_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def append(operation: dict) -> dict:
    history = list_history()
    item = {**operation, "timestamp": datetime.now(timezone.utc).isoformat()}
    history.insert(0, item)
    _history_path().write_text(json.dumps(history[:100], indent=2), encoding="utf-8")
    return item


def update(operation_id: str, replacement: dict) -> dict | None:
    history = list_history()
    for index, item in enumerate(history):
        if item.get("operation_id") == operation_id:
            history[index] = {**item, **replacement}
            _history_path().write_text(json.dumps(history[:100], indent=2), encoding="utf-8")
            return history[index]
    return None