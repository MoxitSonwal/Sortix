"""Safety guardrails shared by preview and execution."""

from pathlib import Path


PROTECTED_NAMES = {
    ".git", ".ssh", ".gnupg", "system32", "program files",
    "library", "applications", "windows",
}


def is_protected(path: Path) -> bool:
    return any(part.lower() in PROTECTED_NAMES for part in path.parts)


def validate_move(source: Path, destination: Path, root: Path) -> None:
    try:
        source.resolve().relative_to(root.resolve())
        destination.parent.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("Sortix only moves files inside the selected folder.") from exc
    if is_protected(source) or is_protected(destination):
        raise ValueError("This path is protected. Choose a safer folder.")
    if source.resolve() == destination.resolve():
        raise ValueError("The file is already in its destination.")