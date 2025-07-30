"""
Vital signs display components for Flet UI.
"""
from datetime import datetime
from typing import Dict, List, Optional

import flet as ft

from essencia.models.vital_signs import (
    BloodPressureCategory,
    HeartRateCategory,
    OxygenSaturationCategory,
    TemperatureCategory,
    VitalSignsSet,
)
from essencia.ui.themes import ColorScheme


class VitalSignCard(ft.Card):
    """Card component for displaying a single vital sign."""
    
    def __init__(
        self,
        title: str,
        value: str,
        unit: str,
        icon: ft.icons,
        color: str = None,
        category: Optional[str] = None,
        trend: Optional[str] = None,
        **kwargs
    ):
        self.title = title
        self.value = value
        self.unit = unit
        self.icon = icon
        self.color = color or ColorScheme.PRIMARY
        self.category = category
        self.trend = trend
        
        super().__init__(**kwargs)
        self._build()
    
    def _build(self):
        """Build the card content."""
        # Trend indicator
        trend_icon = None
        if self.trend == "increasing":
            trend_icon = ft.Icon(
                ft.icons.TRENDING_UP,
                color=ft.colors.RED if "pressure" in self.title.lower() else ft.colors.GREEN,
                size=16
            )
        elif self.trend == "decreasing":
            trend_icon = ft.Icon(
                ft.icons.TRENDING_DOWN,
                color=ft.colors.GREEN if "pressure" in self.title.lower() else ft.colors.RED,
                size=16
            )
        elif self.trend == "stable":
            trend_icon = ft.Icon(
                ft.icons.TRENDING_FLAT,
                color=ft.colors.BLUE,
                size=16
            )
        
        # Category badge
        category_badge = None
        if self.category:
            badge_color = self._get_category_color(self.category)
            category_badge = ft.Container(
                content=ft.Text(
                    self._format_category(self.category),
                    size=10,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=badge_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            )
        
        self.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(self.icon, color=self.color, size=24),
                    ft.Text(self.title, size=12, color=ft.colors.GREY_700),
                    trend_icon if trend_icon else ft.Container(),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(
                        self.value,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.color
                    ),
                    ft.Text(self.unit, size=14, color=ft.colors.GREY_600)
                ]),
                category_badge if category_badge else ft.Container()
            ], spacing=5),
            padding=15
        )
        
        self.elevation = 2
    
    def _get_category_color(self, category: str) -> str:
        """Get color based on category severity."""
        category_lower = category.lower()
        
        if any(word in category_lower for word in ["critical", "crisis", "severe"]):
            return ft.colors.RED_700
        elif any(word in category_lower for word in ["high", "stage2", "hyperpyrexia"]):
            return ft.colors.ORANGE_700
        elif any(word in category_lower for word in ["elevated", "stage1", "mild", "fever"]):
            return ft.colors.AMBER_700
        elif any(word in category_lower for word in ["normal"]):
            return ft.colors.GREEN_700
        else:
            return ft.colors.BLUE_700
    
    def _format_category(self, category: str) -> str:
        """Format category for display."""
        return category.replace("_", " ").title()


class VitalSignsDisplay(ft.UserControl):
    """Component for displaying a complete set of vital signs."""
    
    def __init__(
        self,
        vital_signs: VitalSignsSet,
        show_trends: bool = False,
        trends: Optional[Dict] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vital_signs = vital_signs
        self.show_trends = show_trends
        self.trends = trends or {}
    
    def build(self):
        """Build the vital signs display."""
        cards = []
        
        # Blood Pressure
        if self.vital_signs.blood_pressure:
            bp = self.vital_signs.blood_pressure
            bp_trend = self.trends.get("blood_pressure", {})
            
            cards.append(
                VitalSignCard(
                    title="Pressão Arterial",
                    value=f"{bp['systolic']}/{bp['diastolic']}",
                    unit="mmHg",
                    icon=ft.icons.FAVORITE,
                    color=ft.colors.RED_400,
                    category=self._get_bp_category(bp['systolic'], bp['diastolic']),
                    trend=bp_trend.get("systolic", {}).get("trend") if self.show_trends else None
                )
            )
        
        # Heart Rate
        if self.vital_signs.heart_rate:
            hr_trend = self.trends.get("heart_rate", {})
            
            cards.append(
                VitalSignCard(
                    title="Frequência Cardíaca",
                    value=str(self.vital_signs.heart_rate),
                    unit="bpm",
                    icon=ft.icons.MONITOR_HEART,
                    color=ft.colors.PINK_400,
                    category=self._get_hr_category(self.vital_signs.heart_rate),
                    trend=hr_trend.get("trend") if self.show_trends else None
                )
            )
        
        # Temperature
        if self.vital_signs.temperature:
            temp = self.vital_signs.temperature
            temp_trend = self.trends.get("temperature", {})
            unit_symbol = "°C" if temp.get("unit") == "celsius" else "°F"
            
            cards.append(
                VitalSignCard(
                    title="Temperatura",
                    value=str(temp["value"]),
                    unit=unit_symbol,
                    icon=ft.icons.THERMOSTAT,
                    color=ft.colors.ORANGE_400,
                    category=self._get_temp_category(temp["value"], temp.get("unit", "celsius")),
                    trend=temp_trend.get("trend") if self.show_trends else None
                )
            )
        
        # Respiratory Rate
        if self.vital_signs.respiratory_rate:
            cards.append(
                VitalSignCard(
                    title="Frequência Respiratória",
                    value=str(self.vital_signs.respiratory_rate),
                    unit="/min",
                    icon=ft.icons.AIR,
                    color=ft.colors.BLUE_400,
                    category=self._get_rr_category(self.vital_signs.respiratory_rate)
                )
            )
        
        # Oxygen Saturation
        if self.vital_signs.oxygen_saturation:
            spo2_trend = self.trends.get("oxygen_saturation", {})
            
            cards.append(
                VitalSignCard(
                    title="Saturação de Oxigênio",
                    value=str(self.vital_signs.oxygen_saturation),
                    unit="%",
                    icon=ft.icons.WATER_DROP,
                    color=ft.colors.CYAN_400,
                    category=self._get_spo2_category(self.vital_signs.oxygen_saturation),
                    trend=spo2_trend.get("trend") if self.show_trends else None
                )
            )
        
        # Pain Score
        if self.vital_signs.pain_score is not None:
            cards.append(
                VitalSignCard(
                    title="Escala de Dor",
                    value=str(self.vital_signs.pain_score),
                    unit="/10",
                    icon=ft.icons.SENTIMENT_VERY_DISSATISFIED,
                    color=ft.colors.PURPLE_400,
                    category=self._get_pain_category(self.vital_signs.pain_score)
                )
            )
        
        # Alerts section
        alerts_section = ft.Container()
        if self.vital_signs.alerts:
            alerts_section = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.WARNING, color=ft.colors.RED_700, size=20),
                        ft.Text("Alertas Críticos", weight=ft.FontWeight.BOLD, color=ft.colors.RED_700)
                    ]),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.CIRCLE, size=8, color=ft.colors.RED_700),
                            ft.Text(alert, size=12)
                        ]) for alert in self.vital_signs.alerts
                    ])
                ]),
                bgcolor=ft.colors.RED_50,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(top=10)
            )
        
        # Metadata
        metadata = ft.Container(
            content=ft.Row([
                ft.Text(
                    f"Medido em: {self.vital_signs.measured_at.strftime('%d/%m/%Y %H:%M')}",
                    size=11,
                    color=ft.colors.GREY_600
                ),
                ft.Text(
                    f"Por: {self.vital_signs.measured_by or 'Sistema'}",
                    size=11,
                    color=ft.colors.GREY_600
                ) if self.vital_signs.measured_by else ft.Container()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(top=10)
        )
        
        # Grid layout for cards
        grid = ft.ResponsiveRow(
            cards,
            columns={"xs": 6, "sm": 4, "md": 3, "lg": 2}
        )
        
        return ft.Column([
            grid,
            alerts_section,
            metadata
        ])
    
    def _get_bp_category(self, systolic: int, diastolic: int) -> str:
        """Get blood pressure category."""
        if systolic < 90 or diastolic < 60:
            return "hypotension"
        elif systolic >= 180 or diastolic >= 120:
            return "hypertensive_crisis"
        elif systolic >= 140 or diastolic >= 90:
            return "stage2_hypertension"
        elif systolic >= 130 or diastolic >= 80:
            return "stage1_hypertension"
        elif systolic >= 120:
            return "elevated"
        else:
            return "normal"
    
    def _get_hr_category(self, rate: int) -> str:
        """Get heart rate category."""
        if rate < 60:
            return "bradycardia"
        elif rate <= 100:
            return "normal"
        elif rate <= 150:
            return "tachycardia"
        else:
            return "severe_tachycardia"
    
    def _get_temp_category(self, value: float, unit: str) -> str:
        """Get temperature category."""
        celsius = value if unit == "celsius" else (value - 32) * 5/9
        
        if celsius < 35.0:
            return "hypothermia"
        elif celsius < 37.5:
            return "normal"
        elif celsius < 39.0:
            return "fever"
        elif celsius < 40.0:
            return "high_fever"
        else:
            return "hyperpyrexia"
    
    def _get_rr_category(self, rate: int) -> str:
        """Get respiratory rate category."""
        if rate < 12:
            return "low"
        elif rate <= 20:
            return "normal"
        else:
            return "high"
    
    def _get_spo2_category(self, value: int) -> str:
        """Get oxygen saturation category."""
        if value >= 95:
            return "normal"
        elif value >= 91:
            return "mild_hypoxemia"
        elif value >= 86:
            return "moderate_hypoxemia"
        else:
            return "severe_hypoxemia"
    
    def _get_pain_category(self, score: int) -> str:
        """Get pain category."""
        if score == 0:
            return "no_pain"
        elif score <= 3:
            return "mild"
        elif score <= 6:
            return "moderate"
        elif score <= 9:
            return "severe"
        else:
            return "worst_possible"


class VitalSignsChart(ft.UserControl):
    """Chart component for displaying vital signs trends."""
    
    def __init__(
        self,
        vital_signs_history: List[VitalSignsSet],
        vital_type: str = "blood_pressure",
        hours: int = 24,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vital_signs_history = vital_signs_history
        self.vital_type = vital_type
        self.hours = hours
    
    def build(self):
        """Build the chart display."""
        # This is a placeholder for chart implementation
        # In a real implementation, you would use a charting library
        # or Flet's chart components when available
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Gráfico de {self._get_vital_name()}",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(
                    content=ft.Text(
                        "Gráfico em desenvolvimento...",
                        color=ft.colors.GREY_600
                    ),
                    height=200,
                    bgcolor=ft.colors.GREY_100,
                    border_radius=5,
                    alignment=ft.alignment.center
                )
            ]),
            padding=10
        )
    
    def _get_vital_name(self) -> str:
        """Get localized vital sign name."""
        names = {
            "blood_pressure": "Pressão Arterial",
            "heart_rate": "Frequência Cardíaca",
            "temperature": "Temperatura",
            "respiratory_rate": "Frequência Respiratória",
            "oxygen_saturation": "Saturação de Oxigênio"
        }
        return names.get(self.vital_type, self.vital_type)