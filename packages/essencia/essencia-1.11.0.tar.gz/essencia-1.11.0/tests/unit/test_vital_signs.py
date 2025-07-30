"""
Unit tests for vital signs models and analyzer.
"""
from datetime import datetime, timedelta

import pytest

from essencia.medical.vital_signs_analyzer import VitalSignsAnalyzer
from essencia.models.vital_signs import (
    BloodPressure,
    BloodPressureCategory,
    HeartRate,
    HeartRateCategory,
    OxygenSaturation,
    OxygenSaturationCategory,
    PainScale,
    RespiratoryRate,
    Temperature,
    TemperatureCategory,
    VitalSignsSet,
)


class TestBloodPressure:
    """Test blood pressure model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_blood_pressure_creation(self):
        """Test creating blood pressure measurement."""
        bp = BloodPressure(
            patient_id="patient_123",
            systolic=120,
            diastolic=80,
            measured_by="nurse_456"
        )
        
        assert bp.systolic == 120
        assert bp.diastolic == 80
        assert bp.pulse_pressure == 40
        assert bp.mean_arterial_pressure == pytest.approx(93.3, rel=0.1)
        assert bp.category == BloodPressureCategory.ELEVATED
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_blood_pressure_validation(self):
        """Test blood pressure validation."""
        # Diastolic must be less than systolic
        with pytest.raises(Exception):
            BloodPressure(
                patient_id="patient_123",
                systolic=80,
                diastolic=120
            )
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_blood_pressure_categories(self):
        """Test blood pressure categorization."""
        # Normal
        bp = BloodPressure(patient_id="p1", systolic=115, diastolic=75)
        assert bp.category == BloodPressureCategory.NORMAL
        assert not bp.is_critical()
        
        # Elevated
        bp = BloodPressure(patient_id="p1", systolic=125, diastolic=78)
        assert bp.category == BloodPressureCategory.ELEVATED
        assert not bp.is_critical()
        
        # Stage 1 Hypertension
        bp = BloodPressure(patient_id="p1", systolic=135, diastolic=85)
        assert bp.category == BloodPressureCategory.STAGE1_HYPERTENSION
        assert not bp.is_critical()
        
        # Stage 2 Hypertension
        bp = BloodPressure(patient_id="p1", systolic=145, diastolic=95)
        assert bp.category == BloodPressureCategory.STAGE2_HYPERTENSION
        assert not bp.is_critical()
        
        # Hypertensive Crisis
        bp = BloodPressure(patient_id="p1", systolic=185, diastolic=125)
        assert bp.category == BloodPressureCategory.HYPERTENSIVE_CRISIS
        assert bp.is_critical()
        
        # Hypotension
        bp = BloodPressure(patient_id="p1", systolic=85, diastolic=55)
        assert bp.category == BloodPressureCategory.HYPOTENSION
        assert bp.is_critical()


class TestHeartRate:
    """Test heart rate model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_heart_rate_categories(self):
        """Test heart rate categorization."""
        # Bradycardia
        hr = HeartRate(patient_id="p1", rate=45)
        assert hr.category == HeartRateCategory.BRADYCARDIA
        assert not hr.is_critical()
        
        hr = HeartRate(patient_id="p1", rate=35)
        assert hr.category == HeartRateCategory.BRADYCARDIA
        assert hr.is_critical()
        
        # Normal
        hr = HeartRate(patient_id="p1", rate=75)
        assert hr.category == HeartRateCategory.NORMAL
        assert not hr.is_critical()
        
        # Tachycardia
        hr = HeartRate(patient_id="p1", rate=120)
        assert hr.category == HeartRateCategory.TACHYCARDIA
        assert not hr.is_critical()
        
        # Severe Tachycardia
        hr = HeartRate(patient_id="p1", rate=160)
        assert hr.category == HeartRateCategory.SEVERE_TACHYCARDIA
        assert hr.is_critical()


class TestTemperature:
    """Test temperature model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_temperature_conversion(self):
        """Test temperature unit conversion."""
        # Celsius to Fahrenheit
        temp = Temperature(patient_id="p1", value=37.0, unit="celsius")
        assert temp.to_fahrenheit() == pytest.approx(98.6, rel=0.1)
        
        # Fahrenheit to Celsius
        temp = Temperature(patient_id="p1", value=98.6, unit="fahrenheit")
        assert temp.to_celsius() == pytest.approx(37.0, rel=0.1)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_temperature_categories(self):
        """Test temperature categorization."""
        # Hypothermia
        temp = Temperature(patient_id="p1", value=34.5, unit="celsius")
        assert temp.category == TemperatureCategory.HYPOTHERMIA
        assert temp.is_critical()
        
        # Normal
        temp = Temperature(patient_id="p1", value=37.0, unit="celsius")
        assert temp.category == TemperatureCategory.NORMAL
        assert not temp.is_critical()
        
        # Fever
        temp = Temperature(patient_id="p1", value=38.0, unit="celsius")
        assert temp.category == TemperatureCategory.FEVER
        assert not temp.is_critical()
        
        # High Fever
        temp = Temperature(patient_id="p1", value=39.5, unit="celsius")
        assert temp.category == TemperatureCategory.HIGH_FEVER
        assert not temp.is_critical()
        
        # Hyperpyrexia
        temp = Temperature(patient_id="p1", value=40.5, unit="celsius")
        assert temp.category == TemperatureCategory.HYPERPYREXIA
        assert temp.is_critical()
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_temperature_validation(self):
        """Test temperature validation."""
        # Valid units
        temp = Temperature(patient_id="p1", value=37.0, unit="celsius")
        assert temp.unit == "celsius"
        
        # Invalid unit
        with pytest.raises(Exception):
            Temperature(patient_id="p1", value=37.0, unit="kelvin")
        
        # Valid methods
        for method in ["oral", "rectal", "axillary", "tympanic", "temporal"]:
            temp = Temperature(patient_id="p1", value=37.0, method=method)
            assert temp.method == method


class TestOxygenSaturation:
    """Test oxygen saturation model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_oxygen_saturation_categories(self):
        """Test oxygen saturation categorization."""
        # Normal
        spo2 = OxygenSaturation(patient_id="p1", value=98)
        assert spo2.category == OxygenSaturationCategory.NORMAL
        assert not spo2.is_critical()
        
        # Mild Hypoxemia
        spo2 = OxygenSaturation(patient_id="p1", value=93)
        assert spo2.category == OxygenSaturationCategory.MILD_HYPOXEMIA
        assert not spo2.is_critical()
        
        # Moderate Hypoxemia
        spo2 = OxygenSaturation(patient_id="p1", value=88)
        assert spo2.category == OxygenSaturationCategory.MODERATE_HYPOXEMIA
        assert spo2.is_critical()
        
        # Severe Hypoxemia
        spo2 = OxygenSaturation(patient_id="p1", value=82)
        assert spo2.category == OxygenSaturationCategory.SEVERE_HYPOXEMIA
        assert spo2.is_critical()
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_oxygen_supplementation(self):
        """Test oxygen supplementation tracking."""
        spo2 = OxygenSaturation(
            patient_id="p1",
            value=95,
            on_oxygen=True,
            oxygen_flow_rate=2.0,
            oxygen_delivery="nasal cannula"
        )
        
        assert spo2.on_oxygen is True
        assert spo2.oxygen_flow_rate == 2.0
        assert spo2.oxygen_delivery == "nasal cannula"


class TestRespiratoryRate:
    """Test respiratory rate model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_respiratory_rate_normal(self):
        """Test respiratory rate normal range."""
        # Normal adult range
        rr = RespiratoryRate(patient_id="p1", rate=16)
        assert rr.is_normal()
        assert not rr.is_critical()
        
        # Low but not critical
        rr = RespiratoryRate(patient_id="p1", rate=10)
        assert not rr.is_normal()
        assert not rr.is_critical()
        
        # Critical low
        rr = RespiratoryRate(patient_id="p1", rate=6)
        assert not rr.is_normal()
        assert rr.is_critical()
        
        # Critical high
        rr = RespiratoryRate(patient_id="p1", rate=35)
        assert not rr.is_normal()
        assert rr.is_critical()


class TestPainScale:
    """Test pain scale model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_pain_severity(self):
        """Test pain severity categorization."""
        # No pain
        pain = PainScale(patient_id="p1", score=0)
        assert pain.get_severity() == "no_pain"
        
        # Mild
        pain = PainScale(patient_id="p1", score=2)
        assert pain.get_severity() == "mild"
        
        # Moderate
        pain = PainScale(patient_id="p1", score=5)
        assert pain.get_severity() == "moderate"
        
        # Severe
        pain = PainScale(patient_id="p1", score=8)
        assert pain.get_severity() == "severe"
        
        # Worst possible
        pain = PainScale(patient_id="p1", score=10)
        assert pain.get_severity() == "worst_possible"


class TestVitalSignsSet:
    """Test vital signs set model."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_vital_signs_set_creation(self):
        """Test creating a complete vital signs set."""
        vs = VitalSignsSet(
            patient_id="patient_123",
            measured_by="nurse_456",
            blood_pressure={"systolic": 120, "diastolic": 80},
            heart_rate=72,
            temperature={"value": 37.0, "unit": "celsius"},
            respiratory_rate=16,
            oxygen_saturation=98,
            pain_score=2,
            weight=70.0,
            height=175.0
        )
        
        assert vs.patient_id == "patient_123"
        assert vs.bmi == pytest.approx(22.9, rel=0.1)
        assert len(vs.alerts) == 0
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_critical_alerts(self):
        """Test critical value alerts."""
        vs = VitalSignsSet(
            patient_id="patient_123",
            blood_pressure={"systolic": 185, "diastolic": 125},
            heart_rate=160,
            temperature={"value": 40.5, "unit": "celsius"},
            respiratory_rate=35,
            oxygen_saturation=85
        )
        
        assert len(vs.alerts) > 0
        assert any("blood pressure" in alert for alert in vs.alerts)
        assert any("heart rate" in alert for alert in vs.alerts)
        assert any("temperature" in alert for alert in vs.alerts)
        assert any("respiratory rate" in alert for alert in vs.alerts)
        assert any("SpO2" in alert for alert in vs.alerts)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_vital_signs_summary(self):
        """Test vital signs summary generation."""
        vs = VitalSignsSet(
            patient_id="patient_123",
            blood_pressure={"systolic": 120, "diastolic": 80},
            heart_rate=72,
            temperature={"value": 98.6, "unit": "fahrenheit"},
            respiratory_rate=16,
            oxygen_saturation=98,
            pain_score=0
        )
        
        summary = vs.get_summary()
        
        assert "measured_at" in summary
        assert "alerts" in summary
        assert "values" in summary
        
        assert summary["values"]["blood_pressure"]["value"] == "120/80"
        assert summary["values"]["heart_rate"]["value"] == 72
        assert summary["values"]["temperature"]["value"] == 98.6
        assert summary["values"]["temperature"]["unit"] == "°F"
        assert summary["values"]["respiratory_rate"]["value"] == 16
        assert summary["values"]["oxygen_saturation"]["value"] == 98
        assert summary["values"]["pain_score"]["value"] == 0


class TestVitalSignsAnalyzer:
    """Test vital signs analyzer."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_early_warning_score(self):
        """Test Modified Early Warning Score calculation."""
        # Normal vital signs
        vs = VitalSignsSet(
            patient_id="patient_123",
            blood_pressure={"systolic": 120, "diastolic": 80},
            heart_rate=72,
            temperature={"value": 37.0, "unit": "celsius"},
            respiratory_rate=16
        )
        
        mews = VitalSignsAnalyzer.get_early_warning_score(vs)
        
        assert mews["score"] == 0
        assert mews["risk_level"] == "low"
        assert all(v == 0 for v in mews["components"].values())
        
        # Critical vital signs
        vs_critical = VitalSignsSet(
            patient_id="patient_123",
            blood_pressure={"systolic": 65, "diastolic": 45},
            heart_rate=140,
            temperature={"value": 40.0, "unit": "celsius"},
            respiratory_rate=32
        )
        
        mews_critical = VitalSignsAnalyzer.get_early_warning_score(vs_critical)
        
        assert mews_critical["score"] >= 7
        assert mews_critical["risk_level"] == "critical"
        assert "Immediate" in mews_critical["recommendation"]