"""
Security command - Security tools and utilities.
"""
import base64
import secrets
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from essencia.security.encryption import FieldEncryptor

app = typer.Typer(help="Security tools")
console = Console()


@app.command()
def generate_key(
    save_to_env: bool = typer.Option(
        True, "--save/--no-save",
        help="Save to .env file"
    ),
    env_file: Path = typer.Option(
        ".env", "--env-file", "-e",
        help="Environment file path"
    )
):
    """Generate a new encryption key."""
    key = FieldEncryptor.generate_key()
    
    console.print("[bold green]Generated encryption key:[/bold green]")
    console.print(f"\n[yellow]ESSENCIA_ENCRYPTION_KEY={key}[/yellow]\n")
    
    if save_to_env:
        if env_file.exists():
            # Read existing content
            content = env_file.read_text()
            
            # Check if key already exists
            if "ESSENCIA_ENCRYPTION_KEY=" in content:
                console.print("[yellow]⚠️  ESSENCIA_ENCRYPTION_KEY already exists in .env[/yellow]")
                
                if typer.confirm("Do you want to replace it?"):
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith("ESSENCIA_ENCRYPTION_KEY="):
                            lines[i] = f"ESSENCIA_ENCRYPTION_KEY={key}"
                            break
                    env_file.write_text("\n".join(lines))
                    console.print("[green]✅ Updated encryption key in .env[/green]")
            else:
                # Append key
                with open(env_file, "a") as f:
                    f.write(f"\nESSENCIA_ENCRYPTION_KEY={key}\n")
                console.print("[green]✅ Added encryption key to .env[/green]")
        else:
            # Create new .env file
            env_file.write_text(f"ESSENCIA_ENCRYPTION_KEY={key}\n")
            console.print("[green]✅ Created .env with encryption key[/green]")
    
    console.print("\n[bold]⚠️  Keep this key secure![/bold]")
    console.print("• Never commit it to version control")
    console.print("• Store it in a secure password manager")
    console.print("• Use different keys for different environments")


@app.command()
def hash_password(
    password: str = typer.Option(
        ..., "--password", "-p",
        prompt=True,
        hide_input=True,
        help="Password to hash"
    ),
    algorithm: str = typer.Option(
        "bcrypt", "--algorithm", "-a",
        help="Hashing algorithm (bcrypt, argon2)"
    )
):
    """Hash a password."""
    if algorithm == "bcrypt":
        try:
            import bcrypt
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            console.print(f"\n[green]Hashed password (bcrypt):[/green]")
            console.print(hashed.decode('utf-8'))
        except ImportError:
            console.print("[red]bcrypt not installed. Install with: pip install bcrypt[/red]")
    
    elif algorithm == "argon2":
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            hashed = ph.hash(password)
            console.print(f"\n[green]Hashed password (argon2):[/green]")
            console.print(hashed)
        except ImportError:
            console.print("[red]argon2-cffi not installed. Install with: pip install argon2-cffi[/red]")
    
    else:
        console.print(f"[red]Unknown algorithm: {algorithm}[/red]")


@app.command()
def generate_secret(
    length: int = typer.Option(
        32, "--length", "-l",
        help="Secret length in bytes"
    ),
    format: str = typer.Option(
        "hex", "--format", "-f",
        help="Output format (hex, base64, urlsafe)"
    )
):
    """Generate a secure random secret."""
    secret_bytes = secrets.token_bytes(length)
    
    if format == "hex":
        secret = secrets.token_hex(length)
    elif format == "base64":
        secret = base64.b64encode(secret_bytes).decode('utf-8')
    elif format == "urlsafe":
        secret = secrets.token_urlsafe(length)
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        return
    
    console.print(f"[bold green]Generated secret ({format}):[/bold green]")
    console.print(f"\n[yellow]{secret}[/yellow]")
    console.print(f"\nLength: {len(secret)} characters")


@app.command()
def audit(
    days: int = typer.Option(
        7, "--days", "-d",
        help="Number of days to analyze"
    ),
    user: Optional[str] = typer.Option(
        None, "--user", "-u",
        help="Filter by specific user"
    ),
    event_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Filter by event type"
    )
):
    """Analyze security audit logs."""
    console.print("[bold green]Security Audit Report[/bold green]")
    console.print(f"Period: Last {days} days\n")
    
    # This would query actual audit logs
    # For demo, showing example data
    table = Table(title="Security Events")
    table.add_column("Time", style="cyan")
    table.add_column("User", style="green")
    table.add_column("Event", style="yellow")
    table.add_column("Resource")
    table.add_column("Result")
    
    events = [
        ("2024-01-15 14:32:15", "admin", "LOGIN", "-", "SUCCESS"),
        ("2024-01-15 14:33:22", "admin", "PATIENT_ACCESS", "PAT-001", "SUCCESS"),
        ("2024-01-15 14:45:10", "user123", "LOGIN_FAILED", "-", "FAILED"),
        ("2024-01-15 15:12:33", "doctor01", "PRESCRIPTION_CREATE", "RX-2024-001", "SUCCESS"),
        ("2024-01-15 16:22:45", "nurse02", "VITAL_SIGNS_UPDATE", "VS-1234", "SUCCESS"),
    ]
    
    for event in events:
        if user and event[1] != user:
            continue
        if event_type and event[2] != event_type:
            continue
        
        result_color = "green" if event[4] == "SUCCESS" else "red"
        table.add_row(event[0], event[1], event[2], event[3], f"[{result_color}]{event[4]}[/{result_color}]")
    
    console.print(table)
    
    # Summary statistics
    console.print("\n[bold]Summary:[/bold]")
    console.print("• Total events: 5")
    console.print("• Successful: 4")
    console.print("• Failed: 1")
    console.print("• Unique users: 4")


@app.command()
def check_config():
    """Check security configuration."""
    console.print("[bold green]Security Configuration Check[/bold green]\n")
    
    checks = []
    
    # Check encryption key
    import os
    if os.getenv("ESSENCIA_ENCRYPTION_KEY"):
        checks.append(("Encryption Key", "✅ Configured", "green"))
    else:
        checks.append(("Encryption Key", "❌ Not configured", "red"))
    
    # Check session secret
    if os.getenv("SESSION_SECRET"):
        checks.append(("Session Secret", "✅ Configured", "green"))
    else:
        checks.append(("Session Secret", "❌ Not configured", "red"))
    
    # Check CORS origins
    cors = os.getenv("CORS_ORIGINS", "")
    if cors and cors != "*":
        checks.append(("CORS Origins", f"✅ Restricted to: {cors}", "green"))
    elif cors == "*":
        checks.append(("CORS Origins", "⚠️  Allowing all origins", "yellow"))
    else:
        checks.append(("CORS Origins", "✅ Not configured (safe default)", "green"))
    
    # Check rate limiting
    if os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true":
        checks.append(("Rate Limiting", "✅ Enabled", "green"))
    else:
        checks.append(("Rate Limiting", "⚠️  Disabled", "yellow"))
    
    # Display results
    for check, status, color in checks:
        console.print(f"{check}: [{color}]{status}[/{color}]")
    
    # Recommendations
    failed_checks = [c[0] for c in checks if "❌" in c[1]]
    if failed_checks:
        console.print("\n[bold red]⚠️  Security Issues Found![/bold red]")
        console.print("\nRecommendations:")
        
        if "Encryption Key" in failed_checks:
            console.print("• Run 'essencia security generate-key' to create an encryption key")
        
        if "Session Secret" in failed_checks:
            console.print("• Run 'essencia security generate-secret' to create a session secret")


@app.command()
def permissions(
    user: Optional[str] = typer.Option(
        None, "--user", "-u",
        help="Check permissions for specific user"
    ),
    role: Optional[str] = typer.Option(
        None, "--role", "-r",
        help="List permissions for role"
    )
):
    """Manage user permissions and roles."""
    console.print("[bold green]Permission Management[/bold green]\n")
    
    # Define standard roles and permissions
    roles = {
        "admin": [
            "users:*",
            "patients:*",
            "medical_records:*",
            "prescriptions:*",
            "settings:*",
            "audit:view"
        ],
        "doctor": [
            "patients:read",
            "patients:write",
            "medical_records:*",
            "prescriptions:*",
            "vital_signs:*",
            "assessments:*"
        ],
        "nurse": [
            "patients:read",
            "vital_signs:*",
            "medications:administer",
            "assessments:read"
        ],
        "receptionist": [
            "patients:read",
            "patients:create",
            "appointments:*"
        ],
        "patient": [
            "own_profile:read",
            "own_medical_records:read",
            "own_appointments:*"
        ]
    }
    
    if role:
        if role in roles:
            console.print(f"[cyan]Role: {role}[/cyan]\n")
            console.print("Permissions:")
            for perm in roles[role]:
                console.print(f"  • {perm}")
        else:
            console.print(f"[red]Unknown role: {role}[/red]")
            console.print(f"\nAvailable roles: {', '.join(roles.keys())}")
    
    else:
        # Show all roles
        table = Table(title="Available Roles and Permissions")
        table.add_column("Role", style="cyan")
        table.add_column("Permissions", style="green")
        
        for role_name, perms in roles.items():
            table.add_row(
                role_name,
                "\n".join(perms[:3]) + f"\n... and {len(perms)-3} more" if len(perms) > 3 else "\n".join(perms)
            )
        
        console.print(table)