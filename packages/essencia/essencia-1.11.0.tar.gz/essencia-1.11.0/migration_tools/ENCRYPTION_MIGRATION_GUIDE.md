# Guia de Migração para Encriptação de Dados Sensíveis

Este guia contém todos os procedimentos necessários para migrar dados existentes para campos encriptados no banco de dados. Mantenha este documento separado do framework para referência futura.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração Inicial](#configuração-inicial)
3. [Scripts de Migração](#scripts-de-migração)
4. [Procedimento Passo a Passo](#procedimento-passo-a-passo)
5. [Rollback e Recuperação](#rollback-e-recuperação)
6. [Monitoramento Pós-Migração](#monitoramento-pós-migração)

## Pré-requisitos

- Python 3.12+
- MongoDB em execução
- Acesso administrativo ao banco de dados
- Backup completo do banco de dados
- Framework Essencia instalado

## Configuração Inicial

### 1. Gerar Chave de Encriptação

```bash
# Gerar chave segura de 32 bytes
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### 2. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env na raiz do projeto
cat > .env << EOF
ESSENCIA_ENCRYPTION_KEY="sua-chave-gerada-aqui"
MONGODB_URL="mongodb://localhost:27017/seu_banco"
EOF

# Proteger o arquivo
chmod 600 .env
```

### 3. Adicionar ao .gitignore

```bash
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "backup_*" >> .gitignore
```

## Scripts de Migração

### Script 1: Verificação do Ambiente

```python
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
```

### Script 2: Backup do Banco

```python
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
```

### Script 3: Análise de Dados Sensíveis

```python
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
```

### Script 4: Migração Principal

```python
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
```

### Script 5: Verificação Pós-Migração

```python
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
```

## Procedimento Passo a Passo

### Fase 1: Preparação

1. **Instalar dependências**
   ```bash
   pip install essencia
   ```

2. **Copiar scripts para diretório de trabalho**
   ```bash
   mkdir -p migration_tools
   cp *.py migration_tools/
   cd migration_tools
   ```

3. **Configurar ambiente**
   ```bash
   # Gerar chave
   python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
   
   # Criar .env
   echo 'ESSENCIA_ENCRYPTION_KEY="sua-chave-aqui"' > .env
   ```

4. **Verificar configuração**
   ```bash
   python check_encryption_environment.py
   ```

### Fase 2: Análise e Backup

1. **Analisar dados sensíveis**
   ```bash
   python analyze_sensitive_data.py > analysis_report.txt
   ```

2. **Criar backup completo**
   ```bash
   python backup_database.py
   ```

3. **Verificar backup**
   ```bash
   ls -lh backups/
   ```

### Fase 3: Migração

1. **Executar em modo DRY RUN**
   ```bash
   python migrate_to_encrypted.py
   ```

2. **Revisar o relatório**
   - Verificar quantos documentos serão modificados
   - Identificar possíveis erros

3. **Aplicar migração**
   ```bash
   python migrate_to_encrypted.py --apply --backup
   ```

### Fase 4: Verificação

1. **Verificar encriptação**
   ```bash
   python verify_migration.py
   ```

2. **Testar aplicação**
   - Acessar alguns registros
   - Verificar se dados são descriptografados corretamente

## Rollback e Recuperação

### Restaurar do Backup

```python
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
```

## Monitoramento Pós-Migração

### Script de Monitoramento

```python
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
```

## Checklist de Migração

- [ ] Ambiente configurado (chave de encriptação)
- [ ] Scripts de migração copiados
- [ ] Análise de dados sensíveis executada
- [ ] Backup completo criado e verificado
- [ ] Dry run executado e revisado
- [ ] Migração aplicada
- [ ] Verificação pós-migração executada
- [ ] Testes de aplicação realizados
- [ ] Monitoramento configurado
- [ ] Documentação atualizada

## Problemas Comuns e Soluções

### 1. Chave de encriptação não encontrada
```bash
export ESSENCIA_ENCRYPTION_KEY="sua-chave"
# ou adicione ao .env
```

### 2. Erro de importação do Essencia
```bash
pip install --upgrade essencia
```

### 3. Falha na descriptografia após migração
- Verificar se a mesma chave está sendo usada
- Verificar se o campo foi encriptado corretamente
- Restaurar do backup se necessário

### 4. Performance degradada
- Implementar cache para dados descriptografados
- Considerar índices parciais no MongoDB
- Monitorar e otimizar queries

## Notas de Segurança

1. **NUNCA** compartilhe ou faça commit da chave de encriptação
2. **SEMPRE** faça backup antes de migrar
3. **TESTE** em ambiente de desenvolvimento primeiro
4. **MONITORE** o uso após a migração
5. **DOCUMENTE** o processo e mantenha logs

## Contato e Suporte

Em caso de problemas durante a migração:
1. Verifique os logs de erro
2. Consulte o backup criado
3. Execute o script de verificação
4. Se necessário, restaure do backup

Mantenha este guia atualizado com suas experiências e melhorias!