"""Conservative local file classification."""

from pathlib import Path


CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".heic"},
    "Videos": {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".opus"},
    "PDFs": {".pdf"},
    "Documents": {".doc", ".docx", ".odt", ".txt", ".rtf", ".md", ".pages"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".tsv", ".ods", ".numbers"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"},
    "Code": {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".java", ".c", ".cpp", ".go", ".rs", ".json", ".yaml", ".yml", ".sql", ".sh"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
    "Design": {".fig", ".sketch", ".psd", ".ai", ".xd", ".indd"},
    "E-books": {".epub", ".mobi", ".azw", ".azw3"},
    "Torrents": {".torrent"},
    "Temporary": {".tmp", ".temp", ".crdownload", ".part", ".log"},
}


def classify(path: Path) -> str:
    """Return a stable category using the extension only."""
    extension = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"


def mime_type(path: Path) -> str:
    import mimetypes
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"