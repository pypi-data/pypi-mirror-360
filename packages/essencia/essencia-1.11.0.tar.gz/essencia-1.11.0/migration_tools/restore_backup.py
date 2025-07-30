#!/usr/bin/env python3
"""
restore_backup.py
Restaura banco de dados a partir do backup
"""
import json
import sys
from pathlib import Path

def restore_backup(backup_file: str):
    """Restaura dados do backup"""
    
    if not Path(backup_file).exists():
        print(f"❌ Arquivo não encontrado: {backup_file}")
        return False
    
    print(f"Restaurando de: {backup_file}")
    
    # Confirmação
    response = input("⚠️  Isto irá sobrescrever os dados atuais. Continuar? (yes/no): ")
    if response.lower() != 'yes':
        print("Operação cancelada.")
        return False
    
    try:
        from essencia.database import Database
        db = Database()
        
        # Carregar backup
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Restaurar cada collection
        for collection, docs in backup_data['data'].items():
            print(f"\nRestaurando {collection}...")
            
            # Limpar collection
            db.db[collection].delete_many({})
            
            # Inserir documentos
            if docs:
                db.db[collection].insert_many(docs)
                print(f"  ✅ {len(docs)} documentos restaurados")
        
        print("\n✅ Backup restaurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python restore_backup.py <arquivo_backup>")
        sys.exit(1)
    
    restore_backup(sys.argv[1])