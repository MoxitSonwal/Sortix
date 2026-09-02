"""Exact duplicate detection using size grouping and streaming SHA-256."""

from collections import defaultdict
from hashlib import sha256
from pathlib import Path


def _hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(records: list[dict]) -> dict:
    by_size: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        by_size[int(record.get("size", 0))].append(record)
    groups: dict[str, list[dict]] = defaultdict(list)
    for candidates in by_size.values():
        if len(candidates) < 2:
            continue
        for record in candidates:
            try:
                groups[_hash(Path(record["path"]))].append(record)
            except (OSError, KeyError):
                continue
    duplicate_groups = []
    reclaimable = 0
    for digest, matches in groups.items():
        if len(matches) < 2:
            continue
        size = int(matches[0].get("size", 0))
        reclaimable += size * (len(matches) - 1)
        duplicate_groups.append({"hash": digest, "size": size, "files": matches})
    return {
        "groups": duplicate_groups,
        "group_count": len(duplicate_groups),
        "duplicate_count": sum(len(group["files"]) for group in duplicate_groups),
        "reclaimable_bytes": reclaimable,
    }