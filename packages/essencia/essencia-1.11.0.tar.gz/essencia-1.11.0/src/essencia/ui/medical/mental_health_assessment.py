"""
Mental health assessment UI components for Flet.
"""
from datetime import datetime
from typing import Dict, List, Optional, Callable

import flet as ft

from essencia.models.mental_health import (
    AssessmentQuestion,
    AssessmentResponse,
    AssessmentType,
    MentalHealthAssessment,
    PHQ9Assessment,
    GAD7Assessment,
    SeverityLevel,
)
from essencia.ui.themes import ColorScheme


class AssessmentQuestionCard(ft.Card):
    """Card component for displaying an assessment question."""
    
    def __init__(
        self,
        question: AssessmentQuestion,
        question_number: int,
        total_questions: int,
        on_answer: Callable[[str, int], None],
        initial_value: Optional[int] = None,
        language: str = "pt",
        **kwargs
    ):
        self.question = question
        self.question_number = question_number
        self.total_questions = total_questions
        self.on_answer = on_answer
        self.initial_value = initial_value
        self.language = language
        self.selected_value = initial_value
        
        super().__init__(**kwargs)
        self._build()
    
    def _build(self):
        """Build the question card."""
        # Progress indicator
        progress = ft.ProgressBar(
            value=self.question_number / self.total_questions,
            height=4,
            color=ColorScheme.PRIMARY
        )
        
        # Question header
        header = ft.Row([
            ft.Container(
                content=ft.Text(
                    f"{self.question_number}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE
                ),
                bgcolor=ColorScheme.PRIMARY,
                width=40,
                height=40,
                border_radius=20,
                alignment=ft.alignment.center
            ),
            ft.Text(
                f"Pergunta {self.question_number} de {self.total_questions}",
                size=12,
                color=ft.colors.GREY_600
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Question text
        question_text = ft.Text(
            self.question.text_pt if self.language == "pt" else self.question.text,
            size=16,
            weight=ft.FontWeight.W_500
        )
        
        # Clinical note if present
        clinical_note = ft.Container()
        if self.question.clinical_note:
            clinical_note = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=ft.colors.AMBER_700),
                    ft.Text(
                        self.question.clinical_note,
                        size=11,
                        color=ft.colors.AMBER_900,
                        italic=True
                    )
                ]),
                bgcolor=ft.colors.AMBER_50,
                padding=8,
                border_radius=5,
                margin=ft.margin.only(top=10)
            )
        
        # Answer options
        self.option_group = ft.RadioGroup(
            value=str(self.initial_value) if self.initial_value is not None else None,
            on_change=self._handle_answer
        )
        
        options = []
        for option in self.question.options:
            label = option["label_pt"] if self.language == "pt" else option["label"]
            
            option_container = ft.Container(
                content=ft.Radio(
                    value=str(option["value"]),
                    label=label,
                    fill_color={
                        ft.MaterialState.DEFAULT: ft.colors.GREY_400,
                        ft.MaterialState.SELECTED: self._get_option_color(option["value"])
                    }
                ),
                padding=ft.padding.symmetric(vertical=5)
            )
            options.append(option_container)
        
        self.option_group.content = ft.Column(options)
        
        self.content = ft.Container(
            content=ft.Column([
                progress,
                header,
                ft.Divider(height=20),
                question_text,
                clinical_note,
                self.option_group
            ]),
            padding=20
        )
        
        self.elevation = 2
    
    def _handle_answer(self, e):
        """Handle answer selection."""
        self.selected_value = int(e.control.value)
        if self.on_answer:
            self.on_answer(self.question.question_id, self.selected_value)
    
    def _get_option_color(self, value: int) -> str:
        """Get color based on option value (severity)."""
        if value == 0:
            return ft.colors.GREEN_700
        elif value == 1:
            return ft.colors.YELLOW_700
        elif value == 2:
            return ft.colors.ORANGE_700
        else:
            return ft.colors.RED_700


class AssessmentWizard(ft.UserControl):
    """Wizard component for conducting mental health assessments."""
    
    def __init__(
        self,
        assessment_type: AssessmentType,
        patient_id: str,
        administered_by: Optional[str] = None,
        on_complete: Optional[Callable[[MentalHealthAssessment], None]] = None,
        language: str = "pt",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assessment_type = assessment_type
        self.patient_id = patient_id
        self.administered_by = administered_by
        self.on_complete = on_complete
        self.language = language
        
        self.questions = self._get_questions()
        self.responses = {}
        self.current_question = 0
    
    def _get_questions(self) -> List[AssessmentQuestion]:
        """Get questions for the assessment type."""
        if self.assessment_type == AssessmentType.PHQ9:
            return PHQ9Assessment.get_questions()
        elif self.assessment_type == AssessmentType.GAD7:
            return GAD7Assessment.get_questions()
        else:
            return []
    
    def build(self):
        """Build the assessment wizard."""
        if not self.questions:
            return ft.Container(
                content=ft.Text("Tipo de avaliação não suportado"),
                padding=20
            )
        
        # Navigation buttons
        self.prev_button = ft.OutlinedButton(
            "Anterior",
            icon=ft.icons.ARROW_BACK,
            on_click=self._prev_question,
            disabled=self.current_question == 0
        )
        
        self.next_button = ft.ElevatedButton(
            "Próxima" if self.current_question < len(self.questions) - 1 else "Finalizar",
            icon=ft.icons.ARROW_FORWARD if self.current_question < len(self.questions) - 1 else ft.icons.CHECK,
            on_click=self._next_question,
            disabled=True
        )
        
        navigation = ft.Row(
            [self.prev_button, self.next_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Question container
        self.question_container = ft.Container()
        self._update_question()
        
        # Title
        title_map = {
            AssessmentType.PHQ9: "Questionário de Saúde do Paciente (PHQ-9)",
            AssessmentType.GAD7: "Escala de Ansiedade Generalizada (GAD-7)",
            AssessmentType.SNAP_IV: "Escala SNAP-IV para TDAH"
        }
        
        title = ft.Container(
            content=ft.Column([
                ft.Text(
                    title_map.get(self.assessment_type, "Avaliação de Saúde Mental"),
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Nas últimas 2 semanas, com que frequência você foi incomodado por:",
                    size=14,
                    color=ft.colors.GREY_700
                )
            ]),
            padding=ft.padding.only(bottom=20)
        )
        
        return ft.Column([
            title,
            self.question_container,
            navigation
        ])
    
    def _update_question(self):
        """Update the current question display."""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            self.question_container.content = AssessmentQuestionCard(
                question=question,
                question_number=self.current_question + 1,
                total_questions=len(self.questions),
                on_answer=self._handle_answer,
                initial_value=self.responses.get(question.question_id),
                language=self.language
            )
            
            # Update navigation buttons
            self.prev_button.disabled = self.current_question == 0
            self.next_button.disabled = question.question_id not in self.responses
            self.next_button.text = "Próxima" if self.current_question < len(self.questions) - 1 else "Finalizar"
            self.next_button.icon = ft.icons.ARROW_FORWARD if self.current_question < len(self.questions) - 1 else ft.icons.CHECK
            
            if self.update:
                self.update()
    
    def _handle_answer(self, question_id: str, value: int):
        """Handle answer to a question."""
        self.responses[question_id] = value
        self.next_button.disabled = False
        if self.update:
            self.update()
    
    def _prev_question(self, e):
        """Go to previous question."""
        if self.current_question > 0:
            self.current_question -= 1
            self._update_question()
    
    def _next_question(self, e):
        """Go to next question or complete assessment."""
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self._update_question()
        else:
            self._complete_assessment()
    
    def _complete_assessment(self):
        """Complete the assessment and calculate results."""
        from essencia.models.mental_health import AssessmentService
        
        # Create assessment responses
        responses = [
            AssessmentResponse(
                question_id=q_id,
                value=value
            )
            for q_id, value in self.responses.items()
        ]
        
        # Create assessment
        assessment = AssessmentService.create_assessment(
            assessment_type=self.assessment_type,
            patient_id=self.patient_id,
            responses=responses,
            administered_by=self.administered_by
        )
        
        if self.on_complete:
            self.on_complete(assessment)


class AssessmentResultDisplay(ft.UserControl):
    """Component for displaying assessment results."""
    
    def __init__(
        self,
        assessment: MentalHealthAssessment,
        show_interpretation: bool = True,
        show_recommendations: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assessment = assessment
        self.show_interpretation = show_interpretation
        self.show_recommendations = show_recommendations
    
    def build(self):
        """Build the results display."""
        # Score display
        score_color = self._get_severity_color()
        
        score_display = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Pontuação Total",
                    size=14,
                    color=ft.colors.GREY_700
                ),
                ft.Text(
                    str(self.assessment.total_score),
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=score_color
                ),
                ft.Container(
                    content=ft.Text(
                        self._get_severity_text(),
                        size=14,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor=score_color,
                    padding=ft.padding.symmetric(horizontal=15, vertical=5),
                    border_radius=15
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.colors.GREY_50,
            border_radius=10,
            alignment=ft.alignment.center
        )
        
        # Risk indicators
        risk_indicators = ft.Container()
        if self.assessment.requires_immediate_attention:
            risk_indicators = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.WARNING, color=ft.colors.RED_700, size=24),
                    ft.Column([
                        ft.Text(
                            "Atenção Imediata Necessária",
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.RED_700
                        ),
                        ft.Text(
                            "Este paciente requer avaliação clínica imediata",
                            size=12,
                            color=ft.colors.RED_900
                        )
                    ])
                ]),
                bgcolor=ft.colors.RED_50,
                padding=15,
                border_radius=5,
                margin=ft.margin.only(top=20)
            )
        
        # Clinical interpretation
        interpretation_section = ft.Container()
        if self.show_interpretation and hasattr(self.assessment, 'get_clinical_interpretation'):
            interpretation = self.assessment.get_clinical_interpretation()
            
            interpretation_items = []
            for rec in interpretation.get("treatment_recommendations", []):
                interpretation_items.append(
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color=ft.colors.GREEN_700),
                        ft.Text(rec, size=13)
                    ])
                )
            
            if interpretation_items:
                interpretation_section = ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Interpretação Clínica",
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Column(interpretation_items, spacing=5)
                    ]),
                    padding=ft.padding.only(top=20)
                )
        
        # Recommendations
        recommendations_section = ft.Container()
        if self.show_recommendations and self.assessment.recommendations:
            rec_items = []
            for rec in self.assessment.recommendations:
                rec_items.append(
                    ft.Row([
                        ft.Icon(ft.icons.ARROW_FORWARD, size=16, color=ft.colors.BLUE_700),
                        ft.Text(rec, size=13)
                    ])
                )
            
            recommendations_section = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Recomendações",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Column(rec_items, spacing=5)
                ]),
                padding=ft.padding.only(top=20)
            )
        
        # Metadata
        metadata = ft.Container(
            content=ft.Row([
                ft.Text(
                    f"Avaliado em: {self.assessment.administered_at.strftime('%d/%m/%Y %H:%M')}",
                    size=11,
                    color=ft.colors.GREY_600
                ),
                ft.Text(
                    f"Por: {self.assessment.administered_by or 'Sistema'}",
                    size=11,
                    color=ft.colors.GREY_600
                ) if self.assessment.administered_by else ft.Container()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(top=20)
        )
        
        return ft.Column([
            score_display,
            risk_indicators,
            interpretation_section,
            recommendations_section,
            metadata
        ])
    
    def _get_severity_color(self) -> str:
        """Get color based on severity level."""
        severity_colors = {
            SeverityLevel.NONE: ft.colors.GREY_700,
            SeverityLevel.MINIMAL: ft.colors.GREEN_700,
            SeverityLevel.MILD: ft.colors.YELLOW_700,
            SeverityLevel.MODERATE: ft.colors.ORANGE_700,
            SeverityLevel.MODERATELY_SEVERE: ft.colors.DEEP_ORANGE_700,
            SeverityLevel.SEVERE: ft.colors.RED_700,
            SeverityLevel.VERY_SEVERE: ft.colors.RED_900,
        }
        return severity_colors.get(self.assessment.severity, ft.colors.GREY_700)
    
    def _get_severity_text(self) -> str:
        """Get localized severity text."""
        severity_text = {
            SeverityLevel.NONE: "Sem Sintomas",
            SeverityLevel.MINIMAL: "Mínimo",
            SeverityLevel.MILD: "Leve",
            SeverityLevel.MODERATE: "Moderado",
            SeverityLevel.MODERATELY_SEVERE: "Moderadamente Grave",
            SeverityLevel.SEVERE: "Grave",
            SeverityLevel.VERY_SEVERE: "Muito Grave",
        }
        return severity_text.get(self.assessment.severity, str(self.assessment.severity))


class AssessmentHistoryChart(ft.UserControl):
    """Chart component for displaying assessment history."""
    
    def __init__(
        self,
        assessments: List[MentalHealthAssessment],
        assessment_type: AssessmentType,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.assessments = sorted(assessments, key=lambda x: x.administered_at)
        self.assessment_type = assessment_type
    
    def build(self):
        """Build the history chart."""
        if not self.assessments:
            return ft.Container(
                content=ft.Text(
                    "Sem histórico de avaliações",
                    color=ft.colors.GREY_600
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        
        # Get max score for the assessment type
        max_scores = {
            AssessmentType.PHQ9: 27,
            AssessmentType.GAD7: 21,
            AssessmentType.SNAP_IV: 54
        }
        max_score = max_scores.get(self.assessment_type, 100)
        
        # Create score timeline
        timeline_items = []
        
        for i, assessment in enumerate(self.assessments):
            # Score bar
            score_percentage = assessment.total_score / max_score
            severity_color = self._get_severity_color(assessment.severity)
            
            score_bar = ft.Container(
                bgcolor=severity_color,
                width=max(50, 300 * score_percentage),
                height=30,
                border_radius=5
            )
            
            # Score info
            score_info = ft.Row([
                score_bar,
                ft.Text(
                    f"{assessment.total_score}",
                    weight=ft.FontWeight.BOLD,
                    color=severity_color
                )
            ], spacing=10)
            
            # Date
            date_text = ft.Text(
                assessment.administered_at.strftime("%d/%m/%Y"),
                size=12,
                color=ft.colors.GREY_600
            )
            
            # Trend indicator
            trend_indicator = ft.Container()
            if i > 0:
                prev_score = self.assessments[i-1].total_score
                if assessment.total_score > prev_score:
                    trend_indicator = ft.Icon(
                        ft.icons.TRENDING_UP,
                        color=ft.colors.RED_700,
                        size=16
                    )
                elif assessment.total_score < prev_score:
                    trend_indicator = ft.Icon(
                        ft.icons.TRENDING_DOWN,
                        color=ft.colors.GREEN_700,
                        size=16
                    )
            
            timeline_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([date_text, trend_indicator]),
                        score_info
                    ], spacing=5),
                    padding=ft.padding.only(bottom=15)
                )
            )
        
        # Summary statistics
        scores = [a.total_score for a in self.assessments]
        avg_score = sum(scores) / len(scores)
        
        summary = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Média", size=12, color=ft.colors.GREY_600),
                    ft.Text(f"{avg_score:.1f}", weight=ft.FontWeight.BOLD)
                ]),
                ft.Column([
                    ft.Text("Mínimo", size=12, color=ft.colors.GREY_600),
                    ft.Text(str(min(scores)), weight=ft.FontWeight.BOLD)
                ]),
                ft.Column([
                    ft.Text("Máximo", size=12, color=ft.colors.GREY_600),
                    ft.Text(str(max(scores)), weight=ft.FontWeight.BOLD)
                ]),
                ft.Column([
                    ft.Text("Avaliações", size=12, color=ft.colors.GREY_600),
                    ft.Text(str(len(scores)), weight=ft.FontWeight.BOLD)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.colors.GREY_100,
            padding=15,
            border_radius=5
        )
        
        return ft.Column([
            ft.Text(
                f"Histórico - {self.assessment_type.value.upper()}",
                size=16,
                weight=ft.FontWeight.BOLD
            ),
            summary,
            ft.Container(height=20),
            ft.Column(timeline_items)
        ])
    
    def _get_severity_color(self, severity: SeverityLevel) -> str:
        """Get color based on severity level."""
        severity_colors = {
            SeverityLevel.NONE: ft.colors.GREY_700,
            SeverityLevel.MINIMAL: ft.colors.GREEN_700,
            SeverityLevel.MILD: ft.colors.YELLOW_700,
            SeverityLevel.MODERATE: ft.colors.ORANGE_700,
            SeverityLevel.MODERATELY_SEVERE: ft.colors.DEEP_ORANGE_700,
            SeverityLevel.SEVERE: ft.colors.RED_700,
            SeverityLevel.VERY_SEVERE: ft.colors.RED_900,
        }
        return severity_colors.get(severity, ft.colors.GREY_700)