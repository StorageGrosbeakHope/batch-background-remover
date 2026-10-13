"""Chained matting pipeline.

Runs a sequence of extensions in priority order. Each extension receives
the Frame produced by the previous one, so a pipeline like
`[chroma_key, edge_refine]` does a cheap keyed cutout then a refinement
pass. Extensions that raise `ExtensionError` are skipped for the current
frame and logged; the pipeline continues with the last good Frame.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from bbr.core.contracts import BaseExtension, ExtensionError
from bbr.core.frame import Frame
from bbr.utils.logging import get_logger

_LOG = get_logger(__name__)


@dataclass(slots=True)
class StageResult:
    extension: str
    duration_ms: float
    ok: bool


@dataclass(slots=True)
class PipelineResult:
    frame: Frame
    stages: list[StageResult]


class Pipeline:
    def __init__(self, extensions: list[BaseExtension]) -> None:
        self._extensions = sorted(extensions, key=lambda e: getattr(e, "priority", 100))

    def run(self, frame: Frame) -> PipelineResult:
        current = frame
        stages: list[StageResult] = []
        for ext in self._extensions:
            t0 = perf_counter()
            try:
                current = ext.process(current)
                ok = True
            except ExtensionError as exc:
                _LOG.warning("extension %s failed on %s: %s", ext.name, frame.source, exc)
                ok = False
            stages.append(
                StageResult(
                    extension=ext.name,
                    duration_ms=(perf_counter() - t0) * 1000.0,
                    ok=ok,
                )
            )
        return PipelineResult(frame=current, stages=stages)