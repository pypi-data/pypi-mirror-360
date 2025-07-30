"""
Mental health assessment models and tools.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from pydantic import Field, validator

from essencia.fields import EncryptedStr, EncryptedInt
from essencia.models.base import BaseModel, MongoModel


class AssessmentType(str, Enum):
    """Types of mental health assessments."""
    
    PHQ9 = "phq9"  # Patient Health Questionnaire-9
    GAD7 = "gad7"  # Generalized Anxiety Disorder-7
    MDQ = "mdq"  # Mood Disorder Questionnaire
    ASRS = "asrs"  # Adult ADHD Self-Report Scale
    PCL5 = "pcl5"  # PTSD Checklist for DSM-5
    AUDIT = "audit"  # Alcohol Use Disorders Identification Test
    DAST10 = "dast10"  # Drug Abuse Screening Test
    ISI = "isi"  # Insomnia Severity Index
    EPDS = "epds"  # Edinburgh Postnatal Depression Scale
    YMRS = "ymrs"  # Young Mania Rating Scale
    PANSS = "panss"  # Positive and Negative Syndrome Scale
    BPRS = "bprs"  # Brief Psychiatric Rating Scale
    HAM_D = "ham_d"  # Hamilton Depression Rating Scale
    HAM_A = "ham_a"  # Hamilton Anxiety Rating Scale
    CAGE = "cage"  # CAGE Questionnaire (alcoholism)
    MINI = "mini"  # Mini International Neuropsychiatric Interview
    # Child/Adolescent scales
    SDQ = "sdq"  # Strengths and Difficulties Questionnaire
    SCARED = "scared"  # Screen for Child Anxiety Related Disorders
    CDI = "cdi"  # Children's Depression Inventory
    SNAP_IV = "snap_iv"  # SNAP-IV ADHD Rating Scale
    CBCL = "cbcl"  # Child Behavior Checklist


class SeverityLevel(str, Enum):
    """Severity levels for assessment results."""
    
    NONE = "none"
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    MODERATELY_SEVERE = "moderately_severe"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"


class AssessmentQuestion(BaseModel):
    """Individual question in an assessment."""
    
    question_id: str
    text: str
    text_pt: str  # Portuguese translation
    category: Optional[str] = None
    options: List[Dict[str, any]]  # value, label, label_pt
    required: bool = True
    clinical_note: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Response to an assessment question."""
    
    question_id: str
    value: int
    text_value: Optional[str] = None
    answered_at: datetime = Field(default_factory=datetime.utcnow)


class MentalHealthAssessment(MongoModel):
    """Base model for mental health assessments."""
    
    patient_id: str
    assessment_type: AssessmentType
    administered_by: Optional[str] = None
    administered_at: datetime = Field(default_factory=datetime.utcnow)
    
    responses: List[AssessmentResponse]
    total_score: EncryptedInt
    severity: SeverityLevel
    
    # Clinical interpretation
    clinical_notes: Optional[EncryptedStr] = None
    risk_factors: List[str] = Field(default_factory=list)
    protective_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Follow-up
    requires_immediate_attention: bool = False
    next_assessment_date: Optional[datetime] = None
    
    class Settings:
        collection_name = "mental_health_assessments"
        indexes = [
            ("patient_id", -1),
            ("assessment_type", 1),
            ("administered_at", -1),
            [("patient_id", 1), ("assessment_type", 1), ("administered_at", -1)],
        ]


class PHQ9Assessment(MentalHealthAssessment):
    """Patient Health Questionnaire-9 for depression screening."""
    
    assessment_type: AssessmentType = Field(AssessmentType.PHQ9, const=True)
    
    # PHQ-9 specific fields
    suicidal_ideation: bool = Field(False, description="Question 9 > 0")
    functional_impairment: Optional[str] = None
    
    @classmethod
    def get_questions(cls) -> List[AssessmentQuestion]:
        """Get PHQ-9 questions."""
        return [
            AssessmentQuestion(
                question_id="phq9_1",
                text="Little interest or pleasure in doing things",
                text_pt="Pouco interesse ou prazer em fazer as coisas",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_2",
                text="Feeling down, depressed, or hopeless",
                text_pt="Sentir-se para baixo, deprimido ou sem esperança",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_3",
                text="Trouble falling or staying asleep, or sleeping too much",
                text_pt="Dificuldade para adormecer ou permanecer dormindo, ou dormir demais",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_4",
                text="Feeling tired or having little energy",
                text_pt="Sentir-se cansado ou com pouca energia",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_5",
                text="Poor appetite or overeating",
                text_pt="Pouco apetite ou comer demais",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_6",
                text="Feeling bad about yourself or that you are a failure",
                text_pt="Sentir-se mal consigo mesmo ou achar que é um fracasso",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_7",
                text="Trouble concentrating on things",
                text_pt="Dificuldade para se concentrar nas coisas",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_8",
                text="Moving or speaking slowly or being fidgety/restless",
                text_pt="Mover-se ou falar lentamente ou estar inquieto/agitado",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ]
            ),
            AssessmentQuestion(
                question_id="phq9_9",
                text="Thoughts that you would be better off dead or of hurting yourself",
                text_pt="Pensar que seria melhor estar morto ou em se machucar",
                options=[
                    {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
                    {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
                    {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
                    {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
                ],
                clinical_note="Positive response requires immediate clinical attention"
            )
        ]
    
    @staticmethod
    def calculate_severity(total_score: int) -> SeverityLevel:
        """Calculate PHQ-9 severity level."""
        if total_score <= 4:
            return SeverityLevel.MINIMAL
        elif total_score <= 9:
            return SeverityLevel.MILD
        elif total_score <= 14:
            return SeverityLevel.MODERATE
        elif total_score <= 19:
            return SeverityLevel.MODERATELY_SEVERE
        else:
            return SeverityLevel.SEVERE
    
    def get_clinical_interpretation(self) -> Dict[str, any]:
        """Get clinical interpretation of PHQ-9 results."""
        interpretation = {
            "severity": self.severity,
            "total_score": self.total_score,
            "suicidal_ideation": self.suicidal_ideation,
            "treatment_recommendations": []
        }
        
        if self.severity == SeverityLevel.MINIMAL:
            interpretation["treatment_recommendations"].append("No treatment needed")
            interpretation["follow_up"] = "Reassess in 1 year or if symptoms worsen"
        elif self.severity == SeverityLevel.MILD:
            interpretation["treatment_recommendations"].append("Watchful waiting")
            interpretation["treatment_recommendations"].append("Repeat PHQ-9 at follow-up")
            interpretation["follow_up"] = "Reassess in 4-6 weeks"
        elif self.severity == SeverityLevel.MODERATE:
            interpretation["treatment_recommendations"].append("Treatment plan (counseling, medication)")
            interpretation["treatment_recommendations"].append("Consider referral to mental health specialist")
            interpretation["follow_up"] = "Reassess in 2-4 weeks"
        elif self.severity in [SeverityLevel.MODERATELY_SEVERE, SeverityLevel.SEVERE]:
            interpretation["treatment_recommendations"].append("Active treatment with medication and/or psychotherapy")
            interpretation["treatment_recommendations"].append("Referral to mental health specialist")
            interpretation["follow_up"] = "Reassess in 1-2 weeks"
        
        if self.suicidal_ideation:
            interpretation["immediate_action"] = True
            interpretation["safety_plan_needed"] = True
            interpretation["treatment_recommendations"].insert(0, "Immediate safety assessment required")
        
        return interpretation


class GAD7Assessment(MentalHealthAssessment):
    """Generalized Anxiety Disorder-7 scale."""
    
    assessment_type: AssessmentType = Field(AssessmentType.GAD7, const=True)
    
    @classmethod
    def get_questions(cls) -> List[AssessmentQuestion]:
        """Get GAD-7 questions."""
        options = [
            {"value": 0, "label": "Not at all", "label_pt": "Nenhuma vez"},
            {"value": 1, "label": "Several days", "label_pt": "Vários dias"},
            {"value": 2, "label": "More than half the days", "label_pt": "Mais da metade dos dias"},
            {"value": 3, "label": "Nearly every day", "label_pt": "Quase todos os dias"}
        ]
        
        return [
            AssessmentQuestion(
                question_id="gad7_1",
                text="Feeling nervous, anxious, or on edge",
                text_pt="Sentir-se nervoso, ansioso ou no limite",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_2",
                text="Not being able to stop or control worrying",
                text_pt="Não conseguir parar ou controlar a preocupação",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_3",
                text="Worrying too much about different things",
                text_pt="Preocupar-se demais com diferentes coisas",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_4",
                text="Trouble relaxing",
                text_pt="Dificuldade para relaxar",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_5",
                text="Being so restless that it's hard to sit still",
                text_pt="Estar tão inquieto que é difícil ficar parado",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_6",
                text="Becoming easily annoyed or irritable",
                text_pt="Ficar facilmente aborrecido ou irritado",
                options=options
            ),
            AssessmentQuestion(
                question_id="gad7_7",
                text="Feeling afraid as if something awful might happen",
                text_pt="Sentir medo como se algo terrível pudesse acontecer",
                options=options
            )
        ]
    
    @staticmethod
    def calculate_severity(total_score: int) -> SeverityLevel:
        """Calculate GAD-7 severity level."""
        if total_score <= 4:
            return SeverityLevel.MINIMAL
        elif total_score <= 9:
            return SeverityLevel.MILD
        elif total_score <= 14:
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.SEVERE


class SNAPIV_Assessment(MentalHealthAssessment):
    """SNAP-IV ADHD Rating Scale for children/adolescents."""
    
    assessment_type: AssessmentType = Field(AssessmentType.SNAP_IV, const=True)
    
    # SNAP-IV specific scores
    inattention_score: EncryptedInt
    hyperactivity_score: EncryptedInt
    oppositional_score: Optional[EncryptedInt] = None
    
    @classmethod
    def get_questions(cls) -> List[AssessmentQuestion]:
        """Get SNAP-IV questions."""
        options = [
            {"value": 0, "label": "Not at all", "label_pt": "Nem um pouco"},
            {"value": 1, "label": "Just a little", "label_pt": "Só um pouco"},
            {"value": 2, "label": "Quite a bit", "label_pt": "Bastante"},
            {"value": 3, "label": "Very much", "label_pt": "Demais"}
        ]
        
        questions = []
        
        # Inattention items (1-9)
        inattention_items = [
            ("Often fails to give close attention to details", 
             "Frequentemente não presta atenção em detalhes"),
            ("Often has difficulty sustaining attention", 
             "Frequentemente tem dificuldade em manter atenção"),
            ("Often does not seem to listen when spoken to directly", 
             "Frequentemente parece não escutar quando falam diretamente"),
            ("Often does not follow through on instructions", 
             "Frequentemente não segue instruções completamente"),
            ("Often has difficulty organizing tasks", 
             "Frequentemente tem dificuldade para organizar tarefas"),
            ("Often avoids tasks requiring sustained mental effort", 
             "Frequentemente evita tarefas que exigem esforço mental"),
            ("Often loses things necessary for tasks", 
             "Frequentemente perde coisas necessárias para tarefas"),
            ("Often easily distracted by extraneous stimuli", 
             "Frequentemente se distrai facilmente"),
            ("Often forgetful in daily activities", 
             "Frequentemente é esquecido nas atividades diárias")
        ]
        
        for i, (text_en, text_pt) in enumerate(inattention_items, 1):
            questions.append(AssessmentQuestion(
                question_id=f"snap_inattention_{i}",
                text=text_en,
                text_pt=text_pt,
                category="inattention",
                options=options
            ))
        
        # Hyperactivity/Impulsivity items (10-18)
        hyperactivity_items = [
            ("Often fidgets with hands/feet or squirms", 
             "Frequentemente mexe mãos/pés ou se contorce"),
            ("Often leaves seat when remaining seated is expected", 
             "Frequentemente sai do lugar quando deveria ficar sentado"),
            ("Often runs about or climbs excessively", 
             "Frequentemente corre ou sobe nas coisas excessivamente"),
            ("Often has difficulty playing quietly", 
             "Frequentemente tem dificuldade para brincar quieto"),
            ("Often 'on the go' or acts as if 'driven by a motor'", 
             "Frequentemente 'a mil' ou 'ligado na tomada'"),
            ("Often talks excessively", 
             "Frequentemente fala demais"),
            ("Often blurts out answers before questions completed", 
             "Frequentemente responde antes da pergunta terminar"),
            ("Often has difficulty awaiting turn", 
             "Frequentemente tem dificuldade para esperar sua vez"),
            ("Often interrupts or intrudes on others", 
             "Frequentemente interrompe ou se intromete")
        ]
        
        for i, (text_en, text_pt) in enumerate(hyperactivity_items, 1):
            questions.append(AssessmentQuestion(
                question_id=f"snap_hyperactivity_{i}",
                text=text_en,
                text_pt=text_pt,
                category="hyperactivity",
                options=options
            ))
        
        return questions
    
    def calculate_subscores(self) -> Dict[str, float]:
        """Calculate SNAP-IV subscale scores."""
        inattention_responses = [r for r in self.responses if "inattention" in r.question_id]
        hyperactivity_responses = [r for r in self.responses if "hyperactivity" in r.question_id]
        
        inattention_avg = sum(r.value for r in inattention_responses) / len(inattention_responses)
        hyperactivity_avg = sum(r.value for r in hyperactivity_responses) / len(hyperactivity_responses)
        
        return {
            "inattention_average": round(inattention_avg, 2),
            "hyperactivity_average": round(hyperactivity_avg, 2),
            "meets_inattention_criteria": inattention_avg >= 2.0,
            "meets_hyperactivity_criteria": hyperactivity_avg >= 2.0
        }


class AssessmentService:
    """Service for mental health assessments."""
    
    ASSESSMENT_REGISTRY = {
        AssessmentType.PHQ9: PHQ9Assessment,
        AssessmentType.GAD7: GAD7Assessment,
        AssessmentType.SNAP_IV: SNAPIV_Assessment,
    }
    
    @classmethod
    def get_assessment_class(cls, assessment_type: AssessmentType):
        """Get assessment class by type."""
        return cls.ASSESSMENT_REGISTRY.get(assessment_type, MentalHealthAssessment)
    
    @classmethod
    def create_assessment(
        cls,
        assessment_type: AssessmentType,
        patient_id: str,
        responses: List[AssessmentResponse],
        administered_by: Optional[str] = None
    ) -> MentalHealthAssessment:
        """Create a new assessment with automatic scoring."""
        assessment_class = cls.get_assessment_class(assessment_type)
        
        # Calculate total score
        total_score = sum(r.value for r in responses)
        
        # Get severity based on assessment type
        if hasattr(assessment_class, 'calculate_severity'):
            severity = assessment_class.calculate_severity(total_score)
        else:
            severity = SeverityLevel.NONE
        
        # Create assessment
        assessment = assessment_class(
            patient_id=patient_id,
            administered_by=administered_by,
            responses=responses,
            total_score=total_score,
            severity=severity
        )
        
        # Check for immediate attention flags
        if assessment_type == AssessmentType.PHQ9:
            # Check suicidal ideation (question 9)
            q9_response = next((r for r in responses if r.question_id == "phq9_9"), None)
            if q9_response and q9_response.value > 0:
                assessment.suicidal_ideation = True
                assessment.requires_immediate_attention = True
        
        return assessment
    
    @staticmethod
    async def get_assessment_history(
        patient_id: str,
        assessment_type: Optional[AssessmentType] = None,
        limit: int = 10
    ) -> List[MentalHealthAssessment]:
        """Get assessment history for a patient."""
        query = {"patient_id": patient_id}
        if assessment_type:
            query["assessment_type"] = assessment_type
        
        assessments = await MentalHealthAssessment.find_many(
            query,
            sort=[("administered_at", -1)],
            limit=limit
        )
        
        return assessments
    
    @staticmethod
    def analyze_assessment_trends(
        assessments: List[MentalHealthAssessment]
    ) -> Dict[str, any]:
        """Analyze trends in assessment scores over time."""
        if not assessments:
            return {"trend": "no_data", "assessments_count": 0}
        
        # Sort by date
        sorted_assessments = sorted(assessments, key=lambda x: x.administered_at)
        
        scores = [a.total_score for a in sorted_assessments]
        dates = [a.administered_at for a in sorted_assessments]
        
        # Calculate trend
        if len(scores) < 2:
            trend = "insufficient_data"
        else:
            # Simple linear trend
            first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            
            if second_half_avg < first_half_avg * 0.8:
                trend = "improving"
            elif second_half_avg > first_half_avg * 1.2:
                trend = "worsening"
            else:
                trend = "stable"
        
        # Find significant changes
        significant_changes = []
        for i in range(1, len(sorted_assessments)):
            prev = sorted_assessments[i-1]
            curr = sorted_assessments[i]
            
            # Check for severity level change
            if prev.severity != curr.severity:
                significant_changes.append({
                    "date": curr.administered_at,
                    "previous_severity": prev.severity,
                    "new_severity": curr.severity,
                    "score_change": curr.total_score - prev.total_score
                })
        
        return {
            "trend": trend,
            "assessments_count": len(assessments),
            "first_score": scores[0],
            "latest_score": scores[-1],
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "significant_changes": significant_changes,
            "date_range": {
                "start": dates[0],
                "end": dates[-1]
            }
        }
    
    @staticmethod
    def get_recommended_assessments(
        patient_age: int,
        presenting_concerns: List[str]
    ) -> List[AssessmentType]:
        """Get recommended assessments based on age and concerns."""
        recommendations = []
        
        # Age-based recommendations
        if patient_age < 18:
            # Child/Adolescent assessments
            if any(concern in ["adhd", "attention", "hyperactivity"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.SNAP_IV)
            
            if any(concern in ["anxiety", "worry", "fear"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.SCARED)
            
            if any(concern in ["depression", "mood", "sadness"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.CDI)
            
            # Always include SDQ for general screening
            recommendations.append(AssessmentType.SDQ)
        
        else:
            # Adult assessments
            if any(concern in ["depression", "mood", "sadness"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.PHQ9)
            
            if any(concern in ["anxiety", "worry", "panic"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.GAD7)
            
            if any(concern in ["adhd", "attention", "focus"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.ASRS)
            
            if any(concern in ["trauma", "ptsd"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.PCL5)
            
            if any(concern in ["alcohol", "drinking"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.AUDIT)
            
            if any(concern in ["sleep", "insomnia"] 
                   for concern in presenting_concerns):
                recommendations.append(AssessmentType.ISI)
        
        return list(set(recommendations))  # Remove duplicates