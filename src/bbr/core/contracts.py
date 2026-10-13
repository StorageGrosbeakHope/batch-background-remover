"""Shared contracts for the plugin host.

Everything an extension author needs to import lives here. Keep this
module dependency-light: `typing`, `numpy`, and `bbr.core.frame` only.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from bbr.core.frame import Frame

SUPPORTED_API: frozenset[str] = frozenset({"1"})


@runtime_checkable
class BaseExtension(Protocol):
    """The contract every matting extension implements.

    Attributes:
        name: Canonical, lowercase, hyphenated. Must be unique.
        api_version: Host API the extension targets. Must be in `SUPPORTED_API`.
        capabilities: Free-form tags, e.g. {"gpu", "readonly", "deterministic"}.
        priority: Lower runs earlier in a chained pipeline. Default 100.
    """

    name: str
    api_version: str
    capabilities: frozenset[str]
    priority: int

    def process(self, frame: Frame) -> Frame:
        """Return a new Frame with the alpha channel populated."""
        ...


class ExtensionError(RuntimeError):
    """Raised by an extension when it cannot process a frame."""


class WeightMissingError(ExtensionError):
    """Raised when a required model weight is absent and offline mode is on."""