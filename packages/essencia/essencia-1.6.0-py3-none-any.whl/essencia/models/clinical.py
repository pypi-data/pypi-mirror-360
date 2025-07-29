"""
Clinical models for medical system.
"""

import datetime
from typing import Any, Optional, Annotated
from datetime import date

from pydantic import Field, BeforeValidator

from .bases import MongoModel, StrEnum
from .mixins import PatientRelatedMixin
from .. import fields as fd
from ..fields.base_fields import string_to_date


class Event(PatientRelatedMixin):
    """
    Represents an event related to a patient.

    Attributes:
        title (str): The title of the event.
        date (date): The date of the event.
        notes (Optional[str]): Additional notes about the event.
        creator (str): The creator of the event, default is 'doctor.admin'.
        age (Optional[float]): The age of the patient at the time of the event.
    """
    COLLECTION_NAME = 'event'
    title: str
    date: Annotated[Optional[date], BeforeValidator(string_to_date)] = Field(default=None)  # Allow None when calculating from age
    notes: Optional[str] = None
    creator: str = Field(default='doctor.admin')
    age: Optional[float] = None
    
    def model_post_init(self, __context: Any) -> None:
        """
        Initializes the event model and calculates the event date based on the patient's birthdate and age.
        
        Note: Date calculation from age only occurs if no date is already set, preserving user-selected dates.

        Args:
            __context (Any): The context in which the model is initialized.
        """
        super().model_post_init(__context)
        # Only calculate date from age if date is not already set
        # This preserves user-selected dates while still allowing age-based calculation when needed
        if self.age and not self.date:
            from .people import Patient
            patient = Patient.find_one({'key': self.patient_key})
            if patient and patient.bdate:
                self.date = patient.bdate + datetime.timedelta(days=self.age * 365)
        
        # If no date and no age, default to today
        if not self.date and not self.age:
            self.date = datetime.date.today()
    
    def __str__(self):
        """
        Returns the title of the event.

        Returns:
            str: The title of the event.
        """
        return self.title
    
    def __lt__(self, other):
        """
        Compares this event with another event based on the date.

        Args:
            other (Event): The other event to compare with.

        Returns:
            bool: True if this event's date is earlier than the other event's date, otherwise False.
        """
        return self.date < other.date


class VitalRecord(PatientRelatedMixin):
    """
    Represents a vital record for a patient.

    Attributes:
        weight (Optional[float]): The weight of the patient.
        height (Optional[float]): The height of the patient.
        sbp (Optional[int]): Systolic blood pressure.
        dbp (Optional[int]): Diastolic blood pressure.
        hr (Optional[int]): Heart rate.
        rr (Optional[int]): Respiratory rate.
        hip (Optional[float]): Hip measurement.
        waist (Optional[float]): Waist measurement.
        energy (Optional[Level]): Energy level of the patient.
        mood (Optional[Level]): Mood level of the patient.
        anxiety (Optional[Level]): Anxiety level of the patient.
        attention (Optional[Level]): Attention level of the patient.
    
    Properties:
        date: Returns the date portion of the created datetime field.
    """
    COLLECTION_NAME = 'body'
    
    # Physical measurements
    weight: Optional[float] = None
    height: Optional[float] = None
    sbp: Optional[int] = None
    dbp: Optional[int] = None
    hr: Optional[int] = None
    rr: Optional[int] = None
    hip: Optional[float] = None
    waist: Optional[float] = None
    
    # Default datetime field for tracking
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    
    @property
    def date(self):
        """
        Returns the date portion of the created datetime field.
        
        Returns:
            datetime.date: The date when this vital record was created.
        """
        return self.created.date() if hasattr(self.created, 'date') else self.created
    
    class Level(StrEnum):
        """
        Represents the levels of vital signs.

        Attributes:
            VH (str): Very high level.
            HI (str): High level.
            NR (str): Normal level.
            LO (str): Low level.
            VL (str): Very low level.
        """
        VH = 'muito alto'
        HI = 'alto'
        NR = 'normal'
        LO = 'baixo'
        VL = 'muito baixo'
        
    energy: Optional[Level] = None
    mood: Optional[Level] = None
    anxiety: Optional[Level] = None
    attention: Optional[Level] = None


class ExamResult(PatientRelatedMixin):
    """
    Represents an exam result for a patient.

    Attributes:
        title (str): The name/title of the exam/test (e.g., "RM do crânio").
        content (str): The detailed exam result content/report.
        date (date): The date the exam was performed.
        creator (str): The creator of the exam result record.
    """
    COLLECTION_NAME = 'exam_result'
    
    title: str
    content: str
    date: fd.DefaultDate = Field(default_factory=datetime.date.today)
    creator: str = Field(default='Doctor.admin')
    
    def __str__(self):
        """
        Returns the exam title.

        Returns:
            str: The exam title.
        """
        return self.title
    
    def __lt__(self, other):
        """
        Compares this exam result with another based on the date.

        Args:
            other (ExamResult): The other exam result to compare with.

        Returns:
            bool: True if this exam's date is earlier than the other exam's date, otherwise False.
        """
        return self.date < other.date


class PHQ9Assessment(PatientRelatedMixin):
    """
    PHQ-9 Depression Assessment Scale for systematic depression screening.
    
    The PHQ-9 is a validated instrument for assessing depression severity
    with 9 questions corresponding to DSM-5 criteria for major depression.
    
    Attributes:
        q1-q9: Responses to each PHQ-9 question (0-3 scale)
        total_score: Calculated total score (0-27)
        severity_level: Depression severity category based on score
        completed_by: Who completed the assessment (doctor/patient)
        notes: Additional clinical notes
    """
    COLLECTION_NAME = 'phq9_assessment'
    
    # PHQ-9 Questions (0-3 scale: 0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day)
    q1: int = Field(default=0)  # Little interest or pleasure in doing things
    q2: int = Field(default=0)  # Feeling down, depressed, or hopeless
    q3: int = Field(default=0)  # Trouble falling or staying asleep, or sleeping too much
    q4: int = Field(default=0)  # Feeling tired or having little energy
    q5: int = Field(default=0)  # Poor appetite or overeating
    q6: int = Field(default=0)  # Feeling bad about yourself
    q7: int = Field(default=0)  # Trouble concentrating
    q8: int = Field(default=0)  # Moving or speaking slowly or being fidgety/restless
    q9: int = Field(default=0)  # Thoughts that you would be better off dead
    
    completed_by: str = Field(default='doctor')  # 'doctor' or 'patient'
    notes: Optional[str] = None
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    
    @property
    def total_score(self) -> int:
        """Calculate total PHQ-9 score (sum of all responses)."""
        return self.q1 + self.q2 + self.q3 + self.q4 + self.q5 + self.q6 + self.q7 + self.q8 + self.q9
    
    @property
    def severity_level(self) -> str:
        """Determine depression severity based on total score."""
        score = self.total_score
        if score <= 4:
            return "Mínima"
        elif score <= 9:
            return "Leve"
        elif score <= 14:
            return "Moderada"
        elif score <= 19:
            return "Moderadamente Severa"
        else:
            return "Severa"
    
    @property 
    def risk_level(self) -> str:
        """Determine risk level for clinical alerts."""
        score = self.total_score
        if score >= 20:
            return "Alto"
        elif score >= 15:
            return "Moderado"
        elif score >= 10:
            return "Baixo"
        else:
            return "Mínimo"
    
    @property
    def interpretation(self) -> str:
        """Clinical interpretation of the assessment."""
        score = self.total_score
        if score <= 4:
            return "Sintomas mínimos de depressão. Monitoramento de rotina."
        elif score <= 9:
            return "Sintomas leves de depressão. Considerar acompanhamento."
        elif score <= 14:
            return "Sintomas moderados de depressão. Tratamento recomendado."
        elif score <= 19:
            return "Sintomas moderadamente severos. Tratamento ativo necessário."
        else:
            return "Sintomas severos de depressão. Intervenção imediata necessária."
    
    def __str__(self):
        return f"PHQ-9: {self.total_score} pontos ({self.severity_level})"
    
    def __lt__(self, other):
        return self.created < other.created