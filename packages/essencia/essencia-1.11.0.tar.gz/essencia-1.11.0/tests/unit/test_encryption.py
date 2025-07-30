"""
Unit tests for field encryption.
"""
import pytest

from essencia.security.encryption import FieldEncryptor


class TestFieldEncryption:
    """Test field encryption functionality."""
    
    @pytest.mark.security
    def test_generate_key(self):
        """Test encryption key generation."""
        key = FieldEncryptor.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Should be valid base64
        import base64
        decoded = base64.b64decode(key)
        assert len(decoded) == 32  # 256 bits
    
    @pytest.mark.security
    def test_encrypt_decrypt(self, field_encryptor):
        """Test encryption and decryption."""
        original = "sensitive data"
        
        # Encrypt
        encrypted = field_encryptor.encrypt(original)
        assert encrypted != original
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = field_encryptor.decrypt(encrypted)
        assert decrypted == original
    
    @pytest.mark.security
    def test_encrypt_empty_string(self, field_encryptor):
        """Test encrypting empty string."""
        encrypted = field_encryptor.encrypt("")
        decrypted = field_encryptor.decrypt(encrypted)
        assert decrypted == ""
    
    @pytest.mark.security
    def test_encrypt_unicode(self, field_encryptor):
        """Test encrypting unicode characters."""
        original = "José da Silva 🔒"
        encrypted = field_encryptor.encrypt(original)
        decrypted = field_encryptor.decrypt(encrypted)
        assert decrypted == original
    
    @pytest.mark.security
    def test_encrypt_long_text(self, field_encryptor):
        """Test encrypting long text."""
        original = "A" * 10000
        encrypted = field_encryptor.encrypt(original)
        decrypted = field_encryptor.decrypt(encrypted)
        assert decrypted == original
    
    @pytest.mark.security
    def test_different_encryptions(self, field_encryptor):
        """Test that same data produces different encryptions."""
        original = "test data"
        encrypted1 = field_encryptor.encrypt(original)
        encrypted2 = field_encryptor.encrypt(original)
        
        # Should be different due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same value
        assert field_encryptor.decrypt(encrypted1) == original
        assert field_encryptor.decrypt(encrypted2) == original
    
    @pytest.mark.security
    def test_invalid_key(self):
        """Test encryption with invalid key."""
        with pytest.raises(Exception):
            FieldEncryptor("invalid_key")
    
    @pytest.mark.security
    def test_decrypt_invalid_data(self, field_encryptor):
        """Test decrypting invalid data."""
        with pytest.raises(Exception):
            field_encryptor.decrypt("invalid_encrypted_data")
    
    @pytest.mark.security
    def test_decrypt_tampered_data(self, field_encryptor):
        """Test decrypting tampered data."""
        original = "test data"
        encrypted = field_encryptor.encrypt(original)
        
        # Tamper with the encrypted data
        tampered = encrypted[:-10] + "tampered"
        
        with pytest.raises(Exception):
            field_encryptor.decrypt(tampered)