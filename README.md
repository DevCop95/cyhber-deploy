<div align="center">

![Cyhber Deploy Banner](assets/banner.svg)

# 🔐 Cyhber Deploy

> **DevSecOps AI Assistant** for Claude Code — Security analysis across code, CI/CD & infrastructure

[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-5F6FFF?style=for-the-badge&logo=anthropic)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)](https://github.com/DevCop95/cyhber-deploy)
[![Stars](https://img.shields.io/github/stars/DevCop95/cyhber-deploy?style=for-the-badge)](https://github.com/DevCop95/cyhber-deploy/stargazers)

[![Security](https://img.shields.io/badge/Security-Focused-red?style=flat-square)](https://owasp.org)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Ready-orange?style=flat-square)](https://github.com/features/actions)
[![IaC](https://img.shields.io/badge/IaC-Supported-blue?style=flat-square)](https://www.terraform.io/)
[![SAST](https://img.shields.io/badge/SAST-Integrated-green?style=flat-square)](https://semgrep.dev/)

[🚀 Quick Start](#-instalación) • [📖 Documentation](skills/cyhber-deploy/SKILL.md) • [💡 Examples](examples/) • [🐛 Report Bug](https://github.com/DevCop95/cyhber-deploy/issues)

</div>

---

## 🚀 Características

Cyhber Deploy acompaña tu ciclo de desarrollo y despliegue con análisis de seguridad en 5 capas:

1. **Código** — Validación de entradas, inyección SQL/XSS, autenticación
2. **Dependencias** — Vulnerabilidades conocidas, licencias, versiones obsoletas
3. **Secretos** — Detección de API keys, tokens, certificados expuestos
4. **CI/CD** — Permisos en pipelines, flujo de despliegue, controles previos
5. **Infraestructura** — Exposición de servicios, permisos IAM, cifrado

### Alertas estructuradas

Cada hallazgo incluye:
- 🔴 Severidad (CRITICO/ALTO/MEDIO/BAJO)
- 📍 Componente afectado
- 🔍 Evidencia concreta
- ✅ Remediación específica

---

## 📸 Preview

<div align="center">

### 🔍 Security Analysis in Action

```
┌─────────────────────────────────────────────┐
│ 🔒 SECURITY ANALYSIS REPORT                 │
├─────────────────────────────────────────────┤
│ ❌ 2 CRITICAL  ⚠️  5 HIGH  ⚡ 3 MEDIUM     │
└─────────────────────────────────────────────┘
```

**Example Output:**

| Severity | ID | Component | Issue |
|----------|-----|-----------|-------|
| 🔴 **CRITICAL** | CD-SEC-101 | `api/auth.js:45` | SQL Injection detected |
| 🔴 **CRITICAL** | CD-SEC-102 | `server.js:12` | Hardcoded API key exposed |
| 🟠 **HIGH** | CD-SEC-201 | `.github/workflows/deploy.yml` | Deploy from any branch |
| 🟡 **MEDIUM** | CD-SEC-301 | `terraform/main.tf` | Security group too permissive |

</div>

---

## 📦 Instalación

### Opción 1: Instalación directa desde GitHub

```bash
claude plugins install github:DevCop95/cyhber-deploy
```

### Opción 2: Instalación manual

1. Clona el repositorio:
```bash
git clone https://github.com/DevCop95/cyhber-deploy.git
cd cyhber-deploy
```

2. Instala el plugin:
```bash
# Desde el directorio del plugin
claude plugins install .

# O especifica la ruta
claude plugins install /ruta/a/cyhber-deploy
```

3. Verifica la instalación:
```bash
claude plugins list
```

### Opción 3: Desarrollo local

```bash
# Clona y enlaza para desarrollo
git clone https://github.com/DevCop95/cyhber-deploy.git
cd cyhber-deploy
claude plugins link .
```

## 🎯 Uso

### Activar el skill

```bash
# En Claude Code
/cyhber-deploy
```

O invoca manualmente:
```
@cyhber-deploy revisa este código para producción
```

### Ejemplos

#### 1. Revisión de código

```javascript
// api/user.js
app.post('/user', (req, res) => {
  const sql = `SELECT * FROM users WHERE id = ${req.body.id}`;
  db.query(sql, (err, result) => {
    res.json(result);
  });
});
```

**Cyhber Deploy detecta:**
- 🔴 **CRITICO**: SQL injection en línea 3
- 🟠 **ALTO**: Sin validación de entrada
- 🟡 **MEDIO**: Exposición de datos sensibles sin filtrar

#### 2. Revisión de CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Deploying to production..."
          kubectl apply -f k8s/
```

**Cyhber Deploy detecta:**
- 🟠 **ALTO**: Deploy se ejecuta en cualquier push (sin restricción de rama)
- 🟡 **MEDIO**: Sin step de tests antes de deploy
- 🟢 **BAJO**: Falta escaneo de secretos

#### 3. Revisión de infraestructura

```hcl
# terraform/main.tf
resource "aws_security_group" "web" {
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Cyhber Deploy detecta:**
- 🔴 **CRITICO**: Security group permite todo el tráfico desde internet
- 🟠 **ALTO**: Sin restricción de puertos
- 🟡 **MEDIO**: Falta egress rules explícitas

## 📚 Ejemplos completos

El directorio `examples/` contiene casos de uso reales:

- **`vulnerable-api/`** — API con vulnerabilidades comunes
- **`secure-api/`** — Mismo API con correcciones aplicadas

```bash
# Prueba con ejemplo vulnerable
cd examples/vulnerable-api
claude

# Dentro de Claude Code
/cyhber-deploy
revisa este proyecto
```

## 🛠 Configuración

### Personalizar severidades

Crea `.cyhber-deploy.json` en la raíz del proyecto:

```json
{
  "severity": {
    "sql_injection": "CRITICO",
    "xss": "ALTO",
    "hardcoded_secrets": "CRITICO",
    "outdated_deps": "MEDIO"
  },
  "ignore": [
    "examples/**",
    "test/**"
  ],
  "frameworks": {
    "detect": true,
    "whitelist": ["express", "fastify", "koa"]
  }
}
```

### Integrar con CI/CD

#### GitHub Actions

```yaml
name: Security Scan
on: [pull_request]
jobs:
  cyhber-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: anthropics/setup-claude@v1
      - run: |
          claude plugins install github:DevCop95/cyhber-deploy
          claude /cyhber-deploy --ci-mode > security-report.md
      - uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.md
```

## 📖 Documentación

- [**SKILL.md**](skills/cyhber-deploy/SKILL.md) — Documentación completa del skill
- [**Ejemplos**](examples/) — Casos de uso prácticos
- [**Wiki**](https://github.com/DevCop95/cyhber-deploy/wiki) — Guías y tutoriales

## 🤝 Contribuir

Contribuciones bienvenidas! Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

### Reportar vulnerabilidades

Para reportar problemas de seguridad, envía email a: yared.henriquezb@gmail.com

**NO** abras issues públicos para vulnerabilidades.

## 📋 Roadmap

- [ ] Soporte para más frameworks (Django, Flask, Spring Boot)
- [ ] Integración con SAST tools (Semgrep, CodeQL)
- [ ] Dashboard web para reportes
- [ ] Modo CI con output JSON/SARIF
- [ ] Detección de configuraciones cloud (AWS, GCP, Azure)
- [ ] Plugin para VS Code

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 🙏 Créditos

Desarrollado por [DevCop95](https://github.com/DevCop95)

Inspirado por herramientas como:
- [Semgrep](https://semgrep.dev/)
- [Snyk](https://snyk.io/)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)

## 📞 Soporte

- 🐛 [Issues](https://github.com/DevCop95/cyhber-deploy/issues)
- 💬 [Discussions](https://github.com/DevCop95/cyhber-deploy/discussions)
- 📧 Email: yared.henriquezb@gmail.com
- 🐦 Twitter: [@DevCop95](https://twitter.com/DevCop95)

---

**⚠️ Disclaimer:** Cyhber Deploy es una herramienta de análisis estático y no reemplaza auditorías de seguridad profesionales ni pruebas de penetración. Úsala como complemento a tus prácticas de seguridad existentes.
