# Migration Guide

## Migrating from Old Essencia Package

If you're using the previous version of the essencia package on PyPI, this guide will help you migrate to the new framework.

### ⚠️ Breaking Changes

The new essencia package is a complete rewrite and is **NOT** compatible with the previous version. It's now a comprehensive application framework rather than its previous functionality.

### Migration Options

#### Option 1: Keep Using Old Version
If you need the old functionality, pin your dependency:
```bash
pip install essencia==<old-version>
```

#### Option 2: Migrate to New Framework
The new essencia provides:
- MongoDB integration (sync and async)
- Redis caching
- Field-level encryption
- Brazilian data validators
- Security features (XSS protection, rate limiting)
- Flet UI framework integration

### New Package Structure

**Old Package:**
```python
# Previous import structure (example)
from essencia import something
```

**New Package:**
```python
# New framework imports
from essencia import MongoModel, CPFValidator, EncryptedCPF
from essencia.security import sanitize_input, RateLimiter
from essencia.cache import IntelligentCache
```

### Common Use Cases

#### Working with Brazilian Data
```python
from essencia.utils import CPFValidator, PhoneValidator

# Validate CPF
try:
    CPFValidator.validate("123.456.789-09")
except ValidationError as e:
    print(f"Invalid CPF: {e}")

# Format phone
formatted = PhoneValidator.format("11999998888")
# Result: (11) 99999-8888
```

#### Secure Data Storage
```python
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedMedicalData

class Patient(MongoModel):
    name: str
    cpf: EncryptedCPF  # Automatically encrypted
    medical_notes: EncryptedMedicalData
```

### Environment Setup

Create a `.env` file:
```bash
# Required for encryption features
ESSENCIA_ENCRYPTION_KEY="your-base64-encoded-32-byte-key"

# Database connections
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"
```

### Getting Help

- **Documentation**: [GitHub README](https://github.com/yourusername/essencia)
- **Issues**: [GitHub Issues](https://github.com/yourusername/essencia/issues)
- **Security**: See SECURITY.md

### Alternative Packages

If the new framework doesn't meet your needs:
- For the old functionality: Consider forking the old version
- For similar frameworks: Django, FastAPI, Flask