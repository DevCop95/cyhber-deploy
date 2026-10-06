#!/usr/bin/env python3
"""
Cyhber Deploy - Terminal report renderer.

Renders security findings as colored "alert cards" plus a final
ESTADO DE SEGURIDAD panel. Pure stdlib, no dependencies, ANSI only.

Usage:
    python cyhber_report.py findings.json     # render a findings file
    cat findings.json | python cyhber_report.py   # read from stdin
    python cyhber_report.py --demo            # render the bundled demo

Findings JSON schema:
    {
      "target": "examples/vulnerable-api",      # optional label
      "alerts": [
        {
          "severity": "CRITICO",                 # CRITICO|ALTO|MEDIO|BAJO
          "id": "CD-SEC-001",
          "component": "server.js:21",
          "description": "SQL injection - email concatenated into query",
          "evidence": "SELECT * FROM users WHERE email = '${email}'",
          "remediation": "Use parameterized query with placeholders"
        }
      ]
    }
"""

import sys
import os
import json
import re

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _char_width(ch):
    o = ord(ch)
    if o == 0xFE0F:            # emoji variation selector (zero width)
        return 0
    if (0x1F300 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF) or \
       (0x1F000 <= o <= 0x1F0FF):
        return 2               # emoji / pictographs render as 2 cells
    return 1


def disp_width(s):
    """Visible width of a string, ignoring ANSI codes, counting emoji as 2."""
    return sum(_char_width(ch) for ch in _ANSI_RE.sub("", s))

# --------------------------------------------------------------------------- #
# ANSI / terminal setup
# --------------------------------------------------------------------------- #

def _supports_color():
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    return sys.stdout.isatty()


def _enable_windows_vt():
    """Enable ANSI escape processing on legacy Windows consoles."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE, 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _force_utf8():
    """Ensure box-drawing chars / emoji render on Windows (cp1252) consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


_enable_windows_vt()
_force_utf8()
COLOR = _supports_color()


def c(code, text):
    if not COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


# Severity -> (ansi color code, emoji, label)
SEVERITY = {
    "CRITICO": ("38;5;196", "🔴", "CRITICO"),
    "ALTO":    ("38;5;208", "🟠", "ALTO"),
    "MEDIO":   ("38;5;220", "🟡", "MEDIO"),
    "BAJO":    ("38;5;46",  "🟢", "BAJO"),
}
SEVERITY_ORDER = ["CRITICO", "ALTO", "MEDIO", "BAJO"]

# Accept English / common aliases so findings from other tools aren't silently
# dropped (which would under-count and wrongly pass a CI gate).
SEVERITY_ALIASES = {
    "CRITICO": "CRITICO", "CRITICAL": "CRITICO", "CRIT": "CRITICO",
    "ALTO": "ALTO", "HIGH": "ALTO",
    "MEDIO": "MEDIO", "MEDIUM": "MEDIO", "MED": "MEDIO",
    "BAJO": "BAJO", "LOW": "BAJO", "INFO": "BAJO", "INFORMATIONAL": "BAJO",
}


def norm_sev(raw):
    """Map a severity string to a canonical level, or None if unrecognized."""
    return SEVERITY_ALIASES.get(str(raw).strip().upper())


WIDTH = 64


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #

def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def banner():
    print()
    print(c("38;5;33;1", "  ╔═══════════════════════════════════════════════════════╗"))
    print(c("38;5;33;1", "  ║") + c("1", "        🔐  C Y H B E R   D E P L O Y   v2.0           ") + c("38;5;33;1", "║"))
    print(c("38;5;33;1", "  ║") + c("38;5;245", "        Systematic DevSecOps Review · 5 layers          ") + c("38;5;33;1", "║"))
    print(c("38;5;33;1", "  ╚═══════════════════════════════════════════════════════╝"))


def render_alert(a):
    sev = norm_sev(a.get("severity", "BAJO")) or "BAJO"
    code, emoji, label = SEVERITY[sev]
    bar = c(code, "▌")

    aid = a.get("id", "CD-SEC-???")
    comp = a.get("component", "?")

    print()
    print(f"  {bar} {emoji} {c(code + ';1', label):<8} {c('1', aid)}  {c('38;5;245', comp)}")
    print(f"  {bar}")

    for line in _wrap(a.get("description", ""), WIDTH):
        print(f"  {bar} {line}")

    if a.get("evidence"):
        print(f"  {bar}")
        print(f"  {bar} {c('38;5;245', 'Evidencia:')}")
        for line in _wrap(str(a["evidence"]), WIDTH - 2):
            print(f"  {bar}   {c('38;5;167', line)}")

    if a.get("remediation"):
        print(f"  {bar}")
        print(f"  {bar} {c('38;5;245', 'Remediación:')}")
        for line in _wrap(str(a["remediation"]), WIDTH - 2):
            print(f"  {bar}   {c('38;5;46', line)}")


def risk_level(counts):
    if counts["CRITICO"] >= 1:
        return "CRITICO"
    if counts["ALTO"] >= 3:
        return "ALTO"
    if counts["ALTO"] >= 1 or counts["MEDIO"] >= 1:
        return "MEDIO"
    return "BAJO"


INNER = 55  # visible width between the box borders


def _row(content):
    """Print one box row, padding to INNER based on visible width."""
    pad = INNER - disp_width(content)
    print(f"  │{content}{' ' * max(pad, 0)}│")


def render_panel(counts, target):
    total = sum(counts.values())
    level = risk_level(counts)
    code, emoji, label = SEVERITY[level]

    block = counts["CRITICO"] >= 1 or counts["ALTO"] >= 3
    if block:
        reco = c("38;5;196;1", "BLOQUEAR despliegue — resolver críticos/altos")
    else:
        reco = c("38;5;46;1", "APROBAR con mitigaciones documentadas")

    line = "─" * INNER
    print()
    print(f"  ┌{line}┐")
    _row(" " + c("1", "🔒 ESTADO DE SEGURIDAD"))
    if target:
        _row(" " + c("38;5;245", "Objetivo: " + str(target)))
    print(f"  ├{line}┤")
    _row(f" Nivel de riesgo:  {emoji} {c(code + ';1', label)}")
    _row(f" Alertas totales:  {c('1', str(total))}")
    for sev in SEVERITY_ORDER:
        scode, semoji, slabel = SEVERITY[sev]
        dot = c(scode, "•")
        _row(f"   {dot} {slabel:<8} {c(scode, str(counts[sev]))}")
    print(f"  ├{line}┤")
    _row(" ⚠️  RECOMENDACIÓN:")
    _row(" " + reco)
    print(f"  └{line}┘")
    print()
    return 1 if block else 0


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #

DEMO = {
    "target": "examples/vulnerable-api/server.js",
    "alerts": [
        {"severity": "CRITICO", "id": "CD-SEC-001", "component": "server.js:9",
         "description": "Hardcoded database credentials in source.",
         "evidence": "password: 'admin123'",
         "remediation": "Move to a secrets manager / env var with restricted access."},
        {"severity": "CRITICO", "id": "CD-SEC-002", "component": "server.js:21",
         "description": "SQL injection - email/password concatenated into query.",
         "evidence": "SELECT * FROM users WHERE email = '${email}'",
         "remediation": "Use parameterized queries with placeholders."},
        {"severity": "CRITICO", "id": "CD-SEC-003", "component": "server.js:41",
         "description": "Command injection via unsanitized host parameter.",
         "evidence": "exec(`ping -c 4 ${host}`)",
         "remediation": "Validate host against an allowlist; avoid shell exec."},
        {"severity": "ALTO", "id": "CD-SEC-004", "component": "server.js:51",
         "description": "Reflected XSS - query echoed into HTML unescaped.",
         "evidence": "res.send(`<h1>Search results for: ${q}</h1>`)",
         "remediation": "HTML-escape output or use a templating engine with autoescaping."},
        {"severity": "ALTO", "id": "CD-SEC-005", "component": "server.js:59",
         "description": "IDOR - any user id readable without authorization check.",
         "evidence": "SELECT * FROM users WHERE id = ${id}",
         "remediation": "Enforce ownership/role check before returning the record."},
        {"severity": "ALTO", "id": "CD-SEC-006", "component": "server.js:81",
         "description": "Arbitrary code execution via eval on request body.",
         "evidence": "const result = eval(expression)",
         "remediation": "Remove eval; use a safe math parser."},
        {"severity": "MEDIO", "id": "CD-SEC-007", "component": "server.js:67",
         "description": "DELETE endpoint has no authentication middleware.",
         "evidence": "app.delete('/user/:id', ...)",
         "remediation": "Require auth + authz before destructive operations."},
        {"severity": "BAJO", "id": "CD-SEC-008", "component": "server.js:91",
         "description": "Verbose error handler leaks stack traces to clients.",
         "evidence": "res.status(500).json({ stack: err.stack })",
         "remediation": "Log server-side; return a generic error to the client."},
    ],
}


def load_findings(argv):
    if "--demo" in argv:
        return DEMO
    paths = [a for a in argv[1:] if not a.startswith("-")]
    if paths:
        with open(paths[0], "r", encoding="utf-8") as f:
            return json.load(f)
    if not sys.stdin.isatty():
        return json.load(sys.stdin)
    return None


def main():
    argv = sys.argv
    try:
        data = load_findings(argv)
    except (OSError, json.JSONDecodeError) as e:
        print(c("38;5;196", f"Error reading findings: {e}"), file=sys.stderr)
        return 2

    if data is None:
        print(__doc__)
        return 0

    if not isinstance(data, dict):
        print(c("38;5;196", "Error: findings root must be a JSON object with an "
                            "'alerts' array."), file=sys.stderr)
        return 2

    alerts = data.get("alerts", [])
    if not isinstance(alerts, list):
        print(c("38;5;196", "Error: 'alerts' must be a list."), file=sys.stderr)
        return 2
    alerts = [a for a in alerts if isinstance(a, dict)]

    counts = {s: 0 for s in SEVERITY_ORDER}
    for a in alerts:
        sev = norm_sev(a.get("severity", "BAJO"))
        if sev is None:
            print(c("38;5;220", f"Warning: unknown severity "
                                f"{a.get('severity')!r} on {a.get('id', '?')} "
                                f"— counting as BAJO."), file=sys.stderr)
            sev = "BAJO"
        counts[sev] += 1

    banner()
    # render highest severity first
    for a in sorted(alerts, key=lambda x: SEVERITY_ORDER.index(
            norm_sev(x.get("severity", "BAJO")) or "BAJO")):
        render_alert(a)

    return render_panel(counts, data.get("target"))


if __name__ == "__main__":
    sys.exit(main())
