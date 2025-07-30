#!/usr/bin/env python
"""
Check encryption setup and provide guidance for data migration.

This script:
1. Checks if encryption key exists in environment
2. Generates a secure key if needed
3. Analyzes existing MongoDB data for encryption needs
4. Provides migration recommendations
"""

import os
import base64
import secrets
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from essencia.security.encryption_service import EncryptionService, is_field_encrypted
from essencia.core.exceptions import EncryptionError


def generate_encryption_key() -> str:
    """Generate a secure 32-byte encryption key for AES-256."""
    key_bytes = secrets.token_bytes(32)
    return base64.b64encode(key_bytes).decode('utf-8')


def check_encryption_key() -> tuple[bool, Optional[str]]:
    """Check if encryption key exists and is valid."""
    key = os.environ.get('ESSENCIA_ENCRYPTION_KEY')
    
    if not key:
        return False, None
    
    try:
        # Try to decode the key
        decoded = base64.b64decode(key.encode('utf-8'))
        if len(decoded) != 32:
            print(f"⚠️  Warning: Encryption key should be 32 bytes, found {len(decoded)} bytes")
            return False, key
        return True, key
    except Exception as e:
        print(f"⚠️  Error decoding encryption key: {e}")
        return False, key


def test_encryption_service(key: str) -> bool:
    """Test if encryption service works with the given key."""
    try:
        service = EncryptionService(master_key=key)
        
        # Test encryption/decryption
        test_data = "Test CPF: 123.456.789-00"
        encrypted = service.encrypt(test_data, context="test")
        decrypted = service.decrypt(encrypted, context="test")
        
        if decrypted != test_data:
            print("❌ Encryption/decryption test failed")
            return False
            
        print("✅ Encryption service is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing encryption service: {e}")
        return False


def check_mongodb_connection() -> Optional[MongoClient]:
    """Check MongoDB connection and return client if successful."""
    mongodb_url = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
    
    try:
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ismaster')
        print(f"✅ Connected to MongoDB at {mongodb_url}")
        return client
    except ConnectionFailure:
        print(f"❌ Failed to connect to MongoDB at {mongodb_url}")
        return None
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None


def analyze_collections_for_encryption(client: MongoClient) -> Dict[str, List[str]]:
    """Analyze MongoDB collections for fields that might need encryption."""
    encryption_candidates = {}
    
    # Fields that should be encrypted based on their names
    sensitive_field_patterns = [
        'cpf', 'rg', 'medical', 'prescription', 'diagnosis',
        'medical_history', 'medical_notes', 'treatment',
        'sensitive', 'private', 'confidential'
    ]
    
    try:
        # Get all databases
        for db_name in client.list_database_names():
            if db_name in ['admin', 'config', 'local']:
                continue
                
            db = client[db_name]
            
            # Get all collections
            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                
                # Sample documents to understand structure
                sample_docs = list(collection.find().limit(10))
                if not sample_docs:
                    continue
                
                # Analyze fields
                sensitive_fields = []
                for doc in sample_docs:
                    for field_name, field_value in doc.items():
                        if field_name == '_id':
                            continue
                            
                        # Check if field name suggests sensitive data
                        field_lower = field_name.lower()
                        for pattern in sensitive_field_patterns:
                            if pattern in field_lower:
                                if field_name not in sensitive_fields:
                                    # Check if already encrypted
                                    if isinstance(field_value, str) and is_field_encrypted(field_value):
                                        sensitive_fields.append(f"{field_name} (already encrypted)")
                                    else:
                                        sensitive_fields.append(f"{field_name} (needs encryption)")
                                break
                
                if sensitive_fields:
                    key = f"{db_name}.{collection_name}"
                    encryption_candidates[key] = sensitive_fields
                    
    except Exception as e:
        print(f"⚠️  Error analyzing collections: {e}")
        
    return encryption_candidates


def main():
    """Main function to check encryption setup."""
    print("🔐 Essencia Encryption Setup Check\n")
    
    # Step 1: Check encryption key
    print("1️⃣  Checking encryption key...")
    key_exists, current_key = check_encryption_key()
    
    if not key_exists:
        print("❌ No valid encryption key found in ESSENCIA_ENCRYPTION_KEY environment variable")
        print("\n📝 To generate a new encryption key:")
        new_key = generate_encryption_key()
        print(f"\n   export ESSENCIA_ENCRYPTION_KEY=\"{new_key}\"")
        print("\n⚠️  Save this key securely! It cannot be recovered if lost.")
        print("   Consider using a secrets management system in production.")
        
        # Ask if user wants to set it now
        response = input("\nWould you like to set this key in your environment now? (y/n): ")
        if response.lower() == 'y':
            os.environ['ESSENCIA_ENCRYPTION_KEY'] = new_key
            current_key = new_key
            key_exists = True
            print("✅ Encryption key set in current session")
        else:
            print("\n⚠️  Remember to set the encryption key before using encrypted fields")
            return
    else:
        print("✅ Valid encryption key found")
    
    # Step 2: Test encryption service
    print("\n2️⃣  Testing encryption service...")
    if test_encryption_service(current_key):
        # Get encryption stats
        service = EncryptionService(current_key)
        stats = service.get_encryption_stats()
        print("\n📊 Encryption Configuration:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Step 3: Check MongoDB
    print("\n3️⃣  Checking MongoDB connection...")
    client = check_mongodb_connection()
    
    if client:
        # Step 4: Analyze collections
        print("\n4️⃣  Analyzing collections for sensitive data...")
        candidates = analyze_collections_for_encryption(client)
        
        if candidates:
            print("\n📋 Collections with potentially sensitive fields:")
            for collection, fields in candidates.items():
                print(f"\n   {collection}:")
                for field in fields:
                    print(f"      - {field}")
            
            print("\n💡 Migration Recommendations:")
            print("   1. Back up your database before migration")
            print("   2. Use the migration script to encrypt existing data")
            print("   3. Update your models to use encrypted field types")
            print("   4. Test thoroughly in a staging environment first")
        else:
            print("✅ No sensitive fields detected in existing collections")
    
    # Step 5: Environment file check
    print("\n5️⃣  Checking for .env file...")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ESSENCIA_ENCRYPTION_KEY' not in content:
                print("⚠️  .env file exists but doesn't contain ESSENCIA_ENCRYPTION_KEY")
                print("   Consider adding it for development convenience")
            else:
                print("✅ .env file contains ESSENCIA_ENCRYPTION_KEY")
    else:
        print("⚠️  No .env file found")
        print("   Consider creating one for development:")
        print("\n   # .env")
        print(f"   ESSENCIA_ENCRYPTION_KEY=\"{current_key or generate_encryption_key()}\"")
        print("   MONGODB_URL=\"mongodb://localhost:27017\"")
        print("   REDIS_URL=\"redis://localhost:6379\"")
    
    print("\n✅ Encryption setup check complete!")
    print("\n📖 Next steps:")
    print("   1. Ensure encryption key is securely stored")
    print("   2. Update models to use encrypted field types")
    print("   3. Run migration script if you have existing data")
    print("   4. Test encryption/decryption thoroughly")


if __name__ == "__main__":
    main()