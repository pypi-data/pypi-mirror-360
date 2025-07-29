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
    MedicationDatabase,
    Medication,
    Prescription
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
    'MedicationDatabase',
    'Medication',
    'Prescription',
    
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
    
    # Operational models
    'Task',
    
    # Audit models
    'AuditEventType',
    'AuditOutcome',
    'AuditLog',
    'audit_login',
    'audit_data_access',
    'audit_patient_access',
]