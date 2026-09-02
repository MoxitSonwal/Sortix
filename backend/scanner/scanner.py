"""Responsive, metadata-first recursive scanner."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .classifier import classify, mime_type


@dataclass(frozen=True)
class FileRecord:
    path: str
    name: str
    relative_path: str
    extension: str
    mime_type: str
    category: str
    size: int
    created: str
    modified: str
    accessed: str

    def as_dict(self) -> dict:
        return asdict(self)


def _iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def iter_files(root: Path, include_hidden: bool = False) -> Iterator[FileRecord]:
    """Yield file metadata without reading file contents."""
    root = root.expanduser().resolve()
    for path in root.rglob("*"):
        try:
            if not path.is_file() or path.is_symlink():
                continue
            if not include_hidden and any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            stat = path.stat()
        except (OSError, ValueError):
            continue
        yield FileRecord(
            path=str(path),
            name=path.name,
            relative_path=str(path.relative_to(root)),
            extension=path.suffix.lower().lstrip("."),
            mime_type=mime_type(path),
            category=classify(path),
            size=stat.st_size,
            created=_iso(getattr(stat, "st_ctime", stat.st_mtime)),
            modified=_iso(stat.st_mtime),
            accessed=_iso(stat.st_atime),
        )


def scan(root: str, include_hidden: bool = False) -> dict:
    directory = Path(root).expanduser()
    if not directory.exists() or not directory.is_dir():
        raise ValueError("Choose a folder that exists and is accessible.")
    records = list(iter_files(directory, include_hidden=include_hidden))
    category_counts: dict[str, int] = {}
    category_sizes: dict[str, int] = {}
    for record in records:
        category_counts[record.category] = category_counts.get(record.category, 0) + 1
        category_sizes[record.category] = category_sizes.get(record.category, 0) + record.size
    folder_count = sum(1 for path in directory.rglob("*") if path.is_dir() and not path.is_symlink())
    return {
        "root": str(directory.resolve()),
        "files": [record.as_dict() for record in records],
        "file_count": len(records),
        "folder_count": folder_count,
        "total_size": sum(record.size for record in records),
        "category_counts": category_counts,
        "category_sizes": category_sizes,
        "last_scanned": datetime.now(timezone.utc).isoformat(),
    }