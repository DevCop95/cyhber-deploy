#!/usr/bin/env python3
"""
Cyhber Deploy - Dynamic verification layer (Layer 6).

Spins up / targets a LOCAL, EPHEMERAL instance of the project under review and
runs a bounded, non-destructive set of probes against it to *confirm at runtime*
the issues that static review (Layers 1-5) only suspected. The confirmed findings
are emitted as JSON compatible with cyhber_report.py, so they flow straight into
the final ESTADO DE SEGURIDAD verdict.

Design follows OWASP DAST guidance for ephemeral environments:
  - active checks run ONLY against an isolated, throwaway instance you own
  - scope is restricted and time-boxed (don't DoS your own box)
  - passive checks by default; mutating/destructive probes are opt-in

SAFETY — the hard gate
----------------------
This tool REFUSES any target that is not a loopback address (127.0.0.0/8, ::1,
localhost). It literally cannot be pointed at a third-party host. It is for
testing a server you just started on your own machine, nothing else.

Usage
-----
    # 1) You already started the app on localhost:
    python dynamic_probe.py --target http://127.0.0.1:3000 \
        --route /search:q --route /user/1 --json > dynamic_findings.json

    # 2) Let the tool boot it in an isolated subprocess, probe, then tear down:
    python dynamic_probe.py --boot "node server.js" --cwd examples/vulnerable-api \
        --port 3000 --route /search:q --json | python cyhber_report.py

Flags
-----
    --target URL       Base URL of the already-running local instance.
    --boot "CMD"       Command to start the app (mutually exclusive-ish with --target).
    --cwd DIR          Working dir for --boot.
    --port N           Port to wait for / probe when using --boot (default 3000).
    --route PATH[:P]   A route to probe; optional :param marks the query/body field
                       to fuzz. Repeatable. Defaults to a small generic set.
    --allow-active     Enable the mildly-active probes (SQLi error/boolean, auth
                       bypass GET). Still non-destructive. Default: passive only.
    --timeout S        Per-request timeout seconds (default 5).
    --budget S         Global wall-clock budget seconds (default 60).
    --json             Emit findings JSON to stdout (for piping to cyhber_report).
"""

import argparse
import ipaddress
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

LOOPBACK_NAMES = {"localhost", "ip6-localhost", "ip6-loopback"}

# A unique, benign marker. If it bounces back verbatim inside an HTML response,
# the endpoint reflects input without escaping -> XSS confirmed at runtime.
XSS_MARKER = "cyhb<MARK>207xz"

SQL_ERROR_SIGNS = (
    "sql syntax", "mysql", "mysqli", "sqlstate", "psql", "pg::",
    "sqlite", "odbc", "ora-0", "you have an error in your sql",
    "unclosed quotation", "quoted string not properly terminated",
)
STACK_SIGNS = (
    "at object.", "at module.", "\n    at ",          # Node.js stack frames
    "traceback (most recent call last)",               # Python
    "node_modules",                                    # leaked internal path
)


# --------------------------------------------------------------------------- #
# Safety gate
# --------------------------------------------------------------------------- #

def assert_loopback(url):
    """Refuse anything that is not a loopback target. This is the authorization
    boundary: the tool can only ever hit the machine it runs on."""
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        raise SystemExit(f"[cyhber] refusing: no host in target '{url}'")
    if host.lower() in LOOPBACK_NAMES:
        return
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise SystemExit(f"[cyhber] refusing: cannot resolve '{host}': {e}")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_loopback:
            raise SystemExit(
                f"[cyhber] REFUSED: '{host}' resolves to {ip}, which is not "
                f"loopback. This tool only tests a local, ephemeral instance "
                f"you own. Point it at 127.0.0.1."
            )


# --------------------------------------------------------------------------- #
# Boot / teardown of the ephemeral instance
# --------------------------------------------------------------------------- #

def wait_for_port(host, port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.3)
    return False


def boot(cmd, cwd, port):
    print(f"[cyhber] booting ephemeral instance: {cmd} (cwd={cwd})", file=sys.stderr)
    proc = subprocess.Popen(
        cmd, cwd=cwd, shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not wait_for_port("127.0.0.1", port, timeout=20):
        proc.terminate()
        raise SystemExit(f"[cyhber] app did not open port {port} in time")
    print(f"[cyhber] instance is up on 127.0.0.1:{port}", file=sys.stderr)
    return proc


# --------------------------------------------------------------------------- #
# HTTP helper
# --------------------------------------------------------------------------- #

def http(method, url, timeout, data=None):
    req = urllib.request.Request(url, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(200_000).decode("utf-8", "replace")
            return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        body = e.read(200_000).decode("utf-8", "replace")
        return e.code, dict(e.headers), body
    except Exception as e:  # noqa: BLE001 - probe must never crash the run
        return None, {}, f"__ERROR__ {e}"


# --------------------------------------------------------------------------- #
# Probes (each returns an alert dict or None)
# --------------------------------------------------------------------------- #

def probe_security_headers(base, timeout, seq):
    status, headers, _ = http("GET", base + "/", timeout)
    if status is None:
        return None
    lower = {k.lower() for k in headers}
    wanted = {
        "content-security-policy": "CSP",
        "x-content-type-options": "X-Content-Type-Options",
        "strict-transport-security": "HSTS",
        "x-frame-options": "X-Frame-Options",
    }
    missing = [name for h, name in wanted.items() if h not in lower]
    if not missing:
        return None
    return {
        "severity": "MEDIO", "id": f"CD-DYN-{seq:03d}",
        "component": base + "/", "source": "dynamic", "verified": True,
        "description": "Live response is missing security headers: "
                       + ", ".join(missing),
        "evidence": "Response headers present: "
                    + (", ".join(sorted(lower)) or "(none)"),
        "remediation": "Add the headers (e.g. via helmet in Express) before deploy.",
    }


def probe_reflected_xss(base, route, param, timeout, seq):
    q = urllib.parse.urlencode({param: XSS_MARKER})
    url = f"{base}{route}?{q}"
    status, headers, body = http("GET", url, timeout)
    if status is None:
        return None
    ctype = headers.get("Content-Type", headers.get("content-type", "")).lower()
    if "html" in ctype and XSS_MARKER in body:
        return {
            "severity": "ALTO", "id": f"CD-DYN-{seq:03d}",
            "component": f"{route}?{param}", "source": "dynamic", "verified": True,
            "description": "Reflected XSS confirmed at runtime: the marker was "
                           "echoed unescaped into an HTML response.",
            "evidence": f"Sent {param}={XSS_MARKER!r}; marker returned verbatim "
                        f"with Content-Type {ctype!r}",
            "remediation": "HTML-escape output or return JSON; add a CSP.",
        }
    return None


def probe_error_disclosure(base, route, param, timeout, seq):
    # malformed, non-destructive input
    q = urllib.parse.urlencode({param: "'\"<>"})
    status, _, body = http("GET", f"{base}{route}?{q}", timeout)
    if status is None or body.startswith("__ERROR__"):
        return None
    low = body.lower()
    if any(sign in low for sign in STACK_SIGNS):
        snippet = body.strip().replace("\n", " ")[:120]
        return {
            "severity": "BAJO", "id": f"CD-DYN-{seq:03d}",
            "component": route, "source": "dynamic", "verified": True,
            "description": "Verbose error / stack trace leaked to the client at "
                           "runtime.",
            "evidence": f"HTTP {status} body: {snippet}...",
            "remediation": "Log details server-side; return a generic error.",
        }
    return None


def probe_sqli_error(base, route, param, timeout, seq):
    """ACTIVE but non-destructive: single quote -> look for a DB error signature."""
    q = urllib.parse.urlencode({param: "x'"})
    status, _, body = http("GET", f"{base}{route}?{q}", timeout)
    if status is None or body.startswith("__ERROR__"):
        return None
    low = body.lower()
    if any(sign in low for sign in SQL_ERROR_SIGNS):
        snippet = body.strip().replace("\n", " ")[:120]
        return {
            "severity": "CRITICO", "id": f"CD-DYN-{seq:03d}",
            "component": f"{route}?{param}", "source": "dynamic", "verified": True,
            "description": "SQL error provoked by a single quote -> injection "
                           "point confirmed at runtime.",
            "evidence": f"Sent {param}=x' ; DB error in response: {snippet}...",
            "remediation": "Use parameterized queries; never concatenate input.",
        }
    return None


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def parse_route(spec):
    if ":" in spec:
        path, param = spec.split(":", 1)
        return path, param
    return spec, None


def run(base, routes, allow_active, timeout, budget):
    start = time.time()
    alerts = []
    seq = 1

    def add(a):
        nonlocal seq
        if a:
            alerts.append(a)
            seq += 1

    add(probe_security_headers(base, timeout, seq))

    for path, param in routes:
        if time.time() - start > budget:
            print("[cyhber] time budget reached, stopping probes", file=sys.stderr)
            break
        if param:
            add(probe_reflected_xss(base, path, param, timeout, seq))
            add(probe_error_disclosure(base, path, param, timeout, seq))
            if allow_active:
                add(probe_sqli_error(base, path, param, timeout, seq))

    return alerts


def main():
    ap = argparse.ArgumentParser(description="Cyhber Deploy dynamic verification (localhost-only)")
    ap.add_argument("--target")
    ap.add_argument("--boot")
    ap.add_argument("--cwd")
    ap.add_argument("--port", type=int, default=3000)
    ap.add_argument("--route", action="append", default=[])
    ap.add_argument("--allow-active", action="store_true")
    ap.add_argument("--timeout", type=float, default=5)
    ap.add_argument("--budget", type=float, default=60)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    base = args.target or f"http://127.0.0.1:{args.port}"
    base = base.rstrip("/")
    assert_loopback(base)  # hard gate

    routes = [parse_route(r) for r in args.route] or [("/search", "q"), ("/", None)]

    proc = None
    if args.boot:
        proc = boot(args.boot, args.cwd, args.port)
    try:
        alerts = run(base, routes, args.allow_active, args.timeout, args.budget)
    finally:
        if proc:
            print("[cyhber] tearing down ephemeral instance", file=sys.stderr)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    result = {"target": base, "mode": "dynamic", "alerts": alerts}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"[cyhber] dynamic probes confirmed {len(alerts)} issue(s) on {base}",
              file=sys.stderr)
        for a in alerts:
            print(f"  - [{a['severity']}] {a['id']} {a['component']}: "
                  f"{a['description']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
