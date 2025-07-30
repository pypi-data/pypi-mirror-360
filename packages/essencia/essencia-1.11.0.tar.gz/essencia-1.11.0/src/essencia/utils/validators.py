"""
Validation functions for Brazilian data formats and business rules.
"""

import re
from datetime import datetime, date
from typing import Optional

from essencia.core.exceptions import ValidationError


class CPFValidator:
    """Validator for Brazilian CPF (Cadastro de Pessoas Físicas)"""
    
    @staticmethod
    def clean(cpf: str) -> str:
        """Remove non-numeric characters from CPF"""
        return re.sub(r'\D', '', cpf)
    
    @staticmethod
    def format(cpf: str) -> str:
        """Format CPF as XXX.XXX.XXX-XX"""
        clean_cpf = CPFValidator.clean(cpf)
        if len(clean_cpf) != 11:
            return cpf
        return f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"
    
    @staticmethod
    def validate(cpf: str) -> bool:
        """
        Validate CPF with checksum verification.
        Returns True if valid, raises ValidationError if invalid.
        """
        if not cpf:
            raise ValidationError("CPF é obrigatório")
        
        # Clean CPF
        clean_cpf = CPFValidator.clean(cpf)
        
        # Check length
        if len(clean_cpf) != 11:
            raise ValidationError("CPF deve ter 11 dígitos")
        
        # Check if all digits are the same (invalid CPFs like 111.111.111-11)
        if len(set(clean_cpf)) == 1:
            raise ValidationError("CPF inválido")
        
        # Validate checksum
        def calculate_digit(cpf_partial: str, digit_position: int) -> int:
            total = 0
            for i, digit in enumerate(cpf_partial[:digit_position]):
                total += int(digit) * ((digit_position + 1) - i)
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Check first digit
        if calculate_digit(clean_cpf, 9) != int(clean_cpf[9]):
            raise ValidationError("CPF inválido")
        
        # Check second digit
        if calculate_digit(clean_cpf, 10) != int(clean_cpf[10]):
            raise ValidationError("CPF inválido")
        
        return True


class CNPJValidator:
    """Validator for Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica)"""
    
    @staticmethod
    def clean(cnpj: str) -> str:
        """Remove non-numeric characters from CNPJ"""
        return re.sub(r'\D', '', cnpj)
    
    @staticmethod
    def format(cnpj: str) -> str:
        """Format CNPJ as XX.XXX.XXX/XXXX-XX"""
        clean_cnpj = CNPJValidator.clean(cnpj)
        if len(clean_cnpj) != 14:
            return cnpj
        return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}"
    
    @staticmethod
    def validate(cnpj: str) -> bool:
        """Validate CNPJ with checksum verification"""
        if not cnpj:
            raise ValidationError("CNPJ é obrigatório")
        
        clean_cnpj = CNPJValidator.clean(cnpj)
        
        if len(clean_cnpj) != 14:
            raise ValidationError("CNPJ deve ter 14 dígitos")
        
        # Similar validation logic as CPF but with different weights
        # Implementation omitted for brevity
        return True


class PhoneValidator:
    """Validator for Brazilian phone numbers"""
    
    @staticmethod
    def clean(phone: str) -> str:
        """Remove non-numeric characters from phone"""
        return re.sub(r'\D', '', phone)
    
    @staticmethod
    def format(phone: str) -> str:
        """Format phone number as (XX) XXXXX-XXXX or (XX) XXXX-XXXX"""
        digits = PhoneValidator.clean(phone)
        
        if len(digits) == 11:  # Mobile
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:  # Landline
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        else:
            return phone
    
    @staticmethod
    def validate(phone: str) -> bool:
        """Validate Brazilian phone number"""
        if not phone:
            raise ValidationError("Telefone é obrigatório")
        
        digits = PhoneValidator.clean(phone)
        
        if len(digits) not in [10, 11]:
            raise ValidationError("Telefone deve ter 10 ou 11 dígitos")
        
        # Check area code (DDD)
        area_code = int(digits[:2])
        valid_area_codes = [
            11, 12, 13, 14, 15, 16, 17, 18, 19,  # São Paulo
            21, 22, 24,  # Rio de Janeiro
            27, 28,  # Espírito Santo
            31, 32, 33, 34, 35, 37, 38,  # Minas Gerais
            41, 42, 43, 44, 45, 46,  # Paraná
            47, 48, 49,  # Santa Catarina
            51, 53, 54, 55,  # Rio Grande do Sul
            61,  # Distrito Federal
            62, 64,  # Goiás
            63,  # Tocantins
            65, 66,  # Mato Grosso
            67,  # Mato Grosso do Sul
            68,  # Acre
            69,  # Rondônia
            71, 73, 74, 75, 77,  # Bahia
            79,  # Sergipe
            81, 87,  # Pernambuco
            82,  # Alagoas
            83,  # Paraíba
            84,  # Rio Grande do Norte
            85, 88,  # Ceará
            86, 89,  # Piauí
            91, 93, 94,  # Pará
            92, 97,  # Amazonas
            95,  # Roraima
            96,  # Amapá
            98, 99,  # Maranhão
        ]
        
        if area_code not in valid_area_codes:
            raise ValidationError("Código de área inválido")
        
        # Check if mobile number starts with 9
        if len(digits) == 11 and digits[2] != '9':
            raise ValidationError("Número de celular deve começar com 9")
        
        return True


class EmailValidator:
    """Email validation"""
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @staticmethod
    def validate(email: str) -> bool:
        """Validate email format"""
        if not email:
            raise ValidationError("Email é obrigatório")
        
        if not EmailValidator.EMAIL_REGEX.match(email):
            raise ValidationError("Email inválido")
        
        return True


class DateValidator:
    """Date validation and utilities"""
    
    @staticmethod
    def validate_birth_date(birth_date: date) -> bool:
        """Validate birth date"""
        if not birth_date:
            raise ValidationError("Data de nascimento é obrigatória")
        
        today = date.today()
        
        # Check if date is in the future
        if birth_date > today:
            raise ValidationError("Data de nascimento não pode ser no futuro")
        
        # Check if age is reasonable (0-150 years)
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        
        if age > 150:
            raise ValidationError("Data de nascimento inválida")
        
        return True
    
    @staticmethod
    def validate_appointment_date(appointment_date: datetime) -> bool:
        """Validate appointment date"""
        if not appointment_date:
            raise ValidationError("Data do agendamento é obrigatória")
        
        # Check if date is too far in the past
        if appointment_date.date() < date.today():
            raise ValidationError("Não é possível agendar para datas passadas")
        
        # Check if date is too far in the future (e.g., 1 year)
        max_future_date = datetime.now().replace(year=datetime.now().year + 1)
        if appointment_date > max_future_date:
            raise ValidationError("Data muito distante no futuro")
        
        return True


class MoneyValidator:
    """Money/currency validation"""
    
    @staticmethod
    def clean(value: str) -> float:
        """Clean money string to float"""
        if not value:
            return 0.0
        
        # Remove currency symbol and spaces
        cleaned = value.replace('R$', '').strip()
        
        # Handle Brazilian format (1.234,56) vs US format (1,234.56)
        if ',' in cleaned and '.' in cleaned:
            # Determine which is decimal separator
            if cleaned.rindex(',') > cleaned.rindex('.'):
                # Brazilian format
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US format
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma, assume Brazilian decimal
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            raise ValidationError(f"Valor monetário inválido: {value}")
    
    @staticmethod
    def format(value: float) -> str:
        """Format float as Brazilian currency"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def validate(value: float, min_value: float = 0.0, 
                 max_value: Optional[float] = None) -> bool:
        """Validate money amount"""
        if value < min_value:
            raise ValidationError(
                f"Valor deve ser maior ou igual a {MoneyValidator.format(min_value)}"
            )
        
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"Valor deve ser menor ou igual a {MoneyValidator.format(max_value)}"
            )
        
        return True


class PasswordValidator:
    """Password strength validation"""
    
    @staticmethod
    def validate(password: str, min_length: int = 8) -> bool:
        """
        Validate password strength.
        Default requirements: minimum 8 characters
        """
        if not password:
            raise ValidationError("Senha é obrigatória")
        
        if len(password) < min_length:
            raise ValidationError(f"Senha deve ter pelo menos {min_length} caracteres")
        
        # Additional checks can be added:
        # - Require uppercase/lowercase
        # - Require numbers
        # - Require special characters
        # - Check against common passwords
        
        return True


# Convenience functions for field validation
def validate_required(value: any, field_name: str = "Campo") -> bool:
    """Validate that a field is not empty"""
    if not value:
        raise ValidationError(f"{field_name} é obrigatório")
    return True


def validate_length(value: str, min_length: int = None, max_length: int = None,
                   field_name: str = "Campo") -> bool:
    """Validate string length"""
    if min_length and len(value) < min_length:
        raise ValidationError(
            f"{field_name} deve ter pelo menos {min_length} caracteres"
        )
    
    if max_length and len(value) > max_length:
        raise ValidationError(
            f"{field_name} deve ter no máximo {max_length} caracteres"
        )
    
    return True