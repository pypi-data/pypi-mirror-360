"""
Essencia models package.

This package provides comprehensive data models for medical and business applications.
"""

# Base models and utilities
from .base import BaseModel
from .bases import (
    MongoModel,
    MongoId,
    ObjectReferenceId,
    StrEnum,
    BaseEnum,
    Names
)
from .session import Session

# SQL model support
from .sql_base import (
    SQLModel,
    TimestampedSQLModel,
    SoftDeleteSQLModel
)

# Async support
from .async_models import (
    AsyncModelMixin,
    AsyncTransactionContext,
    async_cache_result
)

# User authentication models
from .user import (
    # Simple API models
    User,
    UserBase,
    UserCreate,
    UserUpdate,
    # Medical system models
    BaseUser,
    SessionUser,
    MedicalUser,
    NewUser
)

# Model mixins
from .mixins import (
    TimestampMixin,
    UserTrackingMixin,
    SoftDeleteMixin,
    PatientRelatedMixin,
    DoctorRelatedMixin,
    AuditableMixin,
    FinancialMixin,
    StatusMixin,
    AddressMixin,
    ContactMixin,
    PersonMixin,
    MedicalMixin,
    QuantifiableMixin,
    CommentableMixin,
    CategorizableMixin,
    BasePatientModel,
    BaseMedicalRecord,
    BaseFinancialRecord,
    BasePerson
)

# People models
from .people import (
    Person,
    BaseProfile,
    Patient,
    Staff,
    Doctor,
    Therapist,
    Employee
)

# Medical models
from .medical import (
    DoctorPatient,
    Visit,
    MedicationDatabase as LegacyMedicationDatabase,
    Medication as LegacyMedication,
    Prescription
)

# Medication management models
from .medication import (
    MedicationCategory,
    DosageForm,
    RouteOfAdministration,
    FrequencyUnit,
    PrescriptionStatus,
    AdherenceStatus,
    MedicationDatabase,
    Medication,
    MedicationAdherence,
    DrugInteraction,
    MedicationService
)

# Laboratory models
from .laboratory import (
    LabTestCategory,
    ReferenceRange,
    LabTestType,
    LabTest,
    LabTestBatch,
    LabTestAnalyzer
)

# Clinical models
from .clinical import (
    Event,
    VitalRecord,
    ExamResult,
    PHQ9Assessment,
    DiagnosisNote
)

# Financial models
from .financial import (
    ExpenseCategory,
    PaymentTerms,
    RecurrencePattern,
    Service,
    FinancialAccount,
    FinancialRecord,
    RevenueStatus,
    PaymentSource,
    Revenue,
    TherapyPackage,
    Expense,
    Budget
)

# Extended financial models
from .financial_extended import (
    GoalType,
    GoalStatus,
    PaymentStatus as TherapyPaymentStatus,
    ExpenseCategory as ExtendedExpenseCategory,
    FinancialGoal,
    CashFlowProjection,
    TherapyPackage as ExtendedTherapyPackage
)

# Appointment models
from .appointment import (
    AppointmentType,
    AppointmentStatus,
    RecurrencePattern as AppointmentRecurrence,
    BlockType,
    Appointment,
    DoctorSchedule,
    ScheduleBlock
)

# Notification models
from .notification import (
    NotificationType,
    NotificationChannel,
    NotificationStatus,
    NotificationTemplate,
    Notification,
    NotificationPreference
)

# Diagnosis/ICD models
from .diagnosis_icd import (
    DiagnosisValidationError,
    ICDCode,
    DiagnosisRecord,
    DiagnosisService
)

# Vital signs models
from .vital_signs import (
    VitalSignCategory,
    BloodPressureCategory,
    HeartRateCategory,
    OxygenSaturationCategory,
    TemperatureCategory,
    VitalSign,
    BloodPressure,
    HeartRate,
    Temperature,
    RespiratoryRate,
    OxygenSaturation,
    PainScale,
    VitalSignsSet,
    AsyncVitalSignsSet
)

# Mental health models
from .mental_health import (
    AssessmentType,
    SeverityLevel,
    AssessmentQuestion,
    AssessmentResponse,
    MentalHealthAssessment,
    PHQ9Assessment,
    GAD7Assessment,
    SNAPIV_Assessment,
    AssessmentService
)

# Operational models
from .operational import Task

# Audit models
from .audit import (
    AuditEventType,
    AuditOutcome,
    AuditLog,
    audit_login,
    audit_data_access,
    audit_patient_access
)

__all__ = [
    # Base models
    'BaseModel',
    'MongoModel',
    'MongoId',
    'ObjectReferenceId',
    'StrEnum',
    'BaseEnum',
    'Names',
    'Session',
    # SQL models
    'SQLModel',
    'TimestampedSQLModel',
    'SoftDeleteSQLModel',
    # Async support
    'AsyncModelMixin',
    'AsyncTransactionContext',
    'async_cache_result',
    
    # User models
    'User',
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'BaseUser',
    'SessionUser',
    'MedicalUser',
    'NewUser',
    
    # Mixins
    'TimestampMixin',
    'UserTrackingMixin',
    'SoftDeleteMixin',
    'PatientRelatedMixin',
    'DoctorRelatedMixin',
    'AuditableMixin',
    'FinancialMixin',
    'StatusMixin',
    'AddressMixin',
    'ContactMixin',
    'PersonMixin',
    'MedicalMixin',
    'QuantifiableMixin',
    'CommentableMixin',
    'CategorizableMixin',
    'BasePatientModel',
    'BaseMedicalRecord',
    'BaseFinancialRecord',
    'BasePerson',
    
    # People models
    'Person',
    'BaseProfile',
    'Patient',
    'Staff',
    'Doctor',
    'Therapist',
    'Employee',
    
    # Medical models
    'DoctorPatient',
    'Visit',
    'LegacyMedicationDatabase',
    'LegacyMedication',
    'Prescription',
    
    # Medication management models
    'MedicationCategory',
    'DosageForm',
    'RouteOfAdministration',
    'FrequencyUnit',
    'PrescriptionStatus',
    'AdherenceStatus',
    'MedicationDatabase',
    'Medication',
    'MedicationAdherence',
    'DrugInteraction',
    'MedicationService',
    
    # Laboratory models
    'LabTestCategory',
    'ReferenceRange',
    'LabTestType',
    'LabTest',
    'LabTestBatch',
    'LabTestAnalyzer',
    
    # Clinical models
    'Event',
    'VitalRecord',
    'ExamResult',
    'PHQ9Assessment',
    'DiagnosisNote',
    
    # Financial models
    'ExpenseCategory',
    'PaymentTerms',
    'RecurrencePattern',
    'Service',
    'FinancialAccount',
    'FinancialRecord',
    'RevenueStatus',
    'PaymentSource',
    'Revenue',
    'TherapyPackage',
    'Expense',
    'Budget',
    
    # Extended financial models
    'GoalType',
    'GoalStatus',
    'TherapyPaymentStatus',
    'ExtendedExpenseCategory',
    'FinancialGoal',
    'CashFlowProjection',
    'ExtendedTherapyPackage',
    
    # Appointment models
    'AppointmentType',
    'AppointmentStatus',
    'AppointmentRecurrence',
    'BlockType',
    'Appointment',
    'DoctorSchedule',
    'ScheduleBlock',
    
    # Notification models
    'NotificationType',
    'NotificationChannel',
    'NotificationStatus',
    'NotificationTemplate',
    'Notification',
    'NotificationPreference',
    
    # Diagnosis/ICD models
    'DiagnosisValidationError',
    'ICDCode',
    'DiagnosisRecord',
    'DiagnosisService',
    
    # Operational models
    'Task',
    
    # Audit models
    'AuditEventType',
    'AuditOutcome',
    'AuditLog',
    'audit_login',
    'audit_data_access',
    'audit_patient_access',
    
    # Vital signs models
    'VitalSignCategory',
    'BloodPressureCategory', 
    'HeartRateCategory',
    'OxygenSaturationCategory',
    'TemperatureCategory',
    'VitalSign',
    'BloodPressure',
    'HeartRate',
    'Temperature',
    'RespiratoryRate',
    'OxygenSaturation',
    'PainScale',
    'VitalSignsSet',
    'AsyncVitalSignsSet',
    
    # Mental health models
    'AssessmentType',
    'SeverityLevel',
    'AssessmentQuestion',
    'AssessmentResponse',
    'MentalHealthAssessment',
    'PHQ9Assessment',
    'GAD7Assessment',
    'SNAPIV_Assessment',
    'AssessmentService',
]