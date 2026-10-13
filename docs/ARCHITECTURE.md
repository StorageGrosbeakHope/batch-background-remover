# Architecture

batch-background-remover is a **plugin host**. The host owns the boring,
correct parts — walking a folder of images, decoding, scheduling workers,
writing cutouts, reporting progress. Extensions own the interesting part
— deciding which pixels are foreground.

## Layers

```
src/bbr/
  bootstrap/     process entry, single-instance guard, crash handler
  core/          frame model, pipeline, scheduler, contracts
  handlers/      per-format decode/encode (png, jpeg, webp, tiff)
  services/      discovery, registry, weight fetch, telemetry (opt-in)
  models/        pydantic schemas: descriptors, job config, run report
  utils/         logging, paths, hashing, image ops, timing
  extensions/    first-party matting plugins
```

## Data Flow

```
folder -> handlers.decode -> Frame
Frame -> pipeline.run(extensions) -> Frame(alpha)
Frame -> handlers.encode -> output/<name>.png
```

A `Frame` is an immutable-ish container: an RGBA `numpy.ndarray` plus
metadata (source path, EXIF orientation, DPI). Extensions receive a
read-only view and return a new `Frame`.

## Extension Contract

Every extension implements:

```python
class BaseExtension(Protocol):
    name: str
    api_version: str
    capabilities: frozenset[str]
    def process(self, frame: Frame) -> Frame: ...
```

The registry validates `api_version` against the host's supported range
(`SUPPORTED_API = {"1"}`). Extensions outside the range are skipped with
a warning, never loaded.

## Scheduling

`core.scheduler.BatchScheduler` runs a bounded pool. Default worker count
is `min(cpu_count(), 8)`. Each worker owns one extension instance; the
host clones extensions per worker via `extension.__class__()`.

## Weights

Extensions that need a model declare a `weights` block in their
descriptor. `services.weight_fetch` downloads to `models/`, verifies
SHA-256, and caches. Offline mode (`--offline`) refuses to fetch and
fails fast if the weight is absent.