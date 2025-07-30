# Sistema de Dados Laboratoriais

## Visão Geral

O sistema de dados laboratoriais do Essencia fornece uma solução completa para importar, armazenar e analisar resultados de exames de laboratório. O sistema foi projetado com foco em segurança (encriptação de dados sensíveis), flexibilidade (suporta múltiplos formatos) e análise temporal.

## Componentes Principais

### 1. Modelos de Dados

#### LabTestType
Catálogo de tipos de exames com valores de referência:
- Nome e código do exame
- Categoria (Hematologia, Bioquímica, etc.)
- Unidade de medida
- Valores de referência por idade/sexo
- Requisitos (jejum, tipo de amostra)

#### LabTest
Resultado individual de exame:
- Valor encriptado do resultado
- Data de coleta e resultado
- Referência ao tipo de exame
- Indicador de anormalidade
- Vínculo com paciente e visita

#### LabTestBatch
Lote de exames importados:
- Rastreamento de importações
- Status de processamento
- Contagem de exames

### 2. Importação de Dados

#### Formato CSV Suportado
```csv
data,05.06.2013,19.12.2013,27.11.2014
hemácias (milhões/mm3),4.23,,4.54
hematócrito (%),35.5,,39.9
hemoglobina (g/dL),11.5,,12.8
```

#### Uso do Importador
```python
from essencia.utils import LabCSVImporter

# Criar importador
importer = LabCSVImporter(patient_key="patient_123", doctor_key="dr_smith")

# Importar arquivo CSV
success_count, errors = importer.import_csv(
    Path("lab.csv"), 
    laboratory="Laboratório Central"
)
```

### 3. Análise de Dados

#### Histórico de Exames
```python
from essencia.models import LabTestAnalyzer

# Obter histórico completo
history = LabTestAnalyzer.get_patient_history(patient_key)

# Filtrar por tipo de exame
glucose_history = LabTestAnalyzer.get_patient_history(
    patient_key, 
    test_name="Glicemia Jejum",
    start_date=date(2024, 1, 1)
)
```

#### Análise de Tendências
```python
# Analisar tendência de um exame
trend = LabTestAnalyzer.get_test_trend(
    patient_key, 
    "Hemoglobina", 
    limit=10
)
# Retorna: valores, estatísticas, direção da tendência
```

#### Resultados Anormais
```python
# Obter exames fora da referência
abnormal = LabTestAnalyzer.get_abnormal_results(patient_key)
```

#### Relatório Resumido
```python
# Gerar relatório anual
summary = LabTestAnalyzer.generate_summary_report(
    patient_key, 
    days=365
)
```

## Segurança

### Encriptação de Dados
Todos os valores de exames são armazenados usando o campo `EncryptedLabResults`:
- Encriptação AES-256-GCM
- Chaves gerenciadas pelo sistema
- Descriptografia transparente na leitura

### Auditoria
- Rastreamento de importações via LabTestBatch
- Vínculo doctor-patient em cada exame
- Timestamps de criação/modificação

## Casos de Uso

### 1. Importação em Massa
Ideal para migração de dados históricos ou integração com sistemas de laboratório.

### 2. Acompanhamento de Tratamento
Visualizar evolução de marcadores ao longo do tempo para avaliar eficácia terapêutica.

### 3. Detecção de Padrões
Identificar tendências e anomalias em séries temporais de exames.

### 4. Integração com Consultas
Vincular resultados de exames às visitas médicas correspondentes.

## Configuração de Valores de Referência

```python
from essencia.models import LabTestType, ReferenceRange

# Criar tipo de exame com referências
hemoglobin = LabTestType(
    code="HB",
    name="Hemoglobina",
    category=LabTestCategory.HEMATOLOGY,
    unit="g/dL",
    reference_ranges=[
        ReferenceRange(
            min_value=13.5,
            max_value=17.5,
            unit="g/dL",
            gender="M"
        ),
        ReferenceRange(
            min_value=12.0,
            max_value=15.5,
            unit="g/dL",
            gender="F"
        )
    ]
)
```

## Melhores Práticas

1. **Padronização**: Use o catálogo LabTestType para padronizar nomes e unidades
2. **Validação**: Verifique erros de importação antes de confirmar
3. **Histórico**: Mantenha dados históricos para análise de tendências
4. **Referências**: Configure valores de referência apropriados por idade/sexo
5. **Integração**: Vincule exames às consultas quando relevante

## Próximos Passos

1. Adicionar gráficos de tendência na UI
2. Implementar alertas automáticos para valores críticos
3. Criar integrações com sistemas de laboratório via API
4. Adicionar exportação de relatórios em PDF
5. Implementar comparação com populações de referência