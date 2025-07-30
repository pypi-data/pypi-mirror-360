# Encryption Migration Guide

This guide helps you migrate existing data to use Essencia's encrypted fields feature.

## Overview

Essencia provides field-level encryption for sensitive data like CPF, RG, and medical information. This ensures data is encrypted at rest in the database while remaining transparent to your application code.

## Quick Start

### 1. Check Current Setup

```bash
python check_encryption_setup.py
```

This script will:
- Check if encryption key exists
- Generate a secure key if needed
- Test encryption service
- Analyze your MongoDB collections for sensitive data
- Provide migration recommendations

### 2. Set Encryption Key

If you don't have an encryption key set:

```bash
# Generate a secure key
export ESSENCIA_ENCRYPTION_KEY="$(python -c 'import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())')"

# Add to your .env file for persistence
echo "ESSENCIA_ENCRYPTION_KEY=\"$ESSENCIA_ENCRYPTION_KEY\"" >> .env
```

⚠️ **Important**: Store this key securely! If lost, encrypted data cannot be recovered.

### 3. Update Your Models

Change your models to use encrypted field types:

**Before:**
```python
from essencia.models import MongoModel
from typing import Optional

class Patient(MongoModel):
    name: str
    cpf: Optional[str] = None  # Plain text
    rg: Optional[str] = None   # Plain text
    medical_history: Optional[str] = None  # Plain text
```

**After:**
```python
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedRG, EncryptedMedicalData
from typing import Optional

class Patient(MongoModel):
    name: str
    cpf: Optional[EncryptedCPF] = None  # Encrypted
    rg: Optional[EncryptedRG] = None   # Encrypted
    medical_history: Optional[EncryptedMedicalData] = None  # Encrypted
```

### 4. Migrate Existing Data

First, do a dry run to see what will be changed:

```bash
python migrate_to_encrypted_fields.py --database mydb
```

Create a backup and apply changes:

```bash
# Create backup first
python migrate_to_encrypted_fields.py --database mydb --backup-path ./backup --apply

# Or use mongodump directly
mongodump --db mydb --out ./backup
```

## Migration Script Options

```bash
python migrate_to_encrypted_fields.py --help

Options:
  --database DATABASE     Database name to migrate (required)
  --collections COLL1 COLL2  Specific collections to migrate (default: all)
  --apply                 Apply changes (default is dry-run mode)
  --backup-path PATH      Path to create backup before migration
  --field-mappings FILE   JSON file with custom field mappings
  --batch-size SIZE       Number of documents per batch (default: 100)
```

### Custom Field Mappings

For custom encryption contexts, create a JSON file:

```json
{
  "patients": {
    "custom_field": "medical",
    "another_field": "financial"
  },
  "doctors": {
    "license_number": "professional"
  }
}
```

Then use:
```bash
python migrate_to_encrypted_fields.py --database mydb --field-mappings mappings.json --apply
```

## Using Encrypted Fields

### Basic Usage

```python
# Creating a patient - CPF is automatically encrypted
patient = Patient(
    name="João Silva",
    cpf="123.456.789-00"  # Validated and encrypted
)

# The CPF is stored encrypted
print(patient.cpf)  # Shows encrypted value
print(patient.cpf.is_encrypted())  # True

# Decrypt when needed
print(patient.cpf.decrypt())  # "12345678900"
print(patient.cpf.decrypt_formatted())  # "123.456.789-00"
print(patient.cpf.decrypt_masked())  # "***.***.*89-00"
```

### Custom Encrypted Fields

Create custom encrypted fields for specific needs:

```python
from essencia.fields import EncryptedStr

class EncryptedLicense(EncryptedStr):
    """Custom encrypted field for professional licenses."""
    
    def __new__(cls, value: str = ""):
        # Add custom validation
        if value and not value.startswith("CRM"):
            raise ValueError("Medical license must start with CRM")
        return super().__new__(cls, value, context="license")
    
    def decrypt_masked(self) -> str:
        """Show only last 4 digits."""
        decrypted = self.decrypt()
        if len(decrypted) > 4:
            return "*" * (len(decrypted) - 4) + decrypted[-4:]
        return "*" * len(decrypted)
```

## Security Best Practices

1. **Key Management**
   - Use environment variables or secret management systems
   - Never commit encryption keys to version control
   - Rotate keys periodically (requires data re-encryption)

2. **Backup Strategy**
   - Always backup before migration
   - Test restore procedures
   - Keep encrypted backups secure

3. **Access Control**
   - Limit who can access the encryption key
   - Use field-level access controls in your application
   - Audit access to sensitive data

4. **Performance Considerations**
   - Encryption/decryption has a small performance cost
   - Consider caching decrypted values in memory if needed
   - Use batch operations for better performance

## Rollback Procedure

If you need to rollback:

1. Restore from backup:
   ```bash
   mongorestore --db mydb ./backup/mydb
   ```

2. Revert model changes in your code

3. Redeploy application

## Troubleshooting

### Common Issues

1. **"Encryption key not configured"**
   - Ensure ESSENCIA_ENCRYPTION_KEY is set in environment
   - Check the key is valid base64-encoded 32 bytes

2. **"Invalid CPF" during migration**
   - Some existing CPFs might be invalid
   - Use custom validation or skip invalid records

3. **Performance issues**
   - Increase batch size for faster migration
   - Consider running migration during off-peak hours

### Verification

After migration, verify encryption:

```python
from essencia.models import Patient

# Load a patient
patient = Patient.get_by_field("name", "João Silva")

# Check if fields are encrypted
print(f"CPF encrypted: {patient.cpf.is_encrypted()}")
print(f"Medical history encrypted: {patient.medical_history.is_encrypted()}")

# Verify decryption works
print(f"Decrypted CPF: {patient.cpf.decrypt()}")
```

## Examples

See the `examples/` directory for complete examples:
- `encrypted_fields_example.py` - Basic usage and migration
- `check_encryption_setup.py` - Verify your setup
- `migrate_to_encrypted_fields.py` - Migration script

## Support

For issues or questions:
- Check the [main documentation](README.md)
- Review [security guidelines](SECURITY.md)
- Open an issue on GitHub