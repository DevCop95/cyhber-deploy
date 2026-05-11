# Secret Detection Patterns

Regex patterns for detecting hardcoded secrets in code, config, and IaC.

## Cloud Provider Keys

```regex
# AWS Access Key
AKIA[0-9A-Z]{16}

# AWS Secret Key  
aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]

# Azure Storage Account Key
AccountKey=.{88}

# GCP Service Account
"type":\s*"service_account"
```

## Version Control Tokens

```regex
# GitHub Personal Access Token
ghp_[a-zA-Z0-9]{36}

# GitHub OAuth Token
gho_[a-zA-Z0-9]{36}

# GitLab Personal Access Token
glpat-[a-zA-Z0-9_\-]{20}

# Bitbucket App Password
bb_[a-zA-Z0-9]{32}
```

## API Keys & Secrets

```regex
# Generic API Key
api[_-]?key[s]?\s*[:=]\s*['"][a-zA-Z0-9]{20,}['"]

# Generic Secret
secret[s]?\s*[:=]\s*['"][a-zA-Z0-9]{20,}['"]

# Generic Token
token[s]?\s*[:=]\s*['"][a-zA-Z0-9]{20,}['"]

# Generic Password (basic patterns)
password\s*[:=]\s*['"][^'"\s]{8,}['"]
```

## Private Keys

```regex
# RSA Private Key
-----BEGIN RSA PRIVATE KEY-----

# EC Private Key
-----BEGIN EC PRIVATE KEY-----

# OpenSSH Private Key
-----BEGIN OPENSSH PRIVATE KEY-----

# PGP Private Key
-----BEGIN PGP PRIVATE KEY BLOCK-----
```

## Database Connection Strings

```regex
# PostgreSQL
postgres(ql)?://[^:]+:[^@]+@[^/]+/\w+

# MySQL
mysql://[^:]+:[^@]+@[^/]+/\w+

# MongoDB
mongodb(\+srv)?://[^:]+:[^@]+@[^/]+

# Redis with password
redis://:[^@]+@[^/]+
```

## Messaging & Communication

```regex
# Slack Token
xox[baprs]-[0-9a-zA-Z]{10,48}

# Slack Webhook
https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8,}/B[a-zA-Z0-9_]{8,}/[a-zA-Z0-9_]{24}

# Discord Token
[MN][a-zA-Z0-9]{23,25}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27}

# Discord Webhook
https://discord(app)?\.com/api/webhooks/\d{17,19}/[a-zA-Z0-9_-]{68}
```

## Payment Providers

```regex
# Stripe Secret Key
sk_live_[0-9a-zA-Z]{24,}

# Stripe Restricted Key
rk_live_[0-9a-zA-Z]{24,}

# PayPal Client ID
A[a-zA-Z0-9_-]{79}

# Square Access Token
sq0atp-[0-9a-zA-Z_-]{22}
```

## JWT Tokens

```regex
# JWT pattern (header.payload.signature)
eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+
```

## SSH & Certificates

```regex
# SSH Public Key
ssh-(rsa|dss|ed25519|ecdsa) [A-Za-z0-9+/=]+

# X.509 Certificate
-----BEGIN CERTIFICATE-----

# PKCS12 / PFX (base64 encoded)
MII[A-Za-z0-9+/]{20,}
```

## CI/CD Secrets

```regex
# Travis CI Token
travis[_-]?token\s*[:=]\s*['"][a-zA-Z0-9]{22}['"]

# CircleCI Token
circle[_-]?token\s*[:=]\s*['"][a-zA-Z0-9]{40}['"]

# Jenkins API Token
jenkins[_-]?token\s*[:=]\s*['"][a-zA-Z0-9]{34}['"]
```

## Usage Notes

- **Case sensitivity:** Most patterns are case-sensitive
- **Context matters:** `password = "test123"` in test file may be acceptable
- **False positives:** Validate matches before flagging as 🔴 CRITICO
- **Git history:** Check if secret was ever committed (even if removed now)
- **Rotation:** If secret exposed, rotation required even after removal
