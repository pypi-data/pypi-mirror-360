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
    calculate_bmi,
    calculate_bsa,
    calculate_gfr,
    categorize_bmi,
    categorize_blood_pressure,
)

from .vital_signs_analyzer import (
    VitalSignTrend,
    VitalSignsAnalyzer,
)

from .drug_interactions import (
    InteractionSeverity,
    InteractionMechanism,
    DrugInteraction,
    DrugInteractionDatabase,
    DrugInteractionChecker,
    ContraindicationChecker,
)

__all__ = [
    # Calculations
    'calculate_bmi',
    'calculate_bsa',
    'calculate_gfr',
    'categorize_bmi',
    'categorize_blood_pressure',
    
    # Vital Signs Analysis
    'VitalSignTrend',
    'VitalSignsAnalyzer',
    
    # Drug Interactions
    'InteractionSeverity',
    'InteractionMechanism',
    'DrugInteraction',
    'DrugInteractionDatabase',
    'DrugInteractionChecker',
    'ContraindicationChecker',
]