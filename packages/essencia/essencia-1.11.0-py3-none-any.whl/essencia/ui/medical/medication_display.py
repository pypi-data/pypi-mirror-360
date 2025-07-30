"""
Medication display components for Flet UI.
"""
from datetime import datetime, time
from typing import Dict, List, Optional

import flet as ft

from essencia.models.medication import (
    AdherenceStatus,
    Medication,
    MedicationAdherence,
    PrescriptionStatus,
)
from essencia.ui.themes import ColorScheme


class MedicationCard(ft.Card):
    """Card component for displaying a medication."""
    
    def __init__(
        self,
        medication: Medication,
        show_schedule: bool = True,
        on_take: Optional[callable] = None,
        on_skip: Optional[callable] = None,
        **kwargs
    ):
        self.medication = medication
        self.show_schedule = show_schedule
        self.on_take = on_take
        self.on_skip = on_skip
        
        super().__init__(**kwargs)
        self._build()
    
    def _build(self):
        """Build the card content."""
        # Status badge
        status_color = self._get_status_color()
        status_badge = ft.Container(
            content=ft.Text(
                self._get_status_text(),
                size=10,
                color=ft.colors.WHITE,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=status_color,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        )
        
        # Medication header
        header = ft.Row([
            ft.Icon(ft.icons.MEDICATION, color=ColorScheme.PRIMARY, size=24),
            ft.Column([
                ft.Text(
                    self.medication.name,
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    self.medication.strength,
                    size=12,
                    color=ft.colors.GREY_700
                )
            ], spacing=0),
            status_badge
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Dosage information
        dosage_info = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SCHEDULE, size=16, color=ft.colors.BLUE_700),
                    ft.Text(
                        f"{self.medication.dosage_amount} {self.medication.dosage_unit} - "
                        f"{self.medication.frequency_value}x ao dia",
                        size=12
                    )
                ]),
                ft.Row([
                    ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color=ft.colors.GREEN_700),
                    ft.Text(
                        f"Duração: {self.medication.duration_days} dias" 
                        if self.medication.duration_days 
                        else "Uso contínuo",
                        size=12
                    )
                ])
            ], spacing=5),
            padding=ft.padding.only(top=10)
        )
        
        # Schedule section
        schedule_section = ft.Container()
        if self.show_schedule and self.medication.is_active():
            daily_schedule = self.medication.get_daily_schedule()
            schedule_items = []
            
            for dose in daily_schedule:
                dose_time = dose["time"]
                schedule_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.ACCESS_TIME, size=14),
                            ft.Text(dose_time.strftime("%H:%M"), size=12),
                            ft.Text(dose["dosage"], size=12, color=ft.colors.GREY_600)
                        ]),
                        bgcolor=ft.colors.BLUE_50,
                        padding=5,
                        border_radius=5
                    )
                )
            
            schedule_section = ft.Container(
                content=ft.Column([
                    ft.Text("Horários:", size=12, weight=ft.FontWeight.BOLD),
                    ft.Row(schedule_items, wrap=True, spacing=5)
                ], spacing=5),
                padding=ft.padding.only(top=10)
            )
        
        # Special instructions
        instructions_section = ft.Container()
        if self.medication.special_instructions:
            instructions_section = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color=ft.colors.AMBER_700),
                    ft.Text(
                        self.medication.special_instructions,
                        size=11,
                        color=ft.colors.AMBER_900
                    )
                ]),
                bgcolor=ft.colors.AMBER_50,
                padding=8,
                border_radius=5,
                margin=ft.margin.only(top=10)
            )
        
        # Action buttons
        action_buttons = ft.Container()
        if self.on_take or self.on_skip:
            buttons = []
            if self.on_take:
                buttons.append(
                    ft.ElevatedButton(
                        "Tomar",
                        icon=ft.icons.CHECK,
                        on_click=lambda _: self.on_take(self.medication),
                        bgcolor=ft.colors.GREEN_700,
                        color=ft.colors.WHITE
                    )
                )
            if self.on_skip:
                buttons.append(
                    ft.OutlinedButton(
                        "Pular",
                        icon=ft.icons.CLOSE,
                        on_click=lambda _: self.on_skip(self.medication)
                    )
                )
            
            action_buttons = ft.Container(
                content=ft.Row(buttons, spacing=10),
                padding=ft.padding.only(top=10)
            )
        
        self.content = ft.Container(
            content=ft.Column([
                header,
                dosage_info,
                schedule_section,
                instructions_section,
                action_buttons
            ]),
            padding=15
        )
        
        self.elevation = 2
    
    def _get_status_color(self) -> str:
        """Get color based on prescription status."""
        status_colors = {
            PrescriptionStatus.ACTIVE: ft.colors.GREEN_700,
            PrescriptionStatus.COMPLETED: ft.colors.BLUE_700,
            PrescriptionStatus.DISCONTINUED: ft.colors.RED_700,
            PrescriptionStatus.ON_HOLD: ft.colors.ORANGE_700,
            PrescriptionStatus.EXPIRED: ft.colors.GREY_700,
        }
        return status_colors.get(self.medication.status, ft.colors.GREY_700)
    
    def _get_status_text(self) -> str:
        """Get localized status text."""
        status_text = {
            PrescriptionStatus.ACTIVE: "Ativo",
            PrescriptionStatus.COMPLETED: "Concluído",
            PrescriptionStatus.DISCONTINUED: "Descontinuado",
            PrescriptionStatus.ON_HOLD: "Pausado",
            PrescriptionStatus.EXPIRED: "Expirado",
        }
        return status_text.get(self.medication.status, self.medication.status)


class MedicationSchedule(ft.UserControl):
    """Component for displaying daily medication schedule."""
    
    def __init__(
        self,
        medications: List[Medication],
        date: Optional[datetime] = None,
        adherence_records: Optional[List[MedicationAdherence]] = None,
        on_take_medication: Optional[callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.medications = medications
        self.date = date or datetime.now()
        self.adherence_records = adherence_records or []
        self.on_take_medication = on_take_medication
    
    def build(self):
        """Build the schedule display."""
        from essencia.models.medication import MedicationService
        
        # Generate schedule for the day
        schedule = MedicationService.generate_medication_schedule(
            self.medications,
            self.date
        )
        
        if not schedule:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.MEDICATION, size=48, color=ft.colors.GREY_400),
                    ft.Text(
                        "Nenhum medicamento agendado para hoje",
                        color=ft.colors.GREY_600
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                alignment=ft.alignment.center
            )
        
        # Group by time
        time_groups = {}
        for item in schedule:
            time_str = item["scheduled_time"].strftime("%H:%M")
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(item)
        
        # Build timeline
        timeline_items = []
        
        for time_str, meds in sorted(time_groups.items()):
            # Check adherence status for this time
            scheduled_time = datetime.strptime(
                f"{self.date.date()} {time_str}",
                "%Y-%m-%d %H:%M"
            )
            
            is_past = scheduled_time < datetime.now()
            adherence_status = self._get_adherence_status(meds, scheduled_time)
            
            # Time header
            time_color = ft.colors.GREEN_700
            if is_past and adherence_status == "missed":
                time_color = ft.colors.RED_700
            elif is_past and adherence_status == "taken":
                time_color = ft.colors.GREY_600
            
            time_header = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.icons.ACCESS_TIME,
                        color=time_color,
                        size=20
                    ),
                    ft.Text(
                        time_str,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=time_color
                    ),
                    ft.Container(
                        content=ft.Text(
                            self._get_adherence_text(adherence_status),
                            size=10,
                            color=ft.colors.WHITE
                        ),
                        bgcolor=time_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=10,
                        visible=is_past
                    )
                ]),
                padding=ft.padding.only(bottom=5)
            )
            
            # Medication items
            med_items = []
            for med_schedule in meds:
                med_item = ft.Container(
                    content=ft.Row([
                        ft.Checkbox(
                            value=adherence_status == "taken",
                            disabled=not is_past or adherence_status == "taken",
                            on_change=lambda e, ms=med_schedule: self._handle_take(e, ms)
                        ),
                        ft.Column([
                            ft.Text(
                                med_schedule["medication_name"],
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Text(
                                f"{med_schedule['strength']} - {med_schedule['dosage']}",
                                size=12,
                                color=ft.colors.GREY_600
                            )
                        ], spacing=0),
                        ft.IconButton(
                            icon=ft.icons.INFO_OUTLINE,
                            icon_size=20,
                            on_click=lambda _, ms=med_schedule: self._show_med_info(ms)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.colors.GREY_100 if is_past else ft.colors.BLUE_50,
                    padding=10,
                    border_radius=5
                )
                med_items.append(med_item)
            
            timeline_items.append(
                ft.Container(
                    content=ft.Column([
                        time_header,
                        ft.Column(med_items, spacing=5)
                    ]),
                    padding=ft.padding.only(left=20, bottom=20),
                    border=ft.border.only(
                        left=ft.BorderSide(2, ft.colors.GREY_300)
                    )
                )
            )
        
        return ft.Column([
            ft.Container(
                content=ft.Text(
                    f"Agenda de Medicamentos - {self.date.strftime('%d/%m/%Y')}",
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                padding=ft.padding.only(bottom=20)
            ),
            ft.Column(timeline_items)
        ])
    
    def _get_adherence_status(
        self,
        meds: List[Dict],
        scheduled_time: datetime
    ) -> str:
        """Get adherence status for medications at a specific time."""
        # This is simplified - would check actual adherence records
        if scheduled_time > datetime.now():
            return "future"
        
        # Check adherence records
        for record in self.adherence_records:
            if record.scheduled_datetime == scheduled_time:
                if record.status == AdherenceStatus.TAKEN:
                    return "taken"
                elif record.status == AdherenceStatus.MISSED:
                    return "missed"
        
        # If past and no record, assume missed
        if scheduled_time < datetime.now():
            return "missed"
        
        return "pending"
    
    def _get_adherence_text(self, status: str) -> str:
        """Get localized adherence status text."""
        texts = {
            "taken": "Tomado",
            "missed": "Não tomado",
            "pending": "Pendente",
            "future": "Agendado"
        }
        return texts.get(status, status)
    
    def _handle_take(self, e, med_schedule: Dict):
        """Handle taking medication."""
        if e.control.value and self.on_take_medication:
            self.on_take_medication(med_schedule)
    
    def _show_med_info(self, med_schedule: Dict):
        """Show medication information dialog."""
        # This would show a dialog with medication details
        pass


class MedicationAdherenceChart(ft.UserControl):
    """Chart component for medication adherence visualization."""
    
    def __init__(
        self,
        adherence_data: Dict[str, float],
        period_days: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.adherence_data = adherence_data
        self.period_days = period_days
    
    def build(self):
        """Build the adherence chart."""
        adherence_rate = self.adherence_data.get("adherence_rate", 0)
        doses_taken = self.adherence_data.get("doses_taken", 0)
        doses_scheduled = self.adherence_data.get("doses_scheduled", 0)
        
        # Color based on adherence rate
        if adherence_rate >= 80:
            color = ft.colors.GREEN_700
            status = "Excelente"
        elif adherence_rate >= 60:
            color = ft.colors.AMBER_700
            status = "Regular"
        else:
            color = ft.colors.RED_700
            status = "Baixa"
        
        # Circular progress indicator
        progress = ft.Stack([
            ft.ProgressRing(
                value=adherence_rate / 100,
                width=120,
                height=120,
                stroke_width=12,
                color=color
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{adherence_rate:.0f}%",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=color
                    ),
                    ft.Text(
                        status,
                        size=12,
                        color=color
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                width=120,
                height=120,
                alignment=ft.alignment.center
            )
        ])
        
        # Statistics
        stats = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_700, size=16),
                ft.Text(f"Doses tomadas: {doses_taken}", size=12)
            ]),
            ft.Row([
                ft.Icon(ft.icons.SCHEDULE, color=ft.colors.BLUE_700, size=16),
                ft.Text(f"Doses agendadas: {doses_scheduled}", size=12)
            ]),
            ft.Row([
                ft.Icon(ft.icons.CANCEL, color=ft.colors.RED_700, size=16),
                ft.Text(f"Doses perdidas: {doses_scheduled - doses_taken}", size=12)
            ])
        ], spacing=5)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Adesão ao Tratamento ({self.period_days} dias)",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Row([
                    progress,
                    ft.Container(width=20),
                    stats
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.colors.GREY_50,
            border_radius=10
        )