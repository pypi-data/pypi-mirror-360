"""
Form validation framework.

Provides validators for common field types and patterns.
"""

import re
from typing import Any, Optional, List, Pattern, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime, date


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    error_message: Optional[str] = None
    
    @staticmethod
    def valid() -> 'ValidationResult':
        """Create a valid result."""
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def invalid(message: str) -> 'ValidationResult':
        """Create an invalid result with error message."""
        return ValidationResult(is_valid=False, error_message=message)


class Validator(ABC):
    """Abstract base class for validators."""
    
    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validate a value."""
        pass
    
    def __call__(self, value: Any) -> ValidationResult:
        """Allow validators to be called directly."""
        return self.validate(value)


class RequiredValidator(Validator):
    """Validates that a field has a value."""
    
    def __init__(self, message: str = "This field is required"):
        self.message = message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value is not empty."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult.invalid(self.message)
        return ValidationResult.valid()


class EmailValidator(Validator):
    """Validates email format."""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, message: str = "Invalid email format"):
        self.message = message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value is a valid email."""
        if not value:
            return ValidationResult.valid()  # Empty is OK, use RequiredValidator for required
            
        if not isinstance(value, str):
            return ValidationResult.invalid(self.message)
            
        if not self.EMAIL_PATTERN.match(value.strip()):
            return ValidationResult.invalid(self.message)
            
        return ValidationResult.valid()


class LengthValidator(Validator):
    """Validates string length."""
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        min_message: Optional[str] = None,
        max_message: Optional[str] = None
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.min_message = min_message or f"Must be at least {min_length} characters"
        self.max_message = max_message or f"Must be at most {max_length} characters"
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value length is within bounds."""
        if not value:
            return ValidationResult.valid()
            
        if not isinstance(value, str):
            value = str(value)
            
        length = len(value)
        
        if self.min_length is not None and length < self.min_length:
            return ValidationResult.invalid(self.min_message)
            
        if self.max_length is not None and length > self.max_length:
            return ValidationResult.invalid(self.max_message)
            
        return ValidationResult.valid()


class PatternValidator(Validator):
    """Validates against a regex pattern."""
    
    def __init__(
        self,
        pattern: Union[str, Pattern],
        message: str = "Invalid format",
        flags: int = 0
    ):
        self.pattern = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        self.message = message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value matches pattern."""
        if not value:
            return ValidationResult.valid()
            
        if not isinstance(value, str):
            value = str(value)
            
        if not self.pattern.match(value):
            return ValidationResult.invalid(self.message)
            
        return ValidationResult.valid()


class NumericValidator(Validator):
    """Validates numeric values."""
    
    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        min_message: Optional[str] = None,
        max_message: Optional[str] = None,
        invalid_message: str = "Must be a valid number"
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.min_message = min_message or f"Must be at least {min_value}"
        self.max_message = max_message or f"Must be at most {max_value}"
        self.invalid_message = invalid_message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value is a valid number within bounds."""
        if not value and value != 0:
            return ValidationResult.valid()
            
        try:
            if self.integer_only:
                num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult.invalid(self.invalid_message)
        
        if self.min_value is not None and num_value < self.min_value:
            return ValidationResult.invalid(self.min_message)
            
        if self.max_value is not None and num_value > self.max_value:
            return ValidationResult.invalid(self.max_message)
            
        return ValidationResult.valid()


class DateValidator(Validator):
    """Validates date values."""
    
    def __init__(
        self,
        min_date: Optional[Union[date, datetime]] = None,
        max_date: Optional[Union[date, datetime]] = None,
        format: str = "%Y-%m-%d",
        min_message: Optional[str] = None,
        max_message: Optional[str] = None,
        invalid_message: str = "Invalid date format"
    ):
        self.min_date = min_date
        self.max_date = max_date
        self.format = format
        self.min_message = min_message or f"Date must be after {min_date}"
        self.max_message = max_message or f"Date must be before {max_date}"
        self.invalid_message = invalid_message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value is a valid date within bounds."""
        if not value:
            return ValidationResult.valid()
            
        # Handle different input types
        if isinstance(value, (date, datetime)):
            date_value = value
        elif isinstance(value, str):
            try:
                date_value = datetime.strptime(value, self.format).date()
            except ValueError:
                return ValidationResult.invalid(self.invalid_message)
        else:
            return ValidationResult.invalid(self.invalid_message)
        
        # Check bounds
        if self.min_date and date_value < self.min_date:
            return ValidationResult.invalid(self.min_message)
            
        if self.max_date and date_value > self.max_date:
            return ValidationResult.invalid(self.max_message)
            
        return ValidationResult.valid()


class CustomValidator(Validator):
    """Custom validator using a provided function."""
    
    def __init__(
        self,
        validate_func: Callable[[Any], bool],
        message: str = "Validation failed"
    ):
        self.validate_func = validate_func
        self.message = message
    
    def validate(self, value: Any) -> ValidationResult:
        """Check if value passes custom validation."""
        try:
            if self.validate_func(value):
                return ValidationResult.valid()
            else:
                return ValidationResult.invalid(self.message)
        except Exception as e:
            return ValidationResult.invalid(f"Validation error: {str(e)}")


class CompositeValidator(Validator):
    """Combines multiple validators."""
    
    def __init__(self, validators: List[Validator]):
        self.validators = validators
    
    def validate(self, value: Any) -> ValidationResult:
        """Run all validators and return first failure."""
        for validator in self.validators:
            result = validator.validate(value)
            if not result.is_valid:
                return result
        return ValidationResult.valid()


class CommonValidators:
    """Common pre-configured validators."""
    
    @staticmethod
    def phone(message: str = "Invalid phone number") -> PatternValidator:
        """Phone number validator."""
        # Accepts various phone formats
        pattern = r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
        return PatternValidator(pattern, message)
    
    @staticmethod
    def postal_code(country: str = "US", message: Optional[str] = None) -> PatternValidator:
        """Postal code validator for different countries."""
        patterns = {
            "US": r'^\d{5}(-\d{4})?$',
            "BR": r'^\d{5}-?\d{3}$',
            "UK": r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
            "CA": r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$',
        }
        
        pattern = patterns.get(country.upper(), patterns["US"])
        msg = message or f"Invalid {country} postal code"
        return PatternValidator(pattern, msg, re.IGNORECASE if country == "UK" else 0)
    
    @staticmethod
    def url(message: str = "Invalid URL") -> PatternValidator:
        """URL validator."""
        pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
        return PatternValidator(pattern, message)
    
    @staticmethod
    def username(
        min_length: int = 3,
        max_length: int = 20,
        message: str = "Username must be 3-20 characters, alphanumeric with underscores"
    ) -> CompositeValidator:
        """Username validator."""
        return CompositeValidator([
            LengthValidator(min_length, max_length),
            PatternValidator(r'^[a-zA-Z0-9_]+$', message)
        ])
    
    @staticmethod
    def password(
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True
    ) -> Callable[[str], ValidationResult]:
        """Password strength validator."""
        def validate_password(value: str) -> ValidationResult:
            if not value:
                return ValidationResult.valid()
                
            errors = []
            
            if len(value) < min_length:
                errors.append(f"at least {min_length} characters")
                
            if require_uppercase and not re.search(r'[A-Z]', value):
                errors.append("one uppercase letter")
                
            if require_lowercase and not re.search(r'[a-z]', value):
                errors.append("one lowercase letter")
                
            if require_digit and not re.search(r'\d', value):
                errors.append("one digit")
                
            if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
                errors.append("one special character")
                
            if errors:
                return ValidationResult.invalid(f"Password must contain {', '.join(errors)}")
                
            return ValidationResult.valid()
            
        return CustomValidator(lambda v: validate_password(v).is_valid, "Invalid password")
    
    @staticmethod
    def cpf(message: str = "Invalid CPF") -> Callable[[str], ValidationResult]:
        """Brazilian CPF validator."""
        def validate_cpf(value: str) -> bool:
            # Remove non-digits
            cpf = re.sub(r'\D', '', value)
            
            # Check length
            if len(cpf) != 11:
                return False
                
            # Check for known invalid CPFs
            if cpf in ['00000000000', '11111111111', '22222222222', '33333333333',
                      '44444444444', '55555555555', '66666666666', '77777777777',
                      '88888888888', '99999999999']:
                return False
                
            # Validate check digits
            # First digit
            sum_digit = sum(int(cpf[i]) * (10 - i) for i in range(9))
            check_digit1 = (sum_digit * 10) % 11
            if check_digit1 == 10:
                check_digit1 = 0
                
            if check_digit1 != int(cpf[9]):
                return False
                
            # Second digit
            sum_digit = sum(int(cpf[i]) * (11 - i) for i in range(10))
            check_digit2 = (sum_digit * 10) % 11
            if check_digit2 == 10:
                check_digit2 = 0
                
            if check_digit2 != int(cpf[10]):
                return False
                
            return True
            
        return CustomValidator(validate_cpf, message)
    
    @staticmethod
    def credit_card(message: str = "Invalid credit card number") -> Callable[[str], ValidationResult]:
        """Credit card number validator (Luhn algorithm)."""
        def validate_card(value: str) -> bool:
            # Remove spaces and dashes
            card_number = re.sub(r'[\s-]', '', value)
            
            # Check if all digits
            if not card_number.isdigit():
                return False
                
            # Check length (most cards are 13-19 digits)
            if not 13 <= len(card_number) <= 19:
                return False
                
            # Luhn algorithm
            total = 0
            reverse_digits = card_number[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
                
            return total % 10 == 0
            
        return CustomValidator(validate_card, message)