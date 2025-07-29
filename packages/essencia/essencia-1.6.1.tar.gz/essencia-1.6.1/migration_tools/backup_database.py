#!/usr/bin/env python3
"""
backup_database.py
Cria backup completo do banco antes da migração
"""
import json
import os
from datetime import datetime
from pathlib import Path

def create_backup(database_name="essencia"):
    """Cria backup JSON do banco de dados"""
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{database_name}_{timestamp}.json"
    
    print(f"Criando backup em: {backup_file}")
    
    try:
        from essencia.database import Database
        db = Database()
        
        backup_data = {
            "metadata": {
                "database": database_name,
                "timestamp": timestamp,
                "collections": []
            },
            "data": {}
        }
        
        # Collections importantes para backup
        collections = ["patient", "doctor", "visit", "prescription", "lab_test"]
        
        for collection in collections:
            try:
                docs = list(db.find(collection, {}))
                backup_data["data"][collection] = docs
                backup_data["metadata"]["collections"].append({
                    "name": collection,
                    "count": len(docs)
                })
                print(f"  ✅ {collection}: {len(docs)} documentos")
            except Exception as e:
                print(f"  ⚠️  {collection}: Erro - {e}")
        
        # Salvar backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, default=str, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Backup criado: {backup_file}")
        print(f"   Tamanho: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        return str(backup_file)
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None

if __name__ == "__main__":
    create_backup()