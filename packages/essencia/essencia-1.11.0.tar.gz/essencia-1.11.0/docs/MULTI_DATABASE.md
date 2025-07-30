# Multi-Database Support in Essencia

Essencia now supports multiple database backends, allowing you to use MongoDB, PostgreSQL, and other databases within the same application. This provides flexibility to choose the best database for each use case.

## Overview

The multi-database architecture allows you to:
- Use MongoDB for document storage with field-level encryption
- Use PostgreSQL for relational data and complex queries
- Mix databases within the same application
- Maintain a consistent API across different databases

## Installation

To use PostgreSQL support, install with the postgresql extra:

```bash
# PostgreSQL support only
uv pip install essencia[postgresql]

# All database support
uv pip install essencia[all]
```

## Configuration

### Basic Setup

```python
from essencia.database import DatabaseFactory, DatabaseConfig

# Configure MongoDB
mongo_config = DatabaseConfig(
    url="mongodb://localhost:27017",
    database_name="essencia_mongo"
)
mongo_db = DatabaseFactory.create_database(
    name="mongodb_main",
    db_type="mongodb",
    config=mongo_config
)

# Configure PostgreSQL
pg_config = DatabaseConfig(
    url="postgresql://user:password@localhost:5432/essencia",
    database_name="essencia",
    options={"pool_size": 20}
)
pg_db = DatabaseFactory.create_database(
    name="postgresql_main", 
    db_type="postgresql",
    config=pg_config
)

# Connect to databases
await mongo_db.connect()
await pg_db.connect()
```

## Creating Models

### MongoDB Models

Use `MongoModel` for MongoDB collections:

```python
from essencia.models import MongoModel
from essencia.fields import EncryptedCPF

class Patient(MongoModel):
    __database__ = mongo_db  # Assign MongoDB instance
    __collection_name__ = "patients"
    
    name: str
    cpf: EncryptedCPF  # Field-level encryption
    email: str
```

### PostgreSQL Models

Use `SQLModel` for PostgreSQL tables:

```python
from essencia.models import SQLModel

class Appointment(SQLModel):
    __database__ = pg_db  # Assign PostgreSQL instance
    __collection_name__ = "appointments"
    
    patient_id: str
    doctor_name: str
    appointment_date: datetime
    status: str = "scheduled"
```

### Model Features

Both model types support:
- CRUD operations (create, read, update, delete)
- Async and sync methods
- Query building
- Validation with Pydantic
- Timestamps (with `TimestampedSQLModel`)
- Soft deletes (with `SoftDeleteSQLModel`)

## Usage Examples

### Basic Operations

```python
# Create records
patient = Patient(name="João Silva", cpf="123.456.789-00", email="joao@example.com")
await patient.save()

appointment = Appointment(
    patient_id=patient.id,
    doctor_name="Dr. Maria",
    appointment_date=datetime.now()
)
await appointment.save()

# Query records
patients = await Patient.find_many(name="João Silva")
appointments = await Appointment.find_many(patient_id=patient.id)

# Update records
appointment.status = "completed"
await appointment.save()

# Delete records
await appointment.delete()
```

### Transactions (PostgreSQL only)

```python
async with pg_db.transaction():
    appointment = await Appointment(...).save()
    payment = await Payment(...).save()
    # Both will be committed or rolled back together
```

### Cross-Database Operations

```python
# Find patient in MongoDB
patient = await Patient.find_by_id(patient_id)

# Find related appointments in PostgreSQL
appointments = await Appointment.find_many(patient_id=patient.id)

# Aggregate data across databases in application code
patient_data = {
    "patient": patient,
    "appointments": appointments
}
```

## When to Use Each Database

### Use MongoDB for:
- Document-oriented data
- Field-level encryption requirements
- Flexible schemas
- Medical records with encrypted fields
- Unstructured or semi-structured data

### Use PostgreSQL for:
- Relational data with foreign keys
- Complex queries and joins
- ACID transactions
- Analytics and reporting
- Time-series data
- Financial records

## Migration Guide

### Migrating from MongoDB-only

1. Install PostgreSQL support:
   ```bash
   uv pip install essencia[postgresql]
   ```

2. Update your models:
   ```python
   # Old MongoDB model
   class Order(MongoModel):
       ...
   
   # New PostgreSQL model
   class Order(SQLModel):
       __database__ = pg_db
       ...
   ```

3. Migrate data:
   ```python
   # Read from MongoDB
   mongo_orders = await MongoOrder.find_many()
   
   # Write to PostgreSQL
   for order in mongo_orders:
       pg_order = PgOrder(**order.model_dump())
       await pg_order.save()
   ```

## Advanced Features

### Custom Table Structure

For PostgreSQL, you can customize the table structure:

```python
from sqlalchemy import Table, Column, String, DateTime

class CustomModel(SQLModel):
    __table__ = Table(
        'custom_table',
        metadata,
        Column('id', String, primary_key=True),
        Column('data', JSONB),
        Column('created_at', DateTime),
        # Add custom columns
        Column('custom_field', String(100))
    )
```

### Query Builder

PostgreSQL models support SQLAlchemy query building:

```python
# Complex query
query = (
    Appointment.query()
    .where(status="scheduled")
    .where(appointment_date__gte=datetime.now())
    .order_by("appointment_date")
    .limit(10)
)
results = await query.execute()
```

## Performance Considerations

1. **Connection Pooling**: Both adapters support connection pooling
2. **Indexes**: Create appropriate indexes for your queries
3. **Batch Operations**: Use bulk inserts when possible
4. **Caching**: Use Redis cache for frequently accessed data
5. **Query Optimization**: Use database-specific features for best performance

## Limitations

1. **No Cross-Database Joins**: Joins must be done in application code
2. **No Cross-Database Transactions**: Transactions are per-database
3. **Different Query Syntax**: Each database has its own query patterns
4. **Feature Parity**: Some features may work differently across databases

## Future Enhancements

- MySQL/MariaDB support
- SQLite support for testing
- Automatic migration tools
- Query translation layer
- Distributed transactions