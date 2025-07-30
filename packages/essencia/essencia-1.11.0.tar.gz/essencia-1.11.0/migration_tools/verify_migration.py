#!/usr/bin/env python3
"""
verify_migration.py
Verifica se a migração foi bem-sucedida
"""
from collections import defaultdict

def verify_encryption():
    """Verifica o status da encriptação no banco"""
    
    print("=== Verificação Pós-Migração ===\n")
    
    from essencia.database import Database
    from essencia.fields import EncryptedCPF, EncryptedRG
    
    db = Database()
    
    stats = defaultdict(lambda: defaultdict(int))
    
    # Collections e campos para verificar
    checks = {
        'patient': ['cpf', 'rg', 'medical_history'],
        'doctor': ['cpf', 'crm'],
        'staff': ['cpf', 'rg']
    }
    
    for collection, fields in checks.items():
        print(f"\nVerificando {collection}:")
        
        docs = list(db.find(collection, {}))
        total = len(docs)
        
        for doc in docs:
            for field in fields:
                if field in doc and doc[field]:
                    value = str(doc[field])
                    
                    # Verificar se está encriptado
                    if value.startswith('ENCRYPTED:'):
                        stats[collection][f"{field}_encrypted"] += 1
                        
                        # Tentar descriptografar
                        try:
                            # Simular descriptografia
                            if field == 'cpf':
                                dec = EncryptedCPF(value).decrypt()
                                stats[collection][f"{field}_verified"] += 1
                        except Exception as e:
                            stats[collection][f"{field}_decrypt_error"] += 1
                    else:
                        stats[collection][f"{field}_plain"] += 1
        
        # Mostrar resultados
        print(f"  Total de documentos: {total}")
        for stat, count in stats[collection].items():
            emoji = "✅" if "encrypted" in stat else "❌" if "plain" in stat else "⚠️"
            print(f"  {emoji} {stat}: {count}")
    
    # Verificar integridade
    print("\n=== Teste de Integridade ===")
    
    # Pegar um documento de teste
    test_patient = db.find_one('patient', {'cpf': {'$regex': '^ENCRYPTED:'}})
    if test_patient:
        print("Testando descriptografia de um paciente:")
        try:
            cpf_enc = test_patient.get('cpf')
            if cpf_enc:
                cpf_dec = EncryptedCPF(cpf_enc).decrypt()
                print(f"  ✅ CPF descriptografado com sucesso")
                print(f"     Formato: {'*' * (len(cpf_dec) - 4) + cpf_dec[-4:]}")
        except Exception as e:
            print(f"  ❌ Erro na descriptografia: {e}")
    
    return stats

if __name__ == "__main__":
    verify_encryption()