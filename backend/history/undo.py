"""Restore the moves from a completed operation."""

from pathlib import Path
import shutil

from backend.filesystem.paths import collision_safe


def undo(operation: dict) -> dict:
    restored = []
    errors = []
    for item in reversed(operation.get("moved", [])):
        current = Path(item["destination"])
        original = Path(item["source"])
        try:
            if not current.exists():
                raise FileNotFoundError("Moved file is no longer at the expected destination.")
            original.parent.mkdir(parents=True, exist_ok=True)
            target = collision_safe(original)
            shutil.move(str(current), str(target))
            restored.append({"from": str(current), "to": str(target)})
        except (OSError, ValueError) as exc:
            errors.append({"path": str(current), "error": str(exc)})
    return {"restored": restored, "errors": errors, "status": "completed" if not errors else "partial"}