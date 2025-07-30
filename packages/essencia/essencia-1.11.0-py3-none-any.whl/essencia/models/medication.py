"""
Medication management models for healthcare applications.
"""
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set

from pydantic import Field, validator

from essencia.core.exceptions import ValidationError
from essencia.fields import EncryptedFloat, EncryptedStr
from essencia.models.base import BaseModel, MongoModel


class MedicationCategory(str, Enum):
    """Categories of medications."""
    
    ANALGESIC = "analgesic"
    ANTIBIOTIC = "antibiotic"
    ANTIDEPRESSANT = "antidepressant"
    ANTIPSYCHOTIC = "antipsychotic"
    ANXIOLYTIC = "anxiolytic"
    ANTIHYPERTENSIVE = "antihypertensive"
    ANTIDIABETIC = "antidiabetic"
    ANTICOAGULANT = "anticoagulant"
    ANTICONVULSANT = "anticonvulsant"
    ANTI_INFLAMMATORY = "anti_inflammatory"
    BRONCHODILATOR = "bronchodilator"
    DIURETIC = "diuretic"
    HORMONE = "hormone"
    IMMUNOSUPPRESSANT = "immunosuppressant"
    MUSCLE_RELAXANT = "muscle_relaxant"
    PROTON_PUMP_INHIBITOR = "proton_pump_inhibitor"
    STATIN = "statin"
    STIMULANT = "stimulant"
    VITAMIN = "vitamin"
    OTHER = "other"


class DosageForm(str, Enum):
    """Forms of medication dosage."""
    
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    PATCH = "patch"
    CREAM = "cream"
    OINTMENT = "ointment"
    GEL = "gel"
    DROPS = "drops"
    SPRAY = "spray"
    INHALER = "inhaler"
    SUPPOSITORY = "suppository"
    IMPLANT = "implant"
    OTHER = "other"


class RouteOfAdministration(str, Enum):
    """Routes of medication administration."""
    
    ORAL = "oral"
    SUBLINGUAL = "sublingual"
    BUCCAL = "buccal"
    RECTAL = "rectal"
    VAGINAL = "vaginal"
    TOPICAL = "topical"
    TRANSDERMAL = "transdermal"
    INHALATION = "inhalation"
    NASAL = "nasal"
    OPHTHALMIC = "ophthalmic"
    OTIC = "otic"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    INTRADERMAL = "intradermal"
    EPIDURAL = "epidural"
    INTRATHECAL = "intrathecal"


class FrequencyUnit(str, Enum):
    """Units for medication frequency."""
    
    DAILY = "daily"
    HOURLY = "hourly"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"


class PrescriptionStatus(str, Enum):
    """Status of a prescription."""
    
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"


class AdherenceStatus(str, Enum):
    """Medication adherence status."""
    
    TAKEN = "taken"
    MISSED = "missed"
    SKIPPED = "skipped"
    DELAYED = "delayed"
    PARTIAL = "partial"


class MedicationDatabase(MongoModel):
    """Database of available medications."""
    
    # Basic information
    name: str = Field(..., description="Generic name of the medication")
    brand_names: List[str] = Field(default_factory=list, description="Brand/trade names")
    active_ingredients: List[str] = Field(..., description="Active ingredients")
    category: MedicationCategory
    
    # Formulation
    available_forms: List[DosageForm] = Field(..., description="Available dosage forms")
    available_strengths: List[str] = Field(..., description="Available strengths (e.g., '500mg', '10mg/ml')")
    
    # Clinical information
    indications: List[str] = Field(default_factory=list, description="Medical conditions treated")
    contraindications: List[str] = Field(default_factory=list, description="Conditions where drug should not be used")
    warnings: List[str] = Field(default_factory=list, description="Important warnings")
    side_effects: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Side effects by frequency (common, uncommon, rare)"
    )
    
    # Interactions
    drug_interactions: List[str] = Field(default_factory=list, description="Known drug interactions")
    food_interactions: List[str] = Field(default_factory=list, description="Food/dietary interactions")
    
    # Regulatory
    controlled_substance: bool = Field(False, description="Is controlled substance")
    controlled_schedule: Optional[str] = Field(None, description="DEA schedule if controlled")
    requires_prescription: bool = Field(True, description="Requires prescription")
    black_box_warning: Optional[str] = Field(None, description="FDA black box warning if any")
    
    # Additional info
    manufacturer: Optional[str] = None
    atc_code: Optional[str] = Field(None, description="WHO ATC classification code")
    
    class Settings:
        collection_name = "medication_database"
        indexes = [
            ("name", 1),
            ("brand_names", 1),
            ("category", 1),
            ("active_ingredients", 1),
        ]


class Medication(MongoModel):
    """Patient-specific medication record."""
    
    patient_id: str = Field(..., description="Patient identifier")
    medication_db_id: Optional[str] = Field(None, description="Reference to MedicationDatabase")
    
    # Medication details
    name: str = Field(..., description="Medication name")
    strength: str = Field(..., description="Strength (e.g., '500mg')")
    form: DosageForm
    route: RouteOfAdministration
    
    # Prescription details
    prescribed_by: str = Field(..., description="Prescriber ID")
    prescribed_date: datetime
    prescription_number: Optional[str] = None
    
    # Dosing
    dosage_amount: float = Field(..., gt=0, description="Amount per dose")
    dosage_unit: str = Field(..., description="Unit (tablets, ml, etc.)")
    frequency_value: int = Field(..., gt=0)
    frequency_unit: FrequencyUnit
    frequency_details: Optional[str] = Field(None, description="Additional frequency details")
    
    # Schedule
    scheduled_times: List[time] = Field(default_factory=list, description="Daily scheduled times")
    take_with_food: Optional[bool] = None
    special_instructions: Optional[EncryptedStr] = None
    
    # Duration
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    refills_authorized: int = Field(0, ge=0)
    refills_remaining: int = Field(0, ge=0)
    
    # Status
    status: PrescriptionStatus = Field(PrescriptionStatus.ACTIVE)
    discontinuation_date: Optional[datetime] = None
    discontinuation_reason: Optional[EncryptedStr] = None
    
    # Clinical info
    indication: Optional[EncryptedStr] = Field(None, description="Reason for prescription")
    notes: Optional[EncryptedStr] = None
    
    class Settings:
        collection_name = "medications"
        indexes = [
            ("patient_id", -1),
            ("status", 1),
            ("prescribed_date", -1),
            [("patient_id", 1), ("status", 1)],
        ]
    
    @validator("end_date")
    def validate_dates(cls, v, values):
        """Ensure end date is after start date."""
        if v and "start_date" in values and v < values["start_date"]:
            raise ValidationError("End date must be after start date")
        return v
    
    def is_active(self) -> bool:
        """Check if medication is currently active."""
        if self.status != PrescriptionStatus.ACTIVE:
            return False
        
        now = datetime.utcnow()
        if now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_daily_schedule(self) -> List[Dict]:
        """Get daily medication schedule."""
        schedule = []
        
        if self.scheduled_times:
            for scheduled_time in self.scheduled_times:
                schedule.append({
                    "time": scheduled_time,
                    "dosage": f"{self.dosage_amount} {self.dosage_unit}",
                    "instructions": self.special_instructions,
                    "take_with_food": self.take_with_food
                })
        else:
            # Generate schedule based on frequency
            if self.frequency_unit == FrequencyUnit.DAILY:
                times_per_day = self.frequency_value
                interval_hours = 24 // times_per_day
                
                for i in range(times_per_day):
                    hour = 8 + (i * interval_hours)  # Start at 8 AM
                    if hour >= 24:
                        hour = hour - 24
                    
                    schedule.append({
                        "time": time(hour=hour),
                        "dosage": f"{self.dosage_amount} {self.dosage_unit}",
                        "instructions": self.special_instructions,
                        "take_with_food": self.take_with_food
                    })
        
        return sorted(schedule, key=lambda x: x["time"])


class MedicationAdherence(MongoModel):
    """Track medication adherence/compliance."""
    
    patient_id: str
    medication_id: str = Field(..., description="Reference to Medication")
    
    scheduled_datetime: datetime = Field(..., description="When medication should be taken")
    actual_datetime: Optional[datetime] = Field(None, description="When actually taken")
    
    status: AdherenceStatus = Field(AdherenceStatus.MISSED)
    dosage_taken: Optional[float] = Field(None, description="Actual dosage taken")
    
    notes: Optional[EncryptedStr] = None
    recorded_by: Optional[str] = Field(None, description="Who recorded (patient, caregiver, etc.)")
    
    # Side effects experienced
    side_effects_reported: List[str] = Field(default_factory=list)
    severity: Optional[str] = Field(None, description="Severity of side effects if any")
    
    class Settings:
        collection_name = "medication_adherence"
        indexes = [
            ("patient_id", -1),
            ("medication_id", -1),
            ("scheduled_datetime", -1),
            [("patient_id", 1), ("scheduled_datetime", -1)],
        ]
    
    def calculate_delay(self) -> Optional[timedelta]:
        """Calculate delay in taking medication."""
        if self.actual_datetime and self.status in [AdherenceStatus.TAKEN, AdherenceStatus.DELAYED]:
            return self.actual_datetime - self.scheduled_datetime
        return None


class DrugInteraction(BaseModel):
    """Model for drug-drug interactions."""
    
    drug1: str = Field(..., description="First drug name")
    drug2: str = Field(..., description="Second drug name")
    
    severity: str = Field(..., description="Interaction severity (minor, moderate, major, contraindicated)")
    description: str = Field(..., description="Description of the interaction")
    mechanism: Optional[str] = Field(None, description="Mechanism of interaction")
    
    management: str = Field(..., description="How to manage the interaction")
    monitoring: Optional[List[str]] = Field(default_factory=list, description="What to monitor")
    
    references: List[str] = Field(default_factory=list, description="Scientific references")


class MedicationService:
    """Service for medication-related operations."""
    
    @staticmethod
    async def check_interactions(medications: List[Medication]) -> List[DrugInteraction]:
        """Check for drug interactions between medications."""
        interactions = []
        
        # This would typically query a drug interaction database
        # For now, return empty list as placeholder
        return interactions
    
    @staticmethod
    async def calculate_adherence_rate(
        patient_id: str,
        medication_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, float]:
        """Calculate medication adherence rate."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = {
            "patient_id": patient_id,
            "scheduled_datetime": {"$gte": since_date}
        }
        
        if medication_id:
            query["medication_id"] = medication_id
        
        # Query adherence records
        adherence_records = await MedicationAdherence.find_many(query)
        
        if not adherence_records:
            return {"adherence_rate": 0.0, "doses_taken": 0, "doses_scheduled": 0}
        
        taken_count = sum(1 for record in adherence_records 
                         if record.status == AdherenceStatus.TAKEN)
        total_count = len(adherence_records)
        
        adherence_rate = (taken_count / total_count * 100) if total_count > 0 else 0.0
        
        return {
            "adherence_rate": round(adherence_rate, 1),
            "doses_taken": taken_count,
            "doses_scheduled": total_count,
            "missed_doses": total_count - taken_count
        }
    
    @staticmethod
    def generate_medication_schedule(
        medications: List[Medication],
        date: Optional[datetime] = None
    ) -> List[Dict]:
        """Generate daily medication schedule for a patient."""
        if date is None:
            date = datetime.utcnow()
        
        schedule = []
        
        for med in medications:
            if not med.is_active():
                continue
            
            daily_schedule = med.get_daily_schedule()
            
            for dose_time in daily_schedule:
                scheduled_datetime = datetime.combine(date.date(), dose_time["time"])
                
                schedule.append({
                    "medication_id": str(med.id),
                    "medication_name": med.name,
                    "strength": med.strength,
                    "scheduled_time": scheduled_datetime,
                    "dosage": dose_time["dosage"],
                    "route": med.route,
                    "instructions": dose_time.get("instructions"),
                    "take_with_food": dose_time.get("take_with_food")
                })
        
        # Sort by scheduled time
        return sorted(schedule, key=lambda x: x["scheduled_time"])
    
    @staticmethod
    def check_duplicate_medications(
        medications: List[Medication]
    ) -> List[Dict[str, List[Medication]]]:
        """Check for duplicate or similar medications."""
        duplicates = {}
        
        # Group by medication name (simplified check)
        for med in medications:
            if med.status == PrescriptionStatus.ACTIVE:
                name_key = med.name.lower()
                if name_key not in duplicates:
                    duplicates[name_key] = []
                duplicates[name_key].append(med)
        
        # Return only groups with more than one medication
        return {name: meds for name, meds in duplicates.items() if len(meds) > 1}
    
    @staticmethod
    def calculate_refill_date(medication: Medication) -> Optional[datetime]:
        """Calculate when medication needs to be refilled."""
        if medication.status != PrescriptionStatus.ACTIVE:
            return None
        
        if medication.refills_remaining == 0:
            return None
        
        # Calculate based on dosage and frequency
        doses_per_day = medication.frequency_value
        if medication.frequency_unit == FrequencyUnit.HOURLY:
            doses_per_day = 24 // medication.frequency_value
        elif medication.frequency_unit == FrequencyUnit.WEEKLY:
            doses_per_day = medication.frequency_value / 7
        elif medication.frequency_unit == FrequencyUnit.MONTHLY:
            doses_per_day = medication.frequency_value / 30
        
        # Assume 30-day supply
        days_supply = 30
        refill_date = medication.start_date + timedelta(days=days_supply)
        
        # Adjust for already used refills
        used_refills = medication.refills_authorized - medication.refills_remaining
        if used_refills > 0:
            refill_date += timedelta(days=days_supply * used_refills)
        
        return refill_date