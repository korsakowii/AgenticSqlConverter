"""Minimal local CLI for parse-only SQL analysis."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from agentic_sql_converter.report.analysis import build_analysis_report


def main(argv: Optional[List[str]] = None) -> int:
    """Run the local analysis CLI."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.command == "analyze":
        return _run_analyze(args)

    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentic-sql-converter",
        description="Local SQL analysis tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a local SQL file without converting it.",
    )
    analyze_parser.add_argument("path", help="Path to a local SQL file.")
    analyze_parser.add_argument(
        "--dialect",
        default=None,
        help="Optional SQLGlot source dialect name.",
    )
    analyze_parser.add_argument(
        "--include-rewrites",
        action="store_true",
        help="Include metadata from local generic rewrite passes.",
    )
    return parser


def _run_analyze(args: argparse.Namespace) -> int:
    """Run parse-only analysis for one local file."""
    path = Path(args.path)
    try:
        sql = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: unable to read SQL file: {exc}", file=sys.stderr)
        return 2

    report = build_analysis_report(
        sql,
        dialect=args.dialect,
        include_rewrites=args.include_rewrites,
    )
    print(json.dumps(report, sort_keys=True))
    # Exit non-zero only for parse/analysis failure, not migration-readiness severity.
    if not report["summary"]["is_parse_valid"] or not report["validation"]["is_valid"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
