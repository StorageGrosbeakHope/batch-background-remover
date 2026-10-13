"""The unit of work: an RGBA raster plus provenance metadata.

`Frame` is a frozen dataclass wrapping a `numpy.ndarray` of shape
`(H, W, 4)` and dtype `uint8`. It is treated as immutable by convention:
extensions must return a *new* `Frame`, never mutate in place. The host
enforces this by handing out a read-only view (`arr.setflags(write=False)`)
to extensions that opt into `capabilities={"readonly"}`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class Frame:
    pixels: np.ndarray  # (H, W, 4) uint8, RGBA
    source: Path
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.pixels.ndim != 3 or self.pixels.shape[2] != 4:
            raise ValueError(f"Frame expects (H, W, 4), got {self.pixels.shape}")
        if self.pixels.dtype != np.uint8:
            raise ValueError(f"Frame expects uint8, got {self.pixels.dtype}")

    @property
    def height(self) -> int:
        return int(self.pixels.shape[0])

    @property
    def width(self) -> int:
        return int(self.pixels.shape[1])

    def with_alpha(self, alpha: np.ndarray) -> "Frame":
        if alpha.shape != (self.height, self.width):
            raise ValueError(
                f"alpha shape {alpha.shape} != frame {(self.height, self.width)}"
            )
        out = self.pixels.copy()
        out[..., 3] = alpha
        return Frame(pixels=out, source=self.source, meta=dict(self.meta))

    def readonly_view(self) -> np.ndarray:
        view = self.pixels.view()
        view.setflags(write=False)
        return view