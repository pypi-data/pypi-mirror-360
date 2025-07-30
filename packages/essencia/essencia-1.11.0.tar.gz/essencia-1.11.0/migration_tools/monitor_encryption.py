#!/usr/bin/env python3
"""
monitor_encryption.py
Monitora o uso de campos encriptados
"""
from datetime import datetime
from collections import defaultdict

def monitor_encryption_usage():
    """Monitora acessos a campos encriptados"""
    
    print(f"=== Monitor de Encriptação - {datetime.now()} ===\n")
    
    from essencia.database import Database
    db = Database()
    
    # Estatísticas
    stats = defaultdict(int)
    
    # Verificar logs de auditoria (se disponível)
    audit_logs = list(db.find('audit_log', {
        'action': 'decrypt_field',
        'timestamp': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
    }))
    
    print(f"Acessos a campos encriptados hoje: {len(audit_logs)}")
    
    # Agrupar por campo
    field_access = defaultdict(int)
    for log in audit_logs:
        field = log.get('details', {}).get('field', 'unknown')
        field_access[field] += 1
    
    print("\nAcessos por campo:")
    for field, count in sorted(field_access.items(), key=lambda x: x[1], reverse=True):
        print(f"  {field}: {count}")
    
    # Verificar performance
    print("\n=== Performance ===")
    
    # Testar tempo de descriptografia
    import time
    from essencia.fields import EncryptedCPF
    
    test_cpf = "123.456.789-00"
    
    # Tempo de encriptação
    start = time.time()
    encrypted = EncryptedCPF(test_cpf)
    enc_time = time.time() - start
    
    # Tempo de descriptografia
    start = time.time()
    decrypted = encrypted.decrypt()
    dec_time = time.time() - start
    
    print(f"Tempo de encriptação: {enc_time*1000:.2f}ms")
    print(f"Tempo de descriptografia: {dec_time*1000:.2f}ms")
    
    # Verificar tamanho do armazenamento
    print("\n=== Impacto no Armazenamento ===")
    
    sample_patient = db.find_one('patient', {'cpf': {'$regex': '^ENCRYPTED:'}})
    if sample_patient and 'cpf' in sample_patient:
        encrypted_size = len(sample_patient['cpf'])
        original_size = 14  # CPF formatado
        overhead = ((encrypted_size / original_size) - 1) * 100
        
        print(f"Tamanho original (CPF): {original_size} bytes")
        print(f"Tamanho encriptado: {encrypted_size} bytes")
        print(f"Overhead: {overhead:.1f}%")

if __name__ == "__main__":
    monitor_encryption_usage()