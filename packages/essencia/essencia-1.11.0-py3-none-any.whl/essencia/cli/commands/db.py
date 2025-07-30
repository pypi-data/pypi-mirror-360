"""
Database command - Database operations and management.
"""
import asyncio
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from essencia.database import AsyncDatabase, Database

app = typer.Typer(help="Database operations")
console = Console()


@app.command()
def status(
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Check database connection status."""
    if not mongodb_url:
        console.print("[red]No MongoDB URL provided. Set MONGODB_URL environment variable or use --url[/red]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking database connection...", total=None)
        
        try:
            # Test sync connection
            db = Database(mongodb_url)
            db_name = db.client.get_database().name
            
            # Get collections
            collections = db.client.get_database().list_collection_names()
            
            # Get database stats
            stats = db.client.get_database().command("dbstats")
            
            progress.update(task, completed=True)
            
            # Display results
            console.print("\n[bold green]✅ Database connection successful![/bold green]")
            console.print(f"\n[cyan]Database:[/cyan] {db_name}")
            console.print(f"[cyan]Collections:[/cyan] {len(collections)}")
            console.print(f"[cyan]Data Size:[/cyan] {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
            console.print(f"[cyan]Storage Size:[/cyan] {stats.get('storageSize', 0) / 1024 / 1024:.2f} MB")
            
            if collections:
                console.print("\n[yellow]Collections:[/yellow]")
                table = Table()
                table.add_column("Collection", style="cyan")
                table.add_column("Documents", justify="right")
                
                for collection in collections[:10]:  # Show first 10
                    count = db.client.get_database()[collection].count_documents({})
                    table.add_row(collection, str(count))
                
                console.print(table)
                
                if len(collections) > 10:
                    console.print(f"\n... and {len(collections) - 10} more collections")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n[red]❌ Database connection failed:[/red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def seed(
    collection: str = typer.Argument(..., help="Collection to seed"),
    count: int = typer.Option(10, "--count", "-c", help="Number of records to create"),
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Seed database with sample data."""
    if not mongodb_url:
        console.print("[red]No MongoDB URL provided[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold green]Seeding {collection} with {count} records...[/bold green]")
    
    # Import models dynamically
    if collection == "patients":
        from essencia.models import Patient
        from faker import Faker
        fake = Faker("pt_BR")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating {count} patients...", total=count)
            
            db = Database(mongodb_url)
            Patient.set_db(db.client.get_database())
            
            for i in range(count):
                patient = Patient(
                    name=fake.name(),
                    cpf=fake.cpf(),
                    birth_date=fake.date_of_birth(minimum_age=0, maximum_age=100),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    blood_type=fake.random_element(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                    medical_record_number=f"MR{fake.random_number(digits=6):06d}"
                )
                patient.save()
                progress.update(task, advance=1)
            
            console.print(f"\n✅ Created {count} patients successfully!")
    
    else:
        console.print(f"[yellow]Seeding for '{collection}' not implemented yet[/yellow]")


@app.command()
def migrate(
    direction: str = typer.Argument("up", help="Migration direction (up/down)"),
    target: Optional[str] = typer.Option(
        None, "--target", "-t",
        help="Target migration version"
    ),
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Run database migrations."""
    console.print(f"[bold green]Running migrations {direction}...[/bold green]")
    
    # This would implement a migration system
    console.print("[yellow]Migration system not yet implemented[/yellow]")
    console.print("\nTo implement migrations:")
    console.print("1. Create a migrations directory")
    console.print("2. Use 'essencia generate migration <name>' to create migrations")
    console.print("3. Run migrations with this command")


@app.command()
def indexes(
    collection: Optional[str] = typer.Option(
        None, "--collection", "-c",
        help="Specific collection to check"
    ),
    create: bool = typer.Option(
        False, "--create",
        help="Create missing indexes"
    ),
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Manage database indexes."""
    if not mongodb_url:
        console.print("[red]No MongoDB URL provided[/red]")
        raise typer.Exit(1)
    
    db = Database(mongodb_url).client.get_database()
    
    if collection:
        collections = [collection]
    else:
        collections = db.list_collection_names()
    
    table = Table(title="Database Indexes")
    table.add_column("Collection", style="cyan")
    table.add_column("Index", style="green")
    table.add_column("Fields")
    table.add_column("Options")
    
    for coll_name in collections:
        coll = db[coll_name]
        indexes = coll.list_indexes()
        
        for index in indexes:
            fields = ", ".join([f"{k}:{v}" for k, v in index["key"].items()])
            options = []
            
            if index.get("unique"):
                options.append("unique")
            if index.get("sparse"):
                options.append("sparse")
            if index.get("expireAfterSeconds"):
                options.append(f"TTL:{index['expireAfterSeconds']}s")
            
            table.add_row(
                coll_name,
                index["name"],
                fields,
                ", ".join(options) if options else "-"
            )
    
    console.print(table)
    
    if create:
        console.print("\n[yellow]Creating indexes from model definitions...[/yellow]")
        # This would read model definitions and create indexes
        console.print("[green]Index creation not yet implemented[/green]")


@app.command()
def backup(
    output: str = typer.Option(
        "./backup", "--output", "-o",
        help="Output directory for backup"
    ),
    collections: Optional[str] = typer.Option(
        None, "--collections", "-c",
        help="Comma-separated list of collections to backup"
    ),
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Backup database collections."""
    import json
    from pathlib import Path
    from datetime import datetime
    
    if not mongodb_url:
        console.print("[red]No MongoDB URL provided[/red]")
        raise typer.Exit(1)
    
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = output_dir / f"backup_{timestamp}"
    backup_dir.mkdir()
    
    db = Database(mongodb_url).client.get_database()
    
    if collections:
        collection_list = collections.split(",")
    else:
        collection_list = db.list_collection_names()
    
    console.print(f"[bold green]Backing up {len(collection_list)} collections to {backup_dir}[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Backing up...", total=len(collection_list))
        
        for coll_name in collection_list:
            coll = db[coll_name]
            documents = list(coll.find())
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            
            # Write to file
            output_file = backup_dir / f"{coll_name}.json"
            with open(output_file, "w") as f:
                json.dump(documents, f, indent=2, default=str)
            
            progress.update(task, advance=1)
    
    console.print(f"\n✅ Backup completed: {backup_dir}")
    console.print(f"Total collections backed up: {len(collection_list)}")


@app.command()
def restore(
    backup_path: str = typer.Argument(..., help="Path to backup directory"),
    collections: Optional[str] = typer.Option(
        None, "--collections", "-c",
        help="Comma-separated list of collections to restore"
    ),
    drop: bool = typer.Option(
        False, "--drop",
        help="Drop existing collections before restore"
    ),
    mongodb_url: Optional[str] = typer.Option(
        None, "--url", "-u",
        help="MongoDB connection URL",
        envvar="MONGODB_URL"
    )
):
    """Restore database from backup."""
    import json
    from pathlib import Path
    from bson import ObjectId
    
    if not mongodb_url:
        console.print("[red]No MongoDB URL provided[/red]")
        raise typer.Exit(1)
    
    backup_dir = Path(backup_path)
    if not backup_dir.exists():
        console.print(f"[red]Backup directory not found: {backup_path}[/red]")
        raise typer.Exit(1)
    
    db = Database(mongodb_url).client.get_database()
    
    # Get JSON files from backup
    json_files = list(backup_dir.glob("*.json"))
    
    if collections:
        collection_filter = collections.split(",")
        json_files = [f for f in json_files if f.stem in collection_filter]
    
    console.print(f"[bold green]Restoring {len(json_files)} collections from {backup_dir}[/bold green]")
    
    if drop:
        console.print("[yellow]⚠️  Dropping existing collections...[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring...", total=len(json_files))
        
        for json_file in json_files:
            coll_name = json_file.stem
            coll = db[coll_name]
            
            if drop:
                coll.drop()
            
            # Load documents
            with open(json_file, "r") as f:
                documents = json.load(f)
            
            # Convert string IDs back to ObjectId
            for doc in documents:
                if "_id" in doc and isinstance(doc["_id"], str):
                    doc["_id"] = ObjectId(doc["_id"])
            
            # Insert documents
            if documents:
                coll.insert_many(documents)
            
            progress.update(task, advance=1)
    
    console.print(f"\n✅ Restore completed successfully!")
    console.print(f"Total collections restored: {len(json_files)}")