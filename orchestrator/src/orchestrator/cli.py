from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .core import ExecutionResult, WestExecutor
from .logger import SessionLogger

DEFAULT_BOARD = "frdm_mcxn947/mcxn947/cpu0"
DEFAULT_LOG_DIR = "logs"


def _validate_project(path_str: str) -> Path:
    project_dir = Path(path_str).resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"Error: directory does not exist: {project_dir}")
    if not (project_dir / "CMakeLists.txt").exists():
        raise SystemExit(f"Error: not a Zephyr project: {project_dir} (no CMakeLists.txt)")
    return project_dir


def _print_result(result: ExecutionResult, verbose: bool) -> None:
    op_label = "Building" if result.operation == "build" else "Flashing"
    status = "OK" if result.success else "FAIL"
    print(f"{op_label} {result.project_name}... done ({result.duration_seconds}s) [{status}]")

    if not result.success and not verbose:
        # Show last few lines of stderr on failure
        lines = result.stderr.strip().splitlines()
        excerpt = lines[-10:] if len(lines) > 10 else lines
        if excerpt:
            print()
            for line in excerpt:
                print(f"  {line}")
            print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orch",
        description="Build and flash orchestrator for Zephyr RTOS projects",
    )

    # Common flags via parent parser
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("project", help="path to a Zephyr project directory")
    common.add_argument("--verbose", "-v", action="store_true", help="stream west output in real-time")
    common.add_argument("--log-dir", default=DEFAULT_LOG_DIR, help=f"log output directory (default: {DEFAULT_LOG_DIR})")

    sub = parser.add_subparsers(dest="command", required=True)

    # build
    build_p = sub.add_parser("build", parents=[common], help="build a Zephyr project")
    build_p.add_argument("--board", "-b", default=DEFAULT_BOARD, help=f"board identifier (default: {DEFAULT_BOARD})")
    build_p.add_argument("--pristine", action="store_true", help="clean rebuild (-p always)")

    # flash
    sub.add_parser("flash", parents=[common], help="flash a Zephyr project")

    # run (build + flash)
    run_p = sub.add_parser("run", parents=[common], help="build then flash a Zephyr project")
    run_p.add_argument("--board", "-b", default=DEFAULT_BOARD, help=f"board identifier (default: {DEFAULT_BOARD})")
    run_p.add_argument("--pristine", action="store_true", help="clean rebuild (-p always)")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    project_dir = _validate_project(args.project)
    executor = WestExecutor(verbose=args.verbose)
    executor.check_west()
    logger = SessionLogger(log_dir=Path(args.log_dir))

    results: list[ExecutionResult] = []
    session_start = time.perf_counter()

    try:
        if args.command == "build":
            result = executor.build(project_dir, args.board, args.pristine)
            _print_result(result, args.verbose)
            logger.log_operation(result)
            results.append(result)

        elif args.command == "flash":
            result = executor.flash(project_dir)
            _print_result(result, args.verbose)
            logger.log_operation(result)
            results.append(result)

        elif args.command == "run":
            build_result = executor.build(project_dir, args.board, args.pristine)
            _print_result(build_result, args.verbose)
            logger.log_operation(build_result)
            results.append(build_result)

            if build_result.success:
                flash_result = executor.flash(project_dir)
                _print_result(flash_result, args.verbose)
                logger.log_operation(flash_result)
                results.append(flash_result)
            else:
                print("Skipping flash due to build failure.")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)

    total_duration = time.perf_counter() - session_start
    logger.log_session_summary(results, total_duration)
    print(f"\nLogs saved to: {logger.session_dir}")

    if any(not r.success for r in results):
        sys.exit(1)
