# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Essencia, please report it responsibly:

1. **DO NOT** open a public issue
2. Email: security@yourdomain.com (replace with your email)
3. Include: Description, steps to reproduce, potential impact

## Security Features

### Encryption
- Field-level encryption using AES-256-GCM
- PBKDF2 key derivation (100,000 iterations)
- Separate encryption contexts for different data types

### Authentication
- Session-based authentication with CSRF protection
- Rate limiting on authentication endpoints
- Secure session regeneration

### Data Protection
- Automatic sanitization of user inputs
- XSS prevention for HTML/Markdown content
- SQL injection prevention through parameterized queries

## Security Best Practices

### Environment Variables
Always set these in production:
```bash
# Generate a secure key:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
export ESSENCIA_ENCRYPTION_KEY="your-base64-encoded-32-byte-key"
export MONGODB_URL="mongodb://user:pass@host:port/db"
export REDIS_URL="redis://user:pass@host:port/0"
```

### Password Storage
**Important**: The demo auth service uses SHA256. For production:
```python
# Install: pip install bcrypt
import bcrypt

# Hash password
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify password
bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Deployment
1. Always use HTTPS in production
2. Set secure session cookies
3. Enable CORS only for trusted domains
4. Keep dependencies updated
5. Monitor for security alerts

## Compliance

This package includes features to support:
- LGPD (Brazilian General Data Protection Law)
- Field-level encryption for PII
- Audit logging capabilities
- Data retention controls