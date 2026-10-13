"""Process entrypoint. Installs crash handler, enforces single instance,
then hands off to the CLI. Kept tiny on purpose — real work lives in core.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bbr.bootstrap.single_instance import SingleInstanceGuard
from bbr.utils.crash import install_crash_handler
from bbr.utils.logging import configure_logging, get_logger

_LOG = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    configure_logging(verbose="--verbose" in argv or "-v" in argv)
    install_crash_handler()

    guard = SingleInstanceGuard(lock_path=Path.home() / ".bbr" / "host.lock")
    if not guard.acquire():
        _LOG.error("another batch-background-remover host is already running")
        return 2

    try:
        from bbr.cli import app  # imported late so logging is configured first

        app(args=argv)
        return 0
    finally:
        guard.release()


if __name__ == "__main__":
    raise SystemExit(main())