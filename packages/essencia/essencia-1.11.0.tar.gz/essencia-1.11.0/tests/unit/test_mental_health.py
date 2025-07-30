"""
Unit tests for mental health assessment tools.
"""
from datetime import datetime, timedelta

import pytest

from essencia.models.mental_health import (
    AssessmentQuestion,
    AssessmentResponse,
    AssessmentService,
    AssessmentType,
    GAD7Assessment,
    MentalHealthAssessment,
    PHQ9Assessment,
    SeverityLevel,
    SNAPIV_Assessment,
)
from essencia.services.mental_health_screening import (
    ClinicalAlert,
    MentalHealthScreeningService,
)


class TestPHQ9Assessment:
    """Test PHQ-9 depression assessment."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_phq9_questions(self):
        """Test PHQ-9 has correct number of questions."""
        questions = PHQ9Assessment.get_questions()
        assert len(questions) == 9
        assert all(isinstance(q, AssessmentQuestion) for q in questions)
        assert all(q.text_pt for q in questions)  # Portuguese translations
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_phq9_severity_calculation(self):
        """Test PHQ-9 severity calculation."""
        assert PHQ9Assessment.calculate_severity(0) == SeverityLevel.MINIMAL
        assert PHQ9Assessment.calculate_severity(4) == SeverityLevel.MINIMAL
        assert PHQ9Assessment.calculate_severity(5) == SeverityLevel.MILD
        assert PHQ9Assessment.calculate_severity(9) == SeverityLevel.MILD
        assert PHQ9Assessment.calculate_severity(10) == SeverityLevel.MODERATE
        assert PHQ9Assessment.calculate_severity(14) == SeverityLevel.MODERATE
        assert PHQ9Assessment.calculate_severity(15) == SeverityLevel.MODERATELY_SEVERE
        assert PHQ9Assessment.calculate_severity(19) == SeverityLevel.MODERATELY_SEVERE
        assert PHQ9Assessment.calculate_severity(20) == SeverityLevel.SEVERE
        assert PHQ9Assessment.calculate_severity(27) == SeverityLevel.SEVERE
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_phq9_suicidal_ideation_detection(self):
        """Test PHQ-9 suicidal ideation detection."""
        # Create responses with suicidal ideation
        responses = [
            AssessmentResponse(question_id=f"phq9_{i}", value=0)
            for i in range(1, 9)
        ]
        # Question 9 with positive response
        responses.append(
            AssessmentResponse(question_id="phq9_9", value=1)
        )
        
        assessment = AssessmentService.create_assessment(
            assessment_type=AssessmentType.PHQ9,
            patient_id="test_patient",
            responses=responses
        )
        
        assert isinstance(assessment, PHQ9Assessment)
        assert assessment.suicidal_ideation is True
        assert assessment.requires_immediate_attention is True
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_phq9_clinical_interpretation(self):
        """Test PHQ-9 clinical interpretation."""
        # Mild depression
        responses = [
            AssessmentResponse(question_id=f"phq9_{i}", value=1)
            for i in range(1, 10)
        ]
        
        assessment = AssessmentService.create_assessment(
            assessment_type=AssessmentType.PHQ9,
            patient_id="test_patient",
            responses=responses
        )
        
        interpretation = assessment.get_clinical_interpretation()
        
        assert interpretation["severity"] == SeverityLevel.MILD
        assert interpretation["total_score"] == 9
        assert "treatment_recommendations" in interpretation
        assert len(interpretation["treatment_recommendations"]) > 0
        assert "follow_up" in interpretation


class TestGAD7Assessment:
    """Test GAD-7 anxiety assessment."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_gad7_questions(self):
        """Test GAD-7 has correct number of questions."""
        questions = GAD7Assessment.get_questions()
        assert len(questions) == 7
        assert all(isinstance(q, AssessmentQuestion) for q in questions)
        assert all(q.text_pt for q in questions)
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_gad7_severity_calculation(self):
        """Test GAD-7 severity calculation."""
        assert GAD7Assessment.calculate_severity(0) == SeverityLevel.MINIMAL
        assert GAD7Assessment.calculate_severity(4) == SeverityLevel.MINIMAL
        assert GAD7Assessment.calculate_severity(5) == SeverityLevel.MILD
        assert GAD7Assessment.calculate_severity(9) == SeverityLevel.MILD
        assert GAD7Assessment.calculate_severity(10) == SeverityLevel.MODERATE
        assert GAD7Assessment.calculate_severity(14) == SeverityLevel.MODERATE
        assert GAD7Assessment.calculate_severity(15) == SeverityLevel.SEVERE
        assert GAD7Assessment.calculate_severity(21) == SeverityLevel.SEVERE


class TestSNAPIVAssessment:
    """Test SNAP-IV ADHD assessment."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_snapiv_questions(self):
        """Test SNAP-IV has correct number of questions."""
        questions = SNAPIV_Assessment.get_questions()
        assert len(questions) == 18  # 9 inattention + 9 hyperactivity
        
        inattention_q = [q for q in questions if q.category == "inattention"]
        hyperactivity_q = [q for q in questions if q.category == "hyperactivity"]
        
        assert len(inattention_q) == 9
        assert len(hyperactivity_q) == 9
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_snapiv_subscores(self):
        """Test SNAP-IV subscore calculation."""
        # Create responses - high inattention, low hyperactivity
        responses = []
        
        # Inattention items - mostly 3s
        for i in range(1, 10):
            responses.append(
                AssessmentResponse(question_id=f"snap_inattention_{i}", value=3)
            )
        
        # Hyperactivity items - mostly 0s
        for i in range(1, 10):
            responses.append(
                AssessmentResponse(question_id=f"snap_hyperactivity_{i}", value=0)
            )
        
        assessment = AssessmentService.create_assessment(
            assessment_type=AssessmentType.SNAP_IV,
            patient_id="test_patient",
            responses=responses
        )
        
        assert isinstance(assessment, SNAPIV_Assessment)
        
        subscores = assessment.calculate_subscores()
        assert subscores["inattention_average"] == 3.0
        assert subscores["hyperactivity_average"] == 0.0
        assert subscores["meets_inattention_criteria"] is True
        assert subscores["meets_hyperactivity_criteria"] is False


class TestAssessmentService:
    """Test assessment service functionality."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_create_assessment(self):
        """Test creating an assessment."""
        responses = [
            AssessmentResponse(question_id=f"phq9_{i}", value=2)
            for i in range(1, 10)
        ]
        
        assessment = AssessmentService.create_assessment(
            assessment_type=AssessmentType.PHQ9,
            patient_id="test_patient",
            responses=responses,
            administered_by="test_clinician"
        )
        
        assert assessment.patient_id == "test_patient"
        assert assessment.administered_by == "test_clinician"
        assert assessment.total_score == 18
        assert assessment.severity == SeverityLevel.MODERATELY_SEVERE
        assert len(assessment.responses) == 9
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_analyze_assessment_trends(self):
        """Test analyzing assessment trends."""
        # Create assessments with improving scores
        assessments = []
        base_date = datetime.utcnow() - timedelta(days=90)
        
        scores = [18, 15, 12, 9, 6]  # Improving trend
        for i, score in enumerate(scores):
            responses = [
                AssessmentResponse(
                    question_id=f"phq9_{j}",
                    value=score // 9 + (1 if j <= score % 9 else 0)
                )
                for j in range(1, 10)
            ]
            
            assessment = PHQ9Assessment(
                patient_id="test_patient",
                administered_at=base_date + timedelta(days=i * 20),
                responses=responses,
                total_score=score,
                severity=PHQ9Assessment.calculate_severity(score)
            )
            assessments.append(assessment)
        
        trend_analysis = AssessmentService.analyze_assessment_trends(assessments)
        
        assert trend_analysis["trend"] == "improving"
        assert trend_analysis["assessments_count"] == 5
        assert trend_analysis["first_score"] == 18
        assert trend_analysis["latest_score"] == 6
        assert len(trend_analysis["significant_changes"]) > 0
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_recommended_assessments(self):
        """Test getting recommended assessments."""
        # Adult with depression and anxiety
        recommendations = AssessmentService.get_recommended_assessments(
            patient_age=35,
            presenting_concerns=["depression", "anxiety", "sleep"]
        )
        
        assert AssessmentType.PHQ9 in recommendations
        assert AssessmentType.GAD7 in recommendations
        assert AssessmentType.ISI in recommendations
        
        # Child with ADHD concerns
        recommendations = AssessmentService.get_recommended_assessments(
            patient_age=10,
            presenting_concerns=["attention", "hyperactivity"]
        )
        
        assert AssessmentType.SNAP_IV in recommendations
        assert AssessmentType.SDQ in recommendations


class TestMentalHealthScreeningService:
    """Test mental health screening service."""
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_screen_for_conditions(self):
        """Test screening for mental health conditions."""
        # Create PHQ-9 with moderate depression
        phq9_responses = [
            AssessmentResponse(question_id=f"phq9_{i}", value=2)
            for i in range(1, 10)
        ]
        
        phq9 = AssessmentService.create_assessment(
            assessment_type=AssessmentType.PHQ9,
            patient_id="test_patient",
            responses=phq9_responses
        )
        
        conditions = MentalHealthScreeningService.screen_for_conditions([phq9])
        
        assert len(conditions) > 0
        assert conditions[0]["condition"] == "Major Depressive Disorder"
        assert "recommendations" in conditions[0]
        assert len(conditions[0]["icd_codes"]) > 0
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_generate_clinical_alerts(self):
        """Test generating clinical alerts."""
        # Create PHQ-9 with suicidal ideation
        responses = [
            AssessmentResponse(question_id=f"phq9_{i}", value=0)
            for i in range(1, 9)
        ]
        responses.append(
            AssessmentResponse(question_id="phq9_9", value=2)
        )
        
        assessment = AssessmentService.create_assessment(
            assessment_type=AssessmentType.PHQ9,
            patient_id="test_patient",
            responses=responses
        )
        
        alerts = MentalHealthScreeningService.generate_clinical_alerts(
            [assessment],
            patient_risk_factors=["previous_attempt", "substance_abuse"]
        )
        
        assert len(alerts) > 0
        assert any(alert.alert_type == "suicide_risk" for alert in alerts)
        
        suicide_alert = next(a for a in alerts if a.alert_type == "suicide_risk")
        assert suicide_alert.requires_immediate_action is True
        assert len(suicide_alert.actions) > 0
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_calculate_risk_score(self):
        """Test calculating mental health risk score."""
        # Create assessments
        assessments = [
            MentalHealthAssessment(
                patient_id="test_patient",
                assessment_type=AssessmentType.PHQ9,
                responses=[],
                total_score=15,
                severity=SeverityLevel.MODERATELY_SEVERE
            ),
            MentalHealthAssessment(
                patient_id="test_patient",
                assessment_type=AssessmentType.GAD7,
                responses=[],
                total_score=12,
                severity=SeverityLevel.MODERATE
            )
        ]
        
        risk_factors = ["family_history_depression", "chronic_medical_condition", "social_isolation"]
        protective_factors = ["strong_social_support", "engaged_in_treatment"]
        
        risk_score = MentalHealthScreeningService.calculate_risk_score(
            assessments,
            risk_factors,
            protective_factors
        )
        
        assert "total_score" in risk_score
        assert "risk_level" in risk_score
        assert "recommendations" in risk_score
        assert risk_score["risk_level"] in ["minimal", "low", "moderate", "high"]
    
    @pytest.mark.unit
    @pytest.mark.medical
    def test_generate_treatment_plan(self):
        """Test generating treatment plan."""
        conditions = [
            {
                "condition": "Major Depressive Disorder",
                "probability": "high",
                "icd_codes": ["F32.9"],
                "severity": "moderate"
            }
        ]
        
        plan = MentalHealthScreeningService.generate_treatment_plan(
            conditions,
            patient_preferences={"prefers_medication": True}
        )
        
        assert "diagnoses" in plan
        assert "medications" in plan
        assert "psychotherapy" in plan
        assert "lifestyle_interventions" in plan
        assert "follow_up_schedule" in plan
        assert "monitoring_plan" in plan
        
        assert len(plan["diagnoses"]) == 1
        assert len(plan["medications"]) > 0
        assert len(plan["psychotherapy"]) > 0