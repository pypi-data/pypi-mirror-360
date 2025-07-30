"""
Unit tests for medication management system.
"""
from datetime import datetime, time, timedelta

import pytest

from essencia.medical.drug_interactions import (
    DrugInteractionChecker,
    InteractionSeverity,
    ContraindicationChecker,
)
from essencia.models.medication import (
    DosageForm,
    FrequencyUnit,
    Medication,
    MedicationAdherence,
    MedicationService,
    PrescriptionStatus,
    RouteOfAdministration,
    AdherenceStatus,
)
from essencia.services.prescription_service import PrescriptionService


class TestMedication:
    """Test medication model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_medication_creation(self):
        """Test creating a medication."""
        med = Medication(
            patient_id="patient_123",
            name="Amoxicilina",
            strength="500mg",
            form=DosageForm.CAPSULE,
            route=RouteOfAdministration.ORAL,
            prescribed_by="doctor_456",
            prescribed_date=datetime.utcnow(),
            dosage_amount=1,
            dosage_unit="cápsula",
            frequency_value=3,
            frequency_unit=FrequencyUnit.DAILY,
            start_date=datetime.utcnow(),
            duration_days=7,
            indication="Infecção respiratória"
        )
        
        assert med.name == "Amoxicilina"
        assert med.frequency_value == 3
        assert med.status == PrescriptionStatus.ACTIVE
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_medication_is_active(self):
        """Test medication active status."""
        now = datetime.utcnow()
        
        # Active medication
        med = Medication(
            patient_id="p1",
            name="Test Med",
            strength="100mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            prescribed_by="d1",
            prescribed_date=now - timedelta(days=1),
            dosage_amount=1,
            dosage_unit="tablet",
            frequency_value=1,
            frequency_unit=FrequencyUnit.DAILY,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=5),
            status=PrescriptionStatus.ACTIVE
        )
        assert med.is_active() is True
        
        # Expired medication
        med.end_date = now - timedelta(days=1)
        assert med.is_active() is False
        
        # Discontinued medication
        med.status = PrescriptionStatus.DISCONTINUED
        assert med.is_active() is False
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_medication_daily_schedule(self):
        """Test generating daily medication schedule."""
        med = Medication(
            patient_id="p1",
            name="Test Med",
            strength="100mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            prescribed_by="d1",
            prescribed_date=datetime.utcnow(),
            dosage_amount=1,
            dosage_unit="tablet",
            frequency_value=3,
            frequency_unit=FrequencyUnit.DAILY,
            start_date=datetime.utcnow()
        )
        
        schedule = med.get_daily_schedule()
        
        assert len(schedule) == 3
        assert all("time" in s for s in schedule)
        assert all("dosage" in s for s in schedule)
        assert schedule[0]["dosage"] == "1 tablet"
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_medication_with_scheduled_times(self):
        """Test medication with specific scheduled times."""
        med = Medication(
            patient_id="p1",
            name="Test Med",
            strength="100mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            prescribed_by="d1",
            prescribed_date=datetime.utcnow(),
            dosage_amount=2,
            dosage_unit="tablets",
            frequency_value=2,
            frequency_unit=FrequencyUnit.DAILY,
            scheduled_times=[time(8, 0), time(20, 0)],
            start_date=datetime.utcnow()
        )
        
        schedule = med.get_daily_schedule()
        
        assert len(schedule) == 2
        assert schedule[0]["time"] == time(8, 0)
        assert schedule[1]["time"] == time(20, 0)
        assert schedule[0]["dosage"] == "2 tablets"


class TestMedicationAdherence:
    """Test medication adherence tracking."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_adherence_delay_calculation(self):
        """Test calculating medication delay."""
        scheduled = datetime.utcnow()
        actual = scheduled + timedelta(hours=2)
        
        adherence = MedicationAdherence(
            patient_id="p1",
            medication_id="m1",
            scheduled_datetime=scheduled,
            actual_datetime=actual,
            status=AdherenceStatus.DELAYED,
            dosage_taken=1.0
        )
        
        delay = adherence.calculate_delay()
        assert delay == timedelta(hours=2)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_adherence_missed(self):
        """Test missed medication."""
        adherence = MedicationAdherence(
            patient_id="p1",
            medication_id="m1",
            scheduled_datetime=datetime.utcnow(),
            status=AdherenceStatus.MISSED
        )
        
        assert adherence.status == AdherenceStatus.MISSED
        assert adherence.calculate_delay() is None


class TestDrugInteractions:
    """Test drug interaction checking."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_drug_interaction_checker(self):
        """Test checking drug interactions."""
        checker = DrugInteractionChecker()
        
        # Known interaction
        interaction = checker.check_interaction("warfarin", "aspirin")
        assert interaction is not None
        assert interaction.severity == InteractionSeverity.MAJOR
        
        # No interaction
        interaction = checker.check_interaction("paracetamol", "omeprazole")
        assert interaction is None
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_multiple_drug_interactions(self):
        """Test checking multiple drug interactions."""
        checker = DrugInteractionChecker()
        
        medications = ["warfarin", "aspirin", "amiodarone"]
        interactions = checker.check_multiple_interactions(medications)
        
        assert len(interactions) >= 2
        assert all(len(i) == 3 for i in interactions)  # (drug1, drug2, interaction)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_interaction_summary(self):
        """Test getting interaction summary."""
        checker = DrugInteractionChecker()
        
        medications = ["warfarin", "aspirin", "simvastatin", "clarithromycin"]
        summary = checker.get_interaction_summary(medications)
        
        assert "total_interactions" in summary
        assert "major" in summary
        assert "requires_immediate_review" in summary
        assert summary["major"] >= 2
        assert summary["requires_immediate_review"] is True
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_drug_name_normalization(self):
        """Test drug name normalization."""
        checker = DrugInteractionChecker()
        
        # Should find interaction despite different formats
        interaction1 = checker.check_interaction("Warfarin 5mg", "Aspirin")
        interaction2 = checker.check_interaction("WARFARIN tablet", "aspirin 100mg")
        
        assert interaction1 is not None
        assert interaction2 is not None
        assert interaction1.severity == interaction2.severity


class TestContraindications:
    """Test contraindication checking."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_contraindication_checker(self):
        """Test checking contraindications."""
        # Metformin with renal impairment
        contras = ContraindicationChecker.check_contraindications(
            "metformin",
            ["severe_renal_impairment", "diabetes"]
        )
        
        assert len(contras) == 1
        assert contras[0]["condition"] == "severe_renal_impairment"
        assert contras[0]["severity"] == "absolute"
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_drug_class_contraindications(self):
        """Test drug class contraindications."""
        # ACE inhibitor with pregnancy
        contras = ContraindicationChecker.check_contraindications(
            "lisinopril",
            ["pregnancy", "hypertension"]
        )
        
        assert len(contras) == 1
        assert contras[0]["condition"] == "pregnancy"
        assert "Teratogenic" in contras[0]["description"]


class TestPrescriptionService:
    """Test prescription service."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_create_from_template(self):
        """Test creating prescription from template."""
        prescription = PrescriptionService.create_prescription_from_template(
            "amoxicillin_standard",
            patient_id="p123",
            doctor_id="d456"
        )
        
        assert prescription.name == "Amoxicilina"
        assert prescription.strength == "500mg"
        assert prescription.frequency_value == 3
        assert prescription.duration_days == 7
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_template_with_adjustments(self):
        """Test prescription template with adjustments."""
        adjustments = {
            "frequency_value": 2,
            "duration_days": 10,
            "special_instructions": "Tomar com bastante água"
        }
        
        prescription = PrescriptionService.create_prescription_from_template(
            "amoxicillin_standard",
            patient_id="p123",
            doctor_id="d456",
            adjustments=adjustments
        )
        
        assert prescription.frequency_value == 2
        assert prescription.duration_days == 10
        assert prescription.special_instructions == "Tomar com bastante água"
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_prescription_validation(self):
        """Test prescription validation."""
        # Valid prescription
        prescription = Medication(
            patient_id="p1",
            name="Paracetamol",
            strength="500mg",
            form=DosageForm.TABLET,
            route=RouteOfAdministration.ORAL,
            prescribed_by="d1",
            prescribed_date=datetime.utcnow(),
            dosage_amount=2,
            dosage_unit="tablets",
            frequency_value=4,
            frequency_unit=FrequencyUnit.DAILY,
            start_date=datetime.utcnow(),
            duration_days=5,
            indication="Dor"
        )
        
        issues = PrescriptionService.validate_prescription(prescription)
        assert len(issues) == 0
        
        # Excessive dose
        prescription.dosage_amount = 3  # 3 * 500mg * 4 times = 6000mg/day
        issues = PrescriptionService.validate_prescription(prescription)
        assert len(issues) > 0
        assert "excede o máximo" in issues[0]
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_prescription_cost_calculation(self):
        """Test prescription cost calculation."""
        prescription = Medication(
            patient_id="p1",
            name="Amoxicilina",
            strength="500mg",
            form=DosageForm.CAPSULE,
            route=RouteOfAdministration.ORAL,
            prescribed_by="d1",
            prescribed_date=datetime.utcnow(),
            dosage_amount=1,
            dosage_unit="capsule",
            frequency_value=3,
            frequency_unit=FrequencyUnit.DAILY,
            start_date=datetime.utcnow(),
            duration_days=7
        )
        
        cost = PrescriptionService.calculate_prescription_cost(prescription)
        
        assert "brand_cost" in cost
        assert "generic_cost" in cost
        assert "savings" in cost
        assert cost["generic_cost"] < cost["brand_cost"]
        assert cost["currency"] == "BRL"


class TestMedicationService:
    """Test medication service operations."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_generate_medication_schedule(self):
        """Test generating daily medication schedule."""
        medications = [
            Medication(
                patient_id="p1",
                name="Med A",
                strength="100mg",
                form=DosageForm.TABLET,
                route=RouteOfAdministration.ORAL,
                prescribed_by="d1",
                prescribed_date=datetime.utcnow(),
                dosage_amount=1,
                dosage_unit="tablet",
                frequency_value=2,
                frequency_unit=FrequencyUnit.DAILY,
                scheduled_times=[time(8, 0), time(20, 0)],
                start_date=datetime.utcnow(),
                status=PrescriptionStatus.ACTIVE
            ),
            Medication(
                patient_id="p1",
                name="Med B",
                strength="50mg",
                form=DosageForm.TABLET,
                route=RouteOfAdministration.ORAL,
                prescribed_by="d1",
                prescribed_date=datetime.utcnow(),
                dosage_amount=1,
                dosage_unit="tablet",
                frequency_value=1,
                frequency_unit=FrequencyUnit.DAILY,
                scheduled_times=[time(10, 0)],
                start_date=datetime.utcnow(),
                status=PrescriptionStatus.ACTIVE
            )
        ]
        
        schedule = MedicationService.generate_medication_schedule(medications)
        
        assert len(schedule) == 3  # 2 doses of Med A + 1 dose of Med B
        assert schedule[0]["scheduled_time"].time() == time(8, 0)
        assert schedule[1]["scheduled_time"].time() == time(10, 0)
        assert schedule[2]["scheduled_time"].time() == time(20, 0)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_check_duplicate_medications(self):
        """Test checking for duplicate medications."""
        medications = [
            Medication(
                patient_id="p1",
                name="Metformina",
                strength="500mg",
                form=DosageForm.TABLET,
                route=RouteOfAdministration.ORAL,
                prescribed_by="d1",
                prescribed_date=datetime.utcnow(),
                dosage_amount=1,
                dosage_unit="tablet",
                frequency_value=2,
                frequency_unit=FrequencyUnit.DAILY,
                start_date=datetime.utcnow(),
                status=PrescriptionStatus.ACTIVE
            ),
            Medication(
                patient_id="p1",
                name="Metformina",
                strength="850mg",
                form=DosageForm.TABLET,
                route=RouteOfAdministration.ORAL,
                prescribed_by="d2",
                prescribed_date=datetime.utcnow() - timedelta(days=5),
                dosage_amount=1,
                dosage_unit="tablet",
                frequency_value=1,
                frequency_unit=FrequencyUnit.DAILY,
                start_date=datetime.utcnow() - timedelta(days=5),
                status=PrescriptionStatus.ACTIVE
            )
        ]
        
        duplicates = MedicationService.check_duplicate_medications(medications)
        
        assert "metformina" in duplicates
        assert len(duplicates["metformina"]) == 2