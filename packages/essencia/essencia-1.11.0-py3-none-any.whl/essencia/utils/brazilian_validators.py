"""
Enhanced Brazilian validators with generation capabilities.
"""
import random
import re
from typing import Optional, List, Dict, Any
import httpx
from unidecode import unidecode


class CPFGenerator:
    """Generate valid CPF numbers."""
    
    @staticmethod
    def generate(formatted: bool = True, state: Optional[str] = None) -> str:
        """
        Generate a valid CPF number.
        
        Args:
            formatted: Whether to return formatted CPF (XXX.XXX.XXX-XX)
            state: Optional state code for regional CPF generation
            
        Returns:
            Generated CPF number
        """
        # State-based digit mapping (9th digit)
        state_digits = {
            'RS': 0, 'SC': 0, 'PR': 0,  # Region 0
            'SP': 1,  # Region 1
            'RJ': 2, 'ES': 2,  # Region 2
            'MG': 3,  # Region 3
            'MS': 4, 'MT': 4, 'GO': 4, 'DF': 4,  # Region 4
            'PA': 5, 'AM': 5, 'AC': 5, 'AP': 5, 'RO': 5, 'RR': 5,  # Region 5
            'CE': 6, 'MA': 6, 'PI': 6,  # Region 6
            'PE': 7, 'PB': 7, 'RN': 7, 'AL': 7,  # Region 7
            'BA': 8, 'SE': 8,  # Region 8
            'TO': 9  # Region 9
        }
        
        # Generate first 8 digits
        digits = [random.randint(0, 9) for _ in range(8)]
        
        # Add state digit
        if state and state.upper() in state_digits:
            digits.append(state_digits[state.upper()])
        else:
            digits.append(random.randint(0, 9))
        
        # Calculate first check digit
        sum1 = sum((10 - i) * digit for i, digit in enumerate(digits))
        check1 = (sum1 * 10) % 11
        if check1 == 10:
            check1 = 0
        digits.append(check1)
        
        # Calculate second check digit
        sum2 = sum((11 - i) * digit for i, digit in enumerate(digits))
        check2 = (sum2 * 10) % 11
        if check2 == 10:
            check2 = 0
        digits.append(check2)
        
        cpf = ''.join(map(str, digits))
        
        if formatted:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def generate_batch(count: int, formatted: bool = True, state: Optional[str] = None) -> List[str]:
        """Generate multiple valid CPF numbers."""
        return [CPFGenerator.generate(formatted, state) for _ in range(count)]


class CNPJGenerator:
    """Generate valid CNPJ numbers."""
    
    @staticmethod
    def generate(formatted: bool = True, branch: int = 1) -> str:
        """
        Generate a valid CNPJ number.
        
        Args:
            formatted: Whether to return formatted CNPJ (XX.XXX.XXX/XXXX-XX)
            branch: Branch number (default: 0001)
            
        Returns:
            Generated CNPJ number
        """
        # Generate first 8 digits (company identifier)
        digits = [random.randint(0, 9) for _ in range(8)]
        
        # Add branch digits (usually 0001 for main branch)
        branch_digits = f"{branch:04d}"
        digits.extend([int(d) for d in branch_digits])
        
        # Calculate first check digit
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = sum(d * w for d, w in zip(digits, weights1))
        check1 = 11 - (sum1 % 11)
        if check1 >= 10:
            check1 = 0
        digits.append(check1)
        
        # Calculate second check digit
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum2 = sum(d * w for d, w in zip(digits, weights2))
        check2 = 11 - (sum2 % 11)
        if check2 >= 10:
            check2 = 0
        digits.append(check2)
        
        cnpj = ''.join(map(str, digits))
        
        if formatted:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    @staticmethod
    def generate_batch(count: int, formatted: bool = True) -> List[str]:
        """Generate multiple valid CNPJ numbers."""
        return [CNPJGenerator.generate(formatted, i + 1) for i in range(count)]


class CEPValidator:
    """Enhanced CEP validator with address lookup."""
    
    BASE_URL = "https://viacep.com.br/ws"
    
    @staticmethod
    def format_cep(cep: str) -> str:
        """Format CEP to XXXXX-XXX."""
        digits = re.sub(r'\D', '', cep)
        if len(digits) == 8:
            return f"{digits[:5]}-{digits[5:]}"
        return digits
    
    @staticmethod
    def validate_cep(cep: str) -> bool:
        """Validate CEP format."""
        digits = re.sub(r'\D', '', cep)
        return len(digits) == 8 and digits.isdigit()
    
    @staticmethod
    async def lookup_address(cep: str) -> Optional[Dict[str, Any]]:
        """
        Look up address information for a CEP.
        
        Args:
            cep: CEP code to look up
            
        Returns:
            Address information or None if not found
        """
        if not CEPValidator.validate_cep(cep):
            return None
        
        digits = re.sub(r'\D', '', cep)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{CEPValidator.BASE_URL}/{digits}/json/")
                if response.status_code == 200:
                    data = response.json()
                    if "erro" not in data:
                        return {
                            "cep": CEPValidator.format_cep(digits),
                            "street": data.get("logradouro", ""),
                            "complement": data.get("complemento", ""),
                            "neighborhood": data.get("bairro", ""),
                            "city": data.get("localidade", ""),
                            "state": data.get("uf", ""),
                            "ibge_code": data.get("ibge", ""),
                            "ddd": data.get("ddd", ""),
                            "siafi": data.get("siafi", "")
                        }
            except Exception:
                pass
        
        return None
    
    @staticmethod
    def lookup_address_sync(cep: str) -> Optional[Dict[str, Any]]:
        """Synchronous version of address lookup."""
        if not CEPValidator.validate_cep(cep):
            return None
        
        digits = re.sub(r'\D', '', cep)
        
        try:
            response = httpx.get(f"{CEPValidator.BASE_URL}/{digits}/json/")
            if response.status_code == 200:
                data = response.json()
                if "erro" not in data:
                    return {
                        "cep": CEPValidator.format_cep(digits),
                        "street": data.get("logradouro", ""),
                        "complement": data.get("complemento", ""),
                        "neighborhood": data.get("bairro", ""),
                        "city": data.get("localidade", ""),
                        "state": data.get("uf", ""),
                        "ibge_code": data.get("ibge", ""),
                        "ddd": data.get("ddd", ""),
                        "siafi": data.get("siafi", "")
                    }
        except Exception:
            pass
        
        return None


class PhoneValidator:
    """Enhanced Brazilian phone validator."""
    
    # Valid area codes by region
    AREA_CODES = {
        # São Paulo
        'SP': ['11', '12', '13', '14', '15', '16', '17', '18', '19'],
        # Rio de Janeiro
        'RJ': ['21', '22', '24'],
        # Espírito Santo
        'ES': ['27', '28'],
        # Minas Gerais
        'MG': ['31', '32', '33', '34', '35', '37', '38'],
        # Paraná
        'PR': ['41', '42', '43', '44', '45', '46'],
        # Santa Catarina
        'SC': ['47', '48', '49'],
        # Rio Grande do Sul
        'RS': ['51', '53', '54', '55'],
        # Bahia
        'BA': ['71', '73', '74', '75', '77'],
        # Sergipe
        'SE': ['79'],
        # Pernambuco
        'PE': ['81', '87'],
        # Alagoas
        'AL': ['82'],
        # Paraíba
        'PB': ['83'],
        # Rio Grande do Norte
        'RN': ['84'],
        # Ceará
        'CE': ['85', '88'],
        # Piauí
        'PI': ['86', '89'],
        # Maranhão
        'MA': ['98', '99'],
        # Pará
        'PA': ['91', '93', '94'],
        # Amapá
        'AP': ['96'],
        # Amazonas
        'AM': ['92', '97'],
        # Roraima
        'RR': ['95'],
        # Acre
        'AC': ['68'],
        # Rondônia
        'RO': ['69'],
        # Tocantins
        'TO': ['63'],
        # Mato Grosso
        'MT': ['65', '66'],
        # Mato Grosso do Sul
        'MS': ['67'],
        # Goiás
        'GO': ['62', '64'],
        # Distrito Federal
        'DF': ['61']
    }
    
    # Flatten area codes
    ALL_AREA_CODES = [code for codes in AREA_CODES.values() for code in codes]
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Brazilian phone number."""
        digits = re.sub(r'\D', '', phone)
        
        # Check length (10 or 11 digits)
        if len(digits) not in [10, 11]:
            return False
        
        # Check area code
        area_code = digits[:2]
        if area_code not in PhoneValidator.ALL_AREA_CODES:
            return False
        
        # Check mobile (9 as first digit for 11-digit numbers)
        if len(digits) == 11 and digits[2] != '9':
            return False
        
        # Check landline (2-5 as first digit for 10-digit numbers)
        if len(digits) == 10 and digits[2] not in '2345':
            return False
        
        return True
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number to (XX) XXXXX-XXXX or (XX) XXXX-XXXX."""
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        
        return phone
    
    @staticmethod
    def get_state_by_area_code(area_code: str) -> Optional[str]:
        """Get state by area code."""
        for state, codes in PhoneValidator.AREA_CODES.items():
            if area_code in codes:
                return state
        return None
    
    @staticmethod
    def generate(state: Optional[str] = None, mobile: bool = True) -> str:
        """Generate a valid Brazilian phone number."""
        if state and state.upper() in PhoneValidator.AREA_CODES:
            area_code = random.choice(PhoneValidator.AREA_CODES[state.upper()])
        else:
            area_code = random.choice(PhoneValidator.ALL_AREA_CODES)
        
        if mobile:
            # Mobile: 9 + 8 digits
            number = '9' + ''.join([str(random.randint(0, 9)) for _ in range(8)])
        else:
            # Landline: 2-5 + 7 digits
            first_digit = random.choice('2345')
            number = first_digit + ''.join([str(random.randint(0, 9)) for _ in range(7)])
        
        return f"({area_code}) {number[:5]}-{number[5:]}" if mobile else f"({area_code}) {number[:4]}-{number[4:]}"


class RGValidator:
    """RG (Registro Geral) validator."""
    
    @staticmethod
    def validate_rg(rg: str, state: str = "SP") -> bool:
        """
        Validate RG number (format varies by state).
        
        Args:
            rg: RG number to validate
            state: State code (default: SP)
            
        Returns:
            Whether the RG is valid for the given state
        """
        digits = re.sub(r'\D', '', rg)
        
        # Basic validation
        if not digits or len(digits) < 7:
            return False
        
        # State-specific validation
        if state.upper() == "SP":
            # São Paulo: XX.XXX.XXX-X or XX.XXX.XXX-XX
            return len(digits) in [9, 10]
        elif state.upper() == "RJ":
            # Rio de Janeiro: XX.XXX.XXX-X
            return len(digits) == 9
        elif state.upper() == "MG":
            # Minas Gerais: MG-XX.XXX.XXX
            return len(digits) >= 8
        else:
            # Generic validation
            return 7 <= len(digits) <= 12
    
    @staticmethod
    def format_rg(rg: str, state: str = "SP") -> str:
        """Format RG number according to state convention."""
        digits = re.sub(r'\D', '', rg)
        
        if state.upper() == "SP":
            if len(digits) == 9:
                return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8]}"
            elif len(digits) == 10:
                return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8:]}"
        elif state.upper() == "RJ":
            if len(digits) == 9:
                return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}-{digits[8]}"
        elif state.upper() == "MG":
            if len(digits) >= 8:
                return f"MG-{digits[:2]}.{digits[2:5]}.{digits[5:8]}"
        
        return rg


class PIXKeyValidator:
    """PIX key validator for Brazilian instant payment system."""
    
    @staticmethod
    def validate_pix_key(key: str) -> Dict[str, Any]:
        """
        Validate and identify PIX key type.
        
        Args:
            key: PIX key to validate
            
        Returns:
            Dictionary with validation result and key type
        """
        key = key.strip()
        
        # CPF
        cpf_digits = re.sub(r'\D', '', key)
        if len(cpf_digits) == 11 and validate_cpf(cpf_digits):
            return {"valid": True, "type": "CPF", "formatted": format_cpf(cpf_digits)}
        
        # CNPJ
        if len(cpf_digits) == 14 and validate_cnpj(cpf_digits):
            return {"valid": True, "type": "CNPJ", "formatted": format_cnpj(cpf_digits)}
        
        # Email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, key.lower()):
            return {"valid": True, "type": "Email", "formatted": key.lower()}
        
        # Phone
        phone_digits = re.sub(r'\D', '', key)
        if PhoneValidator.validate_phone(phone_digits):
            return {"valid": True, "type": "Phone", "formatted": PhoneValidator.format_phone(phone_digits)}
        
        # Random key (UUID format)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, key.lower()):
            return {"valid": True, "type": "Random", "formatted": key.lower()}
        
        return {"valid": False, "type": None, "formatted": None}


# Import original validators to maintain compatibility
from essencia.utils.validators import validate_cpf, validate_cnpj, format_cpf, format_cnpj