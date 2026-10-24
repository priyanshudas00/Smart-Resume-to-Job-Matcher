"""Command-line interface for the resume matcher."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .file_handler import collect_resume_files
from .matcher import Matcher
from .reporter import format_detailed, format_result_table, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-matcher",
        description="Smart Resume-to-Job Matcher: score and rank resumes against a job description.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    match = sub.add_parser("match", help="Match resumes against a job description.")
    match.add_argument("--resumes", "-r", required=True, nargs="+",
                       help="Resume files or directories.")
    match.add_argument("--job", "-j", required=True, help="Job description file.")
    match.add_argument("--output", "-o", help="Optional output report file.")
    match.add_argument("--json", dest="json_output", help="Optional JSON output file.")
    match.add_argument("--top", type=int, default=None, help="Show only top N results.")
    match.add_argument("--min-score", type=float, default=0.0, help="Filter results below score.")

    validate = sub.add_parser("validate", help="Validate input files.")
    validate.add_argument("files", nargs="+", help="Files to validate.")

    return parser


def _expand_resume_inputs(inputs: list[str]) -> list[str]:
    paths: list[str] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            paths.extend(str(f) for f in collect_resume_files(p))
        else:
            paths.append(str(p))
    return paths


def run_match(args) -> int:
    resume_paths = _expand_resume_inputs(args.resumes)
    if not resume_paths:
        print("No resume files found.", file=sys.stderr)
        return 2
    matcher = Matcher()
    try:
        results = matcher.match_from_paths(resume_paths, args.job)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.min_score:
        results = [r for r in results if r.score >= args.min_score]
    for idx, r in enumerate(results, start=1):
        r.rank = idx

    print(format_result_table(results, top_n=args.top))
    print()
    print(format_detailed(results if args.top is None else results[:args.top]))

    if args.output:
        write_report(args.output, results, title="Resume Match Report")
        print(f"\nReport written to {args.output}")
    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as handle:
            json.dump([r.to_dict() for r in results], handle, indent=2)
        print(f"JSON written to {args.json_output}")
    return 0


def run_validate(args) -> int:
    from .file_handler import is_readable, validate_file_path

    ok = True
    for f in args.files:
        try:
            validate_file_path(f)
            print(f"OK   {f} ({'readable' if is_readable(f) else 'unreadable'})")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"FAIL {f}: {exc}")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "match":
        return run_match(args)
    if args.command == "validate":
        return run_validate(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
