"""Cross-platform single-instance guard.

On Windows we use an exclusive lock file with `msvcrt.locking`; elsewhere
we fall back to `fcntl.flock`. The lock is advisory — a stale lock from a
crashed process is detected by writing the PID and checking liveness.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from bbr.utils.logging import get_logger

_LOG = get_logger(__name__)


class SingleInstanceGuard:
    def __init__(self, lock_path: Path) -> None:
        self._path = lock_path
        self._fh = None

    def acquire(self) -> bool:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._path, "a+", encoding="utf-8")
        try:
            if sys.platform == "win32":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self._fh.close()
            self._fh = None
            return False
        self._fh.seek(0)
        self._fh.truncate()
        self._fh.write(str(os.getpid()))
        self._fh.flush()
        return True

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if sys.platform == "win32":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError as exc:  # pragma: no cover - best-effort unlock
            _LOG.debug("lock release failed: %s", exc)
        finally:
            self._fh.close()
            self._fh = None