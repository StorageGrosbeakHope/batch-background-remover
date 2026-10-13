# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :x:                |

## Reporting a Vulnerability

batch-background-remover loads third-party extension modules from the
`bbr.plugins` entry-point group. A malicious or malformed extension can
execute arbitrary Python at import time. If you find a vulnerability in
the host loader, the registry, or any bundled extension, open a private
security advisory on GitHub rather than a public issue.

Include:

- Affected version (`bbr --version`).
- The extension name and entry-point string.
- A minimal reproducer (a `.bbr-ext` descriptor or a wheel that triggers it).
- Windows build number and Python version.

We aim to acknowledge within 72 hours and ship a patch release within 14
days for confirmed issues.

## Threat Model

The host assumes extensions are **semi-trusted**: they run in-process and
have full filesystem access. We do not sandbox. We do validate descriptors,
enforce a declared API version, and refuse to load extensions whose
`api_version` is outside the supported range.

Model weights are fetched over HTTPS from the URL declared in the
extension manifest. We verify SHA-256 before loading. If a mirror is
compromised, the hash check fails and the extension is disabled.

## Out of Scope

- Denial of service from a user feeding 100k images into a batch run.
- Issues that require an already-compromised local account.
- Anything in `tests/fixtures/`.