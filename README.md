# Sortix

![Sortix logo](frontend/assets/sortix-logo.png)

**Your files. Organized intelligently.**

Sortix is a local-first, privacy-oriented file organizer. It scans metadata on your device, generates an explainable sorting plan, waits for approval, moves files without overwriting existing files, and keeps a history that can restore completed operations.

## Why this package is safe

The core flow is always:

**Scan → Analyze → Preview → Approve → Sort → Verify → Undo**

- No file contents are uploaded or sent to a cloud service.
- Preview is required in the UI before a batch move.
- The default engine never deletes files.
- Existing names are preserved with collision-safe names such as `photo (1).jpg`.
- Symlinks and protected path segments are skipped.
- Operations are recorded in `~/.sortix/history.json`.
- Exact duplicates are found using streaming SHA-256 hashes. Sortix never deletes them automatically.

## Run it

Requires Python 3.10 or newer. There are no third-party dependencies.

```bash
cd sortix
python app.py
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765), enter a local folder path such as `~/Downloads`, and choose **Scan folder**. Sortix is intentionally a local web UI served by a local Python process so it can work with real filesystem paths.

Use a different port with:

```bash
python app.py --port 9000
```

### Windows PowerShell

For a fresh Windows installation, see [README_WINDOWS.md](README_WINDOWS.md). The short version is:

```powershell
py --version
Set-Location .\sortix
py .\app.py
```

Then open `http://127.0.0.1:8765`. Windows paths such as `C:\Users\YourName\Downloads` and `~\Downloads` are supported.

## Included functionality

- Recursive metadata-first folder scanning
- File type categories and storage breakdown
- Explainable, rule-based sorting
- Custom rule builder stored in browser local storage
- Dry-run preview with source and destination paths
- Safe execution and collision handling
- Persistent activity history and undo
- Exact duplicate detection
- Filename/category/folder search and sorting
- Light and dark themes
- Keyboard-focusable controls and reduced visual motion

The browser file picker is not used for paths because browsers do not expose arbitrary local directory paths to JavaScript. The local app's folder field is deliberate: it makes the filesystem boundary explicit.

## Architecture

```text
frontend/                 Accessible single-page UI
  css/                    Tokens, base layout, components
  js/                     API client, formatting, rules, application state
  assets/                 Supplied official Sortix logo
backend/
  api/                    Dependency-free local HTTP server
  scanner/                Metadata scanner and classifier
  sorter/                 Preview and transactional moves
  rules/                  Explainable rule evaluator
  duplicates/             Streaming exact duplicate finder
  filesystem/             Path resolution and collision handling
  safety/                 Protected-path and containment guards
  history/                Persistent operation history and undo
tests/                    Temporary-directory tests for filesystem behavior
```

## Test

```bash
python -m unittest discover -s tests -v
```

Tests only use temporary directories; they never touch a user's real files.

## Roadmap

- Pause/resume progress for very large operations
- Persist user-defined rules server-side per workspace
- Similar-image and perceptual duplicate detection
- Optional native desktop packaging
- Natural-language rules that always produce a reviewable plan first

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports belong in [SECURITY.md](SECURITY.md), not public issues.

## License

MIT. See [LICENSE](LICENSE).