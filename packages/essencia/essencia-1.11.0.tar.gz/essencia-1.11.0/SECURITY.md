# Security Policy

## Encryption Key Management

This framework uses field-level encryption for sensitive data. **CRITICAL**: Never hardcode encryption keys in your code.

### Required Setup

1. Generate a secure encryption key:
```bash
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

2. Set environment variable:
```bash
export ESSENCIA_ENCRYPTION_KEY="your-generated-key"
```

3. Use `.env` file (never commit):
```
ESSENCIA_ENCRYPTION_KEY="your-generated-key"
```

### Security Best Practices

1. **Key Storage**
   - Use environment variables or secure key management services
   - Never commit `.env` files (add to `.gitignore`)
   - Rotate keys periodically

2. **Database Security**
   - Encrypted data is stored with prefix `ENCRYPTED:`
   - Even with database access, data cannot be decrypted without the key
   - Use MongoDB connection strings with TLS enabled

3. **Dependencies**
   - Keep `cryptography` package updated
   - Run `pip audit` regularly
   - Enable Dependabot alerts on GitHub

### Preventing Package Confusion

To ensure you're using the official package:

```bash
# Verify package metadata
pip show essencia

# Expected output:
# Name: essencia
# Author: Daniel Arantes
# Author-email: arantesdv@me.com
```

### Reporting Security Issues

For security concerns, please email: arantesdv@me.com

Do NOT open public issues for security vulnerabilities.

## Compliance

This framework supports:
- LGPD (Brazilian Data Protection Law)
- Field-level encryption for PII
- Audit trails for data access
- Secure session management