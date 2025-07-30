"""
GraphQL types for Essencia.
"""
import strawberry
from typing import Optional, List, Any
from datetime import datetime, date
from enum import Enum


# Enums
@strawberry.enum
class UserRole(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"


@strawberry.enum
class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


@strawberry.enum
class VitalSignCategory(Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


# Types
@strawberry.type
class User:
    """User type."""
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


@strawberry.type
class Patient:
    """Patient type."""
    id: str
    full_name: str
    cpf: str  # Masked for security
    birth_date: date
    age: int
    phone: Optional[str]
    email: Optional[str]
    blood_type: Optional[str]
    allergies: List[str]
    chronic_conditions: List[str]
    city: str
    state: str
    created_at: datetime
    
    # Related data
    latest_vital_signs: Optional["VitalSigns"] = None
    active_medications: Optional[List["Medication"]] = None
    upcoming_appointments: Optional[List["Appointment"]] = None


@strawberry.type
class VitalSigns:
    """Vital signs type."""
    id: str
    patient_id: str
    recorded_at: datetime
    recorded_by: Optional[str]
    
    # Measurements
    systolic: Optional[int]
    diastolic: Optional[int]
    heart_rate: Optional[int]
    temperature: Optional[float]
    respiratory_rate: Optional[int]
    oxygen_saturation: Optional[int]
    weight: Optional[float]
    height: Optional[float]
    
    # Calculated
    bmi: Optional[float]
    blood_pressure_category: Optional[VitalSignCategory]
    
    # Related
    patient: Optional[Patient] = None


@strawberry.type
class Medication:
    """Medication type."""
    id: str
    patient_id: str
    name: str
    active_ingredient: str
    dosage: str
    frequency: str
    route: str  # oral, IV, etc.
    
    # Dates
    start_date: date
    end_date: Optional[date]
    discontinued_date: Optional[date]
    
    # Prescription
    prescribed_by: str
    prescribed_at: datetime
    prescription_notes: Optional[str]
    
    # Status
    is_active: bool
    adherence_rate: Optional[float]
    
    # Related
    patient: Optional[Patient] = None
    interactions: Optional[List[str]] = None


@strawberry.type
class Appointment:
    """Appointment type."""
    id: str
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    duration_minutes: int
    
    # Details
    appointment_type: str
    specialty: str
    reason: str
    notes: Optional[str]
    
    # Status
    status: AppointmentStatus
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    
    # Related
    patient: Optional[Patient] = None
    doctor: Optional[User] = None


@strawberry.type
class MentalHealthAssessment:
    """Mental health assessment type."""
    id: str
    patient_id: str
    assessment_type: str  # PHQ-9, GAD-7, etc.
    assessed_at: datetime
    assessed_by: str
    
    # Results
    total_score: int
    severity: str
    responses: List[int]
    interpretation: str
    recommendations: List[str]
    
    # Related
    patient: Optional[Patient] = None


@strawberry.type
class LabTest:
    """Laboratory test type."""
    id: str
    patient_id: str
    test_name: str
    test_code: str
    
    # Results
    value: float
    unit: str
    reference_min: Optional[float]
    reference_max: Optional[float]
    is_abnormal: bool
    
    # Dates
    collected_at: datetime
    resulted_at: Optional[datetime]
    
    # Related
    patient: Optional[Patient] = None


# Input Types
@strawberry.input
class LoginInput:
    """Login input."""
    email: str
    password: str


@strawberry.input
class PatientInput:
    """Patient creation/update input."""
    full_name: str
    cpf: str
    birth_date: date
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    
    # Address
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    cep: str
    
    # Family
    mother_name: str
    father_name: Optional[str] = None


@strawberry.input
class PatientFilter:
    """Patient filter input."""
    city: Optional[str] = None
    state: Optional[str] = None
    has_chronic_conditions: Optional[bool] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None


@strawberry.input
class VitalSignsInput:
    """Vital signs recording input."""
    patient_id: str
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None


@strawberry.input
class MedicationInput:
    """Medication prescription input."""
    patient_id: str
    name: str
    active_ingredient: str
    dosage: str
    frequency: str
    route: str = "oral"
    start_date: date
    end_date: Optional[date] = None
    prescription_notes: Optional[str] = None


@strawberry.input
class AppointmentInput:
    """Appointment scheduling input."""
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    duration_minutes: int = 30
    appointment_type: str
    specialty: str
    reason: str
    notes: Optional[str] = None


# Response Types
@strawberry.type
class LoginResponse:
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


@strawberry.type
class PaginatedPatients:
    """Paginated patient list."""
    items: List[Patient]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool


@strawberry.type
class DashboardStats:
    """Dashboard statistics."""
    total_patients: int
    active_patients: int
    appointments_today: int
    pending_prescriptions: int
    critical_alerts: int
    
    # Trends
    new_patients_month: int
    appointments_month: int
    revenue_month: float