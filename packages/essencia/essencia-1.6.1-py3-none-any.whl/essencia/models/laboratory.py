"""Laboratory test models for managing clinical exam data.

This module contains models for storing and analyzing laboratory test results,
supporting data import from CSV files and temporal analysis of patient exams.
"""
import datetime
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, computed_field

from .bases import MongoModel, StrEnum
from .medical import DoctorPatient
from ..fields import DefaultDate, DefaultDateTime, EncryptedLabResults


class LabTestCategory(StrEnum):
    """Categories of laboratory tests for organization and filtering."""
    HEMATOLOGY = "Hematologia"
    BIOCHEMISTRY = "Bioquímica"
    HORMONES = "Hormônios"
    IMMUNOLOGY = "Imunologia"
    MICROBIOLOGY = "Microbiologia"
    URINALYSIS = "Urinálise"
    SEROLOGY = "Sorologia"
    MOLECULAR = "Molecular"
    TOXICOLOGY = "Toxicologia"
    COAGULATION = "Coagulação"
    ELECTROLYTES = "Eletrólitos"
    VITAMINS = "Vitaminas"
    MINERALS = "Minerais"
    CARDIAC = "Marcadores Cardíacos"
    HEPATIC = "Função Hepática"
    RENAL = "Função Renal"
    LIPIDS = "Lipídios"
    GLUCOSE = "Glicose"
    THYROID = "Tireoide"
    TUMOR = "Marcadores Tumorais"


class ReferenceRange(BaseModel):
    """Reference range for lab test values with gender and age specificity.
    
    Attributes:
        min_value: Minimum normal value
        max_value: Maximum normal value
        unit: Unit of measurement
        gender: Gender-specific range (optional)
        age_min: Minimum age for this range (optional)
        age_max: Maximum age for this range (optional)
        notes: Additional notes about the range
    """
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str
    gender: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    notes: Optional[str] = None
    
    def is_normal(self, value: float, gender: Optional[str] = None, age: Optional[int] = None) -> bool:
        """Check if a value is within the normal range.
        
        Args:
            value: Test result value
            gender: Patient gender for gender-specific ranges
            age: Patient age for age-specific ranges
            
        Returns:
            bool: True if value is within normal range
        """
        # Check gender and age applicability
        if self.gender and gender and self.gender != gender:
            return False
        if self.age_min and age and age < self.age_min:
            return False
        if self.age_max and age and age > self.age_max:
            return False
            
        # Check value range
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
            
        return True


class LabTestType(MongoModel):
    """Catalog of laboratory test types with reference ranges and metadata.
    
    Attributes:
        code: Unique test code
        name: Test name in Portuguese
        name_en: Test name in English (optional)
        category: Test category for grouping
        unit: Standard unit of measurement
        reference_ranges: List of reference ranges
        synonyms: Alternative names for the test
        description: Test description and purpose
        sample_type: Type of sample required (blood, urine, etc.)
        fasting_required: Whether fasting is required
        turnaround_days: Standard turnaround time in days
    """
    COLLECTION_NAME = 'lab_test_type'
    
    code: str = Field(..., description="Unique test code")
    name: str = Field(..., description="Test name in Portuguese")
    name_en: Optional[str] = Field(None, description="Test name in English")
    category: LabTestCategory
    unit: str = Field(..., description="Unit of measurement")
    reference_ranges: List[ReferenceRange] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list, description="Alternative names")
    description: Optional[str] = None
    sample_type: Optional[str] = Field(None, description="Blood, urine, etc.")
    fasting_required: bool = Field(default=False)
    turnaround_days: Optional[int] = Field(None, description="Standard turnaround time")
    
    def __str__(self):
        """Format test type for display."""
        return f"{self.name} ({self.unit})"
    
    def get_reference_range(self, gender: Optional[str] = None, age: Optional[int] = None) -> Optional[ReferenceRange]:
        """Get the most appropriate reference range for a patient.
        
        Args:
            gender: Patient gender
            age: Patient age
            
        Returns:
            ReferenceRange: Most specific applicable range, or None
        """
        applicable_ranges = []
        
        for ref_range in self.reference_ranges:
            # Check if range applies to this patient
            if ref_range.gender and gender and ref_range.gender != gender:
                continue
            if ref_range.age_min and age and age < ref_range.age_min:
                continue
            if ref_range.age_max and age and age > ref_range.age_max:
                continue
                
            # Calculate specificity score
            score = 0
            if ref_range.gender:
                score += 2
            if ref_range.age_min or ref_range.age_max:
                score += 1
                
            applicable_ranges.append((score, ref_range))
        
        if not applicable_ranges:
            # Return first range as default if no specific match
            return self.reference_ranges[0] if self.reference_ranges else None
            
        # Return most specific range
        applicable_ranges.sort(key=lambda x: x[0], reverse=True)
        return applicable_ranges[0][1]


class LabTest(DoctorPatient):
    """Individual laboratory test result with encrypted value storage.
    
    Inherits from DoctorPatient to maintain doctor-patient relationship.
    
    Attributes:
        test_type_key: Reference to LabTestType
        test_name: Test name (denormalized for performance)
        value: Encrypted test result value
        unit: Unit of measurement
        is_abnormal: Flag for abnormal results
        reference_range: Reference range used for this test
        collection_date: When sample was collected
        result_date: When results were available
        laboratory: Laboratory name
        notes: Additional notes or observations
        batch_key: Reference to import batch
        visit_key: Reference to associated medical visit
    """
    COLLECTION_NAME = 'lab_test'
    
    test_type_key: Optional[str] = Field(None, description="Reference to LabTestType")
    test_name: str = Field(..., description="Test name")
    value: EncryptedLabResults = Field(..., description="Encrypted test result")
    unit: str = Field(..., description="Unit of measurement")
    is_abnormal: bool = Field(default=False, description="Flag for abnormal results")
    reference_range: Optional[Dict[str, Any]] = Field(None, description="Reference range snapshot")
    collection_date: DefaultDate = Field(default_factory=datetime.date.today)
    result_date: Optional[date] = None
    laboratory: Optional[str] = Field(None, description="Laboratory name")
    notes: Optional[str] = Field(None, description="Additional notes")
    batch_key: Optional[str] = Field(None, description="Import batch reference")
    visit_key: Optional[str] = Field(None, description="Associated visit")
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        """Ensure value is properly encrypted."""
        if isinstance(v, dict):
            # Handle structured data
            import json
            return EncryptedLabResults(json.dumps(v))
        return EncryptedLabResults(str(v))
    
    @computed_field
    @property
    def numeric_value(self) -> Optional[float]:
        """Get numeric value from encrypted data.
        
        Returns:
            float: Numeric value if parseable, None otherwise
        """
        try:
            decrypted = self.value.decrypt()
            # Handle various numeric formats
            cleaned = decrypted.replace(',', '.').strip()
            # Remove common suffixes
            for suffix in ['mg/dL', 'g/dL', 'mg/L', '%', 'U/L', 'ng/mL', 'mcg/dL']:
                cleaned = cleaned.replace(suffix, '').strip()
            return float(cleaned)
        except:
            return None
    
    def check_abnormal(self, reference_range: Optional[ReferenceRange] = None) -> bool:
        """Check if test result is abnormal based on reference range.
        
        Args:
            reference_range: Reference range to use (optional)
            
        Returns:
            bool: True if value is outside normal range
        """
        numeric_val = self.numeric_value
        if numeric_val is None:
            return False
            
        if reference_range:
            return not reference_range.is_normal(numeric_val)
            
        # Check stored reference range
        if self.reference_range:
            min_val = self.reference_range.get('min_value')
            max_val = self.reference_range.get('max_value')
            if min_val is not None and numeric_val < min_val:
                return True
            if max_val is not None and numeric_val > max_val:
                return True
                
        return False
    
    def __str__(self):
        """Format test result for display."""
        return f"{self.test_name}: {self.value.decrypt()} {self.unit} ({self.collection_date})"


class LabTestBatch(MongoModel):
    """Batch of laboratory tests imported or collected together.
    
    Attributes:
        patient_key: Patient identifier
        import_date: When batch was imported
        source_file: Original file name if imported
        laboratory: Laboratory name
        collection_date: Sample collection date
        test_count: Number of tests in batch
        status: Processing status
        notes: Import notes or observations
    """
    COLLECTION_NAME = 'lab_test_batch'
    
    class Status(StrEnum):
        """Batch processing status."""
        PENDING = "Pendente"
        PROCESSING = "Processando"
        COMPLETED = "Completo"
        ERROR = "Erro"
        PARTIAL = "Parcial"
    
    patient_key: str
    import_date: DefaultDateTime = Field(default_factory=datetime.datetime.now)
    source_file: Optional[str] = None
    laboratory: Optional[str] = None
    collection_date: Optional[date] = None
    test_count: int = Field(default=0)
    status: Status = Field(default=Status.PENDING)
    notes: Optional[str] = None
    
    def __str__(self):
        """Format batch for display."""
        return f"Batch {self.key} - {self.test_count} tests ({self.status.value})"


# Analysis methods for LabTest
class LabTestAnalyzer:
    """Provides analysis methods for laboratory test data."""
    
    @staticmethod
    def get_patient_history(patient_key: str, test_name: Optional[str] = None, 
                          start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[LabTest]:
        """Get patient's lab test history with optional filters.
        
        Args:
            patient_key: Patient identifier
            test_name: Filter by specific test name
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of LabTest objects sorted by date
        """
        query = {'patient_key': patient_key}
        
        if test_name:
            query['test_name'] = test_name
            
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            query['collection_date'] = date_query
            
        return LabTest.find_sorted(query, sort=[('collection_date', -1)])
    
    @staticmethod
    def get_test_trend(patient_key: str, test_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get trend data for a specific test.
        
        Args:
            patient_key: Patient identifier
            test_name: Test name to analyze
            limit: Maximum number of results
            
        Returns:
            Dictionary with trend data including values, dates, and statistics
        """
        tests = LabTest.find_sorted(
            {'patient_key': patient_key, 'test_name': test_name},
            sort=[('collection_date', -1)],
            limit=limit
        )
        
        if not tests:
            return {'error': 'No test data found'}
        
        # Extract numeric values
        values = []
        dates = []
        for test in reversed(tests):  # Reverse to get chronological order
            numeric_val = test.numeric_value
            if numeric_val is not None:
                values.append(numeric_val)
                dates.append(test.collection_date)
        
        if not values:
            return {'error': 'No numeric values found'}
        
        # Calculate statistics
        import statistics
        trend_data = {
            'test_name': test_name,
            'unit': tests[0].unit,
            'count': len(values),
            'values': values,
            'dates': dates,
            'latest': values[-1],
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
        }
        
        if len(values) > 1:
            trend_data['std_dev'] = statistics.stdev(values)
            # Calculate trend direction
            first_half = statistics.mean(values[:len(values)//2])
            second_half = statistics.mean(values[len(values)//2:])
            if second_half > first_half * 1.1:
                trend_data['trend'] = 'increasing'
            elif second_half < first_half * 0.9:
                trend_data['trend'] = 'decreasing'
            else:
                trend_data['trend'] = 'stable'
        
        return trend_data
    
    @staticmethod
    def get_abnormal_results(patient_key: str, limit: int = 20) -> List[LabTest]:
        """Get recent abnormal test results for a patient.
        
        Args:
            patient_key: Patient identifier
            limit: Maximum number of results
            
        Returns:
            List of LabTest objects with abnormal results
        """
        return LabTest.find_sorted(
            {'patient_key': patient_key, 'is_abnormal': True},
            sort=[('collection_date', -1)],
            limit=limit
        )
    
    @staticmethod
    def get_tests_by_category(patient_key: str, category: LabTestCategory, 
                            start_date: Optional[date] = None) -> Dict[str, List[LabTest]]:
        """Get all tests for a patient grouped by test type within a category.
        
        Args:
            patient_key: Patient identifier
            category: Test category to filter by
            start_date: Optional start date filter
            
        Returns:
            Dictionary mapping test names to lists of results
        """
        # First get all test types in this category
        test_types = LabTestType.find({'category': category.value})
        test_names = [tt.name for tt in test_types]
        
        # Build query
        query = {
            'patient_key': patient_key,
            'test_name': {'$in': test_names}
        }
        
        if start_date:
            query['collection_date'] = {'$gte': start_date}
        
        # Get all tests
        tests = LabTest.find_sorted(query, sort=[('collection_date', -1)])
        
        # Group by test name
        grouped = {}
        for test in tests:
            if test.test_name not in grouped:
                grouped[test.test_name] = []
            grouped[test.test_name].append(test)
        
        return grouped
    
    @staticmethod
    def generate_summary_report(patient_key: str, days: int = 365) -> Dict[str, Any]:
        """Generate a summary report of patient's lab tests.
        
        Args:
            patient_key: Patient identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with summary statistics and notable findings
        """
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get all tests in period
        all_tests = LabTest.find_sorted(
            {
                'patient_key': patient_key,
                'collection_date': {'$gte': start_date, '$lte': end_date}
            },
            sort=[('collection_date', -1)]
        )
        
        # Group by test name
        test_groups = {}
        for test in all_tests:
            if test.test_name not in test_groups:
                test_groups[test.test_name] = []
            test_groups[test.test_name].append(test)
        
        # Generate summary
        summary = {
            'patient_key': patient_key,
            'period': {'start': start_date, 'end': end_date, 'days': days},
            'total_tests': len(all_tests),
            'unique_test_types': len(test_groups),
            'abnormal_count': sum(1 for t in all_tests if t.is_abnormal),
            'test_summaries': {}
        }
        
        # Add per-test summaries
        for test_name, tests in test_groups.items():
            numeric_values = [t.numeric_value for t in tests if t.numeric_value is not None]
            
            test_summary = {
                'count': len(tests),
                'latest_date': tests[0].collection_date,
                'latest_value': tests[0].value.decrypt(),
                'unit': tests[0].unit,
                'abnormal_count': sum(1 for t in tests if t.is_abnormal)
            }
            
            if numeric_values:
                import statistics
                test_summary['min'] = min(numeric_values)
                test_summary['max'] = max(numeric_values)
                test_summary['mean'] = statistics.mean(numeric_values)
                
            summary['test_summaries'][test_name] = test_summary
        
        return summary