"""
Specialized encrypted field types for medical data.

Provides enhanced encryption for specific medical data types including:
- Medical history and records
- Prescription data
- Diagnostic information
- Treatment notes
- Mental health assessments
- Laboratory results
"""

import logging
from typing import Any, Optional, Dict, List
import json

from essencia.fields.encrypted_fields import EncryptedStr
from essencia.security.encryption_service import encrypt_medical_data, decrypt_medical_data, is_field_encrypted
from essencia.core.exceptions import EncryptionError

logger = logging.getLogger(__name__)


class EncryptedMedicalHistory(EncryptedStr):
    """
    Encrypted field for patient medical history.
    
    Features:
    - Automatic medical data encryption
    - Structured medical history support
    - Healthcare compliance
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted medical history field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        # Handle structured medical history
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt medical history
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt medical history: {e}")
            raise EncryptionError(f"Failed to encrypt medical history: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt medical history."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))
    
    def decrypt_structured(self) -> Dict[str, Any]:
        """
        Decrypt medical history as structured data.
        
        Returns:
            Dictionary with medical history data
        """
        decrypted = self.decrypt()
        if not decrypted:
            return {}
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            # Return as simple text if not JSON
            return {"content": decrypted}


class EncryptedPrescription(EncryptedStr):
    """
    Encrypted field for prescription data.
    
    Features:
    - Prescription encryption for compliance
    - Medication safety through encryption
    - Healthcare guidelines compliance
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted prescription field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        # Handle structured prescription data
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt prescription
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt prescription: {e}")
            raise EncryptionError(f"Failed to encrypt prescription: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt prescription."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))
    
    def decrypt_prescription(self) -> Dict[str, Any]:
        """
        Decrypt prescription as structured data.
        
        Returns:
            Dictionary with prescription data
        """
        decrypted = self.decrypt()
        if not decrypted:
            return {}
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return {"prescription": decrypted}


class EncryptedDiagnosis(EncryptedStr):
    """
    Encrypted field for diagnostic information.
    
    Features:
    - ICD-10 code encryption
    - Diagnostic notes encryption
    - Medical confidentiality protection
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted diagnosis field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        # Handle structured diagnosis data
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt diagnosis
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt diagnosis: {e}")
            raise EncryptionError(f"Failed to encrypt diagnosis: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt diagnosis."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))
    
    def decrypt_diagnosis(self) -> Dict[str, Any]:
        """
        Decrypt diagnosis as structured data.
        
        Returns:
            Dictionary with diagnosis data
        """
        decrypted = self.decrypt()
        if not decrypted:
            return {}
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return {"diagnosis": decrypted}


class EncryptedTreatmentNotes(EncryptedStr):
    """
    Encrypted field for treatment notes and clinical observations.
    
    Features:
    - Session notes encryption
    - Treatment progress encryption
    - Therapeutic relationship protection
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted treatment notes field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt treatment notes
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt treatment notes: {e}")
            raise EncryptionError(f"Failed to encrypt treatment notes: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt treatment notes."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))


class EncryptedMentalHealthAssessment(EncryptedStr):
    """
    Encrypted field for mental health assessment data.
    
    Features:
    - PHQ-9, GAD-7, and other scale encryption
    - Psychological test results encryption
    - Mental health confidentiality protection
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted mental health assessment field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        # Handle structured assessment data
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt assessment
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt mental health assessment: {e}")
            raise EncryptionError(f"Failed to encrypt mental health assessment: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt mental health assessment."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))
    
    def decrypt_assessment(self) -> Dict[str, Any]:
        """
        Decrypt assessment as structured data.
        
        Returns:
            Dictionary with assessment data
        """
        decrypted = self.decrypt()
        if not decrypted:
            return {}
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return {"assessment": decrypted}


class EncryptedLabResults(EncryptedStr):
    """
    Encrypted field for laboratory and exam results.
    
    Features:
    - Lab test results encryption
    - Medical exam data encryption
    - Health data protection
    """
    
    def __new__(cls, value: Any = ""):
        """Create encrypted lab results field."""
        if not value:
            return super(EncryptedStr, cls).__new__(cls, "")
        
        # Handle structured lab data
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        
        str_value = str(value).strip()
        
        # If already encrypted, store as-is
        if is_field_encrypted(str_value):
            return super(EncryptedStr, cls).__new__(cls, str_value)
        
        # Encrypt lab results
        try:
            encrypted_value = encrypt_medical_data(str_value)
            return super(EncryptedStr, cls).__new__(cls, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt lab results: {e}")
            raise EncryptionError(f"Failed to encrypt lab results: {str(e)}")
    
    def decrypt(self) -> str:
        """Decrypt lab results."""
        if not self:
            return ""
        return decrypt_medical_data(str(self))
    
    def decrypt_results(self) -> Dict[str, Any]:
        """
        Decrypt lab results as structured data.
        
        Returns:
            Dictionary with lab results data
        """
        decrypted = self.decrypt()
        if not decrypted:
            return {}
        
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return {"results": decrypted}


# Pydantic field validators for medical encrypted fields
def validate_encrypted_medical_history(value: Any) -> Optional[EncryptedMedicalHistory]:
    """Pydantic validator for encrypted medical history fields."""
    if value is None:
        return None
    return EncryptedMedicalHistory(value)


def validate_encrypted_prescription(value: Any) -> Optional[EncryptedPrescription]:
    """Pydantic validator for encrypted prescription fields."""
    if value is None:
        return None
    return EncryptedPrescription(value)


def validate_encrypted_diagnosis(value: Any) -> Optional[EncryptedDiagnosis]:
    """Pydantic validator for encrypted diagnosis fields."""
    if value is None:
        return None
    return EncryptedDiagnosis(value)


def validate_encrypted_treatment_notes(value: Any) -> Optional[EncryptedTreatmentNotes]:
    """Pydantic validator for encrypted treatment notes fields."""
    if value is None:
        return None
    return EncryptedTreatmentNotes(value)


def validate_encrypted_mental_health_assessment(value: Any) -> Optional[EncryptedMentalHealthAssessment]:
    """Pydantic validator for encrypted mental health assessment fields."""
    if value is None:
        return None
    return EncryptedMentalHealthAssessment(value)


def validate_encrypted_lab_results(value: Any) -> Optional[EncryptedLabResults]:
    """Pydantic validator for encrypted lab results fields."""
    if value is None:
        return None
    return EncryptedLabResults(value)


# Export medical encrypted field types
__all__ = [
    'EncryptedMedicalHistory',
    'EncryptedPrescription',
    'EncryptedDiagnosis',
    'EncryptedTreatmentNotes',
    'EncryptedMentalHealthAssessment',
    'EncryptedLabResults',
    'validate_encrypted_medical_history',
    'validate_encrypted_prescription',
    'validate_encrypted_diagnosis',
    'validate_encrypted_treatment_notes',
    'validate_encrypted_mental_health_assessment',
    'validate_encrypted_lab_results'
]