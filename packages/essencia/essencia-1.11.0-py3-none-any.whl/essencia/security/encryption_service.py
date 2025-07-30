"""
Field-level encryption service for sensitive data.

Provides AES-256-GCM encryption for sensitive fields.
Implements data protection best practices for healthcare and personal data.
"""

import os
import base64
import hashlib
import logging
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from essencia.core.exceptions import EncryptionError

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Secure field-level encryption service using AES-256-GCM.
    
    Features:
    - AES-256-GCM encryption with authenticated encryption
    - PBKDF2 key derivation for security
    - Base64 encoding for database storage
    - Automatic IV generation for each encryption
    - Configurable contexts for different data types
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption service.
        
        Args:
            master_key: Master encryption key (uses environment variable if not provided)
        """
        self.master_key = master_key or os.environ.get('ESSENCIA_ENCRYPTION_KEY')
        if not self.master_key:
            raise EncryptionError("Encryption key not configured")
        
        self.backend = default_backend()
        self._key_cache: Dict[str, bytes] = {}  # Cache for derived keys
        
    def _derive_key(self, context: str = "default") -> bytes:
        """
        Derive encryption key from master key with context.
        
        Args:
            context: Context for key derivation (e.g., "cpf", "medical")
            
        Returns:
            32-byte derived key
        """
        if context in self._key_cache:
            return self._key_cache[context]
        
        # Use context as salt component for different field types
        salt = hashlib.sha256(f"essencia_encryption_{context}".encode()).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,  # NIST recommended minimum
            backend=self.backend
        )
        
        key = kdf.derive(self.master_key.encode())
        self._key_cache[context] = key
        return key
    
    def encrypt(self, plaintext: str, context: str = "default") -> str:
        """
        Encrypt sensitive data with AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            context: Context for key derivation
            
        Returns:
            Base64-encoded encrypted data with IV and tag
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            if not plaintext:
                return ""
            
            # Generate random IV for each encryption
            iv = os.urandom(12)  # 96-bit IV for GCM
            
            # Derive key for this context
            key = self._derive_key(context)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Encrypt the data
            ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
            
            # Get authentication tag
            tag = encryptor.tag
            
            # Combine IV + tag + ciphertext and encode
            encrypted_data = iv + tag + ciphertext
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            
            logger.debug(f"Encrypted data for context '{context}'")
            return encoded_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str, context: str = "default") -> str:
        """
        Decrypt sensitive data with AES-256-GCM.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            context: Context for key derivation
            
        Returns:
            Decrypted plaintext
            
        Raises:
            EncryptionError: If decryption fails or authentication fails
        """
        try:
            if not encrypted_data:
                return ""
            
            # Decode from base64
            try:
                data = base64.b64decode(encrypted_data.encode('utf-8'))
            except Exception:
                raise EncryptionError("Invalid encrypted data format")
            
            # Extract components (12-byte IV + 16-byte tag + ciphertext)
            if len(data) < 28:  # Minimum: 12 + 16 = 28 bytes
                raise EncryptionError("Encrypted data too small")
            
            iv = data[:12]
            tag = data[12:28]
            ciphertext = data[28:]
            
            # Derive key for this context
            key = self._derive_key(context)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt and verify authentication
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            logger.debug(f"Decrypted data for context '{context}'")
            return plaintext.decode('utf-8')
            
        except EncryptionError:
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def is_encrypted(self, data: str) -> bool:
        """
        Check if data appears to be encrypted.
        
        Args:
            data: Data to check
            
        Returns:
            True if data appears encrypted, False otherwise
        """
        if not data:
            return False
        
        try:
            # Try to decode as base64
            decoded = base64.b64decode(data.encode('utf-8'))
            # Encrypted data should be at least 28 bytes (IV + tag + some data)
            return len(decoded) >= 28
        except:
            return False
    
    def encrypt_cpf(self, cpf: str) -> str:
        """
        Encrypt CPF with specific context.
        
        Args:
            cpf: CPF to encrypt
            
        Returns:
            Encrypted CPF
        """
        return self.encrypt(cpf, context="cpf")
    
    def decrypt_cpf(self, encrypted_cpf: str) -> str:
        """
        Decrypt CPF with specific context.
        
        Args:
            encrypted_cpf: Encrypted CPF
            
        Returns:
            Decrypted CPF
        """
        return self.decrypt(encrypted_cpf, context="cpf")
    
    def encrypt_medical_data(self, medical_data: str) -> str:
        """
        Encrypt medical data with specific context.
        
        Args:
            medical_data: Medical data to encrypt
            
        Returns:
            Encrypted medical data
        """
        return self.encrypt(medical_data, context="medical")
    
    def decrypt_medical_data(self, encrypted_medical_data: str) -> str:
        """
        Decrypt medical data with specific context.
        
        Args:
            encrypted_medical_data: Encrypted medical data
            
        Returns:
            Decrypted medical data
        """
        return self.decrypt(encrypted_medical_data, context="medical")
    
    def encrypt_rg(self, rg: str) -> str:
        """
        Encrypt RG with specific context.
        
        Args:
            rg: RG to encrypt
            
        Returns:
            Encrypted RG
        """
        return self.encrypt(rg, context="rg")
    
    def decrypt_rg(self, encrypted_rg: str) -> str:
        """
        Decrypt RG with specific context.
        
        Args:
            encrypted_rg: Encrypted RG
            
        Returns:
            Decrypted RG
        """
        return self.decrypt(encrypted_rg, context="rg")
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """
        Get encryption service statistics.
        
        Returns:
            Dictionary with encryption stats
        """
        return {
            "encryption_algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-SHA256",
            "iterations": 100000,
            "iv_size": "96 bits",
            "tag_size": "128 bits",
            "contexts_cached": len(self._key_cache),
        }


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get global encryption service instance.
    
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_field(data: str, context: str = "default") -> str:
    """
    Convenience function to encrypt a field.
    
    Args:
        data: Data to encrypt
        context: Encryption context
        
    Returns:
        Encrypted data
    """
    return get_encryption_service().encrypt(data, context)


def decrypt_field(encrypted_data: str, context: str = "default") -> str:
    """
    Convenience function to decrypt a field.
    
    Args:
        encrypted_data: Encrypted data
        context: Encryption context
        
    Returns:
        Decrypted data
    """
    return get_encryption_service().decrypt(encrypted_data, context)


def is_field_encrypted(data: str) -> bool:
    """
    Convenience function to check if field is encrypted.
    
    Args:
        data: Data to check
        
    Returns:
        True if encrypted, False otherwise
    """
    return get_encryption_service().is_encrypted(data)


# Specific encryption functions for common sensitive data
def encrypt_cpf(cpf: str) -> str:
    """Encrypt CPF."""
    return get_encryption_service().encrypt_cpf(cpf)


def decrypt_cpf(encrypted_cpf: str) -> str:
    """Decrypt CPF."""
    return get_encryption_service().decrypt_cpf(encrypted_cpf)


def encrypt_rg(rg: str) -> str:
    """Encrypt RG."""
    return get_encryption_service().encrypt_rg(rg)


def decrypt_rg(encrypted_rg: str) -> str:
    """Decrypt RG."""
    return get_encryption_service().decrypt_rg(encrypted_rg)


def encrypt_medical_data(medical_data: str) -> str:
    """Encrypt medical data."""
    return get_encryption_service().encrypt_medical_data(medical_data)


def decrypt_medical_data(encrypted_medical_data: str) -> str:
    """Decrypt medical data."""
    return get_encryption_service().decrypt_medical_data(encrypted_medical_data)