"""Medical domain models for patient care management.

This module contains core models for managing medical records, prescriptions,
and patient-doctor relationships in a healthcare application.
"""
import datetime
from datetime import date
import io
from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import Annotated, Optional, Union, List, Any

from pydantic import BaseModel, BeforeValidator, computed_field, Field, field_validator
from pydantic import ValidationError

from .bases import MongoModel, StrEnum
from .. import fields as fd
from .people import Patient


class DoctorPatient(MongoModel):
    """Base class for doctor-patient relationship records.
    
    Attributes:
        doctor_key: Identifier for the treating doctor
        patient_key: Identifier for the patient
        created: Timestamp when record was created
        date: Date of the medical interaction
    """
    doctor_key: str = Field(default='admin')
    patient_key: str
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    date: fd.DefaultDate = Field(default_factory=datetime.date.today)
    
    def __lt__(self, other):
        """Compare records by date for sorting.

        Args:
            other: Another DoctorPatient instance to compare with
            
        Returns:
            bool: True if this record's date is earlier than the other
        """
        return self.date < other.date
    
    @property
    def patient(self):
        """Get the associated Patient object.

        Returns:
            Patient: The patient linked to this record
        """
        return self.model_extra.get('patient')

    @patient.setter
    def patient(self, patient: Patient):
        """Set the associated Patient object.

        Args:
            patient: Patient instance to associate with this record
        """
        self.model_extra.setdefault('patient', patient)
        

class Visit(DoctorPatient):
    """Medical visit record tracking patient consultation details.
    
    Attributes:
        type: Classification of visit type (Consulta/Retorno)
        main_complaint: Primary reason for the visit
        intro: Contextual information about the visit
        subjective: Patient-reported symptoms
        objective: Clinician-observed findings  
        assessment: Professional diagnosis (text, maintained for compatibility)
        plan: Treatment plan
        diagnoses: List of structured ICD-11 diagnoses
    """
    COLLECTION_NAME = 'visit'
    
    class VisitType(StrEnum):
        """Classification of medical visit types."""
        C = 'Consulta'
        R = 'Retorno'
  
    type: VisitType = Field(default=VisitType.C)
    main_complaint: Optional[str] = None
    intro: Optional[str] = None
    context: Optional[str] = None
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None  # Mantido para compatibilidade
    plan: Optional[str] = None
    
    # Novos campos para diagnósticos CID-11
    diagnoses: List[dict] = Field(default_factory=list, description="Lista de diagnósticos CID-11")
    
    # Timer fields
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    duration_minutes: Optional[int] = None
    
    # Draft/editing status
    is_draft: bool = Field(default=True)  # True when being edited, False when finalized
    
    # Prescription tracking
    prescription_keys: List[str] = Field(default_factory=list, description="Keys das prescrições desta consulta")
    
    def __str__(self):
        """Format visit information for display.
        
        Returns:
            str: Human-friendly string representation
        """
        return f'{self.type.value}: {self.date}'
    
    def start_timer(self):
        """Start the visit timer."""
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.duration_minutes = None
    
    def finish_timer(self):
        """Finish the visit and calculate duration."""
        if self.start_time:
            self.end_time = datetime.datetime.now()
            
            # Calculate duration in minutes
            total_duration = (self.end_time - self.start_time).total_seconds() / 60
            self.duration_minutes = int(total_duration)
    
    def get_elapsed_time(self) -> Optional[datetime.timedelta]:
        """Get current elapsed time for active visits.
        
        Returns:
            timedelta: Elapsed time or None if not started
        """
        if self.start_time and not self.end_time:
            return datetime.datetime.now() - self.start_time
        return None
    
    @property
    def status(self) -> str:
        """Get visit status.
        
        Returns:
            str: Status description
        """
        if self.is_draft:
            return "Rascunho"
        elif self.start_time and not self.end_time:
            return "Em andamento"
        elif self.end_time:
            return "Finalizada"
        else:
            return "Não iniciada"
    
    @property
    def primary_diagnosis(self) -> Optional[dict]:
        """Get the primary ICD-11 diagnosis.
        
        Returns:
            dict: Primary diagnosis record or None
        """
        for diagnosis in self.diagnoses:
            if diagnosis.get('is_primary', False):
                return diagnosis
        return None
    
    @property
    def diagnosis_summary(self) -> str:
        """Get formatted summary of all diagnoses.
        
        Returns:
            str: Summary of diagnoses for display
        """
        if not self.diagnoses:
            return self.assessment or "Sem diagnóstico registrado"
        
        # Simple summary without dependency on diagnosis model
        codes = [d.get('icd_code', 'N/A') for d in self.diagnoses]
        return f"Diagnósticos CID-11: {', '.join(codes)}"
    
    def add_diagnosis(self, icd_code: str, is_primary: bool = False, 
                     specifiers: List[str] = None, notes: str = None) -> bool:
        """Add an ICD-11 diagnosis to the visit.
        
        Args:
            icd_code: ICD-11 code
            is_primary: Whether this is the primary diagnosis
            specifiers: List of applicable specifiers
            notes: Additional notes
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Se é diagnóstico principal, remove flag dos outros
            if is_primary:
                for diag in self.diagnoses:
                    diag['is_primary'] = False
            
            # Cria novo diagnóstico
            diagnosis_data = {
                'icd_code': icd_code,
                'is_primary': is_primary,
                'specifiers': specifiers or [],
                'notes': notes,
                'created_at': datetime.datetime.now().isoformat()
            }
            
            # Adiciona à lista
            self.diagnoses.append(diagnosis_data)
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar diagnóstico: {e}")
            return False
    
    def remove_diagnosis(self, icd_code: str) -> bool:
        """Remove an ICD-11 diagnosis from the visit.
        
        Args:
            icd_code: ICD-11 code to remove
            
        Returns:
            bool: True if removed successfully
        """
        try:
            initial_count = len(self.diagnoses)
            self.diagnoses = [d for d in self.diagnoses if d.get('icd_code') != icd_code]
            return len(self.diagnoses) < initial_count
        except Exception as e:
            print(f"Erro ao remover diagnóstico: {e}")
            return False
    
    def get_diagnosis_codes(self) -> List[str]:
        """Get list of all ICD-11 codes in this visit.
        
        Returns:
            List[str]: List of ICD-11 codes
        """
        return [d.get('icd_code', '') for d in self.diagnoses if d.get('icd_code')]
    
    def has_diagnosis(self, icd_code: str) -> bool:
        """Check if visit has a specific diagnosis.
        
        Args:
            icd_code: ICD-11 code to check
            
        Returns:
            bool: True if diagnosis exists
        """
        return icd_code in self.get_diagnosis_codes()

    
    
class MedicationDatabase(MongoModel):
    """Database of registered medications for quick search and selection.
    
    Attributes:
        name: Commercial name of medication
        active_sets: List of active ingredient compositions
        manufacturer: Pharmaceutical company
        registration_number: ANVISA registration number
        controlled: Whether medication is controlled
        generic_alternatives: Keys of generic alternatives
        therapeutic_class: Therapeutic classification
        contraindications: List of contraindications
        interactions: Keys of medications with interactions
    """
    COLLECTION_NAME = 'medication_database'
    
    name: str
    active_sets: List['Medication.ActiveSet']  # Reuse ActiveSet from Medication
    manufacturer: str
    country_of_origin: Optional[str] = None  # Country where medication is manufactured
    registration_number: Optional[str] = None
    controlled: bool = Field(default=False)
    generic_alternatives: List[str] = Field(default_factory=list)
    therapeutic_class: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    interactions: List[str] = Field(default_factory=list)
    dosage_forms: List[str] = Field(default_factory=list)  # Available forms (comprimido, cápsula, etc)
    common_dosages: List[float] = Field(default_factory=list)  # Common strengths
    
    def __str__(self):
        """Format medication database entry for display."""
        active_ingredients = " + ".join([a.name for a in self.active_sets])
        return f"{self.name} ({active_ingredients})"


class Medication(MongoModel):
    """Pharmaceutical product with active ingredients and dosage information.

    Attributes:
        name: Brand name of medication
        active_sets: List of active ingredient compositions
        unity: Dosage form and units 
        quantity: Total amount in package
    """
    COLLECTION_NAME = 'medication'
    
    name: Optional[str] = None
    
    class ActiveSet(BaseModel):
        """Active ingredient composition and strength.

        Attributes:
            name: Name of active ingredient
            strength: Amount per dose
            unit: Measurement unit for strength
        """
        class Unit(Enum):
            """Valid units for medication strength."""
            MG = 'mg'
            G = 'g'
            MCG = 'mcg'
            MG_ML = 'mg/ml'
            
        name: str
        strength: Decimal
        unit: Unit = Unit.MG
        
        def __str__(self):
            """Format strength information for display.
            
            Returns:
                str: Human-friendly ingredient strength representation
            """
            return f'{self.name} {self.strength}{self.unit.value}'
    
    @field_validator('active_sets')
    @classmethod
    def validate_active_sets(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one active ingredient is required')
        return v
    
    active_sets: List[ActiveSet]
    
    class Unity(BaseModel):
        """Dosage form and unit conversion logic."""
        
        def __call__(self, quantity: Union[int, float]):
            if self.is_liquid:
                return 'ml'
            elif quantity > 1:
                return self.dosage_form.value + 's'
            return self.dosage_form.value
        
        class DosageForm(StrEnum):
            """Pharmaceutical dosage forms."""
            CO = 'comprimido'
            CA = 'cápsula'
            DR = 'drágea'
            ML = 'ml'
            RD = 'gota'
            MD = 'microgota'
            
            def __float__(self):
                if self.name == 'RD':
                    return 1/20
                elif self.name == 'MD':
                    return 1/60
                return 1.0
            
            @property
            def is_liquid(self):
                """Check if dosage form is liquid.
                
                Returns:
                    bool: True for liquid forms (drops, milliliters)
                """
                return True if self.name in ['RD', 'MD', 'ML'] else False
            
        dosage_form: DosageForm = Field(default=DosageForm.CO)
        extended_release: bool = Field(default=False)
        grooved: bool = Field(default=False)
        
        @property
        def is_liquid(self):
            """Check if medication is in liquid form.
            
            Returns:
                bool: True if dosage form is liquid
            """
            return True if self.dosage_form.name in ['ML', 'RD', 'MD'] else False
        
        def __str__(self):
            """Format dosage form for display.
            
            Returns:
                str: Localized dosage form description
            """
            return f'{self.dosage_form.value}' if not self.is_liquid else 'ml'
        
    
    unity: Unity = Field(default_factory=Unity)
    quantity: float = Field(default=30.0)
    
    @property
    def total_doses(self):
        """Calculate total number of doses in package.
        
        Returns:
            int: Rounded up total doses based on quantity and dosage form
        """
        import math
        return math.ceil(self.quantity / float(self.unity.dosage_form))
    
    def __str__(self):
        """Format complete medication information for display.
        
        Returns:
            str: Human-friendly medication description
        """
        with io.StringIO() as buf:
            if self.name:
                buf.write(f'{self.name} ')
                buf.write(f'({" + ".join([str(i) for i in self.active_sets])}) ')
                buf.write(f'{int(self.quantity)} {self.unity(self.quantity)}')
            return buf.getvalue()
    
    
class Prescription(DoctorPatient):
    """Medical prescription order with administration details.
    
    Attributes:
        medication: Prescribed medication
        start_date: When treatment should begin
        end_date: When treatment should conclude
        frequency: Administration schedule
        route: Method of administration
        dosage: Amount per dose
        duration: Total treatment duration
    """
    COLLECTION_NAME = 'prescription'
    
    medication: Medication
    start_date: fd.DefaultDate = Field(default_factory=datetime.date.today)
    end_date: Optional[date] = None
    
    # Visit and status tracking
    visit_key: Optional[str] = Field(default=None, description="Key da consulta onde foi prescrita")
    status: str = Field(default="active", description="Status: active, suspended, completed")
    renewal_of: Optional[str] = Field(default=None, description="Key da prescrição anterior (renovação)")
    
    class Frequency(BaseModel):
        """Medication administration schedule.
        
        Attributes:
            repetitions: Number of times per period
            period: Time interval between doses
        """
        repetitions: int = Field(default=1)
        
        class Period(StrEnum):
            """Valid time periods for dosage frequency."""
            H = 'Hora'
            D = 'Dia'
            W = 'Semana'
            M = 'Mês'
            
            def __float__(self):
                """Convert period to days for calculations.
                
                Returns:
                    float: Equivalent duration in days
                """
                if self.name == 'H':
                    return 1/24
                elif self.name == 'D':
                    return 1.0
                elif self.name == 'W':
                    return 7.0
                elif self.name == 'M':
                    return 30.0
                elif self.name == 'A':
                    return 365.0
                raise ValueError('erro no calculo do periodo')
            
        period: Period = Field(default=Period.D)
        
        def __float__(self):
            """Calculate daily dosage frequency.
            
            Returns:
                float: Doses per day
            """
            return  self.repetitions / float(self.period)
        
    frequency: Frequency = Field(default_factory=Frequency)
    
    class Route(StrEnum):
        """Administration route options."""
        OR = 'Oral'
        IM = 'Intramuscular'
        EV = 'Endovenosa'
        NS = 'Nasal'
        OF = 'Oftálmica'
        OT = 'Otológica'
        RE = 'Retal'

    route: Route = Field(default=Route.OR)
    
    class Dosage(BaseModel):
        """Medication quantity per dose."""
        value: float = Field(default=1.0)
        
    dosage: Dosage = Field(default_factory=Dosage)
    duration: Optional[int] = None
    
    @property
    def doses_needed(self) -> Optional[int]:
        """Calculate total doses required for treatment.
        
        Returns:
            Optional[int]: Total doses if duration is set, else None
        """
        if self.duration:
            import math
            return math.ceil(float(self.frequency) * self.dosage.value * self.duration)
        return None
    
    @property
    def period_as_float(self):
        """Get frequency period in days.
        
        Returns:
            float: Period duration converted to days
        """
        return float(self.frequency.period)
    
    @computed_field
    @property
    def medication_key(self) -> str:
        """Get the medication's unique identifier.
        
        Returns:
            str: Key of the associated medication
        """
        return self.medication.key
    
    @property
    def boxes(self):
        """Calculate packaging needed for full treatment.
        
        Returns:
            int: Number of medication packages required
        """
        if self.doses_needed and self.medication.total_doses:
            import math
            return math.ceil(self.doses_needed / self.medication.total_doses)
        return 1