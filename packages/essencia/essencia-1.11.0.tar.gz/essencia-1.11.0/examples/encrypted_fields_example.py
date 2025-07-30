#!/usr/bin/env python
"""
Example showing how to migrate models to use encrypted fields.

This example demonstrates:
1. Before: Models with plain text sensitive fields
2. After: Models with encrypted fields
3. Migration process for existing data
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import date

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from essencia.models import MongoModel
from essencia.fields import (
    EncryptedCPF, 
    EncryptedRG, 
    EncryptedMedicalData,
    EncryptedStr
)
from essencia.database import Database


# BEFORE: Model with unencrypted sensitive fields
class PatientOld(MongoModel):
    """Old patient model without encryption."""
    COLLECTION_NAME = 'patients_old'
    
    name: str
    birth_date: date
    cpf: Optional[str] = None  # Plain text CPF
    rg: Optional[str] = None   # Plain text RG
    medical_history: Optional[str] = None  # Plain text medical data
    diagnosis: Optional[str] = None  # Plain text diagnosis
    phone: Optional[str] = None


# AFTER: Model with encrypted sensitive fields
class PatientNew(MongoModel):
    """New patient model with encrypted fields."""
    COLLECTION_NAME = 'patients_new'
    
    name: str
    birth_date: date
    cpf: Optional[EncryptedCPF] = None  # Encrypted CPF
    rg: Optional[EncryptedRG] = None    # Encrypted RG
    medical_history: Optional[EncryptedMedicalData] = None  # Encrypted medical data
    diagnosis: Optional[EncryptedMedicalData] = None  # Encrypted diagnosis
    phone: Optional[str] = None  # Phone remains unencrypted


# Custom encrypted field for specific use case
class EncryptedDiagnosis(EncryptedStr):
    """Custom encrypted field for diagnosis with special handling."""
    
    def __new__(cls, value: str = ""):
        # Add any custom validation or preprocessing here
        if value and len(value) < 10:
            raise ValueError("Diagnosis must be at least 10 characters")
        return super().__new__(cls, value, context="diagnosis")
    
    def decrypt(self) -> str:
        """Decrypt with diagnosis context."""
        return super().decrypt(context="diagnosis")
    
    def get_summary(self, max_length: int = 50) -> str:
        """Get a truncated summary of the diagnosis."""
        decrypted = self.decrypt()
        if len(decrypted) > max_length:
            return decrypted[:max_length] + "..."
        return decrypted


class PatientWithCustomField(MongoModel):
    """Patient model with custom encrypted field."""
    COLLECTION_NAME = 'patients_custom'
    
    name: str
    birth_date: date
    cpf: Optional[EncryptedCPF] = None
    diagnosis: Optional[EncryptedDiagnosis] = None


def demonstrate_encryption():
    """Demonstrate encrypted field usage."""
    print("🔐 Encrypted Fields Demonstration\n")
    
    # Ensure encryption key is set
    if not os.environ.get('ESSENCIA_ENCRYPTION_KEY'):
        print("⚠️  Setting temporary encryption key for demo")
        os.environ['ESSENCIA_ENCRYPTION_KEY'] = 'dGhpc2lzYXRlc3RrZXlmb3JkZW1vbnN0cmF0aW9ucHVycG9zZXM='
    
    # Create database connection
    db = Database()
    
    # 1. Create patient with unencrypted data (old model)
    print("1️⃣  Creating patient with unencrypted data...")
    old_patient = PatientOld(
        name="João Silva",
        birth_date=date(1980, 5, 15),
        cpf="12345678901",  # Stored as plain text
        rg="123456789",
        medical_history="Patient has hypertension and diabetes",
        diagnosis="Type 2 Diabetes Mellitus",
        phone="11999887766"
    )
    
    print(f"   Old model CPF (plain text): {old_patient.cpf}")
    print(f"   Old model medical history: {old_patient.medical_history[:30]}...")
    
    # 2. Create patient with encrypted data (new model)
    print("\n2️⃣  Creating patient with encrypted data...")
    new_patient = PatientNew(
        name="Maria Santos",
        birth_date=date(1975, 3, 20),
        cpf="98765432109",  # Will be encrypted automatically
        rg="987654321",
        medical_history="Patient has asthma and allergies to penicillin",
        diagnosis="Bronchial Asthma",
        phone="11888776655"
    )
    
    print(f"   New model CPF (encrypted): {new_patient.cpf[:20]}...")
    print(f"   Is CPF encrypted? {new_patient.cpf.is_encrypted()}")
    print(f"   Decrypted CPF: {new_patient.cpf.decrypt()}")
    print(f"   Formatted CPF: {new_patient.cpf.decrypt_formatted()}")
    print(f"   Masked CPF: {new_patient.cpf.decrypt_masked()}")
    
    # 3. Save to database
    print("\n3️⃣  Saving to database...")
    try:
        # Save encrypted patient
        saved_id = new_patient.save()
        print(f"   Saved patient with ID: {saved_id}")
        
        # Load from database
        loaded_patient = PatientNew.get(saved_id)
        print(f"   Loaded patient name: {loaded_patient.name}")
        print(f"   Loaded CPF (still encrypted): {loaded_patient.cpf[:20]}...")
        print(f"   Decrypted CPF: {loaded_patient.cpf.decrypt()}")
        
    except Exception as e:
        print(f"   ⚠️  Database operation skipped: {e}")
    
    # 4. Demonstrate custom encrypted field
    print("\n4️⃣  Using custom encrypted field...")
    custom_patient = PatientWithCustomField(
        name="Pedro Oliveira",
        birth_date=date(1990, 8, 10),
        cpf="11122233344",
        diagnosis="Generalized Anxiety Disorder with panic attacks, requiring CBT therapy"
    )
    
    print(f"   Diagnosis (encrypted): {custom_patient.diagnosis[:20]}...")
    print(f"   Diagnosis summary: {custom_patient.diagnosis.get_summary()}")
    print(f"   Full diagnosis: {custom_patient.diagnosis.decrypt()}")
    
    # 5. Migration example
    print("\n5️⃣  Migration example (converting old to new)...")
    
    # Simulate loading old patient data
    old_data = {
        "name": "Ana Costa",
        "birth_date": date(1985, 12, 25),
        "cpf": "55566677788",  # Plain text
        "rg": "556667778",      # Plain text
        "medical_history": "No significant medical history",
        "phone": "11777665544"
    }
    
    # Create new patient from old data
    migrated_patient = PatientNew(**old_data)
    
    print(f"   Original CPF: {old_data['cpf']}")
    print(f"   Migrated CPF (encrypted): {migrated_patient.cpf[:20]}...")
    print(f"   Verify decryption: {migrated_patient.cpf.decrypt()}")
    
    # 6. Bulk operations
    print("\n6️⃣  Bulk operations with encrypted fields...")
    
    # Create multiple patients
    patients = [
        PatientNew(
            name=f"Patient {i}",
            birth_date=date(1980 + i, 1, 1),
            cpf=f"{i:011d}",  # Generate CPF-like number
            medical_history=f"Medical history for patient {i}"
        )
        for i in range(1, 4)
    ]
    
    for i, patient in enumerate(patients):
        print(f"   Patient {i+1} - CPF encrypted: {patient.cpf.is_encrypted()}")
    
    # 7. Error handling
    print("\n7️⃣  Error handling...")
    
    try:
        # Try to create patient with invalid CPF
        invalid_patient = PatientNew(
            name="Invalid Patient",
            birth_date=date(1990, 1, 1),
            cpf="12345",  # Invalid CPF
        )
    except ValueError as e:
        print(f"   ✅ Validation error caught: {e}")
    
    print("\n✅ Demonstration complete!")
    print("\n📝 Key takeaways:")
    print("   - Encrypted fields automatically encrypt on assignment")
    print("   - Data remains encrypted at rest in the database")
    print("   - Decryption happens on-demand when needed")
    print("   - Validation still works with encrypted fields")
    print("   - Custom encrypted fields can add domain-specific logic")


def show_migration_steps():
    """Show step-by-step migration process."""
    print("\n📋 Migration Steps for Existing Projects:\n")
    
    print("1. Set up encryption key:")
    print("   export ESSENCIA_ENCRYPTION_KEY=\"$(python -c 'import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())')\"")
    
    print("\n2. Update your models:")
    print("   - Change: cpf: str")
    print("   - To:     cpf: EncryptedCPF")
    
    print("\n3. Run migration script:")
    print("   python migrate_to_encrypted_fields.py --database mydb --apply")
    
    print("\n4. Update your code:")
    print("   - Access encrypted fields normally: patient.cpf")
    print("   - Decrypt when needed: patient.cpf.decrypt()")
    
    print("\n5. Test thoroughly:")
    print("   - Verify encryption/decryption works")
    print("   - Check performance impact")
    print("   - Ensure backups are working")


if __name__ == "__main__":
    demonstrate_encryption()
    show_migration_steps()