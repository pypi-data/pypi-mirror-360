"""
Vital signs models for healthcare applications.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from pydantic import Field, validator

from essencia.core.exceptions import ValidationError
from essencia.fields import EncryptedFloat, EncryptedInt, EncryptedStr
from essencia.models.base import BaseModel, MongoModel


class VitalSignCategory(str, Enum):
    """Categories for vital signs."""
    
    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORY = "respiratory"
    TEMPERATURE = "temperature"
    NEUROLOGICAL = "neurological"
    METABOLIC = "metabolic"
    PAIN = "pain"


class BloodPressureCategory(str, Enum):
    """Blood pressure categories based on AHA guidelines."""
    
    NORMAL = "normal"
    ELEVATED = "elevated"
    STAGE1_HYPERTENSION = "stage1_hypertension"
    STAGE2_HYPERTENSION = "stage2_hypertension"
    HYPERTENSIVE_CRISIS = "hypertensive_crisis"
    HYPOTENSION = "hypotension"


class HeartRateCategory(str, Enum):
    """Heart rate categories."""
    
    BRADYCARDIA = "bradycardia"
    NORMAL = "normal"
    TACHYCARDIA = "tachycardia"
    SEVERE_TACHYCARDIA = "severe_tachycardia"


class OxygenSaturationCategory(str, Enum):
    """Oxygen saturation categories."""
    
    NORMAL = "normal"
    MILD_HYPOXEMIA = "mild_hypoxemia"
    MODERATE_HYPOXEMIA = "moderate_hypoxemia"
    SEVERE_HYPOXEMIA = "severe_hypoxemia"


class TemperatureCategory(str, Enum):
    """Body temperature categories."""
    
    HYPOTHERMIA = "hypothermia"
    NORMAL = "normal"
    FEVER = "fever"
    HIGH_FEVER = "high_fever"
    HYPERPYREXIA = "hyperpyrexia"


class VitalSign(MongoModel):
    """Base model for individual vital signs."""
    
    patient_id: str = Field(..., description="Patient identifier")
    measured_by: Optional[str] = Field(None, description="Healthcare provider who took the measurement")
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    device_id: Optional[str] = Field(None, description="Device used for measurement")
    notes: Optional[EncryptedStr] = Field(None, description="Clinical notes")
    is_automated: bool = Field(False, description="Whether measurement was automated")
    
    class Settings:
        collection_name = "vital_signs"
        indexes = [
            ("patient_id", -1),
            ("measured_at", -1),
            [("patient_id", 1), ("measured_at", -1)],
        ]


class BloodPressure(VitalSign):
    """Blood pressure measurement model."""
    
    systolic: EncryptedInt = Field(..., ge=40, le=300, description="Systolic pressure in mmHg")
    diastolic: EncryptedInt = Field(..., ge=20, le=200, description="Diastolic pressure in mmHg")
    pulse_pressure: Optional[int] = Field(None, description="Pulse pressure (systolic - diastolic)")
    mean_arterial_pressure: Optional[float] = Field(None, description="MAP = (2*diastolic + systolic)/3")
    arm: Optional[str] = Field("left", description="Arm used for measurement")
    position: Optional[str] = Field("sitting", description="Patient position during measurement")
    category: Optional[BloodPressureCategory] = None
    
    @validator("diastolic")
    def validate_pressures(cls, v, values):
        """Ensure diastolic is less than systolic."""
        if "systolic" in values and v >= values["systolic"]:
            raise ValidationError("Diastolic pressure must be less than systolic pressure")
        return v
    
    def model_post_init(self, __context):
        """Calculate derived values after initialization."""
        super().model_post_init(__context)
        if self.systolic and self.diastolic:
            self.pulse_pressure = self.systolic - self.diastolic
            self.mean_arterial_pressure = round((2 * self.diastolic + self.systolic) / 3, 1)
            self.category = self.categorize()
    
    def categorize(self) -> BloodPressureCategory:
        """Categorize blood pressure based on AHA guidelines."""
        if self.systolic < 90 or self.diastolic < 60:
            return BloodPressureCategory.HYPOTENSION
        elif self.systolic >= 180 or self.diastolic >= 120:
            return BloodPressureCategory.HYPERTENSIVE_CRISIS
        elif self.systolic >= 140 or self.diastolic >= 90:
            return BloodPressureCategory.STAGE2_HYPERTENSION
        elif self.systolic >= 130 or self.diastolic >= 80:
            return BloodPressureCategory.STAGE1_HYPERTENSION
        elif self.systolic >= 120:
            return BloodPressureCategory.ELEVATED
        else:
            return BloodPressureCategory.NORMAL
    
    def is_critical(self) -> bool:
        """Check if blood pressure is in critical range."""
        return self.category in [
            BloodPressureCategory.HYPERTENSIVE_CRISIS,
            BloodPressureCategory.HYPOTENSION
        ]


class HeartRate(VitalSign):
    """Heart rate measurement model."""
    
    rate: EncryptedInt = Field(..., ge=20, le=300, description="Heart rate in beats per minute")
    rhythm: Optional[str] = Field("regular", description="Heart rhythm description")
    category: Optional[HeartRateCategory] = None
    
    def model_post_init(self, __context):
        """Calculate category after initialization."""
        super().model_post_init(__context)
        self.category = self.categorize()
    
    def categorize(self) -> HeartRateCategory:
        """Categorize heart rate."""
        if self.rate < 60:
            return HeartRateCategory.BRADYCARDIA
        elif self.rate <= 100:
            return HeartRateCategory.NORMAL
        elif self.rate <= 150:
            return HeartRateCategory.TACHYCARDIA
        else:
            return HeartRateCategory.SEVERE_TACHYCARDIA
    
    def is_critical(self) -> bool:
        """Check if heart rate is in critical range."""
        return self.rate < 40 or self.rate > 150


class Temperature(VitalSign):
    """Body temperature measurement model."""
    
    value: EncryptedFloat = Field(..., ge=30.0, le=45.0, description="Temperature value")
    unit: str = Field("celsius", description="Temperature unit (celsius or fahrenheit)")
    method: str = Field("oral", description="Measurement method (oral, rectal, axillary, tympanic, temporal)")
    category: Optional[TemperatureCategory] = None
    
    @validator("unit")
    def validate_unit(cls, v):
        """Validate temperature unit."""
        if v not in ["celsius", "fahrenheit"]:
            raise ValidationError("Unit must be 'celsius' or 'fahrenheit'")
        return v
    
    @validator("method")
    def validate_method(cls, v):
        """Validate measurement method."""
        valid_methods = ["oral", "rectal", "axillary", "tympanic", "temporal"]
        if v not in valid_methods:
            raise ValidationError(f"Method must be one of {valid_methods}")
        return v
    
    def model_post_init(self, __context):
        """Calculate category after initialization."""
        super().model_post_init(__context)
        self.category = self.categorize()
    
    def to_celsius(self) -> float:
        """Convert temperature to Celsius."""
        if self.unit == "celsius":
            return self.value
        return round((self.value - 32) * 5/9, 1)
    
    def to_fahrenheit(self) -> float:
        """Convert temperature to Fahrenheit."""
        if self.unit == "fahrenheit":
            return self.value
        return round(self.value * 9/5 + 32, 1)
    
    def categorize(self) -> TemperatureCategory:
        """Categorize temperature based on value in Celsius."""
        celsius = self.to_celsius()
        
        if celsius < 35.0:
            return TemperatureCategory.HYPOTHERMIA
        elif celsius < 37.5:
            return TemperatureCategory.NORMAL
        elif celsius < 39.0:
            return TemperatureCategory.FEVER
        elif celsius < 40.0:
            return TemperatureCategory.HIGH_FEVER
        else:
            return TemperatureCategory.HYPERPYREXIA
    
    def is_critical(self) -> bool:
        """Check if temperature is in critical range."""
        celsius = self.to_celsius()
        return celsius < 35.0 or celsius >= 40.0


class RespiratoryRate(VitalSign):
    """Respiratory rate measurement model."""
    
    rate: EncryptedInt = Field(..., ge=0, le=60, description="Respiratory rate per minute")
    pattern: Optional[str] = Field("regular", description="Breathing pattern")
    effort: Optional[str] = Field("normal", description="Breathing effort (normal, labored, shallow)")
    
    @validator("effort")
    def validate_effort(cls, v):
        """Validate breathing effort."""
        valid_efforts = ["normal", "labored", "shallow", "deep"]
        if v and v not in valid_efforts:
            raise ValidationError(f"Effort must be one of {valid_efforts}")
        return v
    
    def is_normal(self) -> bool:
        """Check if respiratory rate is normal for adults."""
        return 12 <= self.rate <= 20
    
    def is_critical(self) -> bool:
        """Check if respiratory rate is critical."""
        return self.rate < 8 or self.rate > 30


class OxygenSaturation(VitalSign):
    """Oxygen saturation (SpO2) measurement model."""
    
    value: EncryptedInt = Field(..., ge=0, le=100, description="SpO2 percentage")
    on_oxygen: bool = Field(False, description="Whether patient is on supplemental oxygen")
    oxygen_flow_rate: Optional[float] = Field(None, description="Oxygen flow rate in L/min")
    oxygen_delivery: Optional[str] = Field(None, description="Oxygen delivery method")
    category: Optional[OxygenSaturationCategory] = None
    
    def model_post_init(self, __context):
        """Calculate category after initialization."""
        super().model_post_init(__context)
        self.category = self.categorize()
    
    def categorize(self) -> OxygenSaturationCategory:
        """Categorize oxygen saturation."""
        if self.value >= 95:
            return OxygenSaturationCategory.NORMAL
        elif self.value >= 91:
            return OxygenSaturationCategory.MILD_HYPOXEMIA
        elif self.value >= 86:
            return OxygenSaturationCategory.MODERATE_HYPOXEMIA
        else:
            return OxygenSaturationCategory.SEVERE_HYPOXEMIA
    
    def is_critical(self) -> bool:
        """Check if oxygen saturation is critical."""
        return self.value < 90


class PainScale(VitalSign):
    """Pain assessment model."""
    
    score: EncryptedInt = Field(..., ge=0, le=10, description="Pain score (0-10)")
    scale_type: str = Field("numeric", description="Type of pain scale used")
    location: Optional[EncryptedStr] = Field(None, description="Pain location")
    character: Optional[str] = Field(None, description="Pain character (sharp, dull, burning, etc.)")
    duration: Optional[str] = Field(None, description="Pain duration")
    aggravating_factors: Optional[List[str]] = Field(default_factory=list)
    relieving_factors: Optional[List[str]] = Field(default_factory=list)
    
    @validator("scale_type")
    def validate_scale_type(cls, v):
        """Validate pain scale type."""
        valid_types = ["numeric", "faces", "behavioral", "verbal"]
        if v not in valid_types:
            raise ValidationError(f"Scale type must be one of {valid_types}")
        return v
    
    def get_severity(self) -> str:
        """Get pain severity category."""
        if self.score == 0:
            return "no_pain"
        elif self.score <= 3:
            return "mild"
        elif self.score <= 6:
            return "moderate"
        elif self.score <= 9:
            return "severe"
        else:
            return "worst_possible"


class VitalSignsSet(MongoModel):
    """Complete set of vital signs taken at the same time."""
    
    patient_id: str = Field(..., description="Patient identifier")
    measured_by: Optional[str] = Field(None, description="Healthcare provider")
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Vital signs
    blood_pressure: Optional[Dict] = None
    heart_rate: Optional[int] = None
    temperature: Optional[Dict] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    pain_score: Optional[int] = None
    
    # Additional measurements
    weight: Optional[float] = Field(None, description="Weight in kg")
    height: Optional[float] = Field(None, description="Height in cm")
    bmi: Optional[float] = None
    
    # Clinical context
    clinical_context: Optional[str] = Field(None, description="Clinical context (routine, pre-op, emergency, etc.)")
    alerts: List[str] = Field(default_factory=list, description="Critical value alerts")
    
    class Settings:
        collection_name = "vital_signs_sets"
        indexes = [
            ("patient_id", -1),
            ("measured_at", -1),
            [("patient_id", 1), ("measured_at", -1)],
        ]
    
    def model_post_init(self, __context):
        """Calculate BMI and check for alerts."""
        super().model_post_init(__context)
        
        # Calculate BMI if height and weight provided
        if self.height and self.weight and self.height > 0:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 1)
        
        # Check for critical values
        self.check_critical_values()
    
    def check_critical_values(self):
        """Check for critical vital sign values and add alerts."""
        self.alerts = []
        
        # Blood pressure
        if self.blood_pressure:
            bp = BloodPressure(
                patient_id=self.patient_id,
                systolic=self.blood_pressure.get("systolic"),
                diastolic=self.blood_pressure.get("diastolic")
            )
            if bp.is_critical():
                self.alerts.append(f"Critical blood pressure: {bp.systolic}/{bp.diastolic}")
        
        # Heart rate
        if self.heart_rate:
            hr = HeartRate(patient_id=self.patient_id, rate=self.heart_rate)
            if hr.is_critical():
                self.alerts.append(f"Critical heart rate: {self.heart_rate} bpm")
        
        # Temperature
        if self.temperature:
            temp = Temperature(
                patient_id=self.patient_id,
                value=self.temperature.get("value"),
                unit=self.temperature.get("unit", "celsius")
            )
            if temp.is_critical():
                self.alerts.append(f"Critical temperature: {temp.value}°{temp.unit[0].upper()}")
        
        # Respiratory rate
        if self.respiratory_rate:
            rr = RespiratoryRate(patient_id=self.patient_id, rate=self.respiratory_rate)
            if rr.is_critical():
                self.alerts.append(f"Critical respiratory rate: {self.respiratory_rate}/min")
        
        # Oxygen saturation
        if self.oxygen_saturation:
            spo2 = OxygenSaturation(patient_id=self.patient_id, value=self.oxygen_saturation)
            if spo2.is_critical():
                self.alerts.append(f"Critical SpO2: {self.oxygen_saturation}%")
    
    def get_summary(self) -> Dict:
        """Get a summary of vital signs with interpretations."""
        summary = {
            "measured_at": self.measured_at,
            "alerts": self.alerts,
            "values": {}
        }
        
        if self.blood_pressure:
            summary["values"]["blood_pressure"] = {
                "value": f"{self.blood_pressure['systolic']}/{self.blood_pressure['diastolic']}",
                "unit": "mmHg"
            }
        
        if self.heart_rate:
            summary["values"]["heart_rate"] = {
                "value": self.heart_rate,
                "unit": "bpm"
            }
        
        if self.temperature:
            summary["values"]["temperature"] = {
                "value": self.temperature["value"],
                "unit": f"°{self.temperature.get('unit', 'celsius')[0].upper()}"
            }
        
        if self.respiratory_rate:
            summary["values"]["respiratory_rate"] = {
                "value": self.respiratory_rate,
                "unit": "/min"
            }
        
        if self.oxygen_saturation:
            summary["values"]["oxygen_saturation"] = {
                "value": self.oxygen_saturation,
                "unit": "%"
            }
        
        if self.pain_score is not None:
            summary["values"]["pain_score"] = {
                "value": self.pain_score,
                "unit": "/10"
            }
        
        return summary


# Async version
class AsyncVitalSignsSet(BaseModel):
    """Async version of VitalSignsSet."""
    
    patient_id: str = Field(..., description="Patient identifier")
    measured_by: Optional[str] = Field(None, description="Healthcare provider")
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Same fields as VitalSignsSet
    blood_pressure: Optional[Dict] = None
    heart_rate: Optional[int] = None
    temperature: Optional[Dict] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    pain_score: Optional[int] = None
    
    weight: Optional[float] = Field(None, description="Weight in kg")
    height: Optional[float] = Field(None, description="Height in cm")
    bmi: Optional[float] = None
    
    clinical_context: Optional[str] = None
    alerts: List[str] = Field(default_factory=list)
    
    class Settings:
        collection_name = "vital_signs_sets"
        indexes = [
            ("patient_id", -1),
            ("measured_at", -1),
            [("patient_id", 1), ("measured_at", -1)],
        ]