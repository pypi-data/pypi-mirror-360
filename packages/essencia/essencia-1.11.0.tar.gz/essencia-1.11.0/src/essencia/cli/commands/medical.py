"""
Medical command - Medical domain tools.
"""
from datetime import datetime
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from essencia.medical import (
    calculate_bmi,
    calculate_bsa,
    calculate_gfr,
    categorize_bmi,
)

app = typer.Typer(help="Medical domain tools")
console = Console()


@app.command()
def calculate(
    calc_type: str = typer.Argument(
        ...,
        help="Calculation type (bmi, bsa, gfr, dosage)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i",
        help="Interactive mode"
    )
):
    """Perform medical calculations."""
    if calc_type == "bmi":
        if interactive:
            weight = typer.prompt("Weight (kg)")
            height = typer.prompt("Height (cm)")
        else:
            weight = typer.prompt("Weight (kg)")
            height = typer.prompt("Height (cm)")
        
        weight = float(weight)
        height = float(height)
        
        bmi = calculate_bmi(weight, height)
        category = categorize_bmi(bmi)
        
        console.print(f"\n[bold green]BMI Calculation Results:[/bold green]")
        console.print(f"Weight: {weight} kg")
        console.print(f"Height: {height} cm")
        console.print(f"BMI: [bold]{bmi:.1f}[/bold]")
        console.print(f"Category: [yellow]{category}[/yellow]")
        
        # Show BMI ranges
        console.print("\n[dim]BMI Categories:[/dim]")
        console.print("[dim]< 16.0: Muito abaixo do peso[/dim]")
        console.print("[dim]16.0-18.4: Abaixo do peso[/dim]")
        console.print("[dim]18.5-24.9: Peso normal[/dim]")
        console.print("[dim]25.0-29.9: Sobrepeso[/dim]")
        console.print("[dim]30.0-34.9: Obesidade grau I[/dim]")
        console.print("[dim]35.0-39.9: Obesidade grau II[/dim]")
        console.print("[dim]≥ 40.0: Obesidade grau III[/dim]")
    
    elif calc_type == "bsa":
        weight = float(typer.prompt("Weight (kg)"))
        height = float(typer.prompt("Height (cm)"))
        method = typer.prompt("Method (dubois/mosteller/boyd)", default="dubois")
        
        bsa = calculate_bsa(weight, height, method)
        
        console.print(f"\n[bold green]BSA Calculation Results:[/bold green]")
        console.print(f"Weight: {weight} kg")
        console.print(f"Height: {height} cm")
        console.print(f"Method: {method}")
        console.print(f"BSA: [bold]{bsa:.2f} m²[/bold]")
    
    elif calc_type == "gfr":
        creatinine = float(typer.prompt("Creatinine (mg/dL)"))
        age = int(typer.prompt("Age (years)"))
        gender = typer.prompt("Gender (M/F)")
        race = typer.prompt("Race (black/other)", default="other")
        weight = float(typer.prompt("Weight (kg) - optional, press Enter to skip") or "0")
        
        gfr = calculate_gfr(creatinine, age, gender, race)
        
        console.print(f"\n[bold green]GFR Calculation Results:[/bold green]")
        console.print(f"Creatinine: {creatinine} mg/dL")
        console.print(f"Age: {age} years")
        console.print(f"Gender: {gender}")
        console.print(f"Race: {race}")
        console.print(f"eGFR: [bold]{gfr:.1f} mL/min/1.73m²[/bold]")
        
        # CKD stages
        console.print("\n[dim]CKD Stages:[/dim]")
        if gfr >= 90:
            stage = "G1 - Normal or high"
        elif gfr >= 60:
            stage = "G2 - Mildly decreased"
        elif gfr >= 45:
            stage = "G3a - Moderately decreased"
        elif gfr >= 30:
            stage = "G3b - Moderately decreased"
        elif gfr >= 15:
            stage = "G4 - Severely decreased"
        else:
            stage = "G5 - Kidney failure"
        
        console.print(f"Stage: [yellow]{stage}[/yellow]")
    
    elif calc_type == "dosage":
        console.print("[yellow]Dosage calculator coming soon![/yellow]")
    
    else:
        console.print(f"[red]Unknown calculation type: {calc_type}[/red]")
        console.print("Available types: bmi, bsa, gfr, dosage")


@app.command()
def assessment(
    assessment_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Assessment type (PHQ9, GAD7, etc.)"
    ),
    list_types: bool = typer.Option(
        False, "--list", "-l",
        help="List available assessments"
    )
):
    """Mental health assessment tools."""
    if list_types:
        table = Table(title="Available Mental Health Assessments")
        table.add_column("Code", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Purpose")
        table.add_column("Questions")
        
        assessments = [
            ("PHQ-9", "Patient Health Questionnaire-9", "Depression screening", "9"),
            ("GAD-7", "Generalized Anxiety Disorder-7", "Anxiety screening", "7"),
            ("SNAP-IV", "SNAP-IV Rating Scale", "ADHD screening (children)", "18"),
            ("MDQ", "Mood Disorder Questionnaire", "Bipolar disorder screening", "13"),
            ("ASRS", "Adult ADHD Self-Report Scale", "Adult ADHD screening", "18"),
            ("PCL-5", "PTSD Checklist for DSM-5", "PTSD screening", "20"),
            ("AUDIT", "Alcohol Use Disorders Test", "Alcohol use screening", "10"),
            ("ISI", "Insomnia Severity Index", "Sleep disorder screening", "7"),
        ]
        
        for code, name, purpose, questions in assessments:
            table.add_row(code, name, purpose, questions)
        
        console.print(table)
    
    elif assessment_type:
        if assessment_type.upper() == "PHQ9":
            console.print("[bold green]PHQ-9 Depression Screening[/bold green]\n")
            console.print("Over the last 2 weeks, how often have you been bothered by:")
            console.print("0 = Not at all")
            console.print("1 = Several days")
            console.print("2 = More than half the days")
            console.print("3 = Nearly every day\n")
            
            questions = [
                "Little interest or pleasure in doing things",
                "Feeling down, depressed, or hopeless",
                "Trouble falling or staying asleep, or sleeping too much",
                "Feeling tired or having little energy",
                "Poor appetite or overeating",
                "Feeling bad about yourself",
                "Trouble concentrating on things",
                "Moving or speaking slowly or being fidgety",
                "Thoughts that you would be better off dead"
            ]
            
            total = 0
            for i, q in enumerate(questions, 1):
                score = int(typer.prompt(f"{i}. {q} (0-3)"))
                total += score
            
            console.print(f"\n[bold]Total Score: {total}/27[/bold]")
            
            if total <= 4:
                severity = "Minimal depression"
            elif total <= 9:
                severity = "Mild depression"
            elif total <= 14:
                severity = "Moderate depression"
            elif total <= 19:
                severity = "Moderately severe depression"
            else:
                severity = "Severe depression"
            
            console.print(f"Severity: [yellow]{severity}[/yellow]")
            
            if total >= 10:
                console.print("\n[red]⚠️  Clinical intervention recommended[/red]")
        else:
            console.print(f"[red]Assessment '{assessment_type}' not implemented yet[/red]")
    else:
        console.print("Use --list to see available assessments or --type to run one")


@app.command()
def icd(
    search: Optional[str] = typer.Argument(
        None,
        help="Search term for ICD codes"
    ),
    code: Optional[str] = typer.Option(
        None, "--code", "-c",
        help="Look up specific ICD code"
    )
):
    """ICD code lookup and search."""
    # Sample ICD codes for demonstration
    icd_codes = {
        "F32.9": ("Major depressive disorder, single episode, unspecified", "Mental"),
        "F41.1": ("Generalized anxiety disorder", "Mental"),
        "F90.0": ("ADHD, predominantly inattentive type", "Mental"),
        "I10": ("Essential (primary) hypertension", "Circulatory"),
        "E11.9": ("Type 2 diabetes mellitus without complications", "Endocrine"),
        "J45.909": ("Unspecified asthma, uncomplicated", "Respiratory"),
        "M79.3": ("Myalgia", "Musculoskeletal"),
        "R50.9": ("Fever, unspecified", "Symptoms"),
    }
    
    if code:
        if code.upper() in icd_codes:
            desc, category = icd_codes[code.upper()]
            console.print(f"\n[bold cyan]ICD Code: {code.upper()}[/bold cyan]")
            console.print(f"Description: {desc}")
            console.print(f"Category: {category}")
        else:
            console.print(f"[red]ICD code '{code}' not found[/red]")
    
    elif search:
        console.print(f"[bold green]Searching for: '{search}'[/bold green]\n")
        
        results = []
        for icd_code, (desc, category) in icd_codes.items():
            if search.lower() in desc.lower():
                results.append((icd_code, desc, category))
        
        if results:
            table = Table()
            table.add_column("ICD Code", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Category")
            
            for code, desc, cat in results:
                table.add_row(code, desc, cat)
            
            console.print(table)
        else:
            console.print(f"[yellow]No ICD codes found matching '{search}'[/yellow]")
    
    else:
        console.print("Provide a search term or use --code to look up a specific code")


@app.command()
def drug_interaction(
    medications: str = typer.Argument(
        ...,
        help="Comma-separated list of medications"
    )
):
    """Check drug interactions."""
    from essencia.medical.drug_interactions import DrugInteractionChecker
    
    med_list = [med.strip() for med in medications.split(",")]
    
    console.print(f"[bold green]Checking interactions for:[/bold green]")
    for med in med_list:
        console.print(f"  • {med}")
    
    checker = DrugInteractionChecker()
    interactions = checker.check_multiple_interactions(med_list)
    
    if interactions:
        console.print(f"\n[bold red]⚠️  {len(interactions)} interaction(s) found![/bold red]\n")
        
        for drug1, drug2, interaction in interactions:
            severity_color = {
                "minor": "yellow",
                "moderate": "orange3",
                "major": "red",
                "contraindicated": "red bold"
            }.get(interaction.severity.value, "white")
            
            console.print(f"[{severity_color}]{drug1} + {drug2}[/{severity_color}]")
            console.print(f"Severity: [{severity_color}]{interaction.severity.value.upper()}[/{severity_color}]")
            console.print(f"Description: {interaction.description}")
            console.print(f"Management: {interaction.management}")
            console.print()
    else:
        console.print("\n[green]✅ No interactions found[/green]")


@app.command()
def validate_cpf(
    cpf: str = typer.Argument(..., help="CPF to validate")
):
    """Validate Brazilian CPF."""
    from essencia.utils.validators import validate_cpf, format_cpf
    
    is_valid = validate_cpf(cpf)
    
    if is_valid:
        formatted = format_cpf(cpf)
        console.print(f"[green]✅ Valid CPF: {formatted}[/green]")
    else:
        console.print(f"[red]❌ Invalid CPF: {cpf}[/red]")
        
        # Show correct format
        console.print("\n[yellow]CPF format: XXX.XXX.XXX-XX[/yellow]")
        console.print("[yellow]Example: 123.456.789-00[/yellow]")