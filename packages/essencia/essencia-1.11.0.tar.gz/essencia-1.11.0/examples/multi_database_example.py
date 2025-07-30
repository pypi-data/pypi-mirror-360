"""Example of using Essencia with multiple databases (MongoDB and PostgreSQL).

This example demonstrates how to:
1. Configure both MongoDB and PostgreSQL connections
2. Create models that use different databases
3. Perform operations across both databases
"""
import asyncio
import os
from datetime import datetime
from typing import Optional

from essencia.database import DatabaseFactory, DatabaseConfig
from essencia.models import MongoModel, SQLModel
from essencia.fields import EncryptedCPF


# Example 1: Patient model in MongoDB (for encrypted data)
class Patient(MongoModel):
    """Patient model stored in MongoDB with encrypted fields."""
    __collection_name__ = "patients"
    
    name: str
    cpf: EncryptedCPF  # Encrypted field works best with MongoDB
    birth_date: datetime
    email: Optional[str] = None
    
    class Config:
        collection = "patients"


# Example 2: Appointment model in PostgreSQL (for relational queries)
class Appointment(SQLModel):
    """Appointment model stored in PostgreSQL."""
    __collection_name__ = "appointments"
    
    patient_id: str  # Reference to MongoDB patient
    doctor_name: str
    appointment_date: datetime
    status: str = "scheduled"
    notes: Optional[str] = None


# Example 3: Lab results in PostgreSQL (for analytical queries)
class LabResult(SQLModel):
    """Lab results stored in PostgreSQL for better analytical capabilities."""
    __collection_name__ = "lab_results"
    
    patient_id: str
    test_name: str
    value: float
    unit: str
    test_date: datetime
    is_abnormal: bool = False


async def setup_databases():
    """Setup both MongoDB and PostgreSQL connections."""
    
    # Configure MongoDB
    mongo_config = DatabaseConfig(
        url=os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
        database_name="essencia_medical"
    )
    mongo_db = DatabaseFactory.create_database(
        name="mongodb_main",
        db_type="mongodb",
        config=mongo_config
    )
    await mongo_db.connect()
    
    # Configure PostgreSQL
    pg_config = DatabaseConfig(
        url=os.getenv("POSTGRESQL_URL", "postgresql://user:password@localhost:5432/essencia"),
        database_name="essencia",
        options={"echo": True}  # Enable SQL logging
    )
    pg_db = DatabaseFactory.create_database(
        name="postgresql_main",
        db_type="postgresql",
        config=pg_config
    )
    await pg_db.connect()
    
    # Assign databases to models
    Patient.__database__ = mongo_db
    Appointment.__database__ = pg_db
    LabResult.__database__ = pg_db
    
    # Create PostgreSQL tables
    await Appointment.create_table()
    await LabResult.create_table()
    
    return mongo_db, pg_db


async def example_cross_database_operations():
    """Example of operations across both databases."""
    
    # Create a patient in MongoDB
    patient = Patient(
        name="João Silva",
        cpf="123.456.789-00",  # Will be encrypted
        birth_date=datetime(1980, 5, 15),
        email="joao@example.com"
    )
    await patient.save()
    print(f"Created patient in MongoDB: {patient.id}")
    
    # Create an appointment in PostgreSQL
    appointment = Appointment(
        patient_id=patient.id,  # Reference to MongoDB patient
        doctor_name="Dr. Maria Santos",
        appointment_date=datetime(2024, 12, 15, 14, 30),
        status="scheduled"
    )
    await appointment.save()
    print(f"Created appointment in PostgreSQL: {appointment.id}")
    
    # Create lab results in PostgreSQL
    lab_results = [
        LabResult(
            patient_id=patient.id,
            test_name="Hemoglobin",
            value=12.5,
            unit="g/dL",
            test_date=datetime(2024, 12, 10)
        ),
        LabResult(
            patient_id=patient.id,
            test_name="Glucose",
            value=95,
            unit="mg/dL",
            test_date=datetime(2024, 12, 10)
        )
    ]
    
    for result in lab_results:
        await result.save()
    print(f"Created {len(lab_results)} lab results in PostgreSQL")
    
    # Query across databases
    # 1. Find patient in MongoDB
    found_patient = await Patient.find_by_id(patient.id)
    print(f"\nFound patient: {found_patient.name}")
    print(f"Decrypted CPF: {found_patient.cpf}")  # Automatically decrypted
    
    # 2. Find appointments for patient in PostgreSQL
    appointments = await Appointment.find_many(patient_id=patient.id)
    print(f"\nFound {len(appointments)} appointments for patient")
    
    # 3. Analytical query on lab results using PostgreSQL
    lab_results = await LabResult.find_many(
        patient_id=patient.id,
        sort=[("test_date", -1)]
    )
    print(f"\nLab results for patient:")
    for result in lab_results:
        print(f"  - {result.test_name}: {result.value} {result.unit}")
    
    # Transaction example (PostgreSQL only)
    async with pg_db.transaction():
        # Create multiple related records in a transaction
        new_appointment = Appointment(
            patient_id=patient.id,
            doctor_name="Dr. Carlos Mendes",
            appointment_date=datetime(2024, 12, 20, 10, 0)
        )
        await new_appointment.save()
        
        # If this fails, the appointment above will be rolled back
        new_result = LabResult(
            patient_id=patient.id,
            test_name="Cholesterol",
            value=180,
            unit="mg/dL",
            test_date=datetime(2024, 12, 18)
        )
        await new_result.save()
    
    print("\nTransaction completed successfully")


async def main():
    """Main entry point."""
    print("=== Essencia Multi-Database Example ===\n")
    
    # Setup databases
    mongo_db, pg_db = await setup_databases()
    print("✓ Databases connected\n")
    
    try:
        # Run example operations
        await example_cross_database_operations()
        
    finally:
        # Cleanup
        await mongo_db.disconnect()
        await pg_db.disconnect()
        print("\n✓ Databases disconnected")


if __name__ == "__main__":
    # Set encryption key for encrypted fields
    os.environ["ESSENCIA_ENCRYPTION_KEY"] = "your-base64-encoded-32-byte-key-here"
    
    # Run the example
    asyncio.run(main())