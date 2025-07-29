# Essencia

A comprehensive Python framework for building secure medical and business applications with Brazilian market support.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Security First**: Field-level encryption, XSS protection, rate limiting, CSRF tokens
- **Medical Ready**: Encrypted medical fields, LGPD compliance features
- **Brazilian Support**: CPF/CNPJ validators, phone formatting, Portuguese error messages  
- **Dual Database**: Async (Motor) and sync (PyMongo) MongoDB support
- **Smart Caching**: Redis-based intelligent caching with fallback
- **Modern UI**: Built on Flet (Flutter for Python)
- **Type Safe**: Full type hints and Pydantic validation

## Installation

```bash
# Basic installation
pip install essencia

# With security extras (bcrypt, argon2)
pip install essencia[security]
```

## Quick Start

### Environment Setup

Create a `.env` file:

```bash
# Required for encryption features
ESSENCIA_ENCRYPTION_KEY="your-base64-encoded-32-byte-key"

# Database connections (optional, defaults to localhost)
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"
```

Generate an encryption key:
```bash
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### Basic Usage

```python
from essencia import MongoModel, CPFValidator, EncryptedCPF
from essencia.fields import DefaultDateTime

# Define a model with encrypted fields
class Patient(MongoModel):
    COLLECTION_NAME = "patients"
    
    name: str
    cpf: EncryptedCPF  # Automatically encrypted/decrypted
    created_at: DefaultDateTime
    
# Validate Brazilian data
try:
    CPFValidator.validate("123.456.789-09")
except ValidationError as e:
    print(f"Invalid CPF: {e}")

# Use the model
patient = Patient(name="João Silva", cpf="123.456.789-09")
patient.save_self()  # CPF is encrypted in database
```

### Security Features

```python
from essencia.security import sanitize_input, RateLimiter
from essencia.cache import IntelligentCache

# Input sanitization
clean_html = sanitize_input("<script>alert('xss')</script>Hello")
# Result: "Hello"

# Rate limiting
rate_limiter = RateLimiter()
if rate_limiter.is_allowed("user-123", "login"):
    # Process login
    pass

# Intelligent caching
cache = IntelligentCache()
cache.set("user:123", user_data, ttl=3600)
```

### Service Pattern

```python
from essencia.services import EnhancedBaseService

class PatientService(EnhancedBaseService):
    model_class = Patient
    collection_name = "patients"
    
    async def find_by_cpf(self, cpf: str):
        # CPF is automatically encrypted for search
        return await self.find_one({"cpf": cpf})
```

## Components

### Models
- `MongoModel` - Base model for MongoDB with sync operations
- `BaseModel` - Async base model using Motor
- Built-in field types: `MongoId`, `ObjectReferenceId`, `StrEnum`

### Security
- **Sanitization**: HTML/Markdown sanitizers for XSS prevention
- **Session Management**: Secure sessions with CSRF protection
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Multiple strategies (sliding window, token bucket)
- **Encryption**: Field-level encryption for sensitive data

### Validators
- `CPFValidator` - Brazilian CPF validation and formatting
- `CNPJValidator` - Brazilian CNPJ validation
- `PhoneValidator` - Brazilian phone numbers
- `EmailValidator` - Email validation
- `MoneyValidator` - Brazilian currency formatting
- `DateValidator` - Date validation with business rules

### Fields
- `EncryptedCPF`, `EncryptedRG` - Encrypted Brazilian documents
- `EncryptedMedicalData` - For medical records
- `DefaultDate`, `DefaultDateTime` - Auto-populated timestamps

## Documentation

- [Security Policy](SECURITY.md) - Security features and reporting
- [Migration Guide](MIGRATION.md) - Migrating from previous versions
- [Publishing Guide](PUBLISHING.md) - PyPI publication checklist

## Requirements

- Python 3.12+
- MongoDB 4.0+
- Redis 6.0+ (optional, for caching)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- Create an issue for bug reports or feature requests
- For security issues, see [SECURITY.md](SECURITY.md)