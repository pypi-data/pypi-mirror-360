"""
Essencia Doctor - Health check for your application.
"""
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def run_doctor():
    """Run the Essencia doctor health checks."""
    console.print("\n[bold cyan]🩺 Essencia Doctor[/bold cyan]")
    console.print("Checking your application health...\n")
    
    checks = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 12):
        checks.append(("Python Version", f"✅ {python_version.major}.{python_version.minor}.{python_version.micro}", "green"))
    else:
        checks.append(("Python Version", f"❌ {python_version.major}.{python_version.minor}.{python_version.micro} (Need 3.12+)", "red"))
    
    # Check essencia installation
    try:
        import essencia
        checks.append(("Essencia", f"✅ Installed (v{essencia.__version__})", "green"))
    except ImportError:
        checks.append(("Essencia", "❌ Not installed", "red"))
    
    # Check environment file
    env_file = Path(".env")
    if env_file.exists():
        checks.append(("Environment File", "✅ Found", "green"))
        
        # Check critical environment variables
        env_content = env_file.read_text()
        if "ESSENCIA_ENCRYPTION_KEY=" in env_content:
            checks.append(("Encryption Key", "✅ Configured", "green"))
        else:
            checks.append(("Encryption Key", "⚠️  Not configured", "yellow"))
        
        if "MONGODB_URL=" in env_content:
            checks.append(("MongoDB URL", "✅ Configured", "green"))
        else:
            checks.append(("MongoDB URL", "⚠️  Not configured", "yellow"))
    else:
        checks.append(("Environment File", "❌ Not found", "red"))
    
    # Check project structure
    expected_dirs = ["src", "tests", "docs"]
    missing_dirs = []
    for dir_name in expected_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if not missing_dirs:
        checks.append(("Project Structure", "✅ Complete", "green"))
    else:
        checks.append(("Project Structure", f"⚠️  Missing: {', '.join(missing_dirs)}", "yellow"))
    
    # Check dependencies
    try:
        import motor
        checks.append(("Motor (MongoDB)", "✅ Installed", "green"))
    except ImportError:
        checks.append(("Motor (MongoDB)", "❌ Not installed", "red"))
    
    try:
        import flet
        checks.append(("Flet (UI)", "✅ Installed", "green"))
    except ImportError:
        checks.append(("Flet (UI)", "❌ Not installed", "red"))
    
    try:
        import pytest
        checks.append(("Pytest", "✅ Installed", "green"))
    except ImportError:
        checks.append(("Pytest", "⚠️  Not installed (needed for testing)", "yellow"))
    
    # Check MongoDB connection
    mongodb_url = os.getenv("MONGODB_URL")
    if mongodb_url:
        try:
            from essencia.database import Database
            db = Database(mongodb_url)
            db.client.server_info()  # This will raise an exception if can't connect
            checks.append(("MongoDB Connection", "✅ Connected", "green"))
        except Exception as e:
            checks.append(("MongoDB Connection", f"❌ Failed: {str(e)[:50]}...", "red"))
    else:
        checks.append(("MongoDB Connection", "⚠️  No URL configured", "yellow"))
    
    # Display results
    table = Table(show_header=False, box=None)
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="left")
    
    for check, status, color in checks:
        table.add_row(check, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    # Overall health
    errors = sum(1 for _, _, color in checks if color == "red")
    warnings = sum(1 for _, _, color in checks if color == "yellow")
    
    console.print("\n" + "─" * 50 + "\n")
    
    if errors == 0 and warnings == 0:
        console.print("[bold green]✅ All systems operational![/bold green]")
        console.print("\nYour Essencia application is healthy! 🎉")
    elif errors == 0:
        console.print(f"[bold yellow]⚠️  {warnings} warning(s) found[/bold yellow]")
        console.print("\nYour application is functional but could be improved.")
        console.print("\nRecommendations:")
        
        if "Encryption Key" in [c[0] for c in checks if c[2] == "yellow"]:
            console.print("• Run 'essencia security generate-key' to create an encryption key")
        
        if "MongoDB URL" in [c[0] for c in checks if c[2] == "yellow"]:
            console.print("• Configure MongoDB connection in .env file")
        
        if "Pytest" in [c[0] for c in checks if c[2] == "yellow"]:
            console.print("• Install pytest: pip install pytest pytest-asyncio")
    else:
        console.print(f"[bold red]❌ {errors} error(s) found[/bold red]")
        console.print("\nYour application needs attention before it can run properly.")
        console.print("\nCritical issues to fix:")
        
        for check, status, color in checks:
            if color == "red":
                console.print(f"• {check}: {status}")
    
    # Quick tips
    console.print("\n[bold cyan]Quick Tips:[/bold cyan]")
    console.print("• Create a model: essencia create model Patient")
    console.print("• Generate migration: essencia generate migration 'Add patient fields'")
    console.print("• Run tests: essencia test run")
    console.print("• Check security: essencia security check-config")
    
    # Show next steps based on health
    if errors > 0:
        console.print("\n[yellow]Run 'essencia init' to set up a new project[/yellow]")
    elif warnings > 0:
        console.print("\n[yellow]Address the warnings above for optimal performance[/yellow]")
    else:
        console.print("\n[green]You're ready to build amazing medical applications! 🚀[/green]")


if __name__ == "__main__":
    run_doctor()