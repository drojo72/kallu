"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from kellu import doctor
from kellu.__app__ import APP_DISPLAY_NAME, APP_NAME, __version__

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NOT_IMPLEMENTED = 3  # 2 is reserved by argparse for usage errors

# Commands that exist in the design but are not built yet, with their milestone.
_PLANNED: dict[str, str] = {
    "keys": "M3",
    "tools": "M5",
    "lsp": "M6",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description=f"{APP_DISPLAY_NAME}: a secure, modular AI assistant for the Kate editor.",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.add_parser("doctor", help="check the environment (keyring, sandbox tooling, paths)")
    for name, milestone in _PLANNED.items():
        sub.add_parser(name, help=f"(planned for {milestone})")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    command: str | None = args.command

    if command is None:
        parser.print_help()
        print("\nThe interactive assistant arrives in milestone M6.", file=sys.stderr)
        return EXIT_OK
    if command == "doctor":
        return doctor.run()
    milestone = _PLANNED.get(command)
    if milestone is None:  # pragma: no cover - argparse rejects unknown commands first
        parser.error(f"unknown command: {command}")
    print(f"{APP_NAME} {command}: not implemented yet (planned for {milestone}).", file=sys.stderr)
    return EXIT_NOT_IMPLEMENTED
