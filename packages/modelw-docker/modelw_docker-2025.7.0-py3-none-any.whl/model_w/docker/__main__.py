#!/usr/bin/env python3
import argparse
from argparse import ArgumentParser, Namespace
from os import getcwd
from pathlib import Path
from signal import SIGTERM, signal
from typing import Optional, Sequence

from .build import build
from .config import get_config
from .exceptions import UserException
from .install import install
from .output import Printer
from .platform import in_docker
from .run import run
from .serve import serve


def parse_args(argv: Optional[Sequence[str]] = None) -> Namespace:
    """
    Parsing CLI arguments
    """

    parser = ArgumentParser()

    parser.add_argument(
        "--dry-run",
        default=not in_docker(),
        action="store_true",
        help="Don't actually run anything",
    )
    parser.add_argument(
        "-r",
        "--root",
        default=Path(getcwd()),
        type=Path,
        help="Root directory of the project",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install", help="Install the project's env")
    subparsers.add_parser("build", help="Build the project")

    serve_parser = subparsers.add_parser("serve", help="Serve the project")
    serve_parser.add_argument(
        "variant",
        nargs="?",
        default="default",
        help="Variant of the component to serve (default, celery, beat)",
    )

    run_parser = subparsers.add_parser(
        "run",
        help=(
            "Runs a command in the project's env (and with the project's "
            "binaries in PATH)"
        ),
    )
    run_parser.add_argument("bin", help="The binary/command to run")
    run_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Command to run and its args"
    )

    return parser.parse_args(argv)


def sigterm_handler(_, __):
    raise SystemExit(1)


def main(argv: Optional[Sequence[str]] = None):
    """
    Parsing arguments, config and then dispatching to the appropriate handler
    if all is fine
    """

    args = parse_args(argv)

    printer = Printer.instance()
    printer.dry_run = args.dry_run

    config = get_config(args.root)

    if args.command == "install":
        install(config, args.root, args.dry_run)
    elif args.command == "build":
        build(config, args.root)
    elif args.command == "serve":
        serve(config, args.root, args.variant)
    elif args.command == "run":
        run(config, args.root, args.bin, args.args)


def __main__():
    signal(SIGTERM, sigterm_handler)

    try:
        main()
    except KeyboardInterrupt:
        Printer.instance().error("Interrupted by user")
        exit(1)
    except UserException as e:
        Printer.instance().error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    __main__()
