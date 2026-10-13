"""Bounded batch scheduler.

Uses `concurrent.futures.ProcessPoolExecutor` on Windows so a wedged
ONNX session can't take down the host. Each worker builds its own
extension instances via the registry's factory functions — extension
objects are not pickled across the boundary.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from bbr.core.frame import Frame
from bbr.core.pipeline import PipelineResult
from bbr.utils.logging import get_logger

_LOG = get_logger(__name__)


@dataclass(slots=True)
class JobItem:
    source: Path
    output: Path


def default_workers() -> int:
    return max(1, min(os.cpu_count() or 4, 8))


def run_batch(
    items: Iterable[JobItem],
    worker_fn: Callable[[str], PipelineResult],
    *,
    workers: int | None = None,
    on_done: Callable[[JobItem, PipelineResult], None] | None = None,
) -> list[tuple[JobItem, PipelineResult]]:
    workers = workers or default_workers()
    items = list(items)
    results: list[tuple[JobItem, PipelineResult]] = []

    # Single-process path avoids the pickle cost for tiny batches.
    if workers == 1 or len(items) <= 2:
        for item in items:
            res = worker_fn(str(item.source))
            results.append((item, res))
            if on_done:
                on_done(item, res)
        return results

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(worker_fn, str(item.source)): item for item in items}
        for fut in as_completed(futures):
            item = futures[fut]
            res = fut.result()
            results.append((item, res))
            if on_done:
                on_done(item, res)
    return results
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>