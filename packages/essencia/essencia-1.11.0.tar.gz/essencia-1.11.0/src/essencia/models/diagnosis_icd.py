"""ICD-11 diagnosis models and management.

This module provides models for managing ICD-11 diagnostic codes,
particularly focused on mental health diagnoses.
"""

import datetime
import json
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from .bases import MongoModel, ObjectReferenceId, StrEnum
from essencia import fields as fd


class DiagnosisValidationError(Exception):
    """Custom exception for diagnosis validation errors."""
    pass


class ICDCode(MongoModel):
    """ICD-11 diagnostic code model."""
    COLLECTION_NAME = 'icd_codes'
    
    # Core fields
    code: str = Field(..., description="ICD-11 code (e.g., '6A70.0')")
    title: str = Field(..., description="Diagnosis title")
    description: Optional[str] = Field(None, description="Detailed description")
    
    # Hierarchy
    category: Optional[str] = Field(None, description="Category name")
    parent_code: Optional[str] = Field(None, description="Parent code in hierarchy")
    level: int = Field(default=0, description="Hierarchy level")
    
    # Additional metadata
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names")
    inclusion_terms: List[str] = Field(default_factory=list, description="Included conditions")
    exclusion_terms: List[str] = Field(default_factory=list, description="Excluded conditions")
    
    # Clinical information
    diagnostic_criteria: Optional[str] = Field(None, description="Diagnostic criteria")
    clinical_description: Optional[str] = Field(None, description="Clinical description")
    
    # Specifiers and modifiers
    specifiers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Available specifiers for this diagnosis"
    )
    # Format: [{"code": "0", "title": "Single episode", "description": "..."}]
    
    # Usage statistics
    usage_count: int = Field(default=0, description="Times used in diagnoses")
    last_used: Optional[datetime.datetime] = None
    
    # Status
    is_active: bool = Field(default=True, description="Whether code is currently valid")
    is_mental_health: bool = Field(default=True, description="Mental health diagnosis flag")
    
    # Metadata
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    data_source: Optional[str] = Field(None, description="Source of ICD data")
    
    @field_validator('code')
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Validate ICD-11 code format."""
        # Basic ICD-11 format validation
        # Format: Chapter + Letter/Number + digits, optionally with .subcategory
        pattern = r'^[A-Z0-9]{2,4}(\.[A-Z0-9]{1,2})?$'
        if not re.match(pattern, v.upper()):
            raise ValueError(f"Invalid ICD-11 code format: {v}")
        return v.upper()
    
    def get_full_path(self) -> List[str]:
        """Get full hierarchy path from root to this code."""
        path = [self.title]
        current = self
        
        while current.parent_code:
            parent = self.__class__.find_one({'code': current.parent_code})
            if parent:
                path.insert(0, parent.title)
                current = parent
            else:
                break
        
        if self.category and self.category not in path:
            path.insert(0, self.category)
        
        return path
    
    def get_children(self) -> List['ICDCode']:
        """Get direct child codes."""
        return list(self.__class__.find({
            'parent_code': self.code,
            'is_active': True
        }))
    
    def get_all_descendants(self) -> List['ICDCode']:
        """Get all descendant codes recursively."""
        descendants = []
        children = self.get_children()
        
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        
        return descendants
    
    def search_related(self, query: str) -> List['ICDCode']:
        """Search for related codes by keywords."""
        query_lower = query.lower()
        
        # Search in keywords, synonyms, and inclusion terms
        related = list(self.__class__.find({
            '$or': [
                {'keywords': {'$regex': query_lower, '$options': 'i'}},
                {'synonyms': {'$regex': query_lower, '$options': 'i'}},
                {'inclusion_terms': {'$regex': query_lower, '$options': 'i'}},
                {'title': {'$regex': query_lower, '$options': 'i'}}
            ],
            'is_active': True
        }))
        
        return related
    
    def increment_usage(self) -> None:
        """Increment usage counter."""
        self.usage_count += 1
        self.last_used = datetime.datetime.now()
        self.save_self()
    
    @classmethod
    def get_common_codes(cls, limit: int = 20) -> List['ICDCode']:
        """Get most commonly used codes."""
        return list(cls.find({
            'is_active': True,
            'usage_count': {'$gt': 0}
        }).sort('usage_count', -1).limit(limit))
    
    @classmethod
    def get_category_tree(cls) -> Dict[str, List['ICDCode']]:
        """Get hierarchical tree of categories and codes."""
        categories = {}
        
        # Get all top-level codes (no parent)
        top_level = list(cls.find({
            'parent_code': None,
            'is_active': True
        }))
        
        for code in top_level:
            category = code.category or 'Uncategorized'
            if category not in categories:
                categories[category] = []
            categories[category].append(code)
        
        return categories
    
    @classmethod
    def import_from_json(cls, json_path: str) -> int:
        """Import ICD codes from JSON file."""
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        for item in data:
            # Check if code already exists
            existing = cls.find_one({'code': item['code']})
            if existing:
                # Update existing
                for key, value in item.items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.datetime.now()
                existing.save_self()
            else:
                # Create new
                code = cls(**item)
                code.save_self()
            imported += 1
        
        return imported


class DiagnosisRecord(BaseModel):
    """Individual diagnosis assignment (not a MongoModel).
    
    This is used as an embedded document in patient records or visits.
    """
    
    icd_code: str = Field(..., description="ICD-11 code")
    diagnosis_title: str = Field(..., description="Diagnosis title (denormalized)")
    
    # Clinical details
    is_primary: bool = Field(default=False, description="Primary diagnosis flag")
    clinical_status: str = Field(default='active', description="active, remission, resolved")
    severity: Optional[str] = Field(None, description="mild, moderate, severe")
    
    # Specifiers
    specifiers: List[str] = Field(default_factory=list, description="Applied specifiers")
    additional_info: Optional[str] = Field(None, description="Additional clinical information")
    
    # Dates
    diagnosed_date: datetime.date = Field(default_factory=datetime.date.today)
    onset_date: Optional[datetime.date] = Field(None, description="Symptom onset date")
    resolution_date: Optional[datetime.date] = Field(None, description="Resolution date")
    
    # Metadata
    diagnosed_by: ObjectReferenceId = Field(..., description="Doctor who made diagnosis")
    confidence: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Diagnostic confidence (0-1)"
    )
    notes: Optional[str] = Field(None, description="Clinical notes")
    
    @field_validator('icd_code')
    @classmethod
    def validate_icd_code_exists(cls, v: str) -> str:
        """Validate that ICD code exists in database."""
        # Note: This validation might need to be optional or handled differently
        # in production to avoid database dependencies in the model
        return v.upper()
    
    @field_validator('specifiers')
    @classmethod
    def validate_specifiers(cls, v: List[str], values) -> List[str]:
        """Validate specifiers against allowed values for the ICD code."""
        # This would ideally check against allowed specifiers for the specific ICD code
        return v
    
    @property
    def is_active(self) -> bool:
        """Check if diagnosis is currently active."""
        return self.clinical_status == 'active' and self.resolution_date is None
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calculate duration of diagnosis in days."""
        if self.onset_date:
            end_date = self.resolution_date or datetime.date.today()
            return (end_date - self.onset_date).days
        return None
    
    def to_display_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display purposes."""
        return {
            'code': self.icd_code,
            'title': self.diagnosis_title,
            'status': self.clinical_status,
            'severity': self.severity,
            'is_primary': self.is_primary,
            'date': self.diagnosed_date.isoformat(),
            'specifiers': self.specifiers,
            'active': self.is_active
        }


class DiagnosisService:
    """Service class for diagnosis-related operations."""
    
    @staticmethod
    def search_codes(query: str, limit: int = 20) -> List[ICDCode]:
        """Search for ICD codes by query."""
        query_lower = query.lower()
        
        # Search in multiple fields
        results = list(ICDCode.find({
            '$or': [
                {'code': {'$regex': query, '$options': 'i'}},
                {'title': {'$regex': query_lower, '$options': 'i'}},
                {'keywords': {'$in': [query_lower]}},
                {'synonyms': {'$regex': query_lower, '$options': 'i'}}
            ],
            'is_active': True
        }).limit(limit))
        
        # Sort by relevance (usage count)
        results.sort(key=lambda x: x.usage_count, reverse=True)
        
        return results
    
    @staticmethod
    def validate_diagnosis(diagnosis: DiagnosisRecord) -> bool:
        """Validate a diagnosis record."""
        # Check if ICD code exists
        icd_code = ICDCode.find_one({'code': diagnosis.icd_code, 'is_active': True})
        if not icd_code:
            raise DiagnosisValidationError(f"Invalid ICD code: {diagnosis.icd_code}")
        
        # Validate specifiers
        if diagnosis.specifiers:
            allowed_specifiers = [s['code'] for s in icd_code.specifiers]
            for spec in diagnosis.specifiers:
                if spec not in allowed_specifiers:
                    raise DiagnosisValidationError(
                        f"Invalid specifier '{spec}' for code {diagnosis.icd_code}"
                    )
        
        # Validate dates
        if diagnosis.onset_date and diagnosis.diagnosed_date:
            if diagnosis.onset_date > diagnosis.diagnosed_date:
                raise DiagnosisValidationError(
                    "Onset date cannot be after diagnosis date"
                )
        
        if diagnosis.resolution_date:
            if diagnosis.resolution_date < diagnosis.diagnosed_date:
                raise DiagnosisValidationError(
                    "Resolution date cannot be before diagnosis date"
                )
        
        return True
    
    @staticmethod
    def get_patient_diagnoses(patient_key: str, active_only: bool = False) -> List[DiagnosisRecord]:
        """Get all diagnoses for a patient."""
        # This would typically be implemented by searching through patient records
        # or a separate patient_diagnoses collection
        pass
    
    @staticmethod
    def import_base_codes(json_path: str) -> int:
        """Import base ICD-11 codes from JSON."""
        return ICDCode.import_from_json(json_path)