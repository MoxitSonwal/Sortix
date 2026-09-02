"""Start the local Sortix application."""

import argparse

from backend.api.server import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sortix local-first file organizer")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    run(args.host, args.port)