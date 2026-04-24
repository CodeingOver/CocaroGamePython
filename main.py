from __future__ import annotations

import argparse

from cli import main as cli_main
from gui import main as gui_main


def main() -> None:
    parser = argparse.ArgumentParser(description="Caro AI")
    parser.add_argument("--cli", action="store_true", help="Chay che do terminal")
    args = parser.parse_args()

    if args.cli:
        cli_main()
        return
    gui_main()


if __name__ == "__main__":
    main()
