<div align="center">

![Cyhber Deploy Banner](assets/banner1.svg)

# 🔐 Cyhber Deploy

> **Systematic DevSecOps Analysis** for Claude Code — 5-layer security review with standardized severity-tagged alerts

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-5F6FFF?style=for-the-badge&logo=anthropic)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge)](https://github.com/DevCop95/cyhber-deploy)
[![TDD](https://img.shields.io/badge/Built_with-TDD-green?style=for-the-badge)](tests/)

[![Security](https://img.shields.io/badge/Security-Focused-red?style=flat-square)](https://owasp.org)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Ready-orange?style=flat-square)](https://github.com/features/actions)
[![IaC](https://img.shields.io/badge/IaC-Supported-blue?style=flat-square)](https://www.terraform.io/)
[![Tested](https://img.shields.io/badge/Pressure_Tested-Passed-green?style=flat-square)](tests/FINAL-REPORT.md)

[🚀 Quick Start](#-installation) • [📖 Documentation](skills/cyhber-deploy/SKILL.md) • [🧪 Test Results](tests/FINAL-REPORT.md) • [🐛 Report Bug](https://github.com/DevCop95/cyhber-deploy/issues)

</div>

---

## ✨ What's New in v2.0

**Complete rebuild with TDD methodology:**
- ✅ Systematic 5-layer review enforced (no ad-hoc analysis)
- ✅ Standardized severity-tagged alerts (CRITICO/ALTO/MEDIO/BAJO)
- ✅ Proactive scope expansion beyond user request
- ✅ Token-efficient (~450 words, 60% reduction)
- ✅ Pressure-tested with time/authority/exhaustion scenarios
- ✅ Full test documentation included

**Results:** 6-8 categorized alerts vs 1-2 ad-hoc findings in baseline testing.

See [FINAL-REPORT.md](tests/FINAL-REPORT.md) for complete TDD documentation.

---

## 🚀 Features

### Systematic 5-Layer Analysis

Every security review follows this structured methodology:

1. **Code Validation** — Input validation, injection (SQL/XSS/Command), auth/authz, error handling
2. **Dependencies** — CVEs, outdated packages, unmaintained libraries, transitive dependencies
3. **Secrets & PII** — Hardcoded API keys, tokens, certificates, exposed personal data
4. **CI/CD Pipeline** — Branch restrictions, secret exposure, security gates, rollback plans
5. **Infrastructure** — Network exposure, IAM/RBAC permissions, encryption, security groups

**No layer skipped** — even "frontend-only" code triggers full review.

### Standardized Alert Format

Every finding includes:

| Campo | Valor |
|-------|-------|
| **Severidad** | 🔴 CRITICO \| 🟠 ALTO \| 🟡 MEDIO \| 🟢 BAJO |
| **ID** | CD-SEC-XXX (sequential) |
| **Componente** | file.js:line or resource name |
| **Descripción** | What + why it's a risk |
| **Evidencia** | Code snippet or config excerpt |
| **Remediación** | Specific fix steps |

### Risk Assessment Output

```
┌─────────────────────────────────────────────┐
│ 🔒 ESTADO DE SEGURIDAD                      │
├─────────────────────────────────────────────┤
│ Nivel de riesgo:  🔴 CRITICO                │
│ Alertas totales:  8                         │
│   • Críticas:     2                         │
│   • Altas:        3                         │
│   • Medias:       2                         │
│   • Bajas:        1                         │
├─────────────────────────────────────────────┤
│ ⚠️  RECOMENDACIÓN:                          │
│ BLOQUEAR despliegue hasta resolver          │
│ hallazgos críticos y altos.                 │
└─────────────────────────────────────────────┘
```

---

## 📦 Installation

### Claude Code CLI

```bash
# Install from local directory
git clone https://github.com/DevCop95/cyhber-deploy.git
cd cyhber-deploy
cp -r skills/cyhber-deploy ~/.claude/skills/
```

### Verify Installation

```bash
# Check skill is loaded
claude # Start Claude Code session
# Skill auto-triggers on: deploy, CI/CD, Terraform, auth, secrets, injection
```

---

## 🎯 Usage

### Auto-Trigger Keywords

Skill activates when you mention:
- **Deploy:** staging, production, release
- **CI/CD:** GitHub Actions, GitLab CI, Jenkins, CircleCI
- **IaC:** Terraform, Kubernetes, Docker, Helm
- **Cloud:** AWS, GCP, Azure
- **Security:** auth, secrets, injection, SQL, XSS
- **Review:** "security review", "check this code"

### Manual Invocation

```
@cyhber-deploy review this for production
```

---

## 📸 Examples

### Example 1: SQL Injection Detection

**Input:**
```javascript
app.post('/login', (req, res) => {
  db.query(`SELECT * FROM users WHERE email='${req.body.email}'`);
});
```

**Output:**

| Campo | Valor |
|-------|-------|
| **Severidad** | 🔴 CRITICO |
| **ID** | CD-SEC-001 |
| **Componente** | `api/auth.js:2` |
| **Descripción** | SQL injection - user-controlled email concatenated into query |
| **Evidencia** | `` db.query(`SELECT * FROM users WHERE email='${req.body.email}'`) `` |
| **Remediación** | Use parameterized query: `db.query('SELECT * FROM users WHERE email = ?', [req.body.email])` |

---

### Example 2: CI/CD Secret Exposure

**Input:**
```yaml
# .github/workflows/deploy.yml
- run: |
    echo "API_KEY=${{ secrets.API_KEY }}" >> .env
    cat .env
```

**Output:**

| Campo | Valor |
|-------|-------|
| **Severidad** | 🔴 CRITICO |
| **ID** | CD-SEC-001 |
| **Componente** | `.github/workflows/deploy.yml:3` |
| **Descripción** | API key exposed in workflow logs via `cat .env` |
| **Evidencia** | `cat .env` prints secrets to logs accessible to all repo users |
| **Remediación** | Remove `cat .env`. Pass secrets via env vars: `env: API_KEY: ${{ secrets.API_KEY }}` |

---

### Example 3: Infrastructure Overexposure

**Input:**
```hcl
resource "aws_security_group" "db" {
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 5432
    to_port     = 5432
  }
}
```

**Output:**

| Campo | Valor |
|-------|-------|
| **Severidad** | 🔴 CRITICO |
| **ID** | CD-SEC-001 |
| **Componente** | `terraform/main.tf:3` |
| **Descripción** | Database exposed to entire internet via overly permissive security group |
| **Evidencia** | `cidr_blocks = ["0.0.0.0/0"]` allows connections from any IP |
| **Remediación** | Restrict to application subnet: `cidr_blocks = ["10.0.1.0/24"]` or use VPC peering |

---

## 🧪 Testing & Quality

### TDD Methodology

Skill built following complete RED-GREEN-REFACTOR cycle:

- **RED Phase:** Baseline testing without skill (3 pressure scenarios)
- **GREEN Phase:** Skill enforcement verification (systematic 5-layer review)
- **REFACTOR Phase:** Edge case testing (frontend-only code)

### Test Results

| Metric | Baseline (No Skill) | With Skill | Improvement |
|--------|---------------------|------------|-------------|
| **Issues found** | 1-2 | 6-8 | +300-400% |
| **Structure** | Ad-hoc | 5-layer systematic | ✅ |
| **Output format** | Freeform | Severity tables | ✅ |
| **Scope** | Limited | Proactive expansion | ✅ |

**Full documentation:** [tests/FINAL-REPORT.md](tests/FINAL-REPORT.md)

---

## 📚 Documentation

- **[SKILL.md](skills/cyhber-deploy/SKILL.md)** — Complete skill specification
- **[secret-patterns.md](skills/cyhber-deploy/secret-patterns.md)** — 40+ secret detection patterns
- **[FINAL-REPORT.md](tests/FINAL-REPORT.md)** — TDD testing documentation
- **[Examples](examples/)** — Vulnerable and secure code samples

---

## 🛠 Configuration

### Secret Patterns

Built-in detection for:
- AWS keys (AKIA...), Azure, GCP service accounts
- GitHub tokens (ghp_, gho_, glpat-)
- Private keys (RSA, EC, OpenSSH, PGP)
- Database connection strings
- JWT tokens
- Slack/Discord webhooks
- Payment provider keys (Stripe, PayPal, Square)

See [secret-patterns.md](skills/cyhber-deploy/secret-patterns.md) for complete list.

---

## 🤝 Contributing

Contributions welcome! For major changes:

1. Fork repo
2. Create feature branch (`git checkout -b feature/improvement`)
3. Follow TDD methodology (see [tests/](tests/) for examples)
4. Commit with conventional commits
5. Push and open PR

### Reporting Security Issues

**DO NOT** open public issues for vulnerabilities.

Email: yared.henriquezb@gmail.com

---

## 📋 Roadmap

- [ ] SARIF output format for CI/CD integration
- [ ] Custom rule configuration (.cyhber-deploy.json)
- [ ] Multi-language support (Django, Flask, Spring Boot)
- [ ] GitHub Action for automated PR reviews
- [ ] VS Code extension
- [ ] Dashboard for security metrics over time

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Credits

**Author:** [DevCop95](https://github.com/DevCop95)

**Built with guidance from:**
- [Claude Code Superpowers](https://github.com/codeium/claude-plugins-official/tree/main/superpowers) - TDD methodology for skills
- [Anthropic Claude](https://www.anthropic.com/) - AI platform

**Inspired by:**
- [Semgrep](https://semgrep.dev/) - SAST scanning
- [Snyk](https://snyk.io/) - Dependency analysis
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret detection
- [OWASP](https://owasp.org/) - Security standards

---

## 📞 Support

- 🐛 [Issues](https://github.com/DevCop95/cyhber-deploy/issues)
- 💬 [Discussions](https://github.com/DevCop95/cyhber-deploy/discussions)
- 📧 Email: yared.henriquezb@gmail.com
- 🐦 X/Twitter: [@Devcop101](https://x.com/Devcop101)

---

<div align="center">

**⚠️ Disclaimer**

Cyhber Deploy provides static analysis and does not replace professional security audits or penetration testing. Use as complement to existing security practices.

**Production-Ready • TDD-Tested • Open Source**

⭐ Star this repo if it helps your security workflow!

</div>
