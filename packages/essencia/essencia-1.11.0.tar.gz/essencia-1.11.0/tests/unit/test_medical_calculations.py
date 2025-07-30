"""
Unit tests for medical calculations.
"""
import pytest

from essencia.medical import (
    calculate_bmi,
    calculate_bsa,
    calculate_gfr,
    categorize_bmi,
    categorize_blood_pressure,
)


class TestMedicalCalculations:
    """Test medical calculation functions."""
    
    @pytest.mark.medical
    def test_calculate_bmi(self):
        """Test BMI calculation."""
        # Normal case
        assert calculate_bmi(70, 175) == pytest.approx(22.86, rel=0.01)
        
        # Edge cases
        assert calculate_bmi(50, 150) == pytest.approx(22.22, rel=0.01)
        assert calculate_bmi(100, 200) == pytest.approx(25.0, rel=0.01)
        
        # Invalid inputs
        with pytest.raises(ValueError):
            calculate_bmi(0, 175)
        with pytest.raises(ValueError):
            calculate_bmi(70, 0)
        with pytest.raises(ValueError):
            calculate_bmi(-70, 175)
    
    @pytest.mark.medical
    def test_categorize_bmi(self):
        """Test BMI categorization."""
        assert categorize_bmi(15) == "Muito abaixo do peso"
        assert categorize_bmi(18) == "Abaixo do peso"
        assert categorize_bmi(22) == "Peso normal"
        assert categorize_bmi(27) == "Sobrepeso"
        assert categorize_bmi(32) == "Obesidade grau I"
        assert categorize_bmi(37) == "Obesidade grau II"
        assert categorize_bmi(42) == "Obesidade grau III"
    
    @pytest.mark.medical
    def test_calculate_bsa(self):
        """Test Body Surface Area calculation."""
        # DuBois method (default)
        assert calculate_bsa(70, 175) == pytest.approx(1.85, rel=0.01)
        
        # Mosteller method
        assert calculate_bsa(70, 175, method="mosteller") == pytest.approx(1.84, rel=0.01)
        
        # Boyd method
        assert calculate_bsa(70, 175, method="boyd") == pytest.approx(1.85, rel=0.01)
        
        # Invalid method
        with pytest.raises(ValueError):
            calculate_bsa(70, 175, method="invalid")
    
    @pytest.mark.medical
    def test_calculate_gfr(self):
        """Test GFR calculation."""
        # CKD-EPI method
        gfr = calculate_gfr(
            creatinine=1.2,
            age=50,
            gender="M",
            race="black",
            method="ckd-epi"
        )
        assert isinstance(gfr, float)
        assert gfr > 0
        
        # MDRD method
        gfr_mdrd = calculate_gfr(
            creatinine=1.2,
            age=50,
            gender="F",
            race="other",
            method="mdrd"
        )
        assert isinstance(gfr_mdrd, float)
        assert gfr_mdrd > 0
        
        # Invalid inputs
        with pytest.raises(ValueError):
            calculate_gfr(0, 50, "M", "other")
        with pytest.raises(ValueError):
            calculate_gfr(1.2, 0, "M", "other")
        with pytest.raises(ValueError):
            calculate_gfr(1.2, 50, "X", "other")
    
    @pytest.mark.medical
    def test_categorize_blood_pressure(self):
        """Test blood pressure categorization."""
        assert categorize_blood_pressure(115, 75) == "Normal"
        assert categorize_blood_pressure(125, 80) == "Elevada"
        assert categorize_blood_pressure(135, 85) == "Hipertensão Estágio 1"
        assert categorize_blood_pressure(145, 95) == "Hipertensão Estágio 2"
        assert categorize_blood_pressure(185, 125) == "Crise Hipertensiva"
        
        # Edge cases
        assert categorize_blood_pressure(120, 80) == "Elevada"
        assert categorize_blood_pressure(130, 80) == "Hipertensão Estágio 1"
        assert categorize_blood_pressure(140, 90) == "Hipertensão Estágio 2"