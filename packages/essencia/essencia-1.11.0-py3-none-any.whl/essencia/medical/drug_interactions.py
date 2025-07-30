"""
Drug interaction checking and management.
"""
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field


class InteractionSeverity(str, Enum):
    """Severity levels for drug interactions."""
    
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"


class InteractionMechanism(str, Enum):
    """Common drug interaction mechanisms."""
    
    PHARMACOKINETIC = "pharmacokinetic"
    PHARMACODYNAMIC = "pharmacodynamic"
    ABSORPTION = "absorption"
    DISTRIBUTION = "distribution"
    METABOLISM = "metabolism"
    EXCRETION = "excretion"
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"


class DrugInteraction(BaseModel):
    """Model for drug-drug interactions."""
    
    drug1: str
    drug2: str
    severity: InteractionSeverity
    mechanism: InteractionMechanism
    description: str
    clinical_effects: List[str]
    management: str
    monitoring_parameters: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)


class DrugInteractionDatabase:
    """Database of known drug interactions."""
    
    # This is a simplified example. In production, this would be a comprehensive database
    INTERACTIONS: List[DrugInteraction] = [
        # Warfarin interactions
        DrugInteraction(
            drug1="warfarin",
            drug2="aspirin",
            severity=InteractionSeverity.MAJOR,
            mechanism=InteractionMechanism.PHARMACODYNAMIC,
            description="Increased risk of bleeding",
            clinical_effects=["Increased anticoagulation", "Bleeding risk"],
            management="Avoid combination if possible. If used together, monitor INR closely and adjust warfarin dose as needed.",
            monitoring_parameters=["INR", "Signs of bleeding"],
        ),
        DrugInteraction(
            drug1="warfarin",
            drug2="amiodarone",
            severity=InteractionSeverity.MAJOR,
            mechanism=InteractionMechanism.METABOLISM,
            description="Amiodarone inhibits warfarin metabolism",
            clinical_effects=["Increased INR", "Bleeding risk"],
            management="Reduce warfarin dose by 30-50% when starting amiodarone. Monitor INR closely.",
            monitoring_parameters=["INR", "Signs of bleeding"],
        ),
        
        # SSRI interactions
        DrugInteraction(
            drug1="fluoxetine",
            drug2="tramadol",
            severity=InteractionSeverity.MAJOR,
            mechanism=InteractionMechanism.PHARMACODYNAMIC,
            description="Increased risk of serotonin syndrome",
            clinical_effects=["Serotonin syndrome", "Seizure risk"],
            management="Avoid combination if possible. If necessary, use lowest effective doses and monitor closely.",
            monitoring_parameters=["Mental status changes", "Autonomic instability", "Neuromuscular symptoms"],
        ),
        
        # ACE inhibitor interactions
        DrugInteraction(
            drug1="lisinopril",
            drug2="spironolactone",
            severity=InteractionSeverity.MODERATE,
            mechanism=InteractionMechanism.PHARMACODYNAMIC,
            description="Increased risk of hyperkalemia",
            clinical_effects=["Hyperkalemia", "Cardiac arrhythmias"],
            management="Monitor potassium levels regularly. Consider alternative if potassium > 5.0 mEq/L.",
            monitoring_parameters=["Serum potassium", "Renal function"],
        ),
        
        # Metformin interactions
        DrugInteraction(
            drug1="metformin",
            drug2="contrast media",
            severity=InteractionSeverity.MAJOR,
            mechanism=InteractionMechanism.EXCRETION,
            description="Risk of lactic acidosis with iodinated contrast",
            clinical_effects=["Lactic acidosis", "Acute kidney injury"],
            management="Discontinue metformin before contrast procedure. Resume 48 hours after if renal function normal.",
            monitoring_parameters=["Renal function", "Lactic acid if symptomatic"],
        ),
        
        # Statin interactions
        DrugInteraction(
            drug1="simvastatin",
            drug2="clarithromycin",
            severity=InteractionSeverity.MAJOR,
            mechanism=InteractionMechanism.METABOLISM,
            description="CYP3A4 inhibition increases statin levels",
            clinical_effects=["Myopathy", "Rhabdomyolysis risk"],
            management="Avoid combination. Use azithromycin or alternative statin not metabolized by CYP3A4.",
            monitoring_parameters=["CK levels", "Muscle symptoms"],
        ),
        
        # Digoxin interactions
        DrugInteraction(
            drug1="digoxin",
            drug2="verapamil",
            severity=InteractionSeverity.MODERATE,
            mechanism=InteractionMechanism.DISTRIBUTION,
            description="Increased digoxin levels",
            clinical_effects=["Digoxin toxicity", "Bradycardia"],
            management="Reduce digoxin dose by 50%. Monitor levels and heart rate.",
            monitoring_parameters=["Digoxin levels", "Heart rate", "ECG"],
        ),
    ]
    
    @classmethod
    def build_interaction_map(cls) -> Dict[str, Dict[str, DrugInteraction]]:
        """Build a map for quick interaction lookups."""
        interaction_map = {}
        
        for interaction in cls.INTERACTIONS:
            # Add both directions
            drug1_lower = interaction.drug1.lower()
            drug2_lower = interaction.drug2.lower()
            
            if drug1_lower not in interaction_map:
                interaction_map[drug1_lower] = {}
            interaction_map[drug1_lower][drug2_lower] = interaction
            
            if drug2_lower not in interaction_map:
                interaction_map[drug2_lower] = {}
            interaction_map[drug2_lower][drug1_lower] = interaction
        
        return interaction_map


class DrugInteractionChecker:
    """Service for checking drug interactions."""
    
    def __init__(self):
        self.interaction_map = DrugInteractionDatabase.build_interaction_map()
    
    def check_interaction(self, drug1: str, drug2: str) -> Optional[DrugInteraction]:
        """Check for interaction between two drugs."""
        drug1_lower = self._normalize_drug_name(drug1)
        drug2_lower = self._normalize_drug_name(drug2)
        
        if drug1_lower in self.interaction_map:
            if drug2_lower in self.interaction_map[drug1_lower]:
                return self.interaction_map[drug1_lower][drug2_lower]
        
        return None
    
    def check_multiple_interactions(
        self,
        medications: List[str]
    ) -> List[Tuple[str, str, DrugInteraction]]:
        """Check for all interactions in a medication list."""
        interactions = []
        normalized_meds = [(med, self._normalize_drug_name(med)) for med in medications]
        
        # Check all pairs
        for i in range(len(normalized_meds)):
            for j in range(i + 1, len(normalized_meds)):
                med1, norm1 = normalized_meds[i]
                med2, norm2 = normalized_meds[j]
                
                interaction = self.check_interaction(norm1, norm2)
                if interaction:
                    interactions.append((med1, med2, interaction))
        
        # Sort by severity (most severe first)
        severity_order = {
            InteractionSeverity.CONTRAINDICATED: 0,
            InteractionSeverity.MAJOR: 1,
            InteractionSeverity.MODERATE: 2,
            InteractionSeverity.MINOR: 3
        }
        
        interactions.sort(key=lambda x: severity_order[x[2].severity])
        
        return interactions
    
    def get_interaction_summary(
        self,
        medications: List[str]
    ) -> Dict[str, any]:
        """Get a summary of all interactions for a medication list."""
        interactions = self.check_multiple_interactions(medications)
        
        summary = {
            "total_interactions": len(interactions),
            "contraindicated": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0,
            "interactions": []
        }
        
        for med1, med2, interaction in interactions:
            summary[interaction.severity.value] += 1
            summary["interactions"].append({
                "drugs": [med1, med2],
                "severity": interaction.severity.value,
                "description": interaction.description,
                "management": interaction.management
            })
        
        summary["has_contraindications"] = summary["contraindicated"] > 0
        summary["requires_immediate_review"] = summary["contraindicated"] > 0 or summary["major"] > 0
        
        return summary
    
    def _normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name for matching."""
        # Remove common suffixes and normalize
        normalized = drug_name.lower().strip()
        
        # Remove dosage forms
        for suffix in [" tablet", " capsule", " solution", " injection", " cream", " ointment"]:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        # Remove strength information (simplified)
        import re
        normalized = re.sub(r'\s+\d+\s*mg.*$', '', normalized)
        normalized = re.sub(r'\s+\d+\s*mcg.*$', '', normalized)
        normalized = re.sub(r'\s+\d+\s*%.*$', '', normalized)
        
        return normalized.strip()
    
    def get_drug_class_interactions(self, drug_class: str) -> List[DrugInteraction]:
        """Get all interactions for a drug class."""
        # This would be implemented with drug class mappings
        # For now, return empty list
        return []
    
    def get_food_interactions(self, drug_name: str) -> List[Dict[str, str]]:
        """Get food interactions for a drug."""
        food_interactions = {
            "warfarin": [
                {
                    "food": "Vitamin K rich foods",
                    "effect": "Decreased anticoagulation",
                    "management": "Maintain consistent vitamin K intake"
                }
            ],
            "monoamine oxidase inhibitors": [
                {
                    "food": "Tyramine-rich foods",
                    "effect": "Hypertensive crisis",
                    "management": "Avoid aged cheeses, cured meats, fermented foods"
                }
            ],
            "tetracycline": [
                {
                    "food": "Dairy products",
                    "effect": "Decreased absorption",
                    "management": "Take 1 hour before or 2 hours after dairy"
                }
            ],
            "grapefruit juice": [
                {
                    "drugs": ["statins", "calcium channel blockers"],
                    "effect": "Increased drug levels",
                    "management": "Avoid grapefruit juice"
                }
            ]
        }
        
        normalized_drug = self._normalize_drug_name(drug_name)
        return food_interactions.get(normalized_drug, [])


class ContraindicationChecker:
    """Service for checking drug contraindications."""
    
    # Common contraindications database
    CONTRAINDICATIONS = {
        "metformin": [
            {
                "condition": "severe_renal_impairment",
                "description": "eGFR < 30 mL/min/1.73m²",
                "severity": "absolute"
            },
            {
                "condition": "acute_metabolic_acidosis",
                "description": "Including diabetic ketoacidosis",
                "severity": "absolute"
            }
        ],
        "aspirin": [
            {
                "condition": "active_bleeding",
                "description": "Active GI bleeding or bleeding disorder",
                "severity": "absolute"
            },
            {
                "condition": "children_with_viral_illness",
                "description": "Risk of Reye's syndrome",
                "severity": "absolute"
            }
        ],
        "ace_inhibitors": [
            {
                "condition": "pregnancy",
                "description": "Teratogenic effects",
                "severity": "absolute"
            },
            {
                "condition": "bilateral_renal_artery_stenosis",
                "description": "Risk of acute renal failure",
                "severity": "absolute"
            },
            {
                "condition": "angioedema_history",
                "description": "Previous ACE inhibitor-induced angioedema",
                "severity": "absolute"
            }
        ],
        "beta_blockers": [
            {
                "condition": "severe_bradycardia",
                "description": "Heart rate < 50 bpm",
                "severity": "relative"
            },
            {
                "condition": "decompensated_heart_failure",
                "description": "Acute decompensated heart failure",
                "severity": "relative"
            },
            {
                "condition": "severe_asthma",
                "description": "Active bronchospasm",
                "severity": "relative"
            }
        ]
    }
    
    @classmethod
    def check_contraindications(
        cls,
        drug_name: str,
        patient_conditions: List[str]
    ) -> List[Dict[str, str]]:
        """Check if drug is contraindicated for patient conditions."""
        contraindications = []
        normalized_drug = drug_name.lower().strip()
        
        # Check specific drug
        if normalized_drug in cls.CONTRAINDICATIONS:
            for contra in cls.CONTRAINDICATIONS[normalized_drug]:
                if contra["condition"] in patient_conditions:
                    contraindications.append(contra)
        
        # Check drug classes
        drug_classes = cls._get_drug_classes(normalized_drug)
        for drug_class in drug_classes:
            if drug_class in cls.CONTRAINDICATIONS:
                for contra in cls.CONTRAINDICATIONS[drug_class]:
                    if contra["condition"] in patient_conditions:
                        contraindications.append(contra)
        
        return contraindications
    
    @staticmethod
    def _get_drug_classes(drug_name: str) -> List[str]:
        """Get drug classes for a medication."""
        # Simplified mapping - in production this would be comprehensive
        drug_to_class = {
            "lisinopril": ["ace_inhibitors"],
            "enalapril": ["ace_inhibitors"],
            "ramipril": ["ace_inhibitors"],
            "atenolol": ["beta_blockers"],
            "metoprolol": ["beta_blockers"],
            "propranolol": ["beta_blockers"],
        }
        
        return drug_to_class.get(drug_name, [])