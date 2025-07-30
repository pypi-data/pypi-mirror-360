"""
SUS (Sistema Único de Saúde) integration for Brazilian public health system.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field

from essencia.models import MongoModel
from essencia.fields import EncryptedCPF, EncryptedStr
from essencia.utils.brazilian_validators import validate_cpf, format_cpf


class SUSCardStatus(str, Enum):
    """CNS (Cartão Nacional de Saúde) status."""
    ACTIVE = "ativo"
    INACTIVE = "inativo"
    SUSPENDED = "suspenso"
    CANCELLED = "cancelado"


class HealthFacilityType(str, Enum):
    """Types of health facilities in SUS."""
    UBS = "ubs"  # Unidade Básica de Saúde
    USF = "usf"  # Unidade de Saúde da Família
    UPA = "upa"  # Unidade de Pronto Atendimento
    HOSPITAL = "hospital"
    CAPS = "caps"  # Centro de Atenção Psicossocial
    CEO = "ceo"  # Centro de Especialidades Odontológicas
    AMBULATORIO = "ambulatorio"  # Ambulatório de Especialidades
    POLICLINICA = "policlinica"
    SAMU = "samu"  # Serviço de Atendimento Móvel de Urgência


class VaccinationStatus(str, Enum):
    """Vaccination status in the national program."""
    COMPLETE = "completo"
    INCOMPLETE = "incompleto"
    DELAYED = "atrasado"
    NOT_STARTED = "nao_iniciado"


class SUSPatient(MongoModel):
    """Patient registered in SUS."""
    # Personal data
    full_name: str = Field(..., description="Nome completo")
    cpf: EncryptedCPF = Field(..., description="CPF")
    cns: EncryptedStr = Field(..., description="Cartão Nacional de Saúde")
    cns_status: SUSCardStatus = Field(default=SUSCardStatus.ACTIVE)
    
    # Birth data
    birth_date: date
    birth_city: str
    birth_state: str
    mother_name: str = Field(..., description="Nome da mãe")
    father_name: Optional[str] = Field(None, description="Nome do pai")
    
    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Address
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    cep: str
    
    # SUS specific
    family_health_team: Optional[str] = Field(None, description="Equipe de Saúde da Família")
    reference_ubs: Optional[str] = Field(None, description="UBS de referência")
    social_program_beneficiary: bool = Field(False, description="Beneficiário de programa social")
    indigenous: bool = False
    quilombola: bool = False
    
    # Health data
    blood_type: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    continuous_medications: List[str] = Field(default_factory=list)
    
    # Metadata
    registration_date: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        collection_name = "sus_patients"
        indexes = [
            "cpf",
            "cns",
            ("city", "reference_ubs"),
            "family_health_team"
        ]


class SUSHealthFacility(MongoModel):
    """Health facility in the SUS network."""
    cnes: str = Field(..., description="Cadastro Nacional de Estabelecimentos de Saúde")
    name: str = Field(..., description="Nome do estabelecimento")
    facility_type: HealthFacilityType
    
    # Location
    street: str
    number: str
    neighborhood: str
    city: str
    state: str
    cep: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Contact
    phone: str
    email: Optional[str] = None
    manager_name: Optional[str] = None
    
    # Services
    services: List[str] = Field(default_factory=list, description="Serviços oferecidos")
    specialties: List[str] = Field(default_factory=list, description="Especialidades médicas")
    
    # Resources
    total_beds: Optional[int] = None
    icu_beds: Optional[int] = None
    emergency_room: bool = False
    surgery_center: bool = False
    imaging_services: List[str] = Field(default_factory=list)  # X-ray, CT, MRI, etc.
    
    # Teams
    family_health_teams: List[str] = Field(default_factory=list)
    oral_health_teams: List[str] = Field(default_factory=list)
    
    # Schedule
    opening_hours: Dict[str, str] = Field(default_factory=dict)  # day: "HH:MM-HH:MM"
    
    active: bool = True
    
    class Settings:
        collection_name = "sus_facilities"
        indexes = [
            "cnes",
            "city",
            "facility_type",
            ("latitude", "longitude")
        ]


class SUSAppointment(MongoModel):
    """Appointment in the SUS system."""
    patient_cns: str = Field(..., description="CNS do paciente")
    facility_cnes: str = Field(..., description="CNES do estabelecimento")
    
    # Scheduling
    scheduled_date: datetime
    specialty: str
    professional_name: Optional[str] = None
    professional_cns: Optional[str] = None
    
    # Type
    appointment_type: str = Field(..., description="Consulta, Exame, Procedimento")
    first_time: bool = Field(False, description="Primeira consulta")
    referral: bool = Field(False, description="Encaminhamento")
    referral_origin: Optional[str] = None
    
    # Queue management
    queue_entry_date: datetime = Field(default_factory=datetime.now)
    priority: int = Field(0, description="0=Normal, 1=Idoso, 2=Gestante, 3=Urgente")
    regulation_protocol: Optional[str] = None
    
    # Status
    status: str = Field("agendado", description="agendado, confirmado, realizado, faltou, cancelado")
    cancellation_reason: Optional[str] = None
    
    # Result
    attendance_date: Optional[datetime] = None
    procedures_performed: List[str] = Field(default_factory=list)
    prescriptions: List[str] = Field(default_factory=list)
    referrals: List[str] = Field(default_factory=list)
    
    class Settings:
        collection_name = "sus_appointments"
        indexes = [
            "patient_cns",
            "facility_cnes",
            "scheduled_date",
            "status"
        ]


class SUSVaccination(MongoModel):
    """Vaccination record in the national immunization program."""
    patient_cns: str
    vaccine_name: str
    vaccine_lot: str
    
    # Administration
    administration_date: datetime
    facility_cnes: str
    professional_name: str
    professional_cns: Optional[str] = None
    
    # Vaccine details
    dose_number: int
    vaccination_schedule: str  # "Rotina", "Campanha", "Especial"
    manufacturer: Optional[str] = None
    
    # Adverse events
    adverse_event: bool = False
    adverse_event_description: Optional[str] = None
    
    class Settings:
        collection_name = "sus_vaccinations"
        indexes = [
            "patient_cns",
            "vaccine_name",
            "administration_date"
        ]


class SUSIntegration:
    """Integration with SUS services."""
    
    @staticmethod
    def validate_cns(cns: str) -> bool:
        """
        Validate CNS (Cartão Nacional de Saúde) number.
        
        CNS can be:
        - 15 digits starting with 1 or 2 (definitive)
        - 15 digits starting with 7, 8 or 9 (provisional)
        """
        if not cns or len(cns) != 15 or not cns.isdigit():
            return False
        
        first_digit = int(cns[0])
        
        # Definitive CNS (starts with 1 or 2)
        if first_digit in [1, 2]:
            # Calculate using algorithm for definitive CNS
            sum_val = 0
            for i in range(15):
                sum_val += int(cns[i]) * (15 - i)
            return sum_val % 11 == 0
        
        # Provisional CNS (starts with 7, 8 or 9)
        elif first_digit in [7, 8, 9]:
            # Different validation for provisional
            return True  # Simplified for demo
        
        return False
    
    @staticmethod
    def generate_cns(provisional: bool = False) -> str:
        """Generate a valid CNS number."""
        import random
        
        if provisional:
            # Generate provisional CNS (starts with 7, 8 or 9)
            first = random.choice(['7', '8', '9'])
            rest = ''.join([str(random.randint(0, 9)) for _ in range(14)])
            return first + rest
        else:
            # Generate definitive CNS (starts with 1 or 2)
            first = random.choice(['1', '2'])
            # Generate 14 digits
            digits = [int(first)]
            for _ in range(13):
                digits.append(random.randint(0, 9))
            
            # Calculate check digit
            sum_val = sum(d * (15 - i) for i, d in enumerate(digits))
            remainder = sum_val % 11
            
            # Adjust last digit to make sum divisible by 11
            if remainder != 0:
                last_digit = (11 - remainder) % 10
            else:
                last_digit = 0
            
            digits.append(last_digit)
            
            return ''.join(map(str, digits))
    
    @staticmethod
    def calculate_vaccine_schedule(birth_date: date, current_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Calculate vaccination schedule based on age.
        
        Returns list of vaccines with recommended dates.
        """
        if not current_date:
            current_date = date.today()
        
        age_months = (current_date.year - birth_date.year) * 12 + (current_date.month - birth_date.month)
        age_years = age_months // 12
        
        schedule = []
        
        # National Immunization Program vaccines
        vaccines = [
            # Birth
            {"name": "BCG", "age_months": 0, "doses": 1},
            {"name": "Hepatite B", "age_months": 0, "doses": 1},
            
            # 2 months
            {"name": "Pentavalente", "age_months": 2, "doses": 3, "interval": 2},
            {"name": "VIP", "age_months": 2, "doses": 3, "interval": 2},
            {"name": "Pneumocócica 10V", "age_months": 2, "doses": 2, "interval": 2},
            {"name": "Rotavírus", "age_months": 2, "doses": 2, "interval": 2},
            
            # 3 months
            {"name": "Meningocócica C", "age_months": 3, "doses": 2, "interval": 2},
            
            # 9 months
            {"name": "Febre Amarela", "age_months": 9, "doses": 1},
            
            # 12 months
            {"name": "Tríplice Viral", "age_months": 12, "doses": 1},
            {"name": "Pneumocócica 10V (reforço)", "age_months": 12, "doses": 1},
            {"name": "Meningocócica C (reforço)", "age_months": 12, "doses": 1},
            
            # 15 months
            {"name": "DTP", "age_months": 15, "doses": 1},
            {"name": "VOP", "age_months": 15, "doses": 1},
            {"name": "Hepatite A", "age_months": 15, "doses": 1},
            {"name": "Tetraviral", "age_months": 15, "doses": 1},
            
            # 4 years
            {"name": "DTP (2º reforço)", "age_months": 48, "doses": 1},
            {"name": "VOP (2º reforço)", "age_months": 48, "doses": 1},
            
            # 11-14 years (HPV)
            {"name": "HPV", "age_months": 132, "doses": 2, "interval": 6},
        ]
        
        for vaccine in vaccines:
            recommended_date = birth_date.replace(
                year=birth_date.year + vaccine["age_months"] // 12,
                month=((birth_date.month - 1 + vaccine["age_months"]) % 12) + 1
            )
            
            status = "completed" if age_months > vaccine["age_months"] else "pending"
            if age_months == vaccine["age_months"]:
                status = "due_now"
            
            schedule.append({
                "vaccine": vaccine["name"],
                "recommended_date": recommended_date,
                "age_months": vaccine["age_months"],
                "status": status,
                "doses": vaccine.get("doses", 1)
            })
        
        return schedule
    
    @staticmethod
    def check_social_programs_eligibility(income_per_capita: float, family_size: int) -> List[str]:
        """
        Check eligibility for Brazilian social programs.
        
        Args:
            income_per_capita: Monthly income per capita in BRL
            family_size: Number of family members
            
        Returns:
            List of eligible programs
        """
        eligible_programs = []
        
        # Bolsa Família (now Auxílio Brasil)
        if income_per_capita <= 218.00:  # 2024 values
            eligible_programs.append("Auxílio Brasil")
        
        # BPC (Benefício de Prestação Continuada)
        minimum_wage = 1412.00  # 2024 value
        if income_per_capita <= minimum_wage / 4:
            eligible_programs.append("BPC - Benefício de Prestação Continuada")
        
        # Tarifa Social de Energia Elétrica
        if income_per_capita <= minimum_wage / 2:
            eligible_programs.append("Tarifa Social de Energia Elétrica")
        
        # Farmácia Popular
        eligible_programs.append("Farmácia Popular do Brasil")
        
        # Programa Auxílio Gás
        if income_per_capita <= minimum_wage / 2:
            eligible_programs.append("Auxílio Gás")
        
        return eligible_programs
    
    @staticmethod
    def find_nearest_facility(
        latitude: float,
        longitude: float,
        facility_type: HealthFacilityType,
        services_required: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find nearest health facility.
        
        In production, this would query real SUS facility database.
        """
        # Sample implementation
        return {
            "cnes": "2345678",
            "name": "UBS Vila Nova",
            "distance_km": 1.5,
            "address": "Rua das Flores, 123 - Vila Nova",
            "phone": "(11) 3456-7890",
            "services": ["Clínica Geral", "Pediatria", "Ginecologia", "Vacinação"]
        }