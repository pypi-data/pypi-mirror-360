"""
Vital signs analysis and trend detection.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel

from essencia.models.vital_signs import (
    BloodPressure,
    HeartRate,
    OxygenSaturation,
    Temperature,
    VitalSignsSet,
)


class VitalSignTrend(BaseModel):
    """Trend analysis result for a vital sign."""
    
    current_value: float
    previous_value: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # increasing, decreasing, stable
    average: float
    min_value: float
    max_value: float
    std_deviation: float
    measurements_count: int
    time_span_hours: float
    is_improving: Optional[bool] = None
    clinical_significance: Optional[str] = None


class VitalSignsAnalyzer:
    """Analyzer for vital signs trends and patterns."""
    
    @staticmethod
    def analyze_blood_pressure_trend(
        measurements: List[BloodPressure],
        hours: int = 24
    ) -> Dict[str, VitalSignTrend]:
        """Analyze blood pressure trends."""
        if not measurements:
            return {}
        
        # Sort by time
        sorted_measurements = sorted(measurements, key=lambda x: x.measured_at)
        
        # Extract values
        systolic_values = [m.systolic for m in sorted_measurements]
        diastolic_values = [m.diastolic for m in sorted_measurements]
        map_values = [m.mean_arterial_pressure for m in sorted_measurements if m.mean_arterial_pressure]
        
        # Analyze systolic
        systolic_trend = VitalSignTrend(
            current_value=systolic_values[-1],
            previous_value=systolic_values[-2] if len(systolic_values) > 1 else None,
            average=np.mean(systolic_values),
            min_value=min(systolic_values),
            max_value=max(systolic_values),
            std_deviation=np.std(systolic_values),
            measurements_count=len(systolic_values),
            time_span_hours=hours
        )
        
        # Calculate change and trend
        if systolic_trend.previous_value:
            systolic_trend.change = systolic_trend.current_value - systolic_trend.previous_value
            systolic_trend.change_percentage = (systolic_trend.change / systolic_trend.previous_value) * 100
            systolic_trend.trend = VitalSignsAnalyzer._determine_trend(systolic_values)
            
            # Determine if improving (moving toward normal)
            if sorted_measurements[-1].category == "normal":
                systolic_trend.is_improving = True
            elif sorted_measurements[-1].category in ["stage2_hypertension", "hypertensive_crisis"]:
                systolic_trend.is_improving = systolic_trend.change < 0
            elif sorted_measurements[-1].category == "hypotension":
                systolic_trend.is_improving = systolic_trend.change > 0
        
        # Analyze diastolic
        diastolic_trend = VitalSignTrend(
            current_value=diastolic_values[-1],
            previous_value=diastolic_values[-2] if len(diastolic_values) > 1 else None,
            average=np.mean(diastolic_values),
            min_value=min(diastolic_values),
            max_value=max(diastolic_values),
            std_deviation=np.std(diastolic_values),
            measurements_count=len(diastolic_values),
            time_span_hours=hours
        )
        
        if diastolic_trend.previous_value:
            diastolic_trend.change = diastolic_trend.current_value - diastolic_trend.previous_value
            diastolic_trend.change_percentage = (diastolic_trend.change / diastolic_trend.previous_value) * 100
            diastolic_trend.trend = VitalSignsAnalyzer._determine_trend(diastolic_values)
        
        # Analyze MAP if available
        map_trend = None
        if map_values:
            map_trend = VitalSignTrend(
                current_value=map_values[-1],
                previous_value=map_values[-2] if len(map_values) > 1 else None,
                average=np.mean(map_values),
                min_value=min(map_values),
                max_value=max(map_values),
                std_deviation=np.std(map_values),
                measurements_count=len(map_values),
                time_span_hours=hours
            )
        
        results = {
            "systolic": systolic_trend,
            "diastolic": diastolic_trend
        }
        
        if map_trend:
            results["map"] = map_trend
        
        return results
    
    @staticmethod
    def analyze_heart_rate_trend(
        measurements: List[HeartRate],
        hours: int = 24
    ) -> VitalSignTrend:
        """Analyze heart rate trends."""
        if not measurements:
            return None
        
        # Sort by time
        sorted_measurements = sorted(measurements, key=lambda x: x.measured_at)
        values = [m.rate for m in sorted_measurements]
        
        trend = VitalSignTrend(
            current_value=values[-1],
            previous_value=values[-2] if len(values) > 1 else None,
            average=np.mean(values),
            min_value=min(values),
            max_value=max(values),
            std_deviation=np.std(values),
            measurements_count=len(values),
            time_span_hours=hours
        )
        
        if trend.previous_value:
            trend.change = trend.current_value - trend.previous_value
            trend.change_percentage = (trend.change / trend.previous_value) * 100
            trend.trend = VitalSignsAnalyzer._determine_trend(values)
            
            # Determine if improving
            current_category = sorted_measurements[-1].category
            if current_category == "normal":
                trend.is_improving = True
            elif current_category == "bradycardia":
                trend.is_improving = trend.change > 0
            elif current_category in ["tachycardia", "severe_tachycardia"]:
                trend.is_improving = trend.change < 0
        
        return trend
    
    @staticmethod
    def analyze_temperature_trend(
        measurements: List[Temperature],
        hours: int = 24
    ) -> VitalSignTrend:
        """Analyze temperature trends."""
        if not measurements:
            return None
        
        # Sort by time and convert to Celsius
        sorted_measurements = sorted(measurements, key=lambda x: x.measured_at)
        values = [m.to_celsius() for m in sorted_measurements]
        
        trend = VitalSignTrend(
            current_value=values[-1],
            previous_value=values[-2] if len(values) > 1 else None,
            average=np.mean(values),
            min_value=min(values),
            max_value=max(values),
            std_deviation=np.std(values),
            measurements_count=len(values),
            time_span_hours=hours
        )
        
        if trend.previous_value:
            trend.change = trend.current_value - trend.previous_value
            trend.change_percentage = (trend.change / trend.previous_value) * 100
            trend.trend = VitalSignsAnalyzer._determine_trend(values)
            
            # Determine if improving
            current_category = sorted_measurements[-1].category
            if current_category == "normal":
                trend.is_improving = True
            elif current_category in ["fever", "high_fever", "hyperpyrexia"]:
                trend.is_improving = trend.change < 0
            elif current_category == "hypothermia":
                trend.is_improving = trend.change > 0
        
        return trend
    
    @staticmethod
    def analyze_oxygen_saturation_trend(
        measurements: List[OxygenSaturation],
        hours: int = 24
    ) -> VitalSignTrend:
        """Analyze oxygen saturation trends."""
        if not measurements:
            return None
        
        # Sort by time
        sorted_measurements = sorted(measurements, key=lambda x: x.measured_at)
        values = [m.value for m in sorted_measurements]
        
        trend = VitalSignTrend(
            current_value=values[-1],
            previous_value=values[-2] if len(values) > 1 else None,
            average=np.mean(values),
            min_value=min(values),
            max_value=max(values),
            std_deviation=np.std(values),
            measurements_count=len(values),
            time_span_hours=hours
        )
        
        if trend.previous_value:
            trend.change = trend.current_value - trend.previous_value
            trend.change_percentage = (trend.change / trend.previous_value) * 100
            trend.trend = VitalSignsAnalyzer._determine_trend(values)
            
            # For SpO2, improvement is usually an increase
            trend.is_improving = trend.change > 0 or trend.current_value >= 95
        
        # Clinical significance
        if trend.current_value < 90:
            trend.clinical_significance = "critical_hypoxemia"
        elif trend.current_value < 95:
            trend.clinical_significance = "mild_hypoxemia"
        else:
            trend.clinical_significance = "normal"
        
        return trend
    
    @staticmethod
    def _determine_trend(values: List[float], threshold: float = 0.05) -> str:
        """Determine trend direction from values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Normalize slope by average value
        avg_value = np.mean(values)
        normalized_slope = slope / avg_value if avg_value != 0 else 0
        
        if abs(normalized_slope) < threshold:
            return "stable"
        elif normalized_slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    @staticmethod
    def get_early_warning_score(vital_signs: VitalSignsSet) -> Dict[str, any]:
        """Calculate Modified Early Warning Score (MEWS)."""
        score = 0
        components = {}
        
        # Systolic blood pressure
        if vital_signs.blood_pressure:
            sbp = vital_signs.blood_pressure.get("systolic", 0)
            if sbp <= 70:
                score += 3
                components["blood_pressure"] = 3
            elif sbp <= 80:
                score += 2
                components["blood_pressure"] = 2
            elif sbp <= 100:
                score += 1
                components["blood_pressure"] = 1
            elif sbp <= 199:
                components["blood_pressure"] = 0
            else:
                score += 2
                components["blood_pressure"] = 2
        
        # Heart rate
        if vital_signs.heart_rate:
            hr = vital_signs.heart_rate
            if hr <= 40:
                score += 2
                components["heart_rate"] = 2
            elif hr <= 50:
                score += 1
                components["heart_rate"] = 1
            elif hr <= 100:
                components["heart_rate"] = 0
            elif hr <= 110:
                score += 1
                components["heart_rate"] = 1
            elif hr <= 129:
                score += 2
                components["heart_rate"] = 2
            else:
                score += 3
                components["heart_rate"] = 3
        
        # Respiratory rate
        if vital_signs.respiratory_rate:
            rr = vital_signs.respiratory_rate
            if rr < 9:
                score += 2
                components["respiratory_rate"] = 2
            elif rr <= 14:
                components["respiratory_rate"] = 0
            elif rr <= 20:
                score += 1
                components["respiratory_rate"] = 1
            elif rr <= 29:
                score += 2
                components["respiratory_rate"] = 2
            else:
                score += 3
                components["respiratory_rate"] = 3
        
        # Temperature
        if vital_signs.temperature:
            temp_celsius = vital_signs.temperature.get("value", 37.0)
            if vital_signs.temperature.get("unit") == "fahrenheit":
                temp_celsius = (temp_celsius - 32) * 5/9
            
            if temp_celsius < 35:
                score += 2
                components["temperature"] = 2
            elif temp_celsius <= 38.4:
                components["temperature"] = 0
            else:
                score += 2
                components["temperature"] = 2
        
        # Interpret score
        risk_level = "low"
        recommendation = "Routine monitoring"
        
        if score >= 7:
            risk_level = "critical"
            recommendation = "Immediate medical review required"
        elif score >= 5:
            risk_level = "high"
            recommendation = "Urgent medical review within 30 minutes"
        elif score >= 3:
            risk_level = "medium"
            recommendation = "Increased monitoring frequency"
        
        return {
            "score": score,
            "components": components,
            "risk_level": risk_level,
            "recommendation": recommendation
        }
    
    @staticmethod
    def detect_abnormal_patterns(
        patient_id: str,
        vital_signs_history: List[VitalSignsSet],
        hours: int = 24
    ) -> List[Dict[str, any]]:
        """Detect abnormal patterns in vital signs."""
        patterns = []
        
        if len(vital_signs_history) < 2:
            return patterns
        
        # Sort by time
        sorted_history = sorted(vital_signs_history, key=lambda x: x.measured_at)
        
        # Check for sustained hypertension
        bp_high_count = sum(1 for vs in sorted_history[-5:] 
                           if vs.blood_pressure and 
                           (vs.blood_pressure.get("systolic", 0) >= 140 or 
                            vs.blood_pressure.get("diastolic", 0) >= 90))
        if bp_high_count >= 3:
            patterns.append({
                "type": "sustained_hypertension",
                "severity": "moderate",
                "description": "Blood pressure consistently elevated",
                "action": "Consider antihypertensive medication review"
            })
        
        # Check for tachycardia pattern
        hr_high_count = sum(1 for vs in sorted_history[-5:]
                           if vs.heart_rate and vs.heart_rate > 100)
        if hr_high_count >= 3:
            patterns.append({
                "type": "persistent_tachycardia",
                "severity": "moderate",
                "description": "Heart rate consistently elevated",
                "action": "Evaluate for underlying causes"
            })
        
        # Check for fever pattern
        fever_count = sum(1 for vs in sorted_history[-5:]
                         if vs.temperature and 
                         vs.temperature.get("value", 37) > 38.0)
        if fever_count >= 3:
            patterns.append({
                "type": "persistent_fever",
                "severity": "moderate",
                "description": "Temperature consistently elevated",
                "action": "Investigate infection source"
            })
        
        # Check for deteriorating SpO2
        spo2_values = [vs.oxygen_saturation for vs in sorted_history[-5:]
                      if vs.oxygen_saturation is not None]
        if len(spo2_values) >= 3:
            spo2_trend = VitalSignsAnalyzer._determine_trend(spo2_values)
            if spo2_trend == "decreasing" and spo2_values[-1] < 95:
                patterns.append({
                    "type": "deteriorating_oxygenation",
                    "severity": "high",
                    "description": "Oxygen saturation trending downward",
                    "action": "Consider supplemental oxygen"
                })
        
        return patterns