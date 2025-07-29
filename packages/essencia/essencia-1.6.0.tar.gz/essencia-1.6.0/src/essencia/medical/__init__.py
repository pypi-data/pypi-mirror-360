"""
Essencia Medical Module - Healthcare-specific functionality.

This module provides medical domain primitives and utilities:
- Medical calculations and scoring
- Clinical standards integration (ICD-11, SNOMED-CT, LOINC)
- Healthcare data validation
- Medical terminology and units
- Clinical decision support tools
"""

from .calculations import (
    BMICalculator,
    BSACalculator,
    GFRCalculator,
    DosageCalculator,
    ClinicalScore,
    VitalSignsAnalyzer,
    calculate_bmi,
    calculate_bsa,
    calculate_gfr,
    calculate_age,
    calculate_gestational_age,
)

from .standards import (
    ICD11Code,
    SNOMEDConcept,
    LOINCCode,
    MedicalCodeSystem,
    CodeValidator,
    TerminologyMapper,
    get_icd11_validator,
    get_snomed_validator,
    get_loinc_validator,
)

from .validators import (
    MedicalRecordValidator,
    VitalSignsValidator,
    MedicationValidator,
    AllergyValidator,
    LabResultValidator,
    validate_blood_pressure,
    validate_heart_rate,
    validate_temperature,
    validate_weight,
    validate_height,
)

from .units import (
    MedicalUnit,
    UnitConverter,
    WeightUnit,
    HeightUnit,
    TemperatureUnit,
    PressureUnit,
    ConcentrationUnit,
    convert_weight,
    convert_height,
    convert_temperature,
    convert_pressure,
)

from .clinical import (
    ClinicalGuideline,
    ClinicalPathway,
    TreatmentProtocol,
    MedicalAlert,
    DrugInteractionChecker,
    ContraindicationChecker,
    ClinicalDecisionSupport,
)

from .privacy import (
    PHIProtector,
    MedicalDataAnonymizer,
    ConsentManager,
    AuditTrailManager,
    anonymize_patient_data,
    check_consent,
    log_phi_access,
)

__all__ = [
    # Calculations
    'BMICalculator',
    'BSACalculator',
    'GFRCalculator',
    'DosageCalculator',
    'ClinicalScore',
    'VitalSignsAnalyzer',
    'calculate_bmi',
    'calculate_bsa',
    'calculate_gfr',
    'calculate_age',
    'calculate_gestational_age',
    
    # Standards
    'ICD11Code',
    'SNOMEDConcept',
    'LOINCCode',
    'MedicalCodeSystem',
    'CodeValidator',
    'TerminologyMapper',
    'get_icd11_validator',
    'get_snomed_validator',
    'get_loinc_validator',
    
    # Validators
    'MedicalRecordValidator',
    'VitalSignsValidator',
    'MedicationValidator',
    'AllergyValidator',
    'LabResultValidator',
    'validate_blood_pressure',
    'validate_heart_rate',
    'validate_temperature',
    'validate_weight',
    'validate_height',
    
    # Units
    'MedicalUnit',
    'UnitConverter',
    'WeightUnit',
    'HeightUnit',
    'TemperatureUnit',
    'PressureUnit',
    'ConcentrationUnit',
    'convert_weight',
    'convert_height',
    'convert_temperature',
    'convert_pressure',
    
    # Clinical
    'ClinicalGuideline',
    'ClinicalPathway',
    'TreatmentProtocol',
    'MedicalAlert',
    'DrugInteractionChecker',
    'ContraindicationChecker',
    'ClinicalDecisionSupport',
    
    # Privacy
    'PHIProtector',
    'MedicalDataAnonymizer',
    'ConsentManager',
    'AuditTrailManager',
    'anonymize_patient_data',
    'check_consent',
    'log_phi_access',
]