"""Rule-based, explainable sorting decisions."""

from pathlib import Path
import fnmatch
import re

from backend.scanner.classifier import classify


DEFAULT_RULES = [
    {"id": "images", "name": "Images", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Images"}], "destination": "Images"},
    {"id": "videos", "name": "Videos", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Videos"}], "destination": "Videos"},
    {"id": "pdfs", "name": "PDFs", "enabled": True, "conditions": [{"field": "extension", "operator": "is", "value": "pdf"}], "destination": "Documents/PDFs"},
    {"id": "documents", "name": "Documents", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Documents"}], "destination": "Documents"},
    {"id": "spreadsheets", "name": "Spreadsheets", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Spreadsheets"}], "destination": "Documents/Spreadsheets"},
    {"id": "archives", "name": "Archives", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Archives"}], "destination": "Archives"},
    {"id": "code", "name": "Code", "enabled": True, "conditions": [{"field": "category", "operator": "is", "value": "Code"}], "destination": "Code"},
]


def _value(record: dict, field: str) -> str:
    if field == "filename":
        return record.get("name", "")
    if field == "extension":
        return record.get("extension", "")
    if field == "mime_type":
        return record.get("mime_type", "")
    if field == "category":
        return record.get("category") or classify(Path(record.get("path", "")))
    if field == "folder":
        return str(Path(record.get("relative_path", "")).parent)
    return str(record.get(field, ""))


def matches(record: dict, condition: dict) -> bool:
    actual = _value(record, condition.get("field", "")).lower()
    expected = str(condition.get("value", "")).lower()
    operator = condition.get("operator", "is")
    if operator == "is":
        return actual == expected
    if operator == "is_not":
        return actual != expected
    if operator == "contains":
        return expected in actual
    if operator == "starts_with":
        return actual.startswith(expected)
    if operator == "ends_with":
        return actual.endswith(expected)
    if operator == "matches":
        try:
            return re.search(expected, actual) is not None
        except re.error:
            return False
    if operator == "glob":
        return fnmatch.fnmatch(actual, expected)
    return False


def find_destination(record: dict, rules: list[dict]) -> tuple[str, str] | None:
    """Return (destination, rule name) for the first matching enabled rule."""
    for rule in rules:
        if rule.get("enabled", True) and all(matches(record, condition) for condition in rule.get("conditions", [])):
            return str(rule.get("destination", "")).strip(), str(rule.get("name", "Custom rule"))
    return None