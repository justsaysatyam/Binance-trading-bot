#!/usr/bin/env python
"""
Convenience CLI wrapper — runs the Django management command directly.

Usage:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
"""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trading_bot.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    # Prepend the 'trade' subcommand so the user doesn't have to type it
    execute_from_command_line(["manage.py", "trade"] + sys.argv[1:])


if __name__ == "__main__":
    main()
