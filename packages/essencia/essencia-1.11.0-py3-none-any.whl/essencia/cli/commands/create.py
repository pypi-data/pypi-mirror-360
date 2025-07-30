"""
Create command - Generate new components.
"""
from pathlib import Path
from typing import List, Optional

import typer
from rich import print
from rich.console import Console

from essencia.cli.templates import (
    MODEL_TEMPLATE,
    SERVICE_TEMPLATE,
    UI_COMPONENT_TEMPLATE,
    TEST_TEMPLATE,
)

app = typer.Typer(help="Create new components")
console = Console()


@app.command()
def model(
    name: str = typer.Argument(..., help="Model name (e.g., Patient)"),
    fields: Optional[List[str]] = typer.Option(
        None, "--field", "-f",
        help="Add fields in format 'name:type' (e.g., 'cpf:EncryptedCPF')"
    ),
    medical: bool = typer.Option(
        False, "--medical", "-m",
        help="Add medical-specific fields"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p",
        help="Custom path for the model file"
    )
):
    """Create a new model."""
    console.print(f"[bold green]Creating model:[/bold green] {name}")
    
    # Parse fields
    field_definitions = []
    if fields:
        for field in fields:
            if ":" in field:
                field_name, field_type = field.split(":", 1)
                field_definitions.append((field_name, field_type))
            else:
                field_definitions.append((field, "str"))
    
    # Add medical fields if requested
    if medical:
        medical_fields = [
            ("patient_id", "str"),
            ("doctor_id", "Optional[str]"),
            ("diagnosis", "Optional[EncryptedStr]"),
            ("notes", "Optional[EncryptedStr]"),
            ("created_at", "datetime"),
        ]
        field_definitions.extend(medical_fields)
    
    # Generate model code
    fields_code = []
    imports = ["from essencia.models import MongoModel", "from pydantic import Field"]
    
    # Check for special imports
    field_types = [f[1] for f in field_definitions]
    if any("Encrypted" in t for t in field_types):
        imports.append("from essencia.fields import EncryptedStr, EncryptedCPF, EncryptedFloat")
    if any("Optional" in t for t in field_types):
        imports.append("from typing import Optional")
    if any("datetime" in t for t in field_types):
        imports.append("from datetime import datetime")
    if any("List" in t or "list" in t for t in field_types):
        imports.append("from typing import List")
    
    for field_name, field_type in field_definitions:
        if field_type == "str":
            fields_code.append(f'    {field_name}: str = Field(..., description="{field_name.replace("_", " ").title()}")')
        elif "Optional" in field_type:
            fields_code.append(f'    {field_name}: {field_type} = Field(None, description="{field_name.replace("_", " ").title()}")')
        else:
            fields_code.append(f'    {field_name}: {field_type}')
    
    # Generate model
    model_code = MODEL_TEMPLATE.format(
        name=name,
        imports="\n".join(imports),
        fields="\n".join(fields_code) if fields_code else "    pass",
        collection_name=name.lower() + "s"
    )
    
    # Determine output path
    if path:
        output_path = path
    else:
        # Try to find models directory
        cwd = Path.cwd()
        if (cwd / "src").exists():
            # Look for project package
            for item in (cwd / "src").iterdir():
                if item.is_dir() and (item / "models").exists():
                    output_path = item / "models" / f"{name.lower()}.py"
                    break
            else:
                output_path = cwd / f"{name.lower()}.py"
        else:
            output_path = cwd / f"{name.lower()}.py"
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(model_code)
    
    console.print(f"✅ Created model at: {output_path}")
    
    # Create test file
    test_path = output_path.parent.parent.parent / "tests" / "unit" / f"test_{name.lower()}.py"
    if test_path.parent.exists():
        test_code = TEST_TEMPLATE.format(
            name=name,
            module_path=f"{output_path.parent.parent.name}.models.{name.lower()}"
        )
        test_path.write_text(test_code)
        console.print(f"✅ Created test at: {test_path}")


@app.command()
def service(
    name: str = typer.Argument(..., help="Service name (e.g., PatientService)"),
    model: str = typer.Option(
        None, "--model", "-m",
        help="Associated model name"
    ),
    with_repository: bool = typer.Option(
        True, "--with-repository/--no-repository",
        help="Include repository pattern"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p",
        help="Custom path for the service file"
    )
):
    """Create a new service."""
    console.print(f"[bold green]Creating service:[/bold green] {name}")
    
    # Ensure name ends with Service
    if not name.endswith("Service"):
        name = name + "Service"
    
    # Determine model name
    if not model:
        # Try to infer from service name
        model = name.replace("Service", "")
    
    # Generate service code
    service_code = SERVICE_TEMPLATE.format(
        name=name,
        model=model,
        model_lower=model.lower(),
        with_repository="yes" if with_repository else "no"
    )
    
    # Determine output path
    if path:
        output_path = path
    else:
        # Try to find services directory
        cwd = Path.cwd()
        if (cwd / "src").exists():
            for item in (cwd / "src").iterdir():
                if item.is_dir() and (item / "services").exists():
                    output_path = item / "services" / f"{name.lower()}.py"
                    break
            else:
                output_path = cwd / f"{name.lower()}.py"
        else:
            output_path = cwd / f"{name.lower()}.py"
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(service_code)
    
    console.print(f"✅ Created service at: {output_path}")


@app.command()
def ui(
    name: str = typer.Argument(..., help="Component name (e.g., PatientForm)"),
    component_type: str = typer.Option(
        "form", "--type", "-t",
        help="Component type (form, list, card, chart)"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p",
        help="Custom path for the component file"
    )
):
    """Create a new UI component."""
    console.print(f"[bold green]Creating UI component:[/bold green] {name}")
    
    # Generate component code
    component_code = UI_COMPONENT_TEMPLATE.format(
        name=name,
        component_type=component_type
    )
    
    # Determine output path
    if path:
        output_path = path
    else:
        # Try to find ui directory
        cwd = Path.cwd()
        if (cwd / "src").exists():
            for item in (cwd / "src").iterdir():
                if item.is_dir() and (item / "ui").exists():
                    output_path = item / "ui" / f"{name.lower()}.py"
                    break
            else:
                output_path = cwd / f"{name.lower()}.py"
        else:
            output_path = cwd / f"{name.lower()}.py"
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(component_code)
    
    console.print(f"✅ Created UI component at: {output_path}")


@app.command()
def assessment(
    name: str = typer.Argument(..., help="Assessment name (e.g., BDI, DASS21)"),
    questions: int = typer.Option(
        10, "--questions", "-q",
        help="Number of questions"
    ),
    scale: str = typer.Option(
        "0-3", "--scale", "-s",
        help="Response scale (e.g., '0-3', '0-4', '1-5')"
    )
):
    """Create a new mental health assessment."""
    console.print(f"[bold green]Creating assessment:[/bold green] {name}")
    
    # Parse scale
    scale_parts = scale.split("-")
    min_value = int(scale_parts[0])
    max_value = int(scale_parts[1])
    
    # Generate assessment code
    assessment_code = f'''"""
{name} Assessment Implementation.
"""
from typing import List
from essencia.models.mental_health import (
    AssessmentQuestion,
    MentalHealthAssessment,
    AssessmentType,
    SeverityLevel,
)
from pydantic import Field


class {name}Assessment(MentalHealthAssessment):
    """{name} Assessment."""
    
    assessment_type: AssessmentType = Field(AssessmentType.{name.upper()}, const=True)
    
    @classmethod
    def get_questions(cls) -> List[AssessmentQuestion]:
        """Get {name} questions."""
        questions = []
        
        # TODO: Add actual questions
        for i in range(1, {questions + 1}):
            questions.append(
                AssessmentQuestion(
                    question_id=f"{name.lower()}_{i}",
                    text=f"Question {i}",
                    text_pt=f"Pergunta {i}",
                    options=[
                        {{"value": v, "label": f"Option {v}", "label_pt": f"Opção {v}"}}
                        for v in range({min_value}, {max_value + 1})
                    ]
                )
            )
        
        return questions
    
    @staticmethod
    def calculate_severity(total_score: int) -> SeverityLevel:
        """Calculate {name} severity level."""
        # TODO: Implement proper severity calculation
        max_score = {questions * max_value}
        percentage = (total_score / max_score) * 100
        
        if percentage <= 20:
            return SeverityLevel.MINIMAL
        elif percentage <= 40:
            return SeverityLevel.MILD
        elif percentage <= 60:
            return SeverityLevel.MODERATE
        elif percentage <= 80:
            return SeverityLevel.MODERATELY_SEVERE
        else:
            return SeverityLevel.SEVERE
'''
    
    # Write file
    output_path = Path.cwd() / f"{name.lower()}_assessment.py"
    output_path.write_text(assessment_code)
    
    console.print(f"✅ Created assessment at: {output_path}")
    console.print(f"\n[yellow]Don't forget to:[/yellow]")
    console.print(f"1. Add AssessmentType.{name.upper()} to the AssessmentType enum")
    console.print(f"2. Register the assessment in AssessmentService.ASSESSMENT_REGISTRY")
    console.print(f"3. Add the actual questions and scoring logic")