# Cyhber Deploy — Demo

The terminal renderer (`tools/cyhber_report.py`) turns findings into colored alert
cards plus a final `ESTADO DE SEGURIDAD` panel. Pure stdlib, no dependencies.

## Run it

```bash
# Bundled demo (8 sample findings from examples/vulnerable-api)
python tools/cyhber_report.py --demo

# Your own findings file (schema in tools/findings.example.json)
python tools/cyhber_report.py findings.json

# Pipe from the dynamic layer
python tools/dynamic_probe.py --boot "node server.js" --cwd examples/vulnerable-api \
  --port 3000 --route "/search:q" --allow-active --json | python tools/cyhber_report.py
```

## Sample output

Alert cards (one per finding, highest severity first):

```
  ▌ 🔴 CRITICO  CD-SEC-001  server.js:9
  ▌
  ▌ Hardcoded database credentials in source.
  ▌
  ▌ Evidencia:
  ▌   password: 'admin123'
  ▌
  ▌ Remediación:
  ▌   Move to a secrets manager / env var with restricted access.

  ▌ 🟠 ALTO     CD-SEC-004  server.js:51
  ▌
  ▌ Reflected XSS - query echoed into HTML unescaped.
  ▌
  ▌ Evidencia:
  ▌   res.send(`<h1>Search results for: ${q}</h1>`)
  ▌
  ▌ Remediación:
  ▌   HTML-escape output or use a templating engine with autoescaping.
```

Final verdict panel:

```
  ┌────────────────────────────────────────────────┐
  │ ESTADO DE SEGURIDAD                            │
  │ Objetivo: examples/vulnerable-api/server.js    │
  ├────────────────────────────────────────────────┤
  │ Nivel de riesgo:  CRITICO                      │
  │ Alertas totales:  8                            │
  │   - CRITICO  3                                 │
  │   - ALTO     3                                 │
  │   - MEDIO    1                                 │
  │   - BAJO     1                                 │
  ├────────────────────────────────────────────────┤
  │ RECOMENDACIÓN:                                 │
  │ BLOQUEAR despliegue — resolver críticos/altos  │
  └────────────────────────────────────────────────┘
```

> In a real terminal, severity dots (🔴 🟠 🟡 🟢) are colored. The panel above is
> shown without them so the borders line up in Markdown.

## CI gate

`cyhber_report.py` exits `1` when the run should block (any 🔴 CRITICO, or ≥3 🟠 ALTO)
and `0` otherwise — so you can fail a pipeline directly on its exit code:

```yaml
# .github/workflows/security-report.yml
name: Security Report
on: [pull_request]

jobs:
  cyhber-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      # Produce findings.json with your SAST/own tooling, then render + gate:
      - run: python tools/cyhber_report.py findings.json
```

## Usage in Claude Code

The skill auto-triggers on keywords (deploy, CI/CD, Terraform, auth, secrets,
injection). See [SKILL.md](../skills/cyhber-deploy/SKILL.md).

```
review api/auth.js for vulnerabilities
ready to deploy - run a security check
```
