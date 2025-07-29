"""
Essencia Fields Package.

Provides custom field types for Pydantic models including encrypted fields
for sensitive data protection and compliance.
"""

# Import base field types
from essencia.fields.base_fields import (
    DefaultDate, DefaultDateTime, 
    OptionalDate, OptionalDateTime,
    OptionalString,
    today, now, string_to_date, parse_date_to_datetime, slice_if_not_none
)

# Import encrypted field types
from essencia.fields.encrypted_fields import (
    EncryptedStr, EncryptedCPF, EncryptedRG, EncryptedMedicalData,
    CPFField, RGField, MedicalDataField,
    validate_encrypted_cpf, validate_encrypted_rg, validate_encrypted_medical_data
)

# Import specialized medical encrypted fields
from essencia.fields.medical_encrypted_fields import (
    EncryptedMedicalHistory, EncryptedPrescription, EncryptedDiagnosis,
    EncryptedTreatmentNotes, EncryptedMentalHealthAssessment, EncryptedLabResults,
    validate_encrypted_medical_history, validate_encrypted_prescription,
    validate_encrypted_diagnosis, validate_encrypted_treatment_notes,
    validate_encrypted_mental_health_assessment, validate_encrypted_lab_results
)

# Re-export commonly used fields
Date = DefaultDate
DateTime = DefaultDateTime

# Export all field types
__all__ = [
    # Base field types
    'DefaultDate', 'DefaultDateTime', 'OptionalDate', 'OptionalDateTime',
    'OptionalString',
    'Date', 'DateTime',
    
    # Encrypted field types
    'EncryptedStr', 'EncryptedCPF', 'EncryptedRG', 'EncryptedMedicalData',
    'CPFField', 'RGField', 'MedicalDataField',
    
    # Medical encrypted field types
    'EncryptedMedicalHistory', 'EncryptedPrescription', 'EncryptedDiagnosis',
    'EncryptedTreatmentNotes', 'EncryptedMentalHealthAssessment', 'EncryptedLabResults',
    
    # Validators
    'validate_encrypted_cpf', 'validate_encrypted_rg', 'validate_encrypted_medical_data',
    'validate_encrypted_medical_history', 'validate_encrypted_prescription',
    'validate_encrypted_diagnosis', 'validate_encrypted_treatment_notes',
    'validate_encrypted_mental_health_assessment', 'validate_encrypted_lab_results',
    
    # Helper functions
    'today', 'now', 'string_to_date', 'parse_date_to_datetime', 'slice_if_not_none'
]