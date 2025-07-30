"""
Encrypted field types for sensitive data in Pydantic models.

Provides transparent encryption/decryption for sensitive fields like CPF, RG, 
medical data, etc. Fields are automatically encrypted when stored and decrypted 
when accessed.
"""

import logging
from typing import Any, Optional
from pydantic import Field
from pydantic.fields import FieldInfo

from essencia.security.encryption_service import (
    get_encryption_service, 
    encrypt_cpf, decrypt_cpf,
    encrypt_rg, decrypt_rg,
    encrypt_medical_data, decrypt_medical_data,
    is_field_encrypted
)
from essencia.core.exceptions import EncryptionError

logger = logging.getLogger(__name__)


class EncryptedStr(str):
    """
    Base encrypted string field.
    
    Automatically encrypts data when setting and decrypts when accessing.
    Stores encrypted data in database but provides decrypted access.
    """
    
    def __new__(cls, value: Any = "", context: str = "default"):
        """
        Create new encrypted string.
        
        Args:
            value: Value to encrypt (if not already encrypted)
            context: Encryption context for key derivation
        """
        if not value:
            return super().__new__(cls, "")
        
        str_value = str(value)
        
        # Check if already encrypted
        if is_field_encrypted(str_value):
            # Store encrypted value as-is
            return super().__new__(cls, str_value)
        else:
            # Encrypt and store
            try:
                encryption_service = get_encryption_service()
                encrypted_value = encryption_service.encrypt(str_value, context)
                return super().__new__(cls, encrypted_value)
            except Exception as e:
                logger.error(f"Failed to encrypt field: {e}")
                raise EncryptionError(f"Failed to encrypt field: {str(e)}")
    
    def decrypt(self, context: str = "default") -> str:
        """
        Decrypt the field value.
        
        Args:
            context: Decryption context
            
        Returns:
            Decrypted string value
        """
        if not self:
            return ""
        
        try:
            encryption_service = get_encryption_service()
            return encryption_service.decrypt(str(self), context)
        except Exception as e:
            logger.error(f"Failed to decrypt field: {e}")
            raise EncryptionError(f"Failed to decrypt field: {str(e)}")
    
    def is_encrypted(self) -> bool:
        """Check if this field is encrypted."""
        return is_field_encrypted(str(self))


class EncryptedCPF(EncryptedStr):
    """
    Encrypted CPF field with automatic validation and formatting.
    
    Features:
    - Automatic CPF validation
    - CPF formatting (xxx.xxx.xxx-xx)
    - Transparent encryption/decryption
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted CPF field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Clean and validate CPF
        cleaned_cpf = cls._clean_cpf(str_value)
        if cleaned_cpf and cls._validate_cpf(cleaned_cpf):
            try:
                encrypted_value = encrypt_cpf(cleaned_cpf)
                return super(EncryptedStr, cls).__new__(cls, encrypted_value)
            except Exception as e:
                logger.error(f"Failed to encrypt CPF: {e}")
                raise EncryptionError(f"Failed to encrypt CPF: {str(e)}")
        else:
            raise ValueError(f"Invalid CPF: {str_value}")
    
    @staticmethod
    def _clean_cpf(cpf: str) -> str:
        """Remove formatting from CPF."""
        return ''.join(filter(str.isdigit, cpf))
    
    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        """Validate CPF using algorithm."""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Calculate first check digit
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11) if sum1 % 11 >= 2 else 0
        
        # Calculate second check digit
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11) if sum2 % 11 >= 2 else 0
        
        return cpf[9:] == f"{digit1}{digit2}"
    
    def decrypt(self) -> str:
        """Decrypt CPF."""
        if not self:
            return ""
        return decrypt_cpf(str(self))
    
    def decrypt_formatted(self) -> str:
        """Decrypt and format CPF (xxx.xxx.xxx-xx)."""
        decrypted = self.decrypt()
        if len(decrypted) == 11:
            return f"{decrypted[:3]}.{decrypted[3:6]}.{decrypted[6:9]}-{decrypted[9:]}"
        return decrypted
    
    def decrypt_masked(self) -> str:
        """Decrypt and mask CPF (xxx.xxx.xxx-xx -> ***.***.*47-11)."""
        decrypted = self.decrypt()
        if len(decrypted) == 11:
            return f"***.***.*{decrypted[7:9]}-{decrypted[9:]}"
        return "*" * len(decrypted) if decrypted else ""


class EncryptedRG(EncryptedStr):
    """
    Encrypted RG field with automatic validation.
    
    Features:
    - Basic RG validation
    - Transparent encryption/decryption
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted RG field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Clean and validate RG
        cleaned_rg = cls._clean_rg(str_value)
        if cleaned_rg and cls._validate_rg(cleaned_rg):
            try:
                encrypted_value = encrypt_rg(cleaned_rg)
                return super(EncryptedStr, cls).__new__(cls, encrypted_value)
            except Exception as e:
                logger.error(f"Failed to encrypt RG: {e}")
                raise EncryptionError(f"Failed to encrypt RG: {str(e)}")
        else:
            raise ValueError(f"Invalid RG: {str_value}")
    
    @staticmethod
    def _clean_rg(rg: str) -> str:
        """Remove formatting from RG."""
        return ''.join(c for c in rg if c.isalnum())
    
    @staticmethod
    def _validate_rg(rg: str) -> bool:
        """Basic RG validation."""
        # RG should have 7-9 alphanumeric characters
        return 7 <= len(rg) <= 9 and rg.isalnum()
    
    def decrypt(self) -> str:
        """Decrypt RG."""
        if not self:
            return ""
        return decrypt_rg(str(self))
    
    def decrypt_masked(self) -> str:
        """Decrypt and mask RG (partially hidden)."""
        decrypted = self.decrypt()
        if len(decrypted) >= 4:
            return "*" * (len(decrypted) - 2) + decrypted[-2:]
        return "*" * len(decrypted) if decrypted else ""


class EncryptedMedicalData(EncryptedStr):
    """
    Encrypted medical data field for sensitive medical information.
    
    Features:
    - Transparent encryption/decryption
    - Healthcare data compliance
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted medical data field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt medical data
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt medical data: {e}")
            raise EncryptionError(f"Failed to encrypt medical data: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt medical data."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))


# Pydantic field factories for model integration
def CPFField(default: Any = None, **kwargs) -> FieldInfo:
    """
    Create an encrypted CPF field for Pydantic models.
    
    Args:
        default: Default value
        **kwargs: Additional field parameters
        
    Returns:
        Pydantic FieldInfo for encrypted CPF
    """
    return Field(
        default=default,
        description="Encrypted CPF field",
        json_schema_extra={
            "type": "string",
            "format": "encrypted-cpf",
            "example": "12345678901"
        },
        **kwargs
    )


def RGField(default: Any = None, **kwargs) -> FieldInfo:
    """
    Create an encrypted RG field for Pydantic models.
    
    Args:
        default: Default value
        **kwargs: Additional field parameters
        
    Returns:
        Pydantic FieldInfo for encrypted RG
    """
    return Field(
        default=default,
        description="Encrypted RG field",
        json_schema_extra={
            "type": "string", 
            "format": "encrypted-rg",
            "example": "123456789"
        },
        **kwargs
    )


def MedicalDataField(default: Any = None, **kwargs) -> FieldInfo:
    """
    Create an encrypted medical data field for Pydantic models.
    
    Args:
        default: Default value
        **kwargs: Additional field parameters
        
    Returns:
        Pydantic FieldInfo for encrypted medical data
    """
    return Field(
        default=default,
        description="Encrypted medical data field",
        json_schema_extra={
            "type": "string",
            "format": "encrypted-medical",
            "example": "Sensitive medical information"
        },
        **kwargs
    )


# Validators for Pydantic models
def validate_encrypted_cpf(value: Any) -> Optional[EncryptedCPF]:
    """Pydantic validator for encrypted CPF fields."""
    if value is None:
        return None
    return EncryptedCPF(value)


def validate_encrypted_rg(value: Any) -> Optional[EncryptedRG]:
    """Pydantic validator for encrypted RG fields."""
    if value is None:
        return None
    return EncryptedRG(value)


def validate_encrypted_medical_data(value: Any) -> Optional[EncryptedMedicalData]:
    """Pydantic validator for encrypted medical data fields."""
    if value is None:
        return None
    return EncryptedMedicalData(value)


# Export encrypted field types
__all__ = [
    'EncryptedStr',
    'EncryptedCPF', 
    'EncryptedRG',
    'EncryptedMedicalData',
    'CPFField',
    'RGField', 
    'MedicalDataField',
    'validate_encrypted_cpf',
    'validate_encrypted_rg',
    'validate_encrypted_medical_data'
]