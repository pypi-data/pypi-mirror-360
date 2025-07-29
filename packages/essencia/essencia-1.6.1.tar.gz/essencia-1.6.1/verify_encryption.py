#!/usr/bin/env python
"""
Simple script to verify encryption setup without MongoDB dependency.
"""

import os
import sys
import base64
import secrets
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from essencia.security.encryption_service import EncryptionService
from essencia.fields import EncryptedCPF, EncryptedRG, EncryptedMedicalData
from essencia.core.exceptions import EncryptionError


def generate_key():
    """Generate a secure encryption key."""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')


def main():
    print("🔐 Essencia Encryption Verification\n")
    
    # Check current key
    current_key = os.environ.get('ESSENCIA_ENCRYPTION_KEY')
    
    if not current_key:
        print("❌ No encryption key found in ESSENCIA_ENCRYPTION_KEY")
        print("\nGenerating a new key for testing...")
        test_key = generate_key()
        print(f"\nTest key: {test_key}")
        print("\nTo set this key in your environment:")
        print(f'export ESSENCIA_ENCRYPTION_KEY="{test_key}"')
        
        # Set for this session
        os.environ['ESSENCIA_ENCRYPTION_KEY'] = test_key
        print("\n✅ Key set for this session only")
    else:
        print("✅ Encryption key found")
        try:
            decoded = base64.b64decode(current_key)
            print(f"   Key length: {len(decoded)} bytes (should be 32)")
        except:
            print("   ⚠️  Warning: Key doesn't appear to be valid base64")
    
    # Test encryption service
    print("\n📝 Testing encryption service...")
    try:
        service = EncryptionService()
        
        # Test basic encryption
        test_data = "Hello, World!"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        
        print(f"   Original:  {test_data}")
        print(f"   Encrypted: {encrypted[:30]}...")
        print(f"   Decrypted: {decrypted}")
        print(f"   Match:     {test_data == decrypted} ✅")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test encrypted fields
    print("\n🔒 Testing encrypted fields...")
    
    # Test CPF
    try:
        cpf = EncryptedCPF("123.456.789-09")
        print(f"\n   CPF Field:")
        print(f"   - Raw value (encrypted): {str(cpf)[:30]}...")
        print(f"   - Is encrypted: {cpf.is_encrypted()}")
        print(f"   - Decrypted: {cpf.decrypt()}")
        print(f"   - Formatted: {cpf.decrypt_formatted()}")
        print(f"   - Masked: {cpf.decrypt_masked()}")
    except Exception as e:
        print(f"   ❌ CPF Error: {e}")
    
    # Test RG
    try:
        rg = EncryptedRG("12345678")
        print(f"\n   RG Field:")
        print(f"   - Raw value (encrypted): {str(rg)[:30]}...")
        print(f"   - Is encrypted: {rg.is_encrypted()}")
        print(f"   - Decrypted: {rg.decrypt()}")
        print(f"   - Masked: {rg.decrypt_masked()}")
    except Exception as e:
        print(f"   ❌ RG Error: {e}")
    
    # Test Medical Data
    try:
        medical = EncryptedMedicalData("Patient has diabetes type 2")
        print(f"\n   Medical Data Field:")
        print(f"   - Raw value (encrypted): {str(medical)[:30]}...")
        print(f"   - Is encrypted: {medical.is_encrypted()}")
        print(f"   - Decrypted: {medical.decrypt()}")
    except Exception as e:
        print(f"   ❌ Medical Data Error: {e}")
    
    # Show environment setup
    print("\n📋 Environment Setup:")
    print(f"   - Encryption key set: {'✅' if os.environ.get('ESSENCIA_ENCRYPTION_KEY') else '❌'}")
    print(f"   - .env file exists: {'✅' if Path('.env').exists() else '❌'}")
    
    # Show next steps
    print("\n📝 Next Steps:")
    print("   1. Save the encryption key securely")
    print("   2. Add to .env file for development")
    print("   3. Update your models to use encrypted fields")
    print("   4. Run migration for existing data")
    
    print("\n✅ Verification complete!")


if __name__ == "__main__":
    main()