#!/usr/bin/env python3
"""Entry point for the stand project."""

import argparse
import sys

VERSION = "0.1.0"

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="stand — CLI entry point")
    parser.add_argument("-v", "--version", action="store_true", help="show version and exit")
    parser.add_argument("--greet", metavar="NAME", help="greet NAME (default: World)", default="World")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    print(f"Hello, {args.greet}! This is the stand project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
