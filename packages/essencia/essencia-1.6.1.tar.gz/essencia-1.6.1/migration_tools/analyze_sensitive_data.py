#!/usr/bin/env python3
"""
analyze_sensitive_data.py
Analisa o banco para identificar dados sensíveis não encriptados
"""
import re
from collections import defaultdict

def analyze_sensitive_fields():
    """Analisa campos que contêm dados sensíveis"""
    
    print("=== Análise de Dados Sensíveis ===\n")
    
    from essencia.database import Database
    db = Database()
    
    # Padrões para identificar dados sensíveis
    patterns = {
        'cpf': re.compile(r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$'),
        'rg': re.compile(r'^\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}$'),
        'phone': re.compile(r'^[\+\d\s\-\(\)]+$'),
        'email': re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    }
    
    results = defaultdict(lambda: defaultdict(int))
    
    # Collections para analisar
    collections = ["patient", "doctor", "staff", "contact"]
    
    for collection in collections:
        print(f"\nAnalisando collection: {collection}")
        
        try:
            docs = db.find(collection, {})
            total_docs = 0
            
            for doc in docs:
                total_docs += 1
                
                # Verificar cada campo do documento
                for field, value in doc.items():
                    if value and isinstance(value, str):
                        # Verificar se é dado encriptado
                        if value.startswith('ENCRYPTED:'):
                            results[collection][f"{field}_encrypted"] += 1
                        else:
                            # Verificar padrões sensíveis
                            for pattern_name, pattern in patterns.items():
                                if pattern.match(str(value)):
                                    results[collection][f"{field}_{pattern_name}_plain"] += 1
            
            print(f"  Total de documentos: {total_docs}")
            
            # Mostrar resultados da collection
            for field_type, count in results[collection].items():
                if count > 0:
                    status = "✅" if "encrypted" in field_type else "⚠️"
                    print(f"  {status} {field_type}: {count}")
                    
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    # Resumo
    print("\n=== Resumo ===")
    total_plain = sum(
        count for collection in results.values() 
        for field, count in collection.items() 
        if "plain" in field
    )
    total_encrypted = sum(
        count for collection in results.values() 
        for field, count in collection.items() 
        if "encrypted" in field
    )
    
    print(f"Total de campos sensíveis não encriptados: {total_plain}")
    print(f"Total de campos já encriptados: {total_encrypted}")
    
    if total_plain > 0:
        print("\n⚠️  Atenção: Existem dados sensíveis não encriptados!")
        print("   Execute a migração para proteger estes dados.")
    
    return results

if __name__ == "__main__":
    analyze_sensitive_fields()