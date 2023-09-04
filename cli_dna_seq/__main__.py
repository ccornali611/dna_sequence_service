"""CLI entry point script."""
# cli_dna_seq/__main__.py
import asyncio

from cli_dna_seq import __app_name__, cli


def main():
    cli.app(prog_name=__app_name__)

if __name__ == "__main__":
    asyncio.run(main())
