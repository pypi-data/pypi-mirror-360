#!/usr/bin/env python
"""
Migration script to encrypt existing data in MongoDB collections.

This script helps migrate unencrypted sensitive data to encrypted fields.
It can be run in dry-run mode to preview changes before applying them.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
import logging

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from essencia.security.encryption_service import (
    EncryptionService, 
    is_field_encrypted,
    encrypt_cpf,
    encrypt_rg,
    encrypt_medical_data
)
from essencia.core.exceptions import EncryptionError
from essencia.utils.validators import CPFValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EncryptionMigrator:
    """Handles migration of unencrypted data to encrypted fields."""
    
    # Field mappings: field_name -> (encryption_function, validation_function)
    FIELD_MAPPINGS = {
        'cpf': (encrypt_cpf, CPFValidator.validate),
        'rg': (encrypt_rg, None),
        'medical_history': (encrypt_medical_data, None),
        'medical_notes': (encrypt_medical_data, None),
        'prescription': (encrypt_medical_data, None),
        'diagnosis': (encrypt_medical_data, None),
        'treatment': (encrypt_medical_data, None),
    }
    
    def __init__(self, mongodb_url: str, dry_run: bool = True):
        """
        Initialize the migrator.
        
        Args:
            mongodb_url: MongoDB connection URL
            dry_run: If True, only preview changes without applying
        """
        self.client = MongoClient(mongodb_url)
        self.dry_run = dry_run
        self.encryption_service = EncryptionService()
        self.stats = {
            'collections_processed': 0,
            'documents_processed': 0,
            'fields_encrypted': 0,
            'errors': 0,
            'skipped': 0
        }
        
    def migrate_collection(
        self, 
        db_name: str, 
        collection_name: str,
        field_mappings: Optional[Dict[str, str]] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Migrate a single collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            field_mappings: Custom field mappings (field_name -> encryption_context)
            batch_size: Number of documents to process in each batch
            
        Returns:
            Migration statistics for this collection
        """
        collection = self.client[db_name][collection_name]
        collection_stats = {
            'documents': 0,
            'fields_encrypted': 0,
            'errors': 0,
            'skipped': 0
        }
        
        logger.info(f"Processing collection: {db_name}.{collection_name}")
        
        # Get fields that need encryption
        fields_to_encrypt = self._get_fields_to_encrypt(collection, field_mappings)
        
        if not fields_to_encrypt:
            logger.info(f"No fields to encrypt in {collection_name}")
            return collection_stats
        
        logger.info(f"Fields to encrypt: {', '.join(fields_to_encrypt)}")
        
        # Process documents in batches
        cursor = collection.find({})
        batch = []
        
        for doc in cursor:
            update_doc = self._process_document(doc, fields_to_encrypt, field_mappings)
            
            if update_doc:
                batch.append(UpdateOne(
                    {'_id': doc['_id']},
                    {'$set': update_doc}
                ))
                collection_stats['fields_encrypted'] += len(update_doc)
            else:
                collection_stats['skipped'] += 1
            
            collection_stats['documents'] += 1
            
            # Process batch
            if len(batch) >= batch_size:
                self._process_batch(collection, batch, collection_stats)
                batch = []
        
        # Process remaining documents
        if batch:
            self._process_batch(collection, batch, collection_stats)
        
        # Update global stats
        self.stats['collections_processed'] += 1
        self.stats['documents_processed'] += collection_stats['documents']
        self.stats['fields_encrypted'] += collection_stats['fields_encrypted']
        self.stats['errors'] += collection_stats['errors']
        self.stats['skipped'] += collection_stats['skipped']
        
        return collection_stats
    
    def _get_fields_to_encrypt(
        self, 
        collection,
        custom_mappings: Optional[Dict[str, str]] = None
    ) -> Set[str]:
        """Identify fields that need encryption in a collection."""
        fields_to_encrypt = set()
        
        # Sample documents to understand structure
        sample_docs = list(collection.find().limit(100))
        
        for doc in sample_docs:
            for field_name, field_value in doc.items():
                if field_name == '_id':
                    continue
                
                # Skip if already encrypted
                if isinstance(field_value, str) and is_field_encrypted(field_value):
                    continue
                
                # Check if field should be encrypted
                if custom_mappings and field_name in custom_mappings:
                    fields_to_encrypt.add(field_name)
                elif field_name.lower() in self.FIELD_MAPPINGS:
                    fields_to_encrypt.add(field_name)
                else:
                    # Check for pattern matches
                    field_lower = field_name.lower()
                    for pattern in ['medical', 'prescription', 'diagnosis', 'treatment']:
                        if pattern in field_lower:
                            fields_to_encrypt.add(field_name)
                            break
        
        return fields_to_encrypt
    
    def _process_document(
        self, 
        doc: Dict[str, Any],
        fields_to_encrypt: Set[str],
        custom_mappings: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Process a single document and return fields to update."""
        update_fields = {}
        
        for field_name in fields_to_encrypt:
            if field_name not in doc:
                continue
                
            field_value = doc[field_name]
            
            # Skip if already encrypted or empty
            if not field_value:
                continue
            if isinstance(field_value, str) and is_field_encrypted(field_value):
                continue
            
            try:
                # Encrypt the field
                encrypted_value = self._encrypt_field(
                    field_name, 
                    field_value,
                    custom_mappings
                )
                
                if encrypted_value:
                    update_fields[field_name] = encrypted_value
                    
            except Exception as e:
                logger.error(f"Error encrypting {field_name} in document {doc['_id']}: {e}")
                continue
        
        return update_fields if update_fields else None
    
    def _encrypt_field(
        self, 
        field_name: str, 
        value: Any,
        custom_mappings: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Encrypt a single field value."""
        if not isinstance(value, str):
            value = str(value)
        
        # Get encryption function and validator
        field_lower = field_name.lower()
        
        if field_lower in self.FIELD_MAPPINGS:
            encrypt_func, validator = self.FIELD_MAPPINGS[field_lower]
            
            # Validate if validator exists
            if validator:
                try:
                    validator(value)
                except Exception as e:
                    logger.warning(f"Validation failed for {field_name}: {e}")
                    # Optionally skip invalid values
                    # return None
            
            return encrypt_func(value)
        
        # Use custom mapping or default context
        if custom_mappings and field_name in custom_mappings:
            context = custom_mappings[field_name]
        else:
            context = "medical" if any(p in field_lower for p in ['medical', 'prescription', 'diagnosis']) else "default"
        
        return self.encryption_service.encrypt(value, context=context)
    
    def _process_batch(
        self, 
        collection,
        batch: List[UpdateOne],
        stats: Dict[str, int]
    ):
        """Process a batch of updates."""
        if not batch:
            return
            
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update {len(batch)} documents")
            for update in batch[:5]:  # Show first 5 updates
                logger.debug(f"[DRY RUN] Update: {update._asdict()}")
        else:
            try:
                result = collection.bulk_write(batch)
                logger.info(f"Updated {result.modified_count} documents")
            except BulkWriteError as e:
                logger.error(f"Bulk write error: {e}")
                stats['errors'] += len(batch)
    
    def migrate_database(
        self, 
        db_name: str,
        collection_filter: Optional[List[str]] = None,
        field_mappings: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Migrate an entire database.
        
        Args:
            db_name: Database name
            collection_filter: List of collection names to process (None = all)
            field_mappings: Per-collection field mappings
        """
        db = self.client[db_name]
        collections = collection_filter or db.list_collection_names()
        
        for collection_name in collections:
            if collection_name.startswith('system.'):
                continue
                
            collection_mappings = None
            if field_mappings and collection_name in field_mappings:
                collection_mappings = field_mappings[collection_name]
            
            self.migrate_collection(db_name, collection_name, collection_mappings)
    
    def create_backup(self, db_name: str, backup_path: str):
        """Create a backup of the database before migration."""
        logger.info(f"Creating backup of {db_name} to {backup_path}")
        
        # Use mongodump command
        import subprocess
        
        cmd = [
            'mongodump',
            '--uri', self.client.HOST,
            '--db', db_name,
            '--out', backup_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Backup created successfully at {backup_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e}")
            raise
        except FileNotFoundError:
            logger.warning("mongodump not found. Please install MongoDB tools for backup functionality.")
    
    def get_summary(self) -> str:
        """Get migration summary."""
        return f"""
Migration Summary:
==================
Collections processed: {self.stats['collections_processed']}
Documents processed:   {self.stats['documents_processed']}
Fields encrypted:      {self.stats['fields_encrypted']}
Documents skipped:     {self.stats['skipped']}
Errors:               {self.stats['errors']}
Mode:                 {'DRY RUN' if self.dry_run else 'APPLIED'}
        """


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Migrate unencrypted data to encrypted fields in MongoDB"
    )
    parser.add_argument(
        '--mongodb-url',
        default=os.environ.get('MONGODB_URL', 'mongodb://localhost:27017'),
        help='MongoDB connection URL'
    )
    parser.add_argument(
        '--database',
        required=True,
        help='Database name to migrate'
    )
    parser.add_argument(
        '--collections',
        nargs='*',
        help='Specific collections to migrate (default: all)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run mode)'
    )
    parser.add_argument(
        '--backup-path',
        help='Path to create backup before migration'
    )
    parser.add_argument(
        '--field-mappings',
        type=str,
        help='JSON file with custom field mappings'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of documents to process in each batch'
    )
    
    args = parser.parse_args()
    
    # Check encryption key
    if not os.environ.get('ESSENCIA_ENCRYPTION_KEY'):
        logger.error("ESSENCIA_ENCRYPTION_KEY environment variable not set")
        logger.error("Run check_encryption_setup.py first to set up encryption")
        sys.exit(1)
    
    # Load field mappings if provided
    field_mappings = None
    if args.field_mappings:
        with open(args.field_mappings, 'r') as f:
            field_mappings = json.load(f)
    
    # Create migrator
    migrator = EncryptionMigrator(
        mongodb_url=args.mongodb_url,
        dry_run=not args.apply
    )
    
    # Create backup if requested and applying changes
    if args.backup_path and args.apply:
        migrator.create_backup(args.database, args.backup_path)
    
    try:
        # Run migration
        logger.info(f"Starting migration for database: {args.database}")
        logger.info(f"Mode: {'APPLYING CHANGES' if args.apply else 'DRY RUN'}")
        
        migrator.migrate_database(
            db_name=args.database,
            collection_filter=args.collections,
            field_mappings=field_mappings
        )
        
        # Print summary
        print(migrator.get_summary())
        
        if not args.apply:
            print("\n⚠️  This was a DRY RUN. No changes were made.")
            print("   To apply changes, run with --apply flag")
            print("\n💡 Recommendation: Create a backup first with --backup-path")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()