"""
Reusable model mixins and common field patterns.
"""

import datetime
from typing import Optional, List, Dict, Any, ClassVar
from pydantic import Field, field_validator

from ..models.bases import MongoModel, ObjectReferenceId
from .. import fields as fd


class TimestampMixin(MongoModel):
    """Mixin for timestamp fields"""
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    modified: Optional[datetime.datetime] = None
    
    def mark_modified(self):
        """Mark the instance as modified"""
        self.modified = datetime.datetime.now()
    
    class Config:
        arbitrary_types_allowed = True


class UserTrackingMixin(MongoModel):
    """Mixin for user tracking fields"""
    creator: ObjectReferenceId = Field(default='doctor.admin')
    modifier: Optional[ObjectReferenceId] = None
    
    def set_modifier(self, user_reference: str):
        """Set the modifier"""
        self.modifier = ObjectReferenceId(user_reference)
    
    class Config:
        arbitrary_types_allowed = True


class SoftDeleteMixin(MongoModel):
    """Mixin for soft delete functionality"""
    deleted_at: Optional[datetime.datetime] = None
    deleted_by: Optional[ObjectReferenceId] = None
    is_deleted: bool = False
    
    def soft_delete(self, user_reference: str = None):
        """Mark as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.datetime.now()
        if user_reference:
            self.deleted_by = ObjectReferenceId(user_reference)
    
    def restore(self):
        """Restore from soft delete"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
    
    @classmethod
    def find_active(cls, query: Dict[str, Any] = None):
        """Find only non-deleted records"""
        query = query or {}
        query['is_deleted'] = {'$ne': True}
        return cls.find(query)
    
    class Config:
        arbitrary_types_allowed = True


class PatientRelatedMixin(MongoModel):
    """Mixin for models related to patients"""
    patient_key: str = Field(..., description="Reference to patient")
    
    @field_validator('patient_key')
    @classmethod
    def validate_patient_key(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Patient key is required')
        return v
    
    @property
    def patient(self):
        """Get related patient"""
        from .people import Patient
        return Patient.get_by_key(self.patient_key)
    
    class Config:
        arbitrary_types_allowed = True


class DoctorRelatedMixin(MongoModel):
    """Mixin for models related to doctors"""
    doctor_key: str = Field(default='admin')
    
    @property
    def doctor(self):
        """Get related doctor"""
        from .user import User
        return User.get_by_key(self.doctor_key)
    
    class Config:
        arbitrary_types_allowed = True


class AuditableMixin(TimestampMixin, UserTrackingMixin, SoftDeleteMixin):
    """Complete auditable mixin combining timestamp, user tracking, and soft delete"""
    
    def get_audit_info(self) -> Dict[str, Any]:
        """Get audit information"""
        return {
            'created': self.created,
            'modified': self.modified,
            'creator': self.creator,
            'modifier': self.modifier,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by
        }
    
    class Config:
        arbitrary_types_allowed = True


class FinancialMixin(MongoModel):
    """Mixin for financial-related models"""
    amount: float = Field(..., ge=0, description="Amount in currency")
    currency: str = Field(default="BRL", description="Currency code")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return round(v, 2)  # Round to 2 decimal places
    
    @property
    def formatted_amount(self) -> str:
        """Get formatted amount"""
        if self.currency == "BRL":
            return f"R$ {self.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{self.currency} {self.amount:,.2f}"
    
    class Config:
        arbitrary_types_allowed = True


class StatusMixin(MongoModel):
    """Mixin for status tracking"""
    status: str = Field(default="active", description="Current status")
    status_changed_at: Optional[datetime.datetime] = None
    status_changed_by: Optional[ObjectReferenceId] = None
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def change_status(self, new_status: str, user_reference: str = None, 
                     reason: str = None):
        """Change status and track history"""
        old_status = self.status
        
        # Update status
        self.status = new_status
        self.status_changed_at = datetime.datetime.now()
        if user_reference:
            self.status_changed_by = ObjectReferenceId(user_reference)
        
        # Add to history
        history_entry = {
            'from_status': old_status,
            'to_status': new_status,
            'changed_at': self.status_changed_at,
            'changed_by': user_reference,
            'reason': reason
        }
        self.status_history.append(history_entry)
    
    @property
    def is_active(self) -> bool:
        """Check if status is active"""
        return self.status == "active"
    
    class Config:
        arbitrary_types_allowed = True


class AddressMixin(MongoModel):
    """Mixin for address information"""
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = Field(default="Brasil")
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v):
        if v:
            # Remove non-digits
            clean_zip = ''.join(filter(str.isdigit, v))
            if len(clean_zip) != 8:
                raise ValueError('CEP deve ter 8 dígitos')
            return clean_zip
        return v
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = []
        
        if self.street:
            street_part = self.street
            if self.number:
                street_part += f", {self.number}"
            if self.complement:
                street_part += f", {self.complement}"
            parts.append(street_part)
        
        if self.neighborhood:
            parts.append(self.neighborhood)
        
        if self.city and self.state:
            parts.append(f"{self.city}/{self.state}")
        elif self.city:
            parts.append(self.city)
        
        if self.zip_code:
            formatted_zip = f"{self.zip_code[:5]}-{self.zip_code[5:]}" if len(self.zip_code) == 8 else self.zip_code
            parts.append(f"CEP: {formatted_zip}")
        
        return "\n".join(parts)
    
    class Config:
        arbitrary_types_allowed = True


class ContactMixin(MongoModel):
    """Mixin for contact information"""
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Email inválido')
        return v
    
    @field_validator('phone', 'mobile')
    @classmethod
    def validate_phone(cls, v):
        if v:
            # Remove non-digits
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Telefone deve ter pelo menos 10 dígitos')
        return v
    
    @property
    def formatted_phone(self) -> Optional[str]:
        """Get formatted phone number"""
        if not self.phone:
            return None
        
        clean = ''.join(filter(str.isdigit, self.phone))
        if len(clean) == 11:
            return f"({clean[:2]}) {clean[2:7]}-{clean[7:]}"
        elif len(clean) == 10:
            return f"({clean[:2]}) {clean[2:6]}-{clean[6:]}"
        return self.phone
    
    @property
    def formatted_mobile(self) -> Optional[str]:
        """Get formatted mobile number"""
        if not self.mobile:
            return None
        
        clean = ''.join(filter(str.isdigit, self.mobile))
        if len(clean) == 11:
            return f"({clean[:2]}) {clean[2:7]}-{clean[7:]}"
        elif len(clean) == 10:
            return f"({clean[:2]}) {clean[2:6]}-{clean[6:]}"
        return self.mobile
    
    class Config:
        arbitrary_types_allowed = True


class PersonMixin(ContactMixin, AddressMixin):
    """Mixin for person-related information"""
    fname: str = Field(..., min_length=1, description="First name")
    lname: str = Field(..., min_length=1, description="Last name")
    document_type: Optional[str] = Field(default="CPF")
    document_number: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    gender: Optional[str] = None
    
    @field_validator('document_number')
    @classmethod
    def validate_document(cls, v, info):
        if v and info.data.get('document_type') == 'CPF':
            clean_cpf = ''.join(filter(str.isdigit, v))
            if len(clean_cpf) != 11:
                raise ValueError('CPF deve ter 11 dígitos')
        return v
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.fname} {self.lname}".strip()
    
    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth date"""
        if not self.birth_date:
            return None
        
        today = datetime.date.today()
        age = today.year - self.birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today.month < self.birth_date.month or \
           (today.month == self.birth_date.month and today.day < self.birth_date.day):
            age -= 1
        
        return age
    
    @property
    def formatted_document(self) -> Optional[str]:
        """Get formatted document number"""
        if not self.document_number:
            return None
        
        if self.document_type == 'CPF' and len(self.document_number) == 11:
            cpf = self.document_number
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        return self.document_number
    
    def __str__(self) -> str:
        return self.full_name
    
    class Config:
        arbitrary_types_allowed = True


class MedicalMixin(MongoModel):
    """Mixin for medical-related information"""
    diagnosis_codes: List[str] = Field(default_factory=list, description="ICD-10 codes")
    observations: Optional[str] = None
    urgency_level: str = Field(default="normal", description="Urgency level")
    
    @field_validator('urgency_level')
    @classmethod
    def validate_urgency(cls, v):
        valid_levels = ['low', 'normal', 'high', 'urgent']
        if v not in valid_levels:
            raise ValueError(f'Urgency level must be one of: {valid_levels}')
        return v
    
    @property
    def is_urgent(self) -> bool:
        """Check if marked as urgent"""
        return self.urgency_level in ['high', 'urgent']
    
    class Config:
        arbitrary_types_allowed = True


class QuantifiableMixin(MongoModel):
    """Mixin for quantifiable data with units"""
    value: float = Field(..., description="Numeric value")
    unit: str = Field(..., description="Unit of measurement")
    reference_range_min: Optional[float] = None
    reference_range_max: Optional[float] = None
    
    @property
    def formatted_value(self) -> str:
        """Get formatted value with unit"""
        return f"{self.value} {self.unit}"
    
    @property
    def is_within_range(self) -> Optional[bool]:
        """Check if value is within reference range"""
        if self.reference_range_min is None or self.reference_range_max is None:
            return None
        
        return self.reference_range_min <= self.value <= self.reference_range_max
    
    @property
    def range_status(self) -> str:
        """Get range status description"""
        if self.is_within_range is None:
            return "No reference range"
        elif self.is_within_range:
            return "Within normal range"
        elif self.value < self.reference_range_min:
            return "Below normal range"
        else:
            return "Above normal range"
    
    class Config:
        arbitrary_types_allowed = True


class CommentableMixin(MongoModel):
    """Mixin for models that can have comments"""
    comments: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_comment(self, text: str, author: str, comment_type: str = "general"):
        """Add a comment"""
        comment = {
            'text': text,
            'author': author,
            'type': comment_type,
            'created_at': datetime.datetime.now(),
            'id': len(self.comments) + 1
        }
        self.comments.append(comment)
    
    def get_comments_by_type(self, comment_type: str) -> List[Dict[str, Any]]:
        """Get comments by type"""
        return [c for c in self.comments if c.get('type') == comment_type]
    
    @property
    def latest_comment(self) -> Optional[Dict[str, Any]]:
        """Get the most recent comment"""
        if not self.comments:
            return None
        return max(self.comments, key=lambda c: c['created_at'])
    
    class Config:
        arbitrary_types_allowed = True


class CategorizableMixin(MongoModel):
    """Mixin for models that can be categorized"""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    def add_tag(self, tag: str):
        """Add a tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if has a specific tag"""
        return tag in self.tags
    
    @property
    def full_category(self) -> str:
        """Get full category path"""
        if self.category and self.subcategory:
            return f"{self.category} > {self.subcategory}"
        return self.category or "Uncategorized"
    
    class Config:
        arbitrary_types_allowed = True


# Common base classes combining multiple mixins
class BasePatientModel(PatientRelatedMixin, AuditableMixin):
    """Base class for patient-related models"""
    # Remove abstract config - these are now concrete mixins
    pass


class BaseMedicalRecord(BasePatientModel, MedicalMixin, CommentableMixin):
    """Base class for medical records"""
    pass


class BaseFinancialRecord(BasePatientModel, FinancialMixin, StatusMixin):
    """Base class for financial records"""
    pass


class BasePerson(PersonMixin, AuditableMixin):
    """Base class for person entities"""
    pass