# Changelog

All notable changes to Cyhber Deploy are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/);
this project follows [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-10-06

Complete rebuild of the skill plus a verification/visualization toolchain.

### Added
- **Systematic 5-layer DevSecOps review** enforced by the skill (code validation,
  dependencies, secrets & PII, CI/CD, infrastructure), plus an optional Layer 6.
- **Layer 6 — Dynamic verification** (`tools/dynamic_probe.py`): optionally boots a
  **localhost-only, ephemeral** instance of the project, probes it at runtime to
  *confirm* suspected issues, then tears it down. Confirmed findings are tagged
  `verified: true` and flow into the final verdict.
  - Hard safety gate: **refuses any non-loopback target** (127.0.0.1 / localhost only).
  - Non-destructive by default (GET probes, no DELETE/DROP); mildly-active checks
    (SQLi single-quote error) are opt-in via `--allow-active`.
  - Time-boxed (per-request timeout + global budget) to avoid self-DoS.
  - Follows OWASP DAST guidance for ephemeral environments.
- **Terminal report renderer** (`tools/cyhber_report.py`): zero-dependency, colored
  alert cards + `ESTADO DE SEGURIDAD` panel; exit code `1` to gate CI.
- **Standardized severity-tagged alerts** (CRITICO / ALTO / MEDIO / BAJO) with a
  fixed table format (ID, component, description, evidence, remediation).
- **Secret detection patterns** reference (`skills/cyhber-deploy/secret-patterns.md`).
- Vulnerable and secure example APIs under `examples/` for testing.

### Changed
- Skill description rewritten to trigger-only style for better auto-activation.
- README aligned ASCII panels and documented the full toolchain.

### Notes
- Static analysis complemented by optional local dynamic verification; neither
  replaces a professional penetration test or security audit.

[2.0.0]: https://github.com/DevCop95/cyhber-deploy/releases/tag/v2.0.0
