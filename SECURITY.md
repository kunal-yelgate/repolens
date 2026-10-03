# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Privacy and Data Handling

RepoLens is designed with a strict privacy-first architecture:
- **Zero Remote Telemetry**: RepoLens does not send telemetry to remote servers.
- **Deterministic Static Mode**: Offline analysis does not contact any external LLM provider.
- **Secret Redaction**: Secret keys, passwords, and tokens detected in files are automatically redacted and never output in plain text.
- **Safe Command Execution**: Commands require explicit confirmation and reject destructive patterns.

## Reporting a Vulnerability

Please report security vulnerabilities privately to `security@repolens.dev`.
