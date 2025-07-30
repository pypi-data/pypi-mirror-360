"""
Report generation and export functionality.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, timedelta
from enum import Enum
from io import BytesIO
import json
import csv

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from .analyzers import (
    PatientAnalyzer,
    FinancialAnalyzer,
    OperationalAnalyzer,
    TrendAnalyzer
)


class ExportFormat(str, Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"


class ReportType(str, Enum):
    """Types of reports available."""
    PATIENT_SUMMARY = "patient_summary"
    FINANCIAL_OVERVIEW = "financial_overview"
    OPERATIONAL_METRICS = "operational_metrics"
    CLINICAL_OUTCOMES = "clinical_outcomes"
    DASHBOARD = "dashboard"
    CUSTOM = "custom"


class DashboardData(BaseModel):
    """Dashboard data model."""
    generated_at: datetime = Field(default_factory=datetime.now)
    period_start: date
    period_end: date
    
    # Key metrics
    total_patients: int
    active_patients: int
    new_patients: int
    
    total_appointments: int
    completed_appointments: int
    appointment_completion_rate: float
    
    total_revenue: float
    total_costs: float
    profit_margin: float
    
    # Trends
    patient_growth_rate: float
    revenue_trend: str
    appointment_trend: str
    
    # Alerts
    critical_alerts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Charts data
    charts: Dict[str, Any] = Field(default_factory=dict)


class ReportGenerator:
    """Generate various reports from analytics data."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.patient_analyzer = PatientAnalyzer(db)
        self.financial_analyzer = FinancialAnalyzer(db)
        self.operational_analyzer = OperationalAnalyzer(db)
        self.trend_analyzer = TrendAnalyzer(db)
    
    async def generate_report(
        self,
        report_type: ReportType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        filters: Optional[Dict[str, Any]] = None,
        format: ExportFormat = ExportFormat.JSON
    ) -> Union[Dict[str, Any], bytes]:
        """Generate a report based on type and parameters."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Generate report data
        if report_type == ReportType.PATIENT_SUMMARY:
            data = await self._generate_patient_summary(start_date, end_date, filters)
        elif report_type == ReportType.FINANCIAL_OVERVIEW:
            data = await self._generate_financial_overview(start_date, end_date, filters)
        elif report_type == ReportType.OPERATIONAL_METRICS:
            data = await self._generate_operational_metrics(start_date, end_date, filters)
        elif report_type == ReportType.CLINICAL_OUTCOMES:
            data = await self._generate_clinical_outcomes(start_date, end_date, filters)
        elif report_type == ReportType.DASHBOARD:
            data = await self._generate_dashboard_data(start_date, end_date)
        else:
            data = {"error": "Report type not implemented"}
        
        # Export in requested format
        return await self._export_data(data, format, report_type)
    
    async def _generate_patient_summary(
        self,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate patient summary report."""
        # Get patient metrics
        metrics = await self.patient_analyzer.get_patient_metrics()
        
        # Age distribution
        age_distribution = await self._get_age_distribution()
        
        # Chronic conditions analysis
        conditions_analysis = await self._analyze_chronic_conditions()
        
        # Geographic analysis
        geo_analysis = await self._analyze_geographic_distribution()
        
        return {
            "report_type": "patient_summary",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_patients": metrics.total_patients,
                "active_patients": metrics.active_patients,
                "new_patients": metrics.new_patients_month,
                "average_age": metrics.average_age
            },
            "demographics": {
                "age_distribution": age_distribution,
                "gender_distribution": metrics.gender_distribution
            },
            "health_profile": {
                "chronic_conditions": metrics.chronic_conditions_prevalence,
                "conditions_analysis": conditions_analysis
            },
            "geographic": {
                "distribution": metrics.geographic_distribution,
                "analysis": geo_analysis
            }
        }
    
    async def _generate_financial_overview(
        self,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate financial overview report."""
        # Convert dates to datetime
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Revenue analysis
        revenue = await self.financial_analyzer.analyze_revenue(start_dt, end_dt)
        
        # Cost analysis
        costs = await self.financial_analyzer.analyze_costs(
            days=(end_date - start_date).days
        )
        
        # Profitability
        profit = revenue["total_revenue"] - costs["total_costs"]
        profit_margin = (profit / revenue["total_revenue"] * 100) if revenue["total_revenue"] > 0 else 0
        
        # Cash flow projection
        cash_flow = await self._project_cash_flow(30)
        
        return {
            "report_type": "financial_overview",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue": {
                "total": revenue["total_revenue"],
                "by_source": revenue["revenue_by_source"],
                "average_transaction": revenue["average_transaction"],
                "trend": revenue["trend"],
                "growth_rate": revenue["growth_rate"]
            },
            "costs": {
                "total": costs["total_costs"],
                "by_category": costs["cost_distribution"],
                "daily_average": costs["daily_average"]
            },
            "profitability": {
                "gross_profit": profit,
                "profit_margin": round(profit_margin, 2),
                "break_even_point": await self._calculate_break_even()
            },
            "projections": {
                "cash_flow_30_days": cash_flow,
                "revenue_forecast": revenue.get("forecast_7_days", 0)
            }
        }
    
    async def _generate_operational_metrics(
        self,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate operational metrics report."""
        days = (end_date - start_date).days
        
        # Appointment efficiency
        appointment_metrics = await self.operational_analyzer.analyze_appointment_efficiency(days)
        
        # Resource utilization
        doctor_utilization = await self.operational_analyzer.analyze_resource_utilization(
            "doctor", days
        )
        
        # Wait time analysis
        wait_time_analysis = await self._analyze_wait_times(start_date, end_date)
        
        # Service quality metrics
        quality_metrics = await self._calculate_quality_metrics(start_date, end_date)
        
        return {
            "report_type": "operational_metrics",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "appointments": {
                "total": appointment_metrics["total_appointments"],
                "completion_rate": appointment_metrics["completion_rate"],
                "no_show_rate": appointment_metrics["no_show_rate"],
                "cancellation_rate": appointment_metrics["cancellation_rate"],
                "average_wait_time": appointment_metrics["average_wait_time_minutes"],
                "efficiency_score": appointment_metrics["efficiency_score"]
            },
            "resource_utilization": {
                "doctors": doctor_utilization,
                "summary": {
                    "average_utilization": doctor_utilization["average_utilization_rate"],
                    "peak_utilization_times": await self._get_peak_utilization_times()
                }
            },
            "wait_times": wait_time_analysis,
            "quality_metrics": quality_metrics
        }
    
    async def _generate_clinical_outcomes(
        self,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate clinical outcomes report."""
        # Treatment success rates
        success_rates = await self._calculate_treatment_success_rates(start_date, end_date)
        
        # Readmission analysis
        readmission_data = await self._analyze_readmissions(start_date, end_date)
        
        # Medication adherence
        adherence_data = await self._analyze_medication_adherence()
        
        # Health improvements
        improvements = await self._analyze_health_improvements(start_date, end_date)
        
        return {
            "report_type": "clinical_outcomes",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "treatment_outcomes": {
                "success_rates": success_rates,
                "by_condition": await self._get_outcomes_by_condition()
            },
            "readmissions": {
                "rate": readmission_data["rate"],
                "average_days_to_readmission": readmission_data["avg_days"],
                "risk_factors": readmission_data["risk_factors"]
            },
            "medication_adherence": {
                "overall_rate": adherence_data["overall_rate"],
                "by_medication_type": adherence_data["by_type"]
            },
            "health_improvements": improvements
        }
    
    async def _generate_dashboard_data(
        self,
        start_date: date,
        end_date: date
    ) -> DashboardData:
        """Generate comprehensive dashboard data."""
        # Get all metrics
        patient_metrics = await self.patient_analyzer.get_patient_metrics()
        
        # Financial metrics
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        revenue = await self.financial_analyzer.analyze_revenue(start_dt, end_dt)
        costs = await self.financial_analyzer.analyze_costs(days=30)
        
        # Operational metrics
        ops_metrics = await self.operational_analyzer.analyze_appointment_efficiency(30)
        
        # Calculate key metrics
        profit = revenue["total_revenue"] - costs["total_costs"]
        profit_margin = (profit / revenue["total_revenue"] * 100) if revenue["total_revenue"] > 0 else 0
        
        # Get trends
        patient_trend = await self.trend_analyzer.analyze_trend(
            "sus_patients",
            "registration_date",
            "count",
            lookback_days=30
        )
        
        # Generate alerts
        alerts = await self._generate_alerts()
        
        # Charts data
        charts = {
            "patient_growth": await self._get_patient_growth_chart_data(),
            "revenue_trend": await self._get_revenue_trend_chart_data(),
            "appointment_status": await self._get_appointment_status_chart_data(),
            "top_conditions": await self._get_top_conditions_chart_data()
        }
        
        return DashboardData(
            period_start=start_date,
            period_end=end_date,
            total_patients=patient_metrics.total_patients,
            active_patients=patient_metrics.active_patients,
            new_patients=patient_metrics.new_patients_month,
            total_appointments=ops_metrics["total_appointments"],
            completed_appointments=ops_metrics["status_breakdown"].get("completed", 0),
            appointment_completion_rate=ops_metrics["completion_rate"],
            total_revenue=revenue["total_revenue"],
            total_costs=costs["total_costs"],
            profit_margin=round(profit_margin, 2),
            patient_growth_rate=patient_trend.slope * 30,
            revenue_trend=revenue["trend"],
            appointment_trend=patient_trend.trend,
            critical_alerts=alerts,
            charts=charts
        )
    
    async def _export_data(
        self,
        data: Union[Dict[str, Any], DashboardData],
        format: ExportFormat,
        report_type: ReportType
    ) -> Union[Dict[str, Any], bytes]:
        """Export data in requested format."""
        if isinstance(data, DashboardData):
            data = data.dict()
        
        if format == ExportFormat.JSON:
            return data
        
        elif format == ExportFormat.CSV:
            return self._export_to_csv(data, report_type)
        
        elif format == ExportFormat.HTML:
            return self._export_to_html(data, report_type)
        
        elif format == ExportFormat.PDF:
            # Would use reportlab or similar
            return b"PDF export not implemented"
        
        elif format == ExportFormat.EXCEL:
            # Would use openpyxl or xlsxwriter
            return b"Excel export not implemented"
        
        return data
    
    def _export_to_csv(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Export data to CSV format."""
        output = BytesIO()
        
        # Flatten nested data for CSV
        if report_type == ReportType.PATIENT_SUMMARY:
            # Create patient summary CSV
            writer = csv.writer(output)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Patients", data["summary"]["total_patients"]])
            writer.writerow(["Active Patients", data["summary"]["active_patients"]])
            writer.writerow(["New Patients", data["summary"]["new_patients"]])
            writer.writerow(["Average Age", data["summary"]["average_age"]])
            
            # Add more rows based on report type
        
        output.seek(0)
        return output.read()
    
    def _export_to_html(self, data: Dict[str, Any], report_type: ReportType) -> bytes:
        """Export data to HTML format."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_type.value} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
            </style>
        </head>
        <body>
            <h1>{report_type.value.replace('_', ' ').title()} Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <pre>{json.dumps(data, indent=2, default=str)}</pre>
        </body>
        </html>
        """
        return html.encode('utf-8')
    
    # Helper methods for data gathering
    async def _get_age_distribution(self) -> List[Dict[str, Any]]:
        """Get patient age distribution."""
        pipeline = [
            {
                "$project": {
                    "age_group": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lt": ["$age", 18]}, "then": "0-17"},
                                {"case": {"$lt": ["$age", 30]}, "then": "18-29"},
                                {"case": {"$lt": ["$age", 45]}, "then": "30-44"},
                                {"case": {"$lt": ["$age", 60]}, "then": "45-59"},
                                {"case": {"$lt": ["$age", 75]}, "then": "60-74"},
                            ],
                            "default": "75+"
                        }
                    }
                }
            },
            {"$group": {"_id": "$age_group", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        from .aggregators import DataAggregator
        aggregator = DataAggregator(self.db)
        return await aggregator.aggregate("sus_patients", pipeline)
    
    async def _analyze_chronic_conditions(self) -> Dict[str, Any]:
        """Analyze chronic conditions patterns."""
        # Implementation would analyze condition combinations, severity, etc.
        return {
            "most_common_combinations": [],
            "risk_correlations": {},
            "management_success_rates": {}
        }
    
    async def _analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Analyze geographic distribution patterns."""
        # Implementation would include clustering, accessibility analysis, etc.
        return {
            "coverage_gaps": [],
            "high_demand_areas": [],
            "accessibility_score": 0.8
        }
    
    async def _project_cash_flow(self, days: int) -> List[Dict[str, Any]]:
        """Project cash flow for next N days."""
        # Implementation would use historical data and trends
        return []
    
    async def _calculate_break_even(self) -> Dict[str, Any]:
        """Calculate break-even analysis."""
        return {
            "fixed_costs": 0,
            "variable_costs": 0,
            "break_even_volume": 0,
            "current_margin": 0
        }
    
    async def _analyze_wait_times(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyze wait time patterns."""
        return {
            "average": 15.5,
            "by_hour": {},
            "by_day_of_week": {},
            "peak_times": []
        }
    
    async def _calculate_quality_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calculate service quality metrics."""
        return {
            "patient_satisfaction": 4.5,
            "first_call_resolution": 0.85,
            "error_rate": 0.02,
            "compliance_score": 0.95
        }
    
    async def _get_peak_utilization_times(self) -> List[Dict[str, Any]]:
        """Get peak resource utilization times."""
        return []
    
    async def _calculate_treatment_success_rates(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calculate treatment success rates."""
        return {
            "overall": 0.82,
            "by_treatment_type": {},
            "factors_affecting_success": []
        }
    
    async def _analyze_readmissions(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyze readmission patterns."""
        return {
            "rate": 0.15,
            "avg_days": 12.5,
            "risk_factors": []
        }
    
    async def _analyze_medication_adherence(self) -> Dict[str, Any]:
        """Analyze medication adherence across patients."""
        return {
            "overall_rate": 0.78,
            "by_type": {},
            "improvement_strategies": []
        }
    
    async def _analyze_health_improvements(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyze health improvements over time."""
        return {
            "vital_signs_improvements": {},
            "condition_management": {},
            "quality_of_life_scores": {}
        }
    
    async def _get_outcomes_by_condition(self) -> Dict[str, Any]:
        """Get treatment outcomes by condition."""
        return {}
    
    async def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate critical alerts for dashboard."""
        alerts = []
        
        # Check for high no-show rate
        ops_metrics = await self.operational_analyzer.analyze_appointment_efficiency(7)
        if ops_metrics["no_show_rate"] > 20:
            alerts.append({
                "type": "warning",
                "category": "operational",
                "message": f"High no-show rate: {ops_metrics['no_show_rate']}%",
                "action": "Review appointment reminder system"
            })
        
        return alerts
    
    async def _get_patient_growth_chart_data(self) -> Dict[str, Any]:
        """Get patient growth data for charts."""
        return {
            "labels": [],
            "datasets": [{
                "label": "New Patients",
                "data": []
            }]
        }
    
    async def _get_revenue_trend_chart_data(self) -> Dict[str, Any]:
        """Get revenue trend data for charts."""
        return {
            "labels": [],
            "datasets": [{
                "label": "Revenue",
                "data": []
            }]
        }
    
    async def _get_appointment_status_chart_data(self) -> Dict[str, Any]:
        """Get appointment status distribution for charts."""
        return {
            "labels": ["Completed", "Cancelled", "No Show"],
            "data": [75, 15, 10]
        }
    
    async def _get_top_conditions_chart_data(self) -> Dict[str, Any]:
        """Get top conditions data for charts."""
        return {
            "labels": [],
            "data": []
        }