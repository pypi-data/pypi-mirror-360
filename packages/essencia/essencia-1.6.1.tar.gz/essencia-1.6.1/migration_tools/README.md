# Migration Tools - Kit de Ferramentas para Migração de Encriptação

Este diretório contém todas as ferramentas necessárias para migrar dados sensíveis existentes para campos encriptados no MongoDB.

## Arquivos Incluídos

1. **ENCRYPTION_MIGRATION_GUIDE.md** - Guia completo de migração
2. **check_encryption_environment.py** - Verifica configuração do ambiente
3. **backup_database.py** - Cria backup antes da migração
4. **analyze_sensitive_data.py** - Analisa dados sensíveis no banco
5. **migrate_to_encrypted.py** - Script principal de migração
6. **verify_migration.py** - Verifica sucesso da migração
7. **restore_backup.py** - Restaura backup se necessário
8. **monitor_encryption.py** - Monitora uso pós-migração

## Uso Rápido

### 1. Preparar Ambiente

```bash
# Gerar chave de encriptação
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"

# Criar .env
echo 'ESSENCIA_ENCRYPTION_KEY="sua-chave-aqui"' > .env
echo 'MONGODB_URL="mongodb://localhost:27017/seu_banco"' >> .env

# Verificar ambiente
python check_encryption_environment.py
```

### 2. Analisar e Fazer Backup

```bash
# Analisar dados sensíveis
python analyze_sensitive_data.py

# Criar backup
python backup_database.py
```

### 3. Executar Migração

```bash
# Dry run (simulação)
python migrate_to_encrypted.py

# Aplicar migração
python migrate_to_encrypted.py --apply --backup
```

### 4. Verificar Resultado

```bash
# Verificar encriptação
python verify_migration.py

# Monitorar uso
python monitor_encryption.py
```

## Segurança

- **NUNCA** faça commit da chave de encriptação
- **SEMPRE** faça backup antes de migrar
- **TESTE** em ambiente de desenvolvimento primeiro

## Rollback

Se precisar reverter a migração:

```bash
python restore_backup.py backups/backup_essencia_20250130_123456.json
```

## Suporte

Consulte o guia completo em ENCRYPTION_MIGRATION_GUIDE.md para instruções detalhadas e resolução de problemas.