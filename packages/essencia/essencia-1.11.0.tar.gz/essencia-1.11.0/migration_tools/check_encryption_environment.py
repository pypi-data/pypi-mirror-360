#!/usr/bin/env python3
"""
check_encryption_environment.py
Verifica se o ambiente está configurado corretamente para encriptação
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Verifica configuração do ambiente"""
    
    print("=== Verificação do Ambiente de Encriptação ===\n")
    
    # 1. Verificar chave de encriptação
    encryption_key = os.getenv('ESSENCIA_ENCRYPTION_KEY')
    if not encryption_key:
        print("❌ ESSENCIA_ENCRYPTION_KEY não encontrada")
        print("   Execute: export ESSENCIA_ENCRYPTION_KEY='sua-chave'")
        return False
    else:
        print("✅ Chave de encriptação configurada")
        print(f"   Tamanho: {len(encryption_key)} caracteres")
    
    # 2. Verificar MongoDB
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    print(f"✅ MongoDB URL: {mongodb_url}")
    
    # 3. Verificar se .env existe
    if Path('.env').exists():
        print("✅ Arquivo .env encontrado")
    else:
        print("⚠️  Arquivo .env não encontrado (variáveis temporárias)")
    
    # 4. Testar importação do Essencia
    try:
        import essencia
        print("✅ Framework Essencia importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Essencia: {e}")
        return False
    
    # 5. Testar serviço de encriptação
    try:
        from essencia.security.encryption_service import EncryptionService
        service = EncryptionService()
        
        # Teste básico
        test_data = "123.456.789-00"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        
        if decrypted == test_data:
            print("✅ Serviço de encriptação funcionando corretamente")
        else:
            print("❌ Falha no teste de encriptação/descriptografia")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar encriptação: {e}")
        return False
    
    print("\n✅ Ambiente configurado corretamente!")
    return True

if __name__ == "__main__":
    if not check_environment():
        sys.exit(1)