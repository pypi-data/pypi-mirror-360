"""
Mental health screening and clinical decision support service.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from essencia.models.mental_health import (
    AssessmentType,
    MentalHealthAssessment,
    SeverityLevel,
    PHQ9Assessment,
    GAD7Assessment,
    SNAPIV_Assessment,
)


class ClinicalAlert:
    """Clinical alert for mental health concerns."""
    
    def __init__(
        self,
        alert_type: str,
        severity: str,
        message: str,
        actions: List[str],
        requires_immediate_action: bool = False
    ):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.actions = actions
        self.requires_immediate_action = requires_immediate_action
        self.created_at = datetime.utcnow()


class MentalHealthScreeningService:
    """Service for mental health screening and clinical decision support."""
    
    # Risk factors by condition
    RISK_FACTORS = {
        "depression": [
            "family_history_depression",
            "chronic_medical_condition",
            "recent_loss_or_trauma",
            "substance_abuse",
            "social_isolation",
            "unemployment",
            "relationship_problems",
            "previous_depression",
            "postpartum_period"
        ],
        "anxiety": [
            "family_history_anxiety",
            "traumatic_experiences",
            "chronic_stress",
            "substance_abuse",
            "medical_conditions",
            "medication_side_effects",
            "caffeine_overuse"
        ],
        "suicide": [
            "previous_attempt",
            "family_history_suicide",
            "substance_abuse",
            "access_to_means",
            "recent_discharge",
            "chronic_pain",
            "social_isolation",
            "recent_loss",
            "impulsivity",
            "male_gender",
            "age_over_65_or_15_24"
        ],
        "adhd": [
            "family_history_adhd",
            "premature_birth",
            "low_birth_weight",
            "prenatal_exposure_toxins",
            "head_injury",
            "learning_disabilities"
        ]
    }
    
    # Protective factors
    PROTECTIVE_FACTORS = {
        "general": [
            "strong_social_support",
            "engaged_in_treatment",
            "good_coping_skills",
            "religious_spiritual_beliefs",
            "sense_of_purpose",
            "physical_activity",
            "healthy_sleep_patterns",
            "no_substance_abuse",
            "stable_employment",
            "stable_relationships"
        ]
    }
    
    @classmethod
    def screen_for_conditions(
        cls,
        assessments: List[MentalHealthAssessment],
        patient_history: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """Screen for mental health conditions based on assessments."""
        conditions = []
        
        # Group assessments by type
        by_type = {}
        for assessment in assessments:
            if assessment.assessment_type not in by_type:
                by_type[assessment.assessment_type] = []
            by_type[assessment.assessment_type].append(assessment)
        
        # Check PHQ-9 for depression
        if AssessmentType.PHQ9 in by_type:
            phq9_assessments = by_type[AssessmentType.PHQ9]
            latest_phq9 = max(phq9_assessments, key=lambda x: x.administered_at)
            
            if latest_phq9.severity in [SeverityLevel.MODERATE, SeverityLevel.MODERATELY_SEVERE, SeverityLevel.SEVERE]:
                conditions.append({
                    "condition": "Major Depressive Disorder",
                    "probability": "high" if latest_phq9.severity == SeverityLevel.SEVERE else "moderate",
                    "evidence": f"PHQ-9 score: {latest_phq9.total_score}",
                    "icd_codes": ["F32.9", "F33.9"],
                    "recommendations": cls._get_depression_recommendations(latest_phq9)
                })
        
        # Check GAD-7 for anxiety
        if AssessmentType.GAD7 in by_type:
            gad7_assessments = by_type[AssessmentType.GAD7]
            latest_gad7 = max(gad7_assessments, key=lambda x: x.administered_at)
            
            if latest_gad7.severity in [SeverityLevel.MODERATE, SeverityLevel.SEVERE]:
                conditions.append({
                    "condition": "Generalized Anxiety Disorder",
                    "probability": "high" if latest_gad7.severity == SeverityLevel.SEVERE else "moderate",
                    "evidence": f"GAD-7 score: {latest_gad7.total_score}",
                    "icd_codes": ["F41.1"],
                    "recommendations": cls._get_anxiety_recommendations(latest_gad7)
                })
        
        # Check SNAP-IV for ADHD
        if AssessmentType.SNAP_IV in by_type:
            snap_assessments = by_type[AssessmentType.SNAP_IV]
            latest_snap = max(snap_assessments, key=lambda x: x.administered_at)
            
            if isinstance(latest_snap, SNAPIV_Assessment):
                subscores = latest_snap.calculate_subscores()
                
                if subscores["meets_inattention_criteria"] or subscores["meets_hyperactivity_criteria"]:
                    adhd_type = "Combined" if subscores["meets_inattention_criteria"] and subscores["meets_hyperactivity_criteria"] else \
                               "Inattentive" if subscores["meets_inattention_criteria"] else "Hyperactive-Impulsive"
                    
                    conditions.append({
                        "condition": f"ADHD, {adhd_type} presentation",
                        "probability": "high",
                        "evidence": f"SNAP-IV scores - Inattention: {subscores['inattention_average']}, Hyperactivity: {subscores['hyperactivity_average']}",
                        "icd_codes": ["F90.0" if adhd_type == "Hyperactive-Impulsive" else "F90.1" if adhd_type == "Inattentive" else "F90.2"],
                        "recommendations": cls._get_adhd_recommendations(latest_snap, adhd_type)
                    })
        
        return conditions
    
    @classmethod
    def generate_clinical_alerts(
        cls,
        assessments: List[MentalHealthAssessment],
        patient_risk_factors: Optional[List[str]] = None
    ) -> List[ClinicalAlert]:
        """Generate clinical alerts based on assessments and risk factors."""
        alerts = []
        patient_risk_factors = patient_risk_factors or []
        
        # Check for suicidal ideation
        for assessment in assessments:
            if isinstance(assessment, PHQ9Assessment) and assessment.suicidal_ideation:
                # Count suicide risk factors
                suicide_risk_count = sum(1 for rf in patient_risk_factors 
                                       if rf in cls.RISK_FACTORS["suicide"])
                
                severity = "critical" if suicide_risk_count >= 3 else "high"
                
                alerts.append(ClinicalAlert(
                    alert_type="suicide_risk",
                    severity=severity,
                    message="Patient reported suicidal ideation on PHQ-9",
                    actions=[
                        "Conduct immediate safety assessment",
                        "Develop safety plan with patient",
                        "Consider psychiatric consultation",
                        "Ensure means restriction",
                        "Schedule follow-up within 24-48 hours"
                    ],
                    requires_immediate_action=True
                ))
        
        # Check for severe depression
        phq9_assessments = [a for a in assessments if isinstance(a, PHQ9Assessment)]
        if phq9_assessments:
            latest = max(phq9_assessments, key=lambda x: x.administered_at)
            if latest.severity == SeverityLevel.SEVERE:
                alerts.append(ClinicalAlert(
                    alert_type="severe_depression",
                    severity="high",
                    message=f"Severe depression detected (PHQ-9: {latest.total_score})",
                    actions=[
                        "Consider medication management",
                        "Refer to psychiatry",
                        "Initiate psychotherapy",
                        "Weekly follow-up recommended"
                    ]
                ))
        
        # Check for deteriorating condition
        alerts.extend(cls._check_deterioration(assessments))
        
        return alerts
    
    @classmethod
    def _check_deterioration(
        cls,
        assessments: List[MentalHealthAssessment]
    ) -> List[ClinicalAlert]:
        """Check for deteriorating mental health."""
        alerts = []
        
        # Group by assessment type
        by_type = {}
        for assessment in assessments:
            if assessment.assessment_type not in by_type:
                by_type[assessment.assessment_type] = []
            by_type[assessment.assessment_type].append(assessment)
        
        # Check each assessment type
        for assessment_type, type_assessments in by_type.items():
            if len(type_assessments) < 2:
                continue
            
            # Sort by date
            sorted_assessments = sorted(type_assessments, key=lambda x: x.administered_at)
            
            # Compare last two assessments
            previous = sorted_assessments[-2]
            latest = sorted_assessments[-1]
            
            score_increase = latest.total_score - previous.total_score
            percent_increase = (score_increase / previous.total_score * 100) if previous.total_score > 0 else 0
            
            # Alert if significant deterioration
            if percent_increase > 30 or score_increase > 5:
                alerts.append(ClinicalAlert(
                    alert_type="deteriorating_condition",
                    severity="moderate",
                    message=f"{assessment_type.value.upper()} score increased by {score_increase} points ({percent_increase:.0f}%)",
                    actions=[
                        "Review current treatment plan",
                        "Assess medication adherence",
                        "Consider treatment intensification",
                        "Schedule urgent follow-up"
                    ]
                ))
        
        return alerts
    
    @staticmethod
    def _get_depression_recommendations(assessment: PHQ9Assessment) -> List[str]:
        """Get treatment recommendations for depression."""
        recommendations = []
        
        if assessment.severity == SeverityLevel.MILD:
            recommendations.extend([
                "Psychoeducation about depression",
                "Lifestyle modifications (exercise, sleep hygiene)",
                "Consider watchful waiting with follow-up in 4-6 weeks",
                "Self-help resources and apps"
            ])
        elif assessment.severity == SeverityLevel.MODERATE:
            recommendations.extend([
                "Psychotherapy (CBT, IPT)",
                "Consider antidepressant medication",
                "Regular exercise program",
                "Sleep hygiene education",
                "Follow-up in 2-4 weeks"
            ])
        elif assessment.severity in [SeverityLevel.MODERATELY_SEVERE, SeverityLevel.SEVERE]:
            recommendations.extend([
                "Antidepressant medication recommended",
                "Psychotherapy (CBT, IPT) strongly recommended",
                "Consider psychiatric referral",
                "Assess for hospitalization if severe",
                "Weekly follow-up initially",
                "Safety planning if suicidal ideation"
            ])
        
        return recommendations
    
    @staticmethod
    def _get_anxiety_recommendations(assessment: GAD7Assessment) -> List[str]:
        """Get treatment recommendations for anxiety."""
        recommendations = []
        
        if assessment.severity == SeverityLevel.MILD:
            recommendations.extend([
                "Psychoeducation about anxiety",
                "Relaxation techniques (deep breathing, PMR)",
                "Mindfulness and meditation",
                "Regular exercise",
                "Limit caffeine"
            ])
        elif assessment.severity == SeverityLevel.MODERATE:
            recommendations.extend([
                "Cognitive Behavioral Therapy (CBT)",
                "Consider SSRI/SNRI medication",
                "Stress management techniques",
                "Regular follow-up"
            ])
        elif assessment.severity == SeverityLevel.SEVERE:
            recommendations.extend([
                "Medication management (SSRI/SNRI)",
                "Intensive psychotherapy (CBT)",
                "Consider psychiatric referral",
                "Rule out medical causes",
                "Frequent follow-up"
            ])
        
        return recommendations
    
    @staticmethod
    def _get_adhd_recommendations(assessment: SNAPIV_Assessment, adhd_type: str) -> List[str]:
        """Get treatment recommendations for ADHD."""
        recommendations = [
            "Comprehensive ADHD evaluation",
            "Parent and teacher behavior rating scales",
            "Educational accommodations (IEP/504 plan)",
            "Behavioral therapy/parent training"
        ]
        
        if adhd_type in ["Combined", "Hyperactive-Impulsive"]:
            recommendations.extend([
                "Consider stimulant medication",
                "Structured routines and clear expectations",
                "Regular physical activity"
            ])
        
        if adhd_type in ["Combined", "Inattentive"]:
            recommendations.extend([
                "Organizational skills training",
                "Break tasks into smaller steps",
                "Minimize distractions in environment"
            ])
        
        return recommendations
    
    @classmethod
    def generate_treatment_plan(
        cls,
        conditions: List[Dict],
        patient_preferences: Optional[Dict] = None
    ) -> Dict[str, any]:
        """Generate a comprehensive treatment plan."""
        patient_preferences = patient_preferences or {}
        
        plan = {
            "diagnoses": [],
            "medications": [],
            "psychotherapy": [],
            "lifestyle_interventions": [],
            "follow_up_schedule": {},
            "monitoring_plan": []
        }
        
        # Process each condition
        for condition in conditions:
            plan["diagnoses"].append({
                "condition": condition["condition"],
                "icd_codes": condition["icd_codes"],
                "confidence": condition["probability"]
            })
            
            # Add condition-specific elements
            if "Depression" in condition["condition"]:
                if patient_preferences.get("prefers_medication", True):
                    plan["medications"].append({
                        "class": "SSRI",
                        "options": ["Sertraline 50mg", "Escitalopram 10mg", "Fluoxetine 20mg"],
                        "monitoring": "Check in 2 weeks for side effects, 4-6 weeks for efficacy"
                    })
                
                plan["psychotherapy"].append({
                    "type": "Cognitive Behavioral Therapy (CBT)",
                    "frequency": "Weekly x 12-16 sessions",
                    "focus": "Depression"
                })
                
                plan["lifestyle_interventions"].extend([
                    "Regular aerobic exercise 30 min/day, 5 days/week",
                    "Sleep hygiene education",
                    "Social activation"
                ])
            
            elif "Anxiety" in condition["condition"]:
                if patient_preferences.get("prefers_medication", True):
                    plan["medications"].append({
                        "class": "SSRI/SNRI",
                        "options": ["Sertraline 25mg", "Venlafaxine XR 37.5mg"],
                        "monitoring": "Start low, titrate slowly"
                    })
                
                plan["psychotherapy"].append({
                    "type": "CBT for Anxiety",
                    "frequency": "Weekly x 12-16 sessions",
                    "focus": "Anxiety management"
                })
                
                plan["lifestyle_interventions"].extend([
                    "Relaxation training",
                    "Limit caffeine",
                    "Regular exercise"
                ])
        
        # Set follow-up schedule
        severity_max = max([c.get("severity", "moderate") for c in conditions], 
                          key=lambda x: ["mild", "moderate", "severe"].index(x) if x in ["mild", "moderate", "severe"] else 1)
        
        if severity_max == "severe":
            plan["follow_up_schedule"] = {
                "next_appointment": "1 week",
                "frequency": "Weekly until stable, then biweekly"
            }
        elif severity_max == "moderate":
            plan["follow_up_schedule"] = {
                "next_appointment": "2 weeks",
                "frequency": "Every 2-4 weeks"
            }
        else:
            plan["follow_up_schedule"] = {
                "next_appointment": "4 weeks",
                "frequency": "Monthly"
            }
        
        # Monitoring plan
        plan["monitoring_plan"] = [
            "Repeat assessment scales at each visit",
            "Monitor medication side effects",
            "Track functional improvement",
            "Assess treatment adherence"
        ]
        
        return plan
    
    @staticmethod
    def calculate_risk_score(
        assessments: List[MentalHealthAssessment],
        risk_factors: List[str],
        protective_factors: List[str]
    ) -> Dict[str, any]:
        """Calculate overall mental health risk score."""
        # Base risk from assessments
        assessment_risk = 0
        
        for assessment in assessments:
            if assessment.severity == SeverityLevel.SEVERE:
                assessment_risk += 3
            elif assessment.severity == SeverityLevel.MODERATELY_SEVERE:
                assessment_risk += 2.5
            elif assessment.severity == SeverityLevel.MODERATE:
                assessment_risk += 2
            elif assessment.severity == SeverityLevel.MILD:
                assessment_risk += 1
        
        # Risk factors
        risk_factor_score = len(risk_factors) * 0.5
        
        # Protective factors (reduce risk)
        protective_factor_score = len(protective_factors) * 0.3
        
        # Calculate total risk
        total_risk = assessment_risk + risk_factor_score - protective_factor_score
        total_risk = max(0, total_risk)  # Don't go below 0
        
        # Categorize risk
        if total_risk >= 8:
            risk_level = "high"
        elif total_risk >= 4:
            risk_level = "moderate"
        elif total_risk >= 2:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "total_score": round(total_risk, 1),
            "risk_level": risk_level,
            "components": {
                "assessment_risk": assessment_risk,
                "risk_factors": risk_factor_score,
                "protective_factors": protective_factor_score
            },
            "recommendations": cls._get_risk_recommendations(risk_level)
        }
    
    @staticmethod
    def _get_risk_recommendations(risk_level: str) -> List[str]:
        """Get recommendations based on risk level."""
        if risk_level == "high":
            return [
                "Intensive treatment recommended",
                "Consider higher level of care",
                "Frequent monitoring (weekly)",
                "Comprehensive safety planning",
                "Involve support system"
            ]
        elif risk_level == "moderate":
            return [
                "Active treatment recommended",
                "Regular monitoring (biweekly)",
                "Strengthen protective factors",
                "Address modifiable risk factors"
            ]
        elif risk_level == "low":
            return [
                "Preventive interventions",
                "Routine monitoring",
                "Maintain protective factors",
                "Early intervention if symptoms worsen"
            ]
        else:
            return [
                "Continue current supports",
                "Annual screening",
                "Maintain healthy lifestyle"
            ]