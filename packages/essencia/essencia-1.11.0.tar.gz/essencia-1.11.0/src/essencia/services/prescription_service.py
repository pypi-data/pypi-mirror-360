"""
Prescription generation and management service.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from essencia.models.medication import (
    DosageForm,
    FrequencyUnit,
    Medication,
    MedicationCategory,
    PrescriptionStatus,
    RouteOfAdministration,
)
from essencia.models.people import Doctor, Patient


class PrescriptionTemplate:
    """Template for common prescriptions."""
    
    def __init__(
        self,
        name: str,
        strength: str,
        form: DosageForm,
        route: RouteOfAdministration,
        dosage_amount: float,
        dosage_unit: str,
        frequency_value: int,
        frequency_unit: FrequencyUnit,
        duration_days: int,
        indication: str,
        instructions: Optional[str] = None
    ):
        self.name = name
        self.strength = strength
        self.form = form
        self.route = route
        self.dosage_amount = dosage_amount
        self.dosage_unit = dosage_unit
        self.frequency_value = frequency_value
        self.frequency_unit = frequency_unit
        self.duration_days = duration_days
        self.indication = indication
        self.instructions = instructions


class PrescriptionService:
    """Service for managing prescriptions."""
    
    # Common prescription templates
    TEMPLATES = {
        # Antibiotics
        "amoxicillin_standard": PrescriptionTemplate(
            name="Amoxicilina",
            strength="500mg",
            form=DosageForm.CAPSULE,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="cápsula",
            frequency_value=3,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=7,
            indication="Infecção bacteriana",
            instructions="Tomar com alimentos"
        ),
        "azithromycin_standard": PrescriptionTemplate(
            name="Azitromicina",
            strength="500mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=1,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=5,
            indication="Infecção respiratória",
            instructions="Tomar 1 hora antes ou 2 horas após refeições"
        ),
        
        # Pain relief
        "paracetamol_standard": PrescriptionTemplate(
            name="Paracetamol",
            strength="500mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=4,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=5,
            indication="Dor leve a moderada",
            instructions="Máximo 4g por dia"
        ),
        "ibuprofen_standard": PrescriptionTemplate(
            name="Ibuprofeno",
            strength="400mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=3,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=5,
            indication="Dor e inflamação",
            instructions="Tomar com alimentos"
        ),
        
        # Chronic conditions
        "metformin_diabetes": PrescriptionTemplate(
            name="Metformina",
            strength="500mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=2,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=30,
            indication="Diabetes tipo 2",
            instructions="Tomar com refeições"
        ),
        "losartan_hypertension": PrescriptionTemplate(
            name="Losartana",
            strength="50mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=1,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=30,
            indication="Hipertensão arterial",
            instructions="Tomar sempre no mesmo horário"
        ),
        
        # Mental health
        "sertraline_depression": PrescriptionTemplate(
            name="Sertralina",
            strength="50mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=1,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=30,
            indication="Depressão",
            instructions="Tomar pela manhã"
        ),
        "alprazolam_anxiety": PrescriptionTemplate(
            name="Alprazolam",
            strength="0.5mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            dosage_amount=1,
            dosage_unit="comprimido",
            frequency_value=2,
            frequency_unit=FrequencyUnit.DAILY,
            duration_days=15,
            indication="Ansiedade",
            instructions="Não interromper abruptamente"
        ),
    }
    
    @classmethod
    def create_prescription_from_template(
        cls,
        template_name: str,
        patient_id: str,
        doctor_id: str,
        adjustments: Optional[Dict] = None
    ) -> Medication:
        """Create a prescription from a template."""
        if template_name not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = cls.TEMPLATES[template_name]
        
        prescription = Medication(
            patient_id=patient_id,
            prescribed_by=doctor_id,
            prescribed_date=datetime.utcnow(),
            name=template.name,
            strength=template.strength,
            form=template.form,
            route=template.route,
            dosage_amount=template.dosage_amount,
            dosage_unit=template.dosage_unit,
            frequency_value=template.frequency_value,
            frequency_unit=template.frequency_unit,
            start_date=datetime.utcnow(),
            duration_days=template.duration_days,
            indication=template.indication,
            special_instructions=template.instructions,
            status=PrescriptionStatus.ACTIVE
        )
        
        # Apply adjustments if provided
        if adjustments:
            for key, value in adjustments.items():
                if hasattr(prescription, key):
                    setattr(prescription, key, value)
        
        # Calculate end date
        if prescription.duration_days:
            prescription.end_date = prescription.start_date + timedelta(days=prescription.duration_days)
        
        return prescription
    
    @staticmethod
    def generate_prescription_text(
        prescription: Medication,
        patient: Patient,
        doctor: Doctor
    ) -> str:
        """Generate prescription text for printing."""
        text = f"""
RECEITUÁRIO MÉDICO
{'=' * 50}

PACIENTE: {patient.name}
CPF: {patient.cpf}
DATA: {prescription.prescribed_date.strftime('%d/%m/%Y')}

PRESCRIÇÃO:
-----------
{prescription.name} {prescription.strength}

Uso {prescription.route.value}

{prescription.dosage_amount} {prescription.dosage_unit} de {prescription.frequency_value}/{prescription.frequency_value} horas

"""
        
        if prescription.special_instructions:
            text += f"Instruções: {prescription.special_instructions}\n"
        
        if prescription.duration_days:
            text += f"Duração: {prescription.duration_days} dias\n"
        
        if prescription.indication:
            text += f"Indicação: {prescription.indication}\n"
        
        text += f"""

{'=' * 50}
Dr(a). {doctor.name}
CRM: {doctor.professional_id}
{doctor.specialties[0] if doctor.specialties else 'Clínico Geral'}
"""
        
        return text
    
    @staticmethod
    def validate_prescription(prescription: Medication) -> List[str]:
        """Validate prescription for common issues."""
        issues = []
        
        # Check dosage limits
        max_daily_doses = {
            "paracetamol": {"amount": 4000, "unit": "mg"},
            "ibuprofeno": {"amount": 2400, "unit": "mg"},
            "dipirona": {"amount": 4000, "unit": "mg"},
        }
        
        med_name_lower = prescription.name.lower()
        if med_name_lower in max_daily_doses:
            # Calculate daily dose
            daily_dose = prescription.dosage_amount * prescription.frequency_value
            if prescription.frequency_unit == FrequencyUnit.DAILY:
                # Extract numeric value from strength
                import re
                strength_match = re.search(r'(\d+)', prescription.strength)
                if strength_match:
                    strength_value = float(strength_match.group(1))
                    total_daily = daily_dose * strength_value
                    max_dose = max_daily_doses[med_name_lower]["amount"]
                    
                    if total_daily > max_dose:
                        issues.append(
                            f"Dose diária excede o máximo recomendado de {max_dose}mg"
                        )
        
        # Check controlled substances
        controlled_meds = ["alprazolam", "diazepam", "clonazepam", "zolpidem", "tramadol"]
        if any(controlled in med_name_lower for controlled in controlled_meds):
            if prescription.duration_days and prescription.duration_days > 30:
                issues.append("Medicamento controlado prescrito por mais de 30 dias")
        
        # Check pediatric/geriatric considerations
        # This would require patient age information
        
        # Check for missing information
        if not prescription.indication:
            issues.append("Indicação não especificada")
        
        if not prescription.duration_days and not prescription.end_date:
            issues.append("Duração do tratamento não especificada")
        
        return issues
    
    @staticmethod
    async def check_prescription_eligibility(
        patient_id: str,
        medication_name: str
    ) -> Dict[str, any]:
        """Check if patient is eligible for a medication."""
        # This would check:
        # - Patient allergies
        # - Current medications (interactions)
        # - Medical conditions (contraindications)
        # - Previous adverse reactions
        # - Insurance coverage
        
        return {
            "eligible": True,
            "warnings": [],
            "contraindications": [],
            "interactions": [],
            "coverage": "covered"
        }
    
    @staticmethod
    def calculate_prescription_cost(
        prescription: Medication,
        include_generics: bool = True
    ) -> Dict[str, float]:
        """Calculate estimated prescription cost."""
        # Simplified cost calculation
        # In production, this would query pharmacy databases
        
        base_costs = {
            "amoxicilina": 15.00,
            "azitromicina": 25.00,
            "paracetamol": 5.00,
            "ibuprofeno": 8.00,
            "metformina": 10.00,
            "losartana": 12.00,
            "sertralina": 35.00,
            "alprazolam": 20.00,
        }
        
        med_name_lower = prescription.name.lower()
        base_cost = base_costs.get(med_name_lower, 30.00)
        
        # Calculate total pills/doses needed
        if prescription.duration_days:
            if prescription.frequency_unit == FrequencyUnit.DAILY:
                total_doses = prescription.frequency_value * prescription.duration_days
            else:
                total_doses = prescription.duration_days  # Simplified
        else:
            total_doses = 30  # Default month supply
        
        brand_cost = base_cost * (total_doses / 30)  # Adjust for quantity
        generic_cost = brand_cost * 0.3  # Generics typically 70% cheaper
        
        result = {
            "brand_cost": round(brand_cost, 2),
            "currency": "BRL"
        }
        
        if include_generics:
            result["generic_cost"] = round(generic_cost, 2)
            result["savings"] = round(brand_cost - generic_cost, 2)
        
        return result