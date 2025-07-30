"""
ANVISA (Brazilian Health Regulatory Agency) integration.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import httpx
from pydantic import BaseModel, Field

from essencia.models import MongoModel
from essencia.fields import EncryptedStr


class MedicationCategory(str, Enum):
    """Brazilian medication categories."""
    SIMILAR = "similar"  # Medicamento similar
    GENERIC = "generico"  # Medicamento genérico
    REFERENCE = "referencia"  # Medicamento de referência
    PHYTOTHERAPIC = "fitoterapico"  # Fitoterápico
    HOMEOPATHIC = "homeopatico"  # Homeopático
    BIOLOGICAL = "biologico"  # Biológico
    RADIOPHARMACEUTICAL = "radiofarmaco"  # Radiofármaco


class PrescriptionRequirement(str, Enum):
    """Prescription requirements in Brazil."""
    NONE = "isento"  # Isento de prescrição
    WHITE = "branca"  # Receita branca (comum)
    YELLOW = "amarela"  # Receita amarela (retinoides)
    BLUE = "azul"  # Receita azul (B1 e B2)
    WHITE_SPECIAL = "branca_especial"  # Receita branca especial (C1)
    WHITE_TWO_COPIES = "branca_2_vias"  # Receita branca 2 vias (C2-C5)


class AnvisaProduct(BaseModel):
    """ANVISA registered product."""
    registry_number: str = Field(..., description="Número de registro ANVISA")
    process_number: str = Field(..., description="Número do processo")
    product_name: str = Field(..., description="Nome do produto")
    active_ingredient: str = Field(..., description="Princípio ativo")
    company_name: str = Field(..., description="Nome da empresa")
    cnpj: str = Field(..., description="CNPJ da empresa")
    category: MedicationCategory
    prescription_requirement: PrescriptionRequirement
    registry_date: datetime
    expiry_date: datetime
    concentration: Optional[str] = None
    pharmaceutical_form: Optional[str] = None
    presentation: Optional[str] = None
    therapeutic_class: Optional[str] = None
    

class BrazilianMedication(MongoModel):
    """Brazilian medication with ANVISA data."""
    # Basic information
    name: str = Field(..., description="Nome comercial")
    active_ingredient: str = Field(..., description="Princípio ativo")
    laboratory: str = Field(..., description="Laboratório")
    
    # ANVISA data
    anvisa_registry: Optional[str] = Field(None, description="Registro ANVISA")
    category: MedicationCategory
    prescription_requirement: PrescriptionRequirement
    
    # Details
    concentration: str = Field(..., description="Concentração")
    pharmaceutical_form: str = Field(..., description="Forma farmacêutica")
    presentation: str = Field(..., description="Apresentação")
    
    # Classification
    therapeutic_class: Optional[str] = None
    atc_code: Optional[str] = None  # Anatomical Therapeutic Chemical code
    
    # Regulatory
    controlled_substance: bool = Field(False, description="Substância controlada")
    black_stripe: bool = Field(False, description="Tarja preta")
    red_stripe: bool = Field(False, description="Tarja vermelha")
    yellow_stripe: bool = Field(False, description="Tarja amarela")
    
    # Commercial
    reference_price: Optional[float] = None
    maximum_price_consumer: Optional[float] = None  # PMC - Preço Máximo ao Consumidor
    maximum_price_government: Optional[float] = None  # PMVG - Preço Máximo de Venda ao Governo
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    active: bool = True
    
    class Settings:
        collection_name = "brazilian_medications"
        indexes = [
            "name",
            "active_ingredient",
            "anvisa_registry",
            ("active_ingredient", "concentration", "pharmaceutical_form")
        ]


class AnvisaIntegration:
    """Integration with ANVISA services."""
    
    # Common medications database (sample data)
    COMMON_MEDICATIONS = [
        {
            "name": "Dipirona Sódica",
            "active_ingredient": "Dipirona sódica",
            "category": MedicationCategory.GENERIC,
            "prescription_requirement": PrescriptionRequirement.NONE,
            "concentration": "500mg",
            "pharmaceutical_form": "Comprimido",
            "presentation": "Caixa com 20 comprimidos",
            "therapeutic_class": "Analgésico e Antitérmico"
        },
        {
            "name": "Amoxicilina",
            "active_ingredient": "Amoxicilina",
            "category": MedicationCategory.GENERIC,
            "prescription_requirement": PrescriptionRequirement.WHITE,
            "concentration": "500mg",
            "pharmaceutical_form": "Cápsula",
            "presentation": "Caixa com 21 cápsulas",
            "therapeutic_class": "Antibiótico"
        },
        {
            "name": "Rivotril",
            "active_ingredient": "Clonazepam",
            "category": MedicationCategory.REFERENCE,
            "prescription_requirement": PrescriptionRequirement.BLUE,
            "concentration": "2mg",
            "pharmaceutical_form": "Comprimido",
            "presentation": "Caixa com 30 comprimidos",
            "therapeutic_class": "Ansiolítico",
            "controlled_substance": True,
            "black_stripe": True
        },
        {
            "name": "Ritalina",
            "active_ingredient": "Metilfenidato",
            "category": MedicationCategory.REFERENCE,
            "prescription_requirement": PrescriptionRequirement.YELLOW,
            "concentration": "10mg",
            "pharmaceutical_form": "Comprimido",
            "presentation": "Caixa com 30 comprimidos",
            "therapeutic_class": "Psicoestimulante",
            "controlled_substance": True,
            "black_stripe": True
        }
    ]
    
    @staticmethod
    async def search_medication(
        query: str,
        active_ingredient: Optional[str] = None,
        category: Optional[MedicationCategory] = None
    ) -> List[BrazilianMedication]:
        """
        Search for medications in the Brazilian database.
        
        Args:
            query: Search term (name or active ingredient)
            active_ingredient: Filter by active ingredient
            category: Filter by category
            
        Returns:
            List of medications matching the criteria
        """
        results = []
        query_lower = query.lower()
        
        for med_data in AnvisaIntegration.COMMON_MEDICATIONS:
            # Check if matches query
            if (query_lower in med_data["name"].lower() or 
                query_lower in med_data["active_ingredient"].lower()):
                
                # Apply filters
                if active_ingredient and active_ingredient.lower() not in med_data["active_ingredient"].lower():
                    continue
                    
                if category and med_data["category"] != category:
                    continue
                
                # Create medication object
                medication = BrazilianMedication(
                    name=med_data["name"],
                    active_ingredient=med_data["active_ingredient"],
                    laboratory="Genérico" if med_data["category"] == MedicationCategory.GENERIC else "Laboratório Nacional",
                    category=med_data["category"],
                    prescription_requirement=med_data["prescription_requirement"],
                    concentration=med_data["concentration"],
                    pharmaceutical_form=med_data["pharmaceutical_form"],
                    presentation=med_data["presentation"],
                    therapeutic_class=med_data.get("therapeutic_class"),
                    controlled_substance=med_data.get("controlled_substance", False),
                    black_stripe=med_data.get("black_stripe", False)
                )
                results.append(medication)
        
        return results
    
    @staticmethod
    def validate_registry_number(registry: str) -> bool:
        """
        Validate ANVISA registry number format.
        
        Format: X.XXXX.XXXX.XXX-X (onde X são dígitos)
        """
        pattern = r'^\d\.\d{4}\.\d{4}\.\d{3}-\d$'
        return bool(re.match(pattern, registry))
    
    @staticmethod
    def get_prescription_info(requirement: PrescriptionRequirement) -> Dict[str, Any]:
        """Get detailed prescription requirement information."""
        info = {
            PrescriptionRequirement.NONE: {
                "name": "Isento de Prescrição",
                "description": "Medicamento de venda livre",
                "retention": False,
                "special_control": False,
                "validity_days": None
            },
            PrescriptionRequirement.WHITE: {
                "name": "Receita Branca Simples",
                "description": "Receita médica comum",
                "retention": False,
                "special_control": False,
                "validity_days": None
            },
            PrescriptionRequirement.YELLOW: {
                "name": "Receita Amarela",
                "description": "Retinoides de uso sistêmico (Lista C2)",
                "retention": True,
                "special_control": True,
                "validity_days": 30
            },
            PrescriptionRequirement.BLUE: {
                "name": "Receita Azul ou B",
                "description": "Psicotrópicos (Listas B1 e B2)",
                "retention": True,
                "special_control": True,
                "validity_days": 30
            },
            PrescriptionRequirement.WHITE_SPECIAL: {
                "name": "Receita Branca Especial",
                "description": "Substâncias Lista C1",
                "retention": True,
                "special_control": True,
                "validity_days": 30
            },
            PrescriptionRequirement.WHITE_TWO_COPIES: {
                "name": "Receita Branca 2 Vias",
                "description": "Substâncias Listas C2 a C5",
                "retention": True,
                "special_control": True,
                "validity_days": 30
            }
        }
        
        return info.get(requirement, {})
    
    @staticmethod
    async def check_drug_interaction_brazil(
        medication1: str,
        medication2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check drug interactions considering Brazilian medications.
        
        This would integrate with ANVISA's database in production.
        """
        # Sample interaction database
        interactions = {
            ("amoxicilina", "contraceptivo oral"): {
                "severity": "moderate",
                "description": "Amoxicilina pode reduzir a eficácia de contraceptivos orais",
                "recommendation": "Usar método contraceptivo adicional durante o tratamento"
            },
            ("dipirona", "álcool"): {
                "severity": "moderate", 
                "description": "Pode aumentar o risco de problemas gastrointestinais",
                "recommendation": "Evitar consumo de álcool durante o tratamento"
            }
        }
        
        med1_lower = medication1.lower()
        med2_lower = medication2.lower()
        
        # Check both directions
        for (drug1, drug2), interaction in interactions.items():
            if (drug1 in med1_lower and drug2 in med2_lower) or \
               (drug2 in med1_lower and drug1 in med2_lower):
                return interaction
        
        return None


class SUSMedication(MongoModel):
    """Medication available through SUS (Sistema Único de Saúde)."""
    medication_id: str = Field(..., description="Reference to BrazilianMedication")
    rename_code: str = Field(..., description="Código RENAME")
    sus_component: str = Field(..., description="Componente da Assistência Farmacêutica")
    distribution_responsibility: str = Field(..., description="Responsabilidade de fornecimento")
    clinical_protocol: Optional[str] = Field(None, description="Protocolo clínico associado")
    special_program: Optional[str] = Field(None, description="Programa especial (ex: Farmácia Popular)")
    availability_level: str = Field(..., description="Nível de disponibilidade (municipal/estadual/federal)")
    
    class Settings:
        collection_name = "sus_medications"