#!/usr/bin/env python3
"""
migrate_to_encrypted.py
Script principal de migração para campos encriptados
"""
import argparse
from datetime import datetime
from typing import Dict, List, Any

class EncryptionMigrator:
    """Gerencia a migração de dados para campos encriptados"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.stats = {
            'processed': 0,
            'migrated': 0,
            'errors': 0,
            'skipped': 0
        }
        
    def migrate_collection(self, collection_name: str, field_mappings: Dict[str, str]):
        """
        Migra uma collection específica
        
        Args:
            collection_name: Nome da collection
            field_mappings: Mapeamento de campo -> tipo encriptado
                           Ex: {'cpf': 'EncryptedCPF', 'rg': 'EncryptedRG'}
        """
        from essencia.database import Database
        from essencia.fields import EncryptedCPF, EncryptedRG, EncryptedMedicalData
        
        db = Database()
        
        # Mapeamento de tipos
        encryption_types = {
            'EncryptedCPF': EncryptedCPF,
            'EncryptedRG': EncryptedRG,
            'EncryptedMedicalData': EncryptedMedicalData
        }
        
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Migrando collection: {collection_name}")
        
        # Buscar todos os documentos
        docs = list(db.find(collection_name, {}))
        print(f"  Total de documentos: {len(docs)}")
        
        for doc in docs:
            self.stats['processed'] += 1
            doc_id = doc.get('_id')
            changes = {}
            
            # Verificar cada campo mapeado
            for field, enc_type in field_mappings.items():
                if field in doc and doc[field]:
                    value = doc[field]
                    
                    # Verificar se já está encriptado
                    if isinstance(value, str) and value.startswith('ENCRYPTED:'):
                        continue
                    
                    # Encriptar o valor
                    try:
                        enc_class = encryption_types.get(enc_type)
                        if enc_class:
                            encrypted_value = enc_class(value)
                            changes[field] = str(encrypted_value)
                    except Exception as e:
                        print(f"    ❌ Erro ao encriptar {field}: {e}")
                        self.stats['errors'] += 1
            
            # Aplicar mudanças
            if changes:
                if not self.dry_run:
                    try:
                        db.update_one(
                            collection_name,
                            {'_id': doc_id},
                            {'$set': changes}
                        )
                        print(f"    ✅ Documento {doc_id}: {len(changes)} campos encriptados")
                    except Exception as e:
                        print(f"    ❌ Erro ao atualizar {doc_id}: {e}")
                        self.stats['errors'] += 1
                else:
                    print(f"    🔍 Documento {doc_id}: {len(changes)} campos seriam encriptados")
                
                self.stats['migrated'] += 1
            else:
                self.stats['skipped'] += 1
    
    def run_migration(self):
        """Executa a migração completa"""
        
        print(f"\n=== Migração para Campos Encriptados ===")
        print(f"Modo: {'DRY RUN' if self.dry_run else 'APLICANDO MUDANÇAS'}")
        print(f"Início: {datetime.now()}")
        
        # Definir mapeamentos por collection
        migrations = {
            'patient': {
                'cpf': 'EncryptedCPF',
                'rg': 'EncryptedRG',
                'medical_history': 'EncryptedMedicalData'
            },
            'doctor': {
                'cpf': 'EncryptedCPF',
                'crm': 'EncryptedRG'  # Usando EncryptedRG para CRM
            },
            'staff': {
                'cpf': 'EncryptedCPF',
                'rg': 'EncryptedRG'
            }
        }
        
        # Executar migrações
        for collection, mappings in migrations.items():
            self.migrate_collection(collection, mappings)
        
        # Relatório final
        print(f"\n=== Relatório Final ===")
        print(f"Documentos processados: {self.stats['processed']}")
        print(f"Documentos migrados: {self.stats['migrated']}")
        print(f"Documentos ignorados: {self.stats['skipped']}")
        print(f"Erros: {self.stats['errors']}")
        print(f"Fim: {datetime.now()}")
        
        if self.dry_run:
            print("\n⚠️  Este foi um DRY RUN. Nenhuma mudança foi aplicada.")
            print("   Para aplicar as mudanças, execute com --apply")

def main():
    parser = argparse.ArgumentParser(description='Migrar dados para campos encriptados')
    parser.add_argument('--apply', action='store_true', 
                       help='Aplicar mudanças (sem esta flag, executa em dry-run)')
    parser.add_argument('--backup', action='store_true',
                       help='Criar backup antes de migrar')
    
    args = parser.parse_args()
    
    # Verificar ambiente
    from check_encryption_environment import check_environment
    if not check_environment():
        print("\n❌ Ambiente não está configurado corretamente!")
        return 1
    
    # Criar backup se solicitado
    if args.backup and args.apply:
        from backup_database import create_backup
        backup_file = create_backup()
        if not backup_file:
            print("\n❌ Falha ao criar backup. Abortando migração.")
            return 1
    
    # Executar migração
    migrator = EncryptionMigrator(dry_run=not args.apply)
    migrator.run_migration()
    
    return 0

if __name__ == "__main__":
    exit(main())