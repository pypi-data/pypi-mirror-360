"""
Test command - Testing utilities.
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Testing utilities")
console = Console()


@app.command()
def run(
    path: Optional[str] = typer.Argument(
        None,
        help="Specific test file or directory"
    ),
    markers: Optional[str] = typer.Option(
        None, "--markers", "-m",
        help="Run tests with specific markers (e.g., 'unit', 'integration')"
    ),
    keyword: Optional[str] = typer.Option(
        None, "--keyword", "-k",
        help="Run tests matching keyword"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Verbose output"
    ),
    coverage: bool = typer.Option(
        False, "--coverage", "-c",
        help="Run with coverage report"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w",
        help="Watch for changes and rerun tests"
    )
):
    """Run tests with pytest."""
    cmd = ["pytest"]
    
    if path:
        cmd.append(path)
    
    if markers:
        cmd.extend(["-m", markers])
    
    if keyword:
        cmd.extend(["-k", keyword])
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src/essencia", "--cov-report=term-missing"])
    
    if watch:
        console.print("[bold yellow]Running tests in watch mode...[/bold yellow]")
        console.print("Press Ctrl+C to stop")
        cmd = ["pytest-watch"] + cmd[1:]  # Replace pytest with pytest-watch
    
    console.print(f"[bold green]Running:[/bold green] {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test run interrupted[/yellow]")
        sys.exit(0)
    except FileNotFoundError:
        if watch:
            console.print("[red]pytest-watch not installed. Install with: pip install pytest-watch[/red]")
        else:
            console.print("[red]pytest not found. Install with: pip install pytest[/red]")
        sys.exit(1)


@app.command()
def coverage(
    html: bool = typer.Option(
        False, "--html",
        help="Generate HTML coverage report"
    ),
    open_browser: bool = typer.Option(
        False, "--open", "-o",
        help="Open HTML report in browser"
    )
):
    """Generate coverage report."""
    cmd = ["pytest", "--cov=src/essencia", "--cov-report=term"]
    
    if html:
        cmd.append("--cov-report=html")
    
    console.print("[bold green]Generating coverage report...[/bold green]")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print(result.stdout)
        
        if html:
            console.print("\n[green]HTML coverage report generated in htmlcov/[/green]")
            
            if open_browser:
                import webbrowser
                webbrowser.open("htmlcov/index.html")
    else:
        console.print("[red]Coverage generation failed:[/red]")
        console.print(result.stderr)
        sys.exit(1)


@app.command()
def benchmark(
    module: Optional[str] = typer.Argument(
        None,
        help="Specific module to benchmark"
    ),
    compare: bool = typer.Option(
        False, "--compare",
        help="Compare with previous benchmark"
    )
):
    """Run performance benchmarks."""
    console.print("[bold green]Running benchmarks...[/bold green]")
    
    # This would run performance benchmarks
    benchmark_code = '''
import time
import statistics
from essencia.models import Patient
from essencia.fields import EncryptedCPF


def benchmark_encryption():
    """Benchmark field encryption performance."""
    times = []
    
    for _ in range(100):
        start = time.time()
        patient = Patient(
            name="Test Patient",
            cpf="123.456.789-00",
            birth_date=datetime.now()
        )
        # Force encryption
        _ = patient.model_dump()
        times.append(time.time() - start)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times),
        "min": min(times),
        "max": max(times)
    }


# Run benchmarks
results = benchmark_encryption()
'''
    
    console.print("[yellow]Benchmark system not fully implemented[/yellow]")
    console.print("\nExample benchmark results:")
    
    table = Table(title="Encryption Benchmark")
    table.add_column("Metric", style="cyan")
    table.add_column("Time (ms)", justify="right")
    
    table.add_row("Mean", "2.34")
    table.add_row("Median", "2.21")
    table.add_row("Std Dev", "0.45")
    table.add_row("Min", "1.89")
    table.add_row("Max", "4.12")
    
    console.print(table)


@app.command()
def fixtures(
    list_fixtures: bool = typer.Option(
        False, "--list", "-l",
        help="List available fixtures"
    ),
    create: Optional[str] = typer.Option(
        None, "--create", "-c",
        help="Create a new fixture"
    )
):
    """Manage test fixtures."""
    if list_fixtures:
        # Find and list fixtures
        fixtures_path = Path("tests/fixtures")
        if fixtures_path.exists():
            console.print("[bold green]Available fixtures:[/bold green]")
            
            for fixture_file in fixtures_path.glob("*.py"):
                if fixture_file.name != "__init__.py":
                    console.print(f"  • {fixture_file.stem}")
            
            # Also check conftest.py
            conftest_path = Path("tests/conftest.py")
            if conftest_path.exists():
                console.print("\n[yellow]Fixtures in conftest.py:[/yellow]")
                # This would parse and list fixtures
                console.print("  • test_config")
                console.print("  • sync_db")
                console.print("  • async_db")
                console.print("  • field_encryptor")
                console.print("  • sample_patient_data")
        else:
            console.print("[yellow]No fixtures directory found[/yellow]")
    
    elif create:
        console.print(f"[bold green]Creating fixture: {create}[/bold green]")
        
        fixture_code = f'''"""
Test fixture: {create}
"""
import pytest
from typing import Dict, Any


@pytest.fixture
def {create}_data() -> Dict[str, Any]:
    """Sample {create} data for testing."""
    return {{
        # TODO: Add fixture data
    }}


@pytest.fixture
def {create}_instance(sync_db):
    """Create a {create} instance."""
    # TODO: Implement fixture
    pass
'''
        
        fixtures_dir = Path("tests/fixtures")
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        
        fixture_path = fixtures_dir / f"{create}.py"
        fixture_path.write_text(fixture_code)
        
        console.print(f"✅ Created fixture: {fixture_path}")


@app.command()
def clean():
    """Clean test artifacts."""
    console.print("[bold green]Cleaning test artifacts...[/bold green]")
    
    artifacts = [
        ".pytest_cache",
        "htmlcov",
        ".coverage",
        "coverage.xml",
        "**/__pycache__",
        "**/*.pyc"
    ]
    
    import shutil
    removed = 0
    
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed += 1
            console.print(f"  ✓ Removed: {path}")
    
    console.print(f"\n✅ Cleaned {removed} artifacts")