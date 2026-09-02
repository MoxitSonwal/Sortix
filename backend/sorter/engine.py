"""Dry-run planning and safe transactional execution."""

from pathlib import Path
import shutil
import uuid

from backend.filesystem.paths import collision_safe, contained, resolve_directory
from backend.rules.engine import DEFAULT_RULES, find_destination
from backend.safety.guards import validate_move


def preview(root: str, records: list[dict], rules: list[dict] | None = None) -> dict:
    base = resolve_directory(root)
    active_rules = rules or DEFAULT_RULES
    moves = []
    skipped = []
    for record in records:
        source = Path(record["path"]).expanduser().resolve()
        if not source.exists() or not contained(source, base):
            skipped.append({"path": str(source), "reason": "File is no longer inside the selected folder."})
            continue
        decision = find_destination(record, active_rules)
        if not decision:
            skipped.append({"path": str(source), "reason": "No enabled rule matched this file."})
            continue
        destination_dir, rule_name = decision
        destination = (base / destination_dir / source.name).resolve()
        try:
            validate_move(source, destination, base)
        except ValueError as exc:
            skipped.append({"path": str(source), "reason": str(exc)})
            continue
        if contained(destination, base) and destination.parent == source.parent:
            skipped.append({"path": str(source), "reason": "File is already organized."})
            continue
        planned = collision_safe(destination)
        moves.append({
            "source": str(source),
            "destination": str(planned),
            "relative_source": str(source.relative_to(base)),
            "relative_destination": str(planned.relative_to(base)),
            "rule": rule_name,
            "status": "planned",
        })
    return {"root": str(base), "moves": moves, "skipped": skipped, "count": len(moves)}


def execute(plan: dict) -> dict:
    base = resolve_directory(plan["root"])
    operation_id = str(uuid.uuid4())
    moved = []
    errors = []
    for item in plan.get("moves", []):
        source = Path(item["source"]).resolve()
        destination = Path(item["destination"]).resolve()
        try:
            validate_move(source, destination, base)
            if not source.exists():
                raise FileNotFoundError("Source file no longer exists.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination = collision_safe(destination)
            shutil.move(str(source), str(destination))
            moved.append({
                "source": str(source),
                "destination": str(destination),
                "relative_source": str(source.relative_to(base)),
                "relative_destination": str(destination.relative_to(base)),
            })
        except (OSError, ValueError) as exc:
            errors.append({"source": str(source), "destination": str(destination), "error": str(exc)})
    return {
        "operation_id": operation_id,
        "root": str(base),
        "moved": moved,
        "errors": errors,
        "count": len(moved),
        "status": "completed" if not errors else ("partial" if moved else "failed"),
    }