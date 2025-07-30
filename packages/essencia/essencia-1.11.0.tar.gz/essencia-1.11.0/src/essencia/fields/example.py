"""
Example demonstrating the usage of encrypted fields.

This example shows how to use the encrypted field types in Pydantic models.
"""

from typing import Optional
from pydantic import BaseModel
from essencia.fields import (
    EncryptedCPF, EncryptedRG, EncryptedMedicalData,
    EncryptedMedicalHistory, EncryptedPrescription,
    DefaultDate, OptionalString,
    CPFField, RGField, MedicalDataField
)


class Patient(BaseModel):
    """Example patient model with encrypted fields."""
    
    name: str
    birth_date: DefaultDate
    
    # Using encrypted field types directly
    cpf: EncryptedCPF
    rg: EncryptedRG
    
    # Using field factories (alternative approach)
    medical_notes: str = MedicalDataField(default="")
    
    # Optional encrypted fields
    medical_history: Optional[EncryptedMedicalHistory] = None
    current_prescription: Optional[EncryptedPrescription] = None
    
    # Regular optional field
    phone: OptionalString = None


def main():
    """Demonstrate encrypted field usage."""
    import os
    
    # Set encryption key (in production, use environment variable)
    os.environ['ESSENCIA_ENCRYPTION_KEY'] = 'your-32-character-encryption-key'
    
    # Create a patient with encrypted data
    patient = Patient(
        name="João Silva",
        birth_date="1990-05-15",
        cpf="123.456.789-01",  # Will be validated and encrypted
        rg="12345678",  # Will be validated and encrypted
        medical_notes="Patient has diabetes type 2",
        phone="+55 11 98765-4321"
    )
    
    # The CPF and RG are stored encrypted
    print(f"Encrypted CPF: {patient.cpf}")
    print(f"Is CPF encrypted: {patient.cpf.is_encrypted()}")
    
    # But can be decrypted when needed
    print(f"Decrypted CPF: {patient.cpf.decrypt()}")
    print(f"Formatted CPF: {patient.cpf.decrypt_formatted()}")
    print(f"Masked CPF: {patient.cpf.decrypt_masked()}")
    
    # Convert to dict for storage (encrypted values remain encrypted)
    patient_dict = patient.model_dump()
    print(f"\\nPatient data for storage: {patient_dict}")
    
    # Load from dict (encrypted values are preserved)
    loaded_patient = Patient(**patient_dict)
    print(f"\\nLoaded patient CPF (still encrypted): {loaded_patient.cpf}")
    print(f"Decrypted CPF: {loaded_patient.cpf.decrypt()}")
    
    # Add medical history
    patient.medical_history = EncryptedMedicalHistory({
        "conditions": ["Diabetes Type 2", "Hypertension"],
        "allergies": ["Penicillin"],
        "surgeries": ["Appendectomy - 2010"]
    })
    
    # Retrieve structured medical history
    history = patient.medical_history.decrypt_structured()
    print(f"\\nMedical history: {history}")


if __name__ == "__main__":
    main()