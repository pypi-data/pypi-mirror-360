#!/usr/bin/env python
"""
Minimal test of encryption functionality.
"""

import os
import base64
import secrets


def generate_key():
    """Generate a secure encryption key."""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')


def main():
    print("🔐 Essencia Encryption Test\n")
    
    # Check current key
    current_key = os.environ.get('ESSENCIA_ENCRYPTION_KEY')
    
    if not current_key:
        print("❌ No encryption key found in ESSENCIA_ENCRYPTION_KEY")
        print("\nTo generate and set a new key:")
        test_key = generate_key()
        print(f'\nexport ESSENCIA_ENCRYPTION_KEY="{test_key}"')
        print("\n⚠️  Save this key securely! It cannot be recovered if lost.")
        
        # Also show .env format
        print("\nFor .env file:")
        print(f'ESSENCIA_ENCRYPTION_KEY="{test_key}"')
    else:
        print("✅ Encryption key is set")
        try:
            decoded = base64.b64decode(current_key)
            print(f"   Key length: {len(decoded)} bytes (expected: 32)")
            if len(decoded) == 32:
                print("   ✅ Key length is correct")
            else:
                print("   ⚠️  Warning: Key should be 32 bytes for AES-256")
        except Exception as e:
            print(f"   ❌ Error decoding key: {e}")
    
    # Check for .env file
    from pathlib import Path
    env_file = Path(".env")
    
    print(f"\n📄 .env file exists: {'✅' if env_file.exists() else '❌'}")
    
    if env_file.exists() and current_key:
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ESSENCIA_ENCRYPTION_KEY' in content:
                print("   ✅ .env contains ESSENCIA_ENCRYPTION_KEY")
            else:
                print("   ⚠️  .env exists but doesn't contain ESSENCIA_ENCRYPTION_KEY")
    
    print("\n📝 Summary:")
    print(f"   • Encryption key configured: {'✅' if current_key else '❌'}")
    print(f"   • Environment file exists: {'✅' if env_file.exists() else '❌'}")
    
    if not current_key:
        print("\n⚠️  Action required: Set the ESSENCIA_ENCRYPTION_KEY environment variable")
    else:
        print("\n✅ Encryption is configured and ready to use!")
        print("\n📖 See ENCRYPTION_MIGRATION.md for migration instructions")


if __name__ == "__main__":
    main()