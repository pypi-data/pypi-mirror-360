"""
People models for the medical system.
"""

import datetime
from typing import Self, Optional, ClassVar
from datetime import date
from dateutil.relativedelta import relativedelta
import io
from calendar import leapdays
from typing import Annotated

from pydantic import computed_field, field_validator, EmailStr, BeforeValidator
from unidecode import unidecode

from .bases import MongoModel, StrEnum


def today() -> date:
    """Get current date."""
    return datetime.date.today()


class Person(MongoModel):
    """Represents a core individual in the medical system with personal identifiers.
    
    Inherits from MongoModel for MongoDB document persistence. Provides base fields
    and methods common to all person types in the system.
    
    Attributes:
        fname: First name (required)
        lname: Last name (required)
        gender: Gender identity from predefined enum
        bdate: Birth date (required)
        cpf: Brazilian tax ID (11 digits, optional)
        ddate: Death date if deceased (optional)
        sname: Social/preferred name (optional)
    """
    
    class Gender(StrEnum):
        """Enumeration of gender identities following Brazilian health system standards.
        
        Attributes:
            M: Masculino (Male)
            F: Feminino (Female)
            Y: Trans Masculino (Trans Masculine)
            X: Trans Feminino (Trans Feminine)
            T: Travesti (Travesti)
            N: Não binário (Non-binary)
        """
        M = 'Masculino'
        F = 'Feminino'
        Y = 'Trans Masculino'
        X = 'Trans Feminino'
        T = 'Travesti'
        N = 'Não binário'
        
    fname: str
    lname: str
    gender: Gender
    bdate: date
    cpf: Optional[str] = None
    ddate: Optional[date] = None
    sname: Optional[str] = None

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: Optional[str]) -> Optional[str]:
        """Validate Brazilian CPF (Cadastro de Pessoas Físicas) format.
        
        Args:
            v: CPF value to validate. Can be None for optional field.
            
        Returns:
            Validated CPF string if valid, None if input was None.
            
        Raises:
            ValueError: If CPF is invalid (not 11 digits or contains non-numeric chars)
        """
        if v is None:
            return v
        if v == '':
            return None
        v = ''.join([i for i in v if i.isdigit()])
        
        # For 10-digit CPFs (missing leading zero), pad with zero
        if len(v) == 10 and v.isdigit():
            v = '0' + v
            
        if len(v) != 11 or not v.isdigit():
            raise ValueError('CPF must contain 11 digits')
        return v

    def calculate_age(self, ref_date: Optional[date] = None) -> relativedelta:
        """Calculate accurate age using dateutil.relativedelta for precise year calculation.
        
        Handles leap years and month/day boundaries more accurately than simple year subtraction.
        
        Args:
            ref_date: Reference date for age calculation (defaults to current date).
                Uses deceased date (ddate) if available for deceased individuals.
                
        Returns:
            relativedelta: Age as a relativedelta object.
        """
        end_date = self.ddate or ref_date or today()
        return relativedelta(end_date, self.bdate)

    @property
    def age(self) -> int:
        """Shorthand property for current age using default calculate_age parameters.
        
        Returns:
            int: Current age in years based on system date.
        """
        return self.calculate_age().years

    def __repr__(self) -> str:
        return f"<Person {self.code} {self.fname} {self.lname}>"

    def __hash__(self) -> int:
        return hash((self.code, self.bdate))

    @computed_field
    @property
    def code(self) -> str:
        """Generates unique identifier code combining key person attributes.
        
        Code format: YYYYMMDD + gender code + first 3 letters of first name +
        first 3 letters of last surname, normalized to ASCII lowercase.
        
        Example:
            19901231MJOHSMI -> Male born 1990-12-31 named John Smith
            
        Returns:
            str: 14-16 character unique identifier
        """
        base = (
            f"{self.bdate.isoformat().replace('-', '')}"
            f"{self.gender.name}"
            f"{self.fname[:3]}"
            f"{self.lname.split()[-1][:3]}"
        )
        return unidecode(base.lower())

    @classmethod
    def search_query(cls, value: str) -> dict:
        # Normalize the search value to match how the 'search' field is generated
        normalized_value = unidecode(value.lower())
        return {'search': {'$regex': normalized_value}}
    
    def __lt__(self, other):
        return unidecode(str(self).lower()) < unidecode(str(other).lower())

    def __str__(self):
        return self.sname if self.sname else f"{self.fname} {self.lname}"
        
        
class BaseProfile(Person):
    """Base class for extended user profiles with contact information.
    
    Inherits all fields from Person and adds common profile fields used by
    both patients and staff members.
    
    Attributes:
        inactive: Flag marking profile as inactive (default False)
        address: Full street address (optional)
        city: City of residence (optional)
        phone: International phone number (optional)
        email: Valid email address (optional)
    """
    inactive: bool = False
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validates international phone number format.
        
        Args:
            v: Phone number string to validate. Can include spaces, hyphens, and + prefix.
            
        Returns:
            str: Cleaned phone number with only digits (no formatting)
            
        Raises:
            ValueError: If contains non-digit characters after cleaning
        """
        if v is None:
            return v
            
        clean = ''.join([i for i in v if any([i.isdigit(), i in ['-', '+']])])
        return clean
    
    
class Patient(BaseProfile):
    """Represents a patient receiving medical care in the system.
    
    Inherits from BaseProfile. MongoDB collection name 'patient'.
    
    Attributes:
        COLLECTION_NAME: MongoDB collection name ('patient')
        NAMES: Localized display names for UI
    """
    COLLECTION_NAME: ClassVar[str] = 'patient'
    NAMES: ClassVar[dict] = {
            'singular': 'Paciente',
            'plural': 'Pacientes',
            'key': 'patient_key',
            'instance': 'patient'
    }


class Staff(BaseProfile):
    """Base class for staff members with required email.
    
    Inherits from BaseProfile and adds email validation.
    
    Attributes:
        email: Required valid email address (EmailStr validated)
    """
    email: EmailStr


class Doctor(Staff):
    """Represents a medical doctor in the system.
    
    Inherits from Staff. MongoDB collection name 'doctor'.
    
    Attributes:
        COLLECTION_NAME: MongoDB collection name ('doctor')
        NAMES: Localized display names for UI
    """
    COLLECTION_NAME: ClassVar[str] = 'doctor'
    NAMES: ClassVar[dict] = {
            'singular': 'Médico',
            'plural': 'Médicos',
            'key': 'doctor_key',
            'instance': 'doctor'
    }

class Therapist(Staff):
    """Represents a therapeutic specialist (psychologist, physiotherapist, etc).
    
    Inherits from Staff. MongoDB collection name 'therapist'.
    
    Attributes:
        COLLECTION_NAME: MongoDB collection name ('therapist')
        NAMES: Localized display names for UI
    """
    COLLECTION_NAME: ClassVar[str] = 'therapist'
    NAMES: ClassVar[dict] = {
            'singular': 'Terapeuta',
            'plural': 'Terapeutas',
            'key': 'therapist_key',
            'instance': 'therapist'
    }

class Employee(Staff):
    """Represents an administrative/non-medical staff member.
    
    Inherits from Staff. MongoDB collection name 'employee'.
    
    Attributes:
        COLLECTION_NAME: MongoDB collection name ('employee')
        NAMES: Localized display names for UI
    """
    COLLECTION_NAME: ClassVar[str] = 'employee'
    NAMES: ClassVar[dict] = {
            'singular': 'Funcionário',
            'plural': 'Funcionários',
            'key': 'employee_key',
            'instance': 'employee'
    }