"""
Medical calculations and scoring systems.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import math


class Gender(Enum):
    """Biological gender for medical calculations."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BMICategory(Enum):
    """BMI categories according to WHO."""
    UNDERWEIGHT_SEVERE = "severe_underweight"
    UNDERWEIGHT_MODERATE = "moderate_underweight"
    UNDERWEIGHT_MILD = "mild_underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE_I = "obese_class_i"
    OBESE_II = "obese_class_ii"
    OBESE_III = "obese_class_iii"


@dataclass
class BMIResult:
    """Result of BMI calculation."""
    bmi: float
    category: BMICategory
    ideal_weight_range: Tuple[float, float]
    weight_to_lose: Optional[float] = None
    weight_to_gain: Optional[float] = None


class BMICalculator:
    """Body Mass Index calculator."""
    
    @staticmethod
    def calculate(weight_kg: float, height_m: float) -> BMIResult:
        """
        Calculate BMI and categorize.
        
        Args:
            weight_kg: Weight in kilograms
            height_m: Height in meters
            
        Returns:
            BMIResult with calculation and category
        """
        if height_m <= 0 or weight_kg <= 0:
            raise ValueError("Height and weight must be positive")
            
        bmi = weight_kg / (height_m ** 2)
        
        # Categorize BMI
        if bmi < 16:
            category = BMICategory.UNDERWEIGHT_SEVERE
        elif bmi < 17:
            category = BMICategory.UNDERWEIGHT_MODERATE
        elif bmi < 18.5:
            category = BMICategory.UNDERWEIGHT_MILD
        elif bmi < 25:
            category = BMICategory.NORMAL
        elif bmi < 30:
            category = BMICategory.OVERWEIGHT
        elif bmi < 35:
            category = BMICategory.OBESE_I
        elif bmi < 40:
            category = BMICategory.OBESE_II
        else:
            category = BMICategory.OBESE_III
            
        # Calculate ideal weight range (BMI 18.5-24.9)
        ideal_weight_min = 18.5 * (height_m ** 2)
        ideal_weight_max = 24.9 * (height_m ** 2)
        
        # Calculate weight adjustments needed
        weight_to_lose = None
        weight_to_gain = None
        
        if weight_kg > ideal_weight_max:
            weight_to_lose = weight_kg - ideal_weight_max
        elif weight_kg < ideal_weight_min:
            weight_to_gain = ideal_weight_min - weight_kg
            
        return BMIResult(
            bmi=round(bmi, 1),
            category=category,
            ideal_weight_range=(round(ideal_weight_min, 1), round(ideal_weight_max, 1)),
            weight_to_lose=round(weight_to_lose, 1) if weight_to_lose else None,
            weight_to_gain=round(weight_to_gain, 1) if weight_to_gain else None
        )
        
    @staticmethod
    def calculate_for_children(
        weight_kg: float,
        height_m: float,
        age_years: float,
        gender: Gender
    ) -> Dict[str, Any]:
        """Calculate BMI for children with percentile."""
        # This would use WHO growth charts
        # Simplified implementation
        bmi = weight_kg / (height_m ** 2)
        
        return {
            'bmi': round(bmi, 1),
            'age_years': age_years,
            'gender': gender.value,
            'percentile': None,  # Would calculate from growth charts
            'category': 'requires_growth_chart_data'
        }


class BSACalculator:
    """Body Surface Area calculator."""
    
    @staticmethod
    def mosteller(weight_kg: float, height_cm: float) -> float:
        """
        Calculate BSA using Mosteller formula.
        BSA = √((height × weight) / 3600)
        """
        return math.sqrt((height_cm * weight_kg) / 3600)
        
    @staticmethod
    def dubois(weight_kg: float, height_cm: float) -> float:
        """
        Calculate BSA using DuBois formula.
        BSA = 0.007184 × weight^0.425 × height^0.725
        """
        return 0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725)
        
    @staticmethod
    def haycock(weight_kg: float, height_cm: float) -> float:
        """
        Calculate BSA using Haycock formula (for children).
        BSA = 0.024265 × weight^0.5378 × height^0.3964
        """
        return 0.024265 * (weight_kg ** 0.5378) * (height_cm ** 0.3964)


class GFRCalculator:
    """Glomerular Filtration Rate calculator."""
    
    @staticmethod
    def ckd_epi(
        creatinine_mg_dl: float,
        age_years: int,
        gender: Gender,
        is_black: bool = False
    ) -> float:
        """
        Calculate eGFR using CKD-EPI equation.
        
        Args:
            creatinine_mg_dl: Serum creatinine in mg/dL
            age_years: Patient age in years
            gender: Patient gender
            is_black: Whether patient is Black/African American
            
        Returns:
            eGFR in mL/min/1.73m²
        """
        # CKD-EPI constants
        if gender == Gender.FEMALE:
            kappa = 0.7
            alpha = -0.329
            gender_mult = 1.018
        else:
            kappa = 0.9
            alpha = -0.411
            gender_mult = 1.0
            
        race_mult = 1.159 if is_black else 1.0
        
        # Calculate eGFR
        min_ratio = min(creatinine_mg_dl / kappa, 1)
        max_ratio = max(creatinine_mg_dl / kappa, 1)
        
        egfr = 141 * (min_ratio ** alpha) * (max_ratio ** -1.209) * (0.993 ** age_years)
        egfr *= gender_mult * race_mult
        
        return round(egfr, 1)
        
    @staticmethod
    def mdrd(
        creatinine_mg_dl: float,
        age_years: int,
        gender: Gender,
        is_black: bool = False
    ) -> float:
        """Calculate eGFR using MDRD equation."""
        gender_mult = 0.742 if gender == Gender.FEMALE else 1.0
        race_mult = 1.212 if is_black else 1.0
        
        egfr = 175 * (creatinine_mg_dl ** -1.154) * (age_years ** -0.203)
        egfr *= gender_mult * race_mult
        
        return round(egfr, 1)
        
    @staticmethod
    def schwartz_pediatric(
        creatinine_mg_dl: float,
        height_cm: float
    ) -> float:
        """Calculate eGFR for children using Schwartz formula."""
        # Updated Schwartz constant
        k = 0.413
        return round((k * height_cm) / creatinine_mg_dl, 1)


class DosageCalculator:
    """Medication dosage calculator."""
    
    @staticmethod
    def by_weight(
        dose_per_kg: float,
        weight_kg: float,
        max_dose: Optional[float] = None,
        frequency: int = 1
    ) -> Dict[str, float]:
        """
        Calculate dosage based on weight.
        
        Args:
            dose_per_kg: Dose per kilogram
            weight_kg: Patient weight in kg
            max_dose: Maximum allowed dose
            frequency: Doses per day
            
        Returns:
            Dict with dose calculations
        """
        single_dose = dose_per_kg * weight_kg
        
        if max_dose and single_dose > max_dose:
            single_dose = max_dose
            
        daily_dose = single_dose * frequency
        
        return {
            'single_dose': round(single_dose, 2),
            'daily_dose': round(daily_dose, 2),
            'frequency': frequency,
            'dose_per_kg': dose_per_kg
        }
        
    @staticmethod
    def by_bsa(
        dose_per_m2: float,
        bsa: float,
        max_dose: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculate dosage based on body surface area."""
        dose = dose_per_m2 * bsa
        
        if max_dose and dose > max_dose:
            dose = max_dose
            
        return {
            'dose': round(dose, 2),
            'dose_per_m2': dose_per_m2,
            'bsa': bsa
        }
        
    @staticmethod
    def renal_adjustment(
        normal_dose: float,
        gfr: float,
        adjustment_table: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Adjust dosage based on renal function.
        
        Args:
            normal_dose: Normal adult dose
            gfr: Glomerular filtration rate
            adjustment_table: GFR ranges and dose percentages
            
        Returns:
            Adjusted dose
        """
        if not adjustment_table:
            # Default adjustment table
            adjustment_table = {
                'normal': (60, float('inf'), 1.0),      # GFR > 60: 100%
                'mild': (30, 60, 0.75),                 # GFR 30-60: 75%
                'moderate': (15, 30, 0.5),              # GFR 15-30: 50%
                'severe': (0, 15, 0.25)                 # GFR < 15: 25%
            }
            
        # Find appropriate adjustment
        for category, (min_gfr, max_gfr, factor) in adjustment_table.items():
            if min_gfr <= gfr < max_gfr:
                return round(normal_dose * factor, 2)
                
        return normal_dose


class ClinicalScore:
    """Base class for clinical scoring systems."""
    
    @staticmethod
    def apgar(
        heart_rate: int,
        respiratory_effort: int,
        muscle_tone: int,
        reflex_response: int,
        color: int
    ) -> Dict[str, Any]:
        """
        Calculate APGAR score for newborns.
        Each parameter scored 0-2.
        """
        total = heart_rate + respiratory_effort + muscle_tone + reflex_response + color
        
        interpretation = ""
        if total >= 7:
            interpretation = "Normal"
        elif total >= 4:
            interpretation = "Moderate distress"
        else:
            interpretation = "Severe distress"
            
        return {
            'total_score': total,
            'components': {
                'heart_rate': heart_rate,
                'respiratory_effort': respiratory_effort,
                'muscle_tone': muscle_tone,
                'reflex_response': reflex_response,
                'color': color
            },
            'interpretation': interpretation
        }
        
    @staticmethod
    def glasgow_coma_scale(
        eye_opening: int,
        verbal_response: int,
        motor_response: int
    ) -> Dict[str, Any]:
        """
        Calculate Glasgow Coma Scale.
        Eye: 1-4, Verbal: 1-5, Motor: 1-6
        """
        total = eye_opening + verbal_response + motor_response
        
        if total >= 13:
            severity = "Mild"
        elif total >= 9:
            severity = "Moderate"
        else:
            severity = "Severe"
            
        return {
            'total_score': total,
            'components': {
                'eye_opening': eye_opening,
                'verbal_response': verbal_response,
                'motor_response': motor_response
            },
            'severity': severity
        }


class VitalSignsAnalyzer:
    """Analyze vital signs for abnormalities."""
    
    @staticmethod
    def analyze_blood_pressure(
        systolic: int,
        diastolic: int,
        age_years: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze blood pressure readings."""
        # Adult categories (simplified)
        if systolic < 90 or diastolic < 60:
            category = "Hypotension"
            risk = "high"
        elif systolic < 120 and diastolic < 80:
            category = "Normal"
            risk = "low"
        elif systolic < 130 and diastolic < 80:
            category = "Elevated"
            risk = "moderate"
        elif systolic < 140 or diastolic < 90:
            category = "Stage 1 Hypertension"
            risk = "moderate"
        elif systolic < 180 or diastolic < 120:
            category = "Stage 2 Hypertension"
            risk = "high"
        else:
            category = "Hypertensive Crisis"
            risk = "critical"
            
        return {
            'systolic': systolic,
            'diastolic': diastolic,
            'category': category,
            'risk_level': risk,
            'map': round((systolic + 2 * diastolic) / 3),  # Mean arterial pressure
            'pulse_pressure': systolic - diastolic
        }
        
    @staticmethod
    def analyze_heart_rate(
        rate: int,
        age_years: Optional[int] = None,
        at_rest: bool = True
    ) -> Dict[str, Any]:
        """Analyze heart rate."""
        # Adult resting heart rate
        if at_rest:
            if rate < 60:
                category = "Bradycardia"
            elif rate <= 100:
                category = "Normal"
            else:
                category = "Tachycardia"
        else:
            # Exercise heart rate would have different ranges
            category = "Exercise"
            
        return {
            'rate': rate,
            'category': category,
            'at_rest': at_rest
        }


# Convenience functions
def calculate_bmi(weight_kg: float, height_m: float) -> BMIResult:
    """Calculate BMI."""
    return BMICalculator.calculate(weight_kg, height_m)


def calculate_bsa(weight_kg: float, height_cm: float, method: str = "mosteller") -> float:
    """Calculate body surface area."""
    calculator = BSACalculator()
    method_map = {
        "mosteller": calculator.mosteller,
        "dubois": calculator.dubois,
        "haycock": calculator.haycock
    }
    return method_map[method](weight_kg, height_cm)


def calculate_gfr(
    creatinine_mg_dl: float,
    age_years: int,
    gender: Gender,
    method: str = "ckd_epi",
    **kwargs
) -> float:
    """Calculate glomerular filtration rate."""
    calculator = GFRCalculator()
    if method == "ckd_epi":
        return calculator.ckd_epi(creatinine_mg_dl, age_years, gender, **kwargs)
    elif method == "mdrd":
        return calculator.mdrd(creatinine_mg_dl, age_years, gender, **kwargs)
    else:
        raise ValueError(f"Unknown GFR calculation method: {method}")


def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> Dict[str, int]:
    """Calculate age in years, months, and days."""
    if reference_date is None:
        reference_date = date.today()
        
    # Calculate differences
    years = reference_date.year - birth_date.year
    months = reference_date.month - birth_date.month
    days = reference_date.day - birth_date.day
    
    # Adjust for negative values
    if days < 0:
        months -= 1
        # Get days in previous month
        if reference_date.month == 1:
            prev_month = 12
            prev_year = reference_date.year - 1
        else:
            prev_month = reference_date.month - 1
            prev_year = reference_date.year
            
        import calendar
        days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
        days += days_in_prev_month
        
    if months < 0:
        years -= 1
        months += 12
        
    total_days = (reference_date - birth_date).days
    
    return {
        'years': years,
        'months': months,
        'days': days,
        'total_days': total_days,
        'decimal_years': round(total_days / 365.25, 2)
    }


def calculate_gestational_age(
    lmp_date: date,
    reference_date: Optional[date] = None
) -> Dict[str, int]:
    """Calculate gestational age from last menstrual period."""
    if reference_date is None:
        reference_date = date.today()
        
    days = (reference_date - lmp_date).days
    weeks = days // 7
    remaining_days = days % 7
    
    trimester = 1 if weeks < 13 else 2 if weeks < 27 else 3
    
    return {
        'weeks': weeks,
        'days': remaining_days,
        'total_days': days,
        'trimester': trimester,
        'edd': lmp_date + timedelta(days=280)  # Estimated due date
    }