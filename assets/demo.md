# Cyhber Deploy Demo

## Security Analysis Output Example

```
🔐 Cyhber Deploy v1.0.0 - Security Analysis Starting...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Scanning: examples/vulnerable-api/
🔍 Files analyzed: 2
⏱️  Time: 1.2s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 SECURITY ALERTS

┌──────────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL - CD-SEC-101                                         │
├──────────────────────────────────────────────────────────────────┤
│ Component:   server.js:23                                        │
│ Issue:       SQL Injection vulnerability                         │
│ Evidence:    db.query(`SELECT * FROM users WHERE id=${id}`)     │
│ Impact:      Attacker can extract/modify database contents       │
│                                                                  │
│ ✅ Fix:                                                          │
│   Use prepared statements:                                       │
│   db.query('SELECT * FROM users WHERE id = ?', [id])           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL - CD-SEC-102                                         │
├──────────────────────────────────────────────────────────────────┤
│ Component:   server.js:12                                        │
│ Issue:       Hardcoded database credentials                      │
│ Evidence:    password: 'admin123'                                │
│ Impact:      Credentials exposed in version control              │
│                                                                  │
│ ✅ Fix:                                                          │
│   Move to environment variables:                                 │
│   password: process.env.DB_PASSWORD                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 🟠 HIGH - CD-SEC-201                                             │
├──────────────────────────────────────────────────────────────────┤
│ Component:   server.js:34                                        │
│ Issue:       Command injection vulnerability                     │
│ Evidence:    exec(`ping -c 4 ${host}`)                          │
│ Impact:      Arbitrary command execution possible                │
│                                                                  │
│ ✅ Fix:                                                          │
│   Validate input against whitelist or use safe library          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 🟠 HIGH - CD-SEC-202                                             │
├──────────────────────────────────────────────────────────────────┤
│ Component:   server.js:45                                        │
│ Issue:       XSS vulnerability in search endpoint                │
│ Evidence:    res.send(`<h1>Results: ${q}</h1>`)                 │
│ Impact:      Client-side script injection possible               │
│                                                                  │
│ ✅ Fix:                                                          │
│   Use validator.escape(q) or return JSON instead of HTML        │
└──────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY

┌─────────────────────────────────────────────┐
│ 🔒 SECURITY STATUS                          │
├─────────────────────────────────────────────┤
│ Risk Level:       🔴 CRITICAL               │
│ Total Alerts:     12                        │
│   • Critical:     2                         │
│   • High:         5                         │
│   • Medium:       3                         │
│   • Low:          2                         │
├─────────────────────────────────────────────┤
│ ⚠️  RECOMMENDATION                          │
│                                             │
│ 🚫 BLOCK deployment until:                 │
│   • Fix all CRITICAL issues                 │
│   • Address HIGH priority alerts            │
│   • Review MEDIUM findings                  │
└─────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Resources:
  • OWASP Top 10: https://owasp.org/www-project-top-ten/
  • CWE Database: https://cwe.mitre.org/
  • Fix examples: examples/secure-api/

🔧 Next steps:
  1. Address CRITICAL alerts immediately
  2. Review HIGH priority findings
  3. Run /cyhber-deploy again after fixes
  4. Integrate with CI/CD for continuous monitoring

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Analysis complete! Type /help for more options.
```

## CI/CD Integration Example

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [pull_request]

jobs:
  cyhber-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: anthropics/setup-claude@v1
      - name: Run Security Analysis
        run: |
          claude plugins install github:DevCop95/cyhber-deploy
          claude /cyhber-deploy --ci-mode
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: cyhber-deploy-report.md
```

## Usage in Claude Code

```bash
# Activate the skill
/cyhber-deploy

# Analyze current directory
analyze this project for security issues

# Review specific file
review api/auth.js for vulnerabilities

# Check before deployment
ready to deploy - run security check

# Scan infrastructure
check terraform configuration security
```
