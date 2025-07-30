"""
Key management system for field-level encryption.

Provides secure key generation, rotation, and management for encrypted fields.
Implements industry best practices for cryptographic key management.
"""

import os
import logging
import secrets
import hashlib
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import json

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Secure key management system for encryption operations.
    
    Features:
    - Master key derivation and rotation
    - Context-specific key generation
    - Key lifecycle management
    - Secure key storage recommendations
    - Compliance tracking
    
    Example:
        >>> key_manager = KeyManager(master_key="your-secure-master-key")
        >>> 
        >>> # Derive context-specific key
        >>> encryption_key = key_manager.get_key_for_context("user_data")
        >>> 
        >>> # Check for needed rotations
        >>> contexts_to_rotate = key_manager.check_key_rotation_needed()
        >>> 
        >>> # Perform scheduled rotations
        >>> rotations = key_manager.perform_scheduled_rotations()
    """
    
    def __init__(
        self,
        master_key: Optional[str] = None,
        default_key_lifetime: int = 90,
        max_key_lifetime: int = 365
    ):
        """
        Initialize key manager.
        
        Args:
            master_key: Master key for key derivation
            default_key_lifetime: Default key lifetime in days (default: 90)
            max_key_lifetime: Maximum key lifetime in days (default: 365)
        """
        if not master_key:
            # Try to get from environment
            master_key = os.environ.get('ENCRYPTION_MASTER_KEY')
            
        if not master_key:
            raise ValueError("Master encryption key not configured")
        
        self.master_key = master_key
        self.backend = default_backend()
        self._derived_keys: Dict[str, bytes] = {}
        self._key_metadata: Dict[str, Dict] = {}
        self._key_rotation_schedule: Dict[str, datetime] = {}
        
        # Key rotation settings
        self.default_key_lifetime = timedelta(days=default_key_lifetime)
        self.max_key_lifetime = timedelta(days=max_key_lifetime)
        
        logger.info("Key manager initialized")
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate a new cryptographically secure master key.
        
        Returns:
            Base64-encoded master key (256 bits)
            
        Example:
            >>> master_key = KeyManager.generate_master_key()
            >>> print(f"New master key: {master_key}")
        """
        import base64
        
        # Generate 256-bit (32-byte) random key
        key_bytes = secrets.token_bytes(32)
        master_key = base64.b64encode(key_bytes).decode('utf-8')
        
        logger.info("New master key generated")
        return master_key
    
    def derive_key(self, context: str, version: int = 1) -> bytes:
        """
        Derive a context-specific encryption key from master key.
        
        Args:
            context: Context for key derivation (e.g., "user_data", "medical")
            version: Key version for rotation support
            
        Returns:
            32-byte derived key
        """
        key_id = f"{context}_v{version}"
        
        if key_id in self._derived_keys:
            return self._derived_keys[key_id]
        
        # Create unique salt for this context and version
        salt_material = f"essencia_encryption_{context}_v{version}".encode()
        salt = hashlib.sha256(salt_material).digest()[:16]
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,  # NIST recommended minimum
            backend=self.backend
        )
        
        derived_key = kdf.derive(self.master_key.encode())
        
        # Store derived key and metadata
        self._derived_keys[key_id] = derived_key
        self._key_metadata[key_id] = {
            "context": context,
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "algorithm": "PBKDF2-SHA256",
            "iterations": 100000,
            "key_length": 256
        }
        
        # Schedule key rotation
        self._schedule_key_rotation(key_id)
        
        logger.debug(f"Derived key for context '{context}' version {version}")
        return derived_key
    
    def _schedule_key_rotation(self, key_id: str) -> None:
        """
        Schedule automatic key rotation.
        
        Args:
            key_id: Key identifier to schedule rotation for
        """
        rotation_date = datetime.utcnow() + self.default_key_lifetime
        self._key_rotation_schedule[key_id] = rotation_date
        
        logger.debug(f"Scheduled key rotation for {key_id} at {rotation_date}")
    
    def rotate_key(self, context: str) -> int:
        """
        Rotate key for a specific context.
        
        Args:
            context: Context to rotate key for
            
        Returns:
            New key version number
        """
        # Find current version
        current_version = self.get_current_key_version(context)
        new_version = current_version + 1
        
        # Generate new key
        self.derive_key(context, new_version)
        
        logger.info(f"Rotated key for context '{context}' to version {new_version}")
        return new_version
    
    def get_current_key_version(self, context: str) -> int:
        """
        Get current key version for a context.
        
        Args:
            context: Context to check
            
        Returns:
            Current key version number
        """
        versions = [
            metadata["version"] 
            for key_id, metadata in self._key_metadata.items()
            if metadata["context"] == context
        ]
        return max(versions) if versions else 0
    
    def get_key_for_context(self, context: str, version: Optional[int] = None) -> bytes:
        """
        Get encryption key for a specific context.
        
        Args:
            context: Context to get key for
            version: Specific version (uses current if not specified)
            
        Returns:
            Encryption key bytes
        """
        if version is None:
            version = self.get_current_key_version(context)
            if version == 0:
                version = 1  # Create first version if none exists
        
        return self.derive_key(context, version)
    
    def check_key_rotation_needed(self) -> List[str]:
        """
        Check which keys need rotation.
        
        Returns:
            List of context names that need key rotation
        """
        now = datetime.utcnow()
        contexts_to_rotate = []
        
        for key_id, rotation_date in self._key_rotation_schedule.items():
            if now >= rotation_date:
                context = self._key_metadata[key_id]["context"]
                if context not in contexts_to_rotate:
                    contexts_to_rotate.append(context)
        
        return contexts_to_rotate
    
    def perform_scheduled_rotations(self) -> Dict[str, int]:
        """
        Perform all scheduled key rotations.
        
        Returns:
            Dictionary mapping context to new version number
        """
        contexts_to_rotate = self.check_key_rotation_needed()
        rotations = {}
        
        for context in contexts_to_rotate:
            try:
                new_version = self.rotate_key(context)
                rotations[context] = new_version
                logger.info(f"Completed scheduled rotation for context '{context}'")
            except Exception as e:
                logger.error(f"Failed to rotate key for context '{context}': {e}")
        
        return rotations
    
    def export_key_metadata(self) -> Dict[str, Any]:
        """
        Export key metadata for auditing and compliance.
        
        Returns:
            Dictionary with key metadata (no actual keys)
        """
        return {
            "key_contexts": list(set(
                metadata["context"] for metadata in self._key_metadata.values()
            )),
            "total_keys": len(self._key_metadata),
            "key_metadata": {
                key_id: {**metadata, "in_rotation_schedule": key_id in self._key_rotation_schedule}
                for key_id, metadata in self._key_metadata.items()
            },
            "rotation_schedule": {
                key_id: rotation_date.isoformat()
                for key_id, rotation_date in self._key_rotation_schedule.items()
            },
            "compliance": {
                "key_algorithm": "AES-256-GCM",
                "key_derivation": "PBKDF2-SHA256",
                "default_rotation_period": str(self.default_key_lifetime),
                "max_key_lifetime": str(self.max_key_lifetime)
            },
            "export_timestamp": datetime.utcnow().isoformat()
        }
    
    def validate_key_security(self) -> Dict[str, Any]:
        """
        Validate key security configuration.
        
        Returns:
            Security validation report
        """
        report = {
            "master_key_configured": bool(self.master_key),
            "master_key_length": len(self.master_key) if self.master_key else 0,
            "derived_keys_count": len(self._derived_keys),
            "contexts_with_keys": len(set(
                metadata["context"] for metadata in self._key_metadata.values()
            )),
            "keys_needing_rotation": len(self.check_key_rotation_needed()),
            "security_issues": [],
            "recommendations": []
        }
        
        # Security checks
        if not self.master_key:
            report["security_issues"].append("Master key not configured")
        elif len(self.master_key) < 32:
            report["security_issues"].append("Master key is too short (< 32 characters)")
        
        if not self._derived_keys:
            report["recommendations"].append("No derived keys generated yet")
        
        keys_needing_rotation = self.check_key_rotation_needed()
        if keys_needing_rotation:
            report["security_issues"].append(f"Keys need rotation: {', '.join(keys_needing_rotation)}")
            report["recommendations"].append("Perform scheduled key rotations")
        
        # Overall security status
        report["security_status"] = "SECURE" if not report["security_issues"] else "NEEDS_ATTENTION"
        
        return report
    
    def get_encryption_statistics(self) -> Dict[str, Any]:
        """
        Get encryption system statistics.
        
        Returns:
            Dictionary with encryption statistics
        """
        contexts = list(set(
            metadata["context"] for metadata in self._key_metadata.values()
        ))
        
        return {
            "encryption_algorithm": "AES-256-GCM",
            "key_derivation_function": "PBKDF2-SHA256",
            "key_derivation_iterations": 100000,
            "active_contexts": contexts,
            "total_derived_keys": len(self._derived_keys),
            "scheduled_rotations": len(self._key_rotation_schedule),
            "default_key_lifetime_days": self.default_key_lifetime.days,
            "compliance_features": {
                "data_protection_by_design": True,
                "encryption_at_rest": True,
                "key_management": True,
                "key_rotation": True,
                "audit_trail": True
            }
        }


# Global key manager instance storage
_key_manager: Optional[KeyManager] = None


def get_key_manager(master_key: Optional[str] = None) -> KeyManager:
    """
    Get global key manager instance.
    
    Args:
        master_key: Master key to use (creates new instance if different)
    
    Returns:
        KeyManager instance
    """
    global _key_manager
    
    if _key_manager is None or (master_key and master_key != _key_manager.master_key):
        _key_manager = KeyManager(master_key=master_key)
        
    return _key_manager


def generate_new_master_key() -> str:
    """
    Generate a new master key for the system.
    
    Returns:
        New master key string
        
    Example:
        >>> new_key = generate_new_master_key()
        >>> print(f"Store this key securely: {new_key}")
    """
    return KeyManager.generate_master_key()


def rotate_context_key(context: str, master_key: Optional[str] = None) -> int:
    """
    Rotate key for a specific context.
    
    Args:
        context: Context to rotate key for
        master_key: Master key (uses global instance if not provided)
        
    Returns:
        New key version
    """
    return get_key_manager(master_key).rotate_key(context)


def check_key_rotations_needed(master_key: Optional[str] = None) -> List[str]:
    """
    Check which keys need rotation.
    
    Args:
        master_key: Master key (uses global instance if not provided)
    
    Returns:
        List of contexts needing rotation
    """
    return get_key_manager(master_key).check_key_rotation_needed()


def perform_key_rotations(master_key: Optional[str] = None) -> Dict[str, int]:
    """
    Perform all scheduled key rotations.
    
    Args:
        master_key: Master key (uses global instance if not provided)
    
    Returns:
        Dictionary of rotated contexts and new versions
    """
    return get_key_manager(master_key).perform_scheduled_rotations()


def get_key_security_report(master_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive key security report.
    
    Args:
        master_key: Master key (uses global instance if not provided)
    
    Returns:
        Security validation report
    """
    return get_key_manager(master_key).validate_key_security()


def get_encryption_stats(master_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get encryption system statistics.
    
    Args:
        master_key: Master key (uses global instance if not provided)
    
    Returns:
        Encryption statistics dictionary
    """
    return get_key_manager(master_key).get_encryption_statistics()