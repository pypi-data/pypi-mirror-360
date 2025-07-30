# Quick Start Guide

Get up and running with Essencia in just 5 minutes! This guide will walk you through creating your first medical application.

## Prerequisites

- Python 3.12 or higher
- MongoDB installed and running
- Basic knowledge of Python

## Installation

```bash
# Install essencia with all dependencies
pip install essencia[all]

# Or use uv (recommended)
uv pip install essencia[all]
```

## Create Your First Application

### 1. Set Up Environment

Create a `.env` file in your project root:

```env
# MongoDB connection
MONGODB_URL=mongodb://localhost:27017/essencia_quickstart

# Encryption key (generate with: essencia security generate-key)
ESSENCIA_ENCRYPTION_KEY=your-base64-encoded-key-here

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

### 2. Create a Simple Patient Management App

```python
# app.py
import flet as ft
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedStr
from essencia.ui.inputs import ThemedTextField
from essencia.ui.buttons import PrimaryButton
from essencia.ui.layout import Dashboard
from datetime import date, datetime

# Define Patient model
class Patient(MongoModel):
    name: str
    cpf: EncryptedCPF
    birth_date: date
    phone: str
    email: str
    medical_history: EncryptedStr = ""
    
    class Settings:
        collection_name = "patients"

# Create the Flet app
def main(page: ft.Page):
    page.title = "Essencia Quick Start - Patient Management"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Apply Essencia security
    from essencia.integrations.flet import apply_security_to_page
    apply_security_to_page(page)
    
    # Patient list
    patient_list = ft.ListView(expand=True, spacing=10)
    
    # Form fields
    name_field = ThemedTextField(label="Nome Completo")
    cpf_field = ThemedTextField(label="CPF", hint_text="000.000.000-00")
    birth_field = ThemedTextField(label="Data de Nascimento", hint_text="DD/MM/AAAA")
    phone_field = ThemedTextField(label="Telefone", hint_text="(00) 00000-0000")
    email_field = ThemedTextField(label="Email")
    
    async def load_patients():
        """Load patients from database."""
        patients = await Patient.find_many()
        patient_list.controls.clear()
        
        for patient in patients:
            patient_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(patient.name, size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"CPF: {patient.cpf.get_secret_value()[:3]}..."),
                            ft.Text(f"Nascimento: {patient.birth_date.strftime('%d/%m/%Y')}"),
                            ft.Row([
                                ft.Icon(ft.icons.PHONE, size=16),
                                ft.Text(patient.phone),
                                ft.Icon(ft.icons.EMAIL, size=16),
                                ft.Text(patient.email)
                            ])
                        ]),
                        padding=10
                    )
                )
            )
        
        page.update()
    
    async def save_patient(e):
        """Save new patient."""
        try:
            # Parse birth date
            birth_parts = birth_field.value.split("/")
            birth_date = date(
                int(birth_parts[2]),
                int(birth_parts[1]),
                int(birth_parts[0])
            )
            
            # Create patient
            patient = Patient(
                name=name_field.value,
                cpf=cpf_field.value,
                birth_date=birth_date,
                phone=phone_field.value,
                email=email_field.value
            )
            
            await patient.save()
            
            # Clear form
            name_field.value = ""
            cpf_field.value = ""
            birth_field.value = ""
            phone_field.value = ""
            email_field.value = ""
            
            # Reload list
            await load_patients()
            
            # Show success
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Paciente cadastrado com sucesso!"),
                    bgcolor=ft.colors.GREEN
                )
            )
            
        except Exception as ex:
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Erro: {str(ex)}"),
                    bgcolor=ft.colors.RED
                )
            )
    
    # Create dashboard
    dashboard = Dashboard(
        title="Gestão de Pacientes",
        body=ft.Row([
            # Form column
            ft.Container(
                content=ft.Column([
                    ft.Text("Novo Paciente", size=20, weight=ft.FontWeight.BOLD),
                    name_field,
                    cpf_field,
                    birth_field,
                    phone_field,
                    email_field,
                    PrimaryButton(
                        text="Salvar Paciente",
                        on_click=save_patient,
                        icon=ft.icons.SAVE
                    )
                ], spacing=10),
                padding=20,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10,
                width=400
            ),
            # Patient list column
            ft.Container(
                content=ft.Column([
                    ft.Text("Pacientes Cadastrados", size=20, weight=ft.FontWeight.BOLD),
                    patient_list
                ]),
                padding=20,
                expand=True
            )
        ])
    )
    
    page.add(dashboard)
    
    # Load initial data
    page.run_task(load_patients)

# Run the app
if __name__ == "__main__":
    ft.app(target=main)
```

### 3. Run Your Application

```bash
# Generate encryption key
essencia security generate-key

# Run the app
python app.py
```

## Adding More Features

### Vital Signs Recording

```python
from essencia.models.vital_signs import BloodPressure, Temperature

# Record vital signs
async def record_vitals(patient_id: str):
    bp = BloodPressure(
        patient_id=patient_id,
        systolic=120,
        diastolic=80,
        pulse=72
    )
    await bp.save()
    
    # Automatic categorization
    category = bp.categorize()  # Returns "Normal", "Elevated", etc.
```

### Medication Management

```python
from essencia.models.medication import Medication, MedicationSchedule

# Create medication
medication = Medication(
    patient_id=patient_id,
    name="Losartana",
    dosage="50mg",
    frequency="1x ao dia",
    start_date=date.today()
)
await medication.save()

# Generate schedule
schedule = medication.get_daily_schedule()
```

### Mental Health Assessment

```python
from essencia.models.mental_health import PHQ9Assessment

# Create PHQ-9 assessment
assessment = PHQ9Assessment(
    patient_id=patient_id,
    responses=[2, 1, 0, 1, 2, 0, 1, 0, 0]  # 0-3 scale
)
await assessment.save()

# Get interpretation
result = assessment.get_clinical_interpretation()
print(f"Score: {result['total_score']}, Severity: {result['severity']}")
```

## Using the CLI

Essencia comes with a powerful CLI for common tasks:

```bash
# Check system health
essencia doctor

# Create a new model
essencia create model Consultation

# Generate a service
essencia create service ConsultationService

# Run tests
essencia test run

# Database operations
essencia db list-collections
essencia db create-indexes
```

## API Development

Create a REST API with automatic OpenAPI documentation:

```python
# api.py
from fastapi import FastAPI
from essencia.api import create_app, setup_metrics_endpoint

# Create app with all features
app = create_app()

# Your endpoints are automatically documented at /docs
```

Run with:
```bash
uvicorn api:app --reload
```

## Brazilian Features

Essencia includes comprehensive Brazilian support:

```python
from essencia.utils.brazilian_validators import (
    CPFGenerator, validate_cpf,
    CEPValidator, PhoneValidator
)

# Generate valid CPF
cpf = CPFGenerator.generate(formatted=True, state="SP")

# Validate and lookup CEP
address = await CEPValidator.lookup_address("01310-100")
print(f"Street: {address['street']}, City: {address['city']}")

# ANVISA medication lookup
from essencia.integrations.anvisa import AnvisaIntegration
medications = await AnvisaIntegration.search_medication("dipirona")
```

## Monitoring

Essencia includes built-in monitoring:

```python
# Access metrics at /metrics (Prometheus format)
# Access health checks at /health

# Custom metrics
from essencia.monitoring import track_business_metric
track_business_metric("appointment_created", {"type": "consultation"})
```

## Next Steps

1. **Explore the Examples**: Check out `/examples` for complete applications
2. **Read the Guides**: Deep dive into specific topics in our guides
3. **Join the Community**: Report issues and contribute on GitHub
4. **Deploy to Production**: See our deployment guide for best practices

## Getting Help

- **Documentation**: Full docs at `/docs`
- **CLI Help**: Run `essencia --help`
- **Examples**: See `/examples` directory
- **Issues**: [GitHub Issues](https://github.com/arantesdv/essencia/issues)

Happy coding with Essencia! 🚀