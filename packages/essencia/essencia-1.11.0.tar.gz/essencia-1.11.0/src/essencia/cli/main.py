"""
Main CLI application for Essencia framework.
"""
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from essencia import __version__
from essencia.cli.commands import (
    create,
    generate,
    db,
    test,
    security,
    medical,
)

# Initialize Typer app
app = typer.Typer(
    name="essencia",
    help="Essencia Framework CLI - Tools for building secure medical applications",
    add_completion=True,
    rich_markup_mode="rich"
)

# Initialize Rich console
console = Console()

# Add command groups
app.add_typer(create.app, name="create", help="Create new components")
app.add_typer(generate.app, name="generate", help="Generate code from templates")
app.add_typer(db.app, name="db", help="Database operations")
app.add_typer(test.app, name="test", help="Testing utilities")
app.add_typer(security.app, name="security", help="Security tools")
app.add_typer(medical.app, name="medical", help="Medical domain tools")


@app.callback()
def callback():
    """
    Essencia Framework CLI
    
    A comprehensive toolkit for building secure medical and business applications.
    """
    pass


@app.command()
def version():
    """Show the Essencia version."""
    print(f"[bold green]Essencia[/bold green] version [cyan]{__version__}[/cyan]")


@app.command()
def info():
    """Display information about the Essencia framework."""
    panel = Panel.fit(
        f"""[bold green]Essencia Framework[/bold green] v{__version__}
        
[yellow]A comprehensive Python framework for building secure medical applications[/yellow]

[bold]Features:[/bold]
• 🔒 Field-level encryption for sensitive data
• 🏥 Medical domain models and calculations
• 💊 Medication management system
• 🧠 Mental health assessment tools
• 📊 Vital signs tracking and analysis
• 🎨 Beautiful Flet UI components
• 🇧🇷 Brazilian market focus with full localization
• ✅ Comprehensive test infrastructure

[bold]Documentation:[/bold] https://github.com/arantesdv/essencia
[bold]Issues:[/bold] https://github.com/arantesdv/essencia/issues""",
        title="Essencia Framework",
        border_style="green"
    )
    console.print(panel)


@app.command()
def init(
    path: Path = typer.Argument(
        Path.cwd(),
        help="Path to initialize Essencia project"
    ),
    name: str = typer.Option(
        None,
        "--name", "-n",
        help="Project name"
    ),
    with_examples: bool = typer.Option(
        False,
        "--with-examples", "-e",
        help="Include example code"
    )
):
    """Initialize a new Essencia project."""
    console.print(f"[bold green]Initializing Essencia project at:[/bold green] {path}")
    
    # Create project structure
    project_name = name or path.name
    
    # Create directories
    directories = [
        "src",
        f"src/{project_name}",
        f"src/{project_name}/models",
        f"src/{project_name}/services",
        f"src/{project_name}/ui",
        f"src/{project_name}/api",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "scripts",
    ]
    
    for directory in directories:
        dir_path = path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Created: {directory}")
    
    # Create essential files
    # pyproject.toml
    pyproject_content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "A medical application built with Essencia"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "essencia>=1.10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    
    (path / "pyproject.toml").write_text(pyproject_content)
    console.print("✅ Created: pyproject.toml")
    
    # .env.example
    env_content = '''# Essencia Configuration
ESSENCIA_ENCRYPTION_KEY=your-base64-encoded-32-byte-key
MONGODB_URL=mongodb://localhost:27017/your_database
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO

# Security
SESSION_SECRET=your-session-secret
CORS_ORIGINS=http://localhost:3000

# Medical Settings
DEFAULT_LANGUAGE=pt
TIMEZONE=America/Sao_Paulo
'''
    
    (path / ".env.example").write_text(env_content)
    console.print("✅ Created: .env.example")
    
    # README.md
    readme_content = f'''# {project_name}

A medical application built with the Essencia framework.

## Setup

1. Install dependencies:
```bash
uv pip install -e .
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Generate encryption key:
```bash
essencia security generate-key
```

4. Run tests:
```bash
pytest
```

## Development

- Create a new model: `essencia create model Patient`
- Generate migration: `essencia db migrate`
- Run development server: `python -m {project_name}`

## Documentation

Built with [Essencia](https://github.com/arantesdv/essencia) - A comprehensive framework for secure medical applications.
'''
    
    (path / "README.md").write_text(readme_content)
    console.print("✅ Created: README.md")
    
    # Create main __init__.py
    init_content = f'''"""
{project_name} - Medical application built with Essencia.
"""

__version__ = "0.1.0"
'''
    
    (path / f"src/{project_name}/__init__.py").write_text(init_content)
    console.print(f"✅ Created: src/{project_name}/__init__.py")
    
    # Create example files if requested
    if with_examples:
        # Example model
        model_content = '''"""
Example patient model.
"""
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedStr
from pydantic import Field
from datetime import datetime


class Patient(MongoModel):
    """Patient model with encrypted sensitive data."""
    
    name: str = Field(..., description="Patient full name")
    cpf: EncryptedCPF = Field(..., description="Brazilian CPF")
    birth_date: datetime = Field(..., description="Date of birth")
    medical_record_number: str = Field(..., description="Medical record number")
    
    # Encrypted sensitive data
    phone: EncryptedStr = Field(None, description="Contact phone")
    email: EncryptedStr = Field(None, description="Email address")
    
    # Medical information
    blood_type: str = Field(None, description="Blood type")
    allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)
    
    class Settings:
        collection_name = "patients"
        indexes = [
            ("cpf", 1),
            ("medical_record_number", 1),
            ("name", "text"),
        ]
'''
        
        (path / f"src/{project_name}/models/patient.py").write_text(model_content)
        console.print("✅ Created: Example patient model")
        
        # Example service
        service_content = '''"""
Example patient service.
"""
from typing import List, Optional
from essencia.services import Repository, ServiceResult
from ..models.patient import Patient


class PatientRepository(Repository[Patient]):
    """Repository for patient data access."""
    
    model_class = Patient
    
    async def find_by_cpf(self, cpf: str) -> Optional[Patient]:
        """Find patient by CPF."""
        return await self.find_one({"cpf": cpf})
    
    async def search_by_name(self, name: str) -> List[Patient]:
        """Search patients by name."""
        return await self.find_many({
            "$text": {"$search": name}
        })


class PatientService:
    """Service for patient operations."""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def register_patient(self, patient_data: dict) -> ServiceResult[Patient]:
        """Register a new patient."""
        # Check if patient already exists
        existing = await self.repository.find_by_cpf(patient_data["cpf"])
        if existing:
            return ServiceResult.failure("Patient with this CPF already exists")
        
        # Create patient
        patient = Patient(**patient_data)
        saved = await self.repository.create(patient)
        
        return ServiceResult.success(saved)
'''
        
        (path / f"src/{project_name}/services/patient_service.py").write_text(service_content)
        console.print("✅ Created: Example patient service")
    
    # Summary
    console.print("\n[bold green]✨ Essencia project initialized successfully![/bold green]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print("1. cd " + str(path))
    console.print("2. uv pip install -e .")
    console.print("3. cp .env.example .env")
    console.print("4. essencia security generate-key")
    console.print("5. Start coding! 🚀")


@app.command()
def doctor():
    """Display the Essencia doctor for health checks."""
    from essencia.cli.doctor import run_doctor
    run_doctor()


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()