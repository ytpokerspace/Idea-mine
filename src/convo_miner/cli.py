from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import load_export, write_batches, write_catalog


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="convo-miner",
        description="Prepare a ChatGPT export for five-conversation research batches.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import", help="Parse export and create catalog plus batch files")
    imp.add_argument("export_json", type=Path, help="Path to conversations.json from your export")
    imp.add_argument("--output", type=Path, default=Path("data/processed"))
    imp.add_argument("--batch-size", type=int, default=5)
    imp.add_argument("--max-chars", type=int, default=12000, help="Maximum characters per source section")
    args = parser.parse_args()
    try:
        conversations = load_export(args.export_json)
        if not conversations:
            print("No conversations with readable user/assistant text were found.")
            return 2
        args.output.mkdir(parents=True, exist_ok=True)
        write_catalog(conversations, args.output / "catalog.json")
        files = write_batches(conversations, args.output / "batches", args.batch_size, args.max_chars)
        print(json.dumps({
            "conversations_imported": len(conversations),
            "batch_size": args.batch_size,
            "batch_count": (len(conversations) + args.batch_size - 1) // args.batch_size,
            "files_written": [str(p) for p in files],
            "catalog": str(args.output / "catalog.json"),
        }, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Import failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
