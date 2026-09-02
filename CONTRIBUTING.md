# Contributing to Sortix

Thanks for helping make file organization safer and more understandable.

## Development

Sortix intentionally uses the Python standard library and browser-native APIs. Keep filesystem behavior isolated under `backend/`, keep UI state in small frontend modules, and avoid adding a dependency when the standard library is sufficient.

Before opening a pull request:

```bash
python -m unittest discover -s tests -v
python -m compileall backend app.py
```

Do not run tests against real user folders. Add coverage using `tempfile.TemporaryDirectory`.

## Pull requests

Explain the user-facing behavior, safety implications, and how you tested it. Changes that move, rename, or delete files require a clear preview and rollback story.