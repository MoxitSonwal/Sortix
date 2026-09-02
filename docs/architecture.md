# Sortix architecture notes

## Request flow

The browser never performs filesystem operations itself. It sends a local request to the Python server:

1. `POST /api/scan` resolves and recursively scans the selected directory.
2. `POST /api/preview` evaluates the current ordered rules and returns source/destination pairs.
3. `POST /api/sort` executes only the returned plan after the user presses Approve & sort.
4. `GET /api/history` exposes the JSON audit trail.
5. `POST /api/undo` reverses the recorded moves in reverse order.

## Trust boundaries

The selected root is the boundary for both preview and execution. A destination must remain inside it, symlinks are not followed, and protected path segments are rejected. The server binds to loopback by default.

## Extensibility

The `FileRecord` model is metadata-oriented so future classifiers can be added without changing the move engine. `find_destination` accepts ordered rules, leaving room for a natural-language planner that produces the same reviewable plan format. Duplicate detection is isolated behind `find_duplicates`, allowing future perceptual hash implementations.