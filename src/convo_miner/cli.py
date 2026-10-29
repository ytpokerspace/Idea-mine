from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import load_export, search_index, write_batches, write_catalog, write_search_index


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="convo-miner",
        description="Import, index, and search a local conversation export.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import", help="Parse export and create catalog plus batch files")
    imp.add_argument("export_json", type=Path, help="Path to conversations.json from your export")
    imp.add_argument("--output", type=Path, default=Path("data/processed"))
    imp.add_argument("--batch-size", type=int, default=5)
    imp.add_argument("--max-chars", type=int, default=12000, help="Maximum characters per source section")
    search = sub.add_parser("search", help="Search a generated local text index")
    search.add_argument("query", help="All query words must match")
    search.add_argument("--index", type=Path, default=Path("data/processed/search-index.json"))
    search.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    try:
        if args.command == "search":
            results = search_index(args.index, args.query, args.limit)
            print(json.dumps({"query": args.query, "result_count": len(results), "results": results}, indent=2, ensure_ascii=False))
            return 0
        conversations = load_export(args.export_json)
        if not conversations:
            print("No conversations with readable user/assistant text were found.")
            return 2
        args.output.mkdir(parents=True, exist_ok=True)
        write_catalog(conversations, args.output / "catalog.json")
        write_search_index(conversations, args.output / "search-index.json")
        files = write_batches(conversations, args.output / "batches", args.batch_size, args.max_chars)
        print(json.dumps({
            "conversations_imported": len(conversations),
            "batch_size": args.batch_size,
            "batch_count": (len(conversations) + args.batch_size - 1) // args.batch_size,
            "files_written": [str(p) for p in files],
            "catalog": str(args.output / "catalog.json"),
            "search_index": str(args.output / "search-index.json"),
        }, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"{args.command.title()} failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
