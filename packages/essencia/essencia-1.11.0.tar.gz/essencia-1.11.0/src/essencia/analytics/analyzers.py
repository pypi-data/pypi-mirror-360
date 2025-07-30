"""
Data analyzers for specific domains.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import statistics
import numpy as np

from motor.motor_asyncio import AsyncIOMotorDatabase
from .aggregators import DataAggregator, TimeSeriesAggregator, AggregationPeriod, AggregationFunction


@dataclass
class TrendAnalysis:
    """Result of trend analysis."""
    trend: str  # increasing, decreasing, stable
    slope: float
    r_squared: float
    forecast: Optional[List[float]] = None
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class PatientMetrics:
    """Patient population metrics."""
    total_patients: int
    active_patients: int
    new_patients_month: int
    average_age: float
    gender_distribution: Dict[str, int]
    chronic_conditions_prevalence: Dict[str, float]
    geographic_distribution: Dict[str, int]


class TrendAnalyzer:
    """Analyze trends in time-series data."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.aggregator = TimeSeriesAggregator(db)
    
    async def analyze_trend(
        self,
        collection: str,
        date_field: str,
        value_field: str,
        period: AggregationPeriod = AggregationPeriod.DAILY,
        lookback_days: int = 30
    ) -> TrendAnalysis:
        """Analyze trend in time-series data."""
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        data = await self.aggregator.aggregate_by_time(
            collection,
            date_field,
            value_field,
            period,
            AggregationFunction.SUM,
            start_date,
            end_date
        )
        
        if len(data) < 3:
            return TrendAnalysis(
                trend="insufficient_data",
                slope=0.0,
                r_squared=0.0
            )
        
        # Extract values and calculate trend
        values = [d.value for d in data]
        x = list(range(len(values)))
        
        # Calculate linear regression
        slope, intercept, r_squared = self._calculate_linear_regression(x, values)
        
        # Determine trend
        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Generate forecast
        forecast_periods = 7
        forecast = [
            slope * (len(values) + i) + intercept
            for i in range(forecast_periods)
        ]
        
        return TrendAnalysis(
            trend=trend,
            slope=slope,
            r_squared=r_squared,
            forecast=forecast
        )
    
    def _calculate_linear_regression(
        self,
        x: List[float],
        y: List[float]
    ) -> Tuple[float, float, float]:
        """Calculate linear regression coefficients."""
        n = len(x)
        if n < 2:
            return 0.0, 0.0, 0.0
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate slope and intercept
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, y_mean, 0.0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return slope, intercept, r_squared
    
    async def detect_anomalies(
        self,
        collection: str,
        date_field: str,
        value_field: str,
        threshold_std: float = 2.0,
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in time-series data."""
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        data = await self.aggregator.aggregate_by_time(
            collection,
            date_field,
            value_field,
            AggregationPeriod.DAILY,
            AggregationFunction.AVG,
            start_date,
            end_date
        )
        
        if len(data) < 7:
            return []
        
        # Calculate statistics
        values = [d.value for d in data]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Detect anomalies
        anomalies = []
        for i, d in enumerate(data):
            z_score = (d.value - mean) / std_dev if std_dev > 0 else 0
            
            if abs(z_score) > threshold_std:
                anomalies.append({
                    "date": d.period,
                    "value": d.value,
                    "z_score": z_score,
                    "expected_range": (
                        mean - threshold_std * std_dev,
                        mean + threshold_std * std_dev
                    )
                })
        
        return anomalies


class PatientAnalyzer:
    """Analyze patient population and health metrics."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.aggregator = DataAggregator(db)
    
    async def get_patient_metrics(self) -> PatientMetrics:
        """Get comprehensive patient population metrics."""
        # Total patients
        total_patients = await self.aggregator.count_documents("sus_patients")
        
        # Active patients (accessed in last 90 days)
        active_date = datetime.now() - timedelta(days=90)
        active_patients = await self.aggregator.count_documents(
            "sus_patients",
            {"last_update": {"$gte": active_date}}
        )
        
        # New patients this month
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        new_patients = await self.aggregator.count_documents(
            "sus_patients",
            {"registration_date": {"$gte": month_start}}
        )
        
        # Average age
        age_pipeline = [
            {
                "$project": {
                    "age": {
                        "$divide": [
                            {"$subtract": [datetime.now(), "$birth_date"]},
                            365.25 * 24 * 60 * 60 * 1000  # Convert to years
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_age": {"$avg": "$age"}
                }
            }
        ]
        age_result = await self.aggregator.aggregate("sus_patients", age_pipeline)
        avg_age = age_result[0]["avg_age"] if age_result else 0
        
        # Gender distribution
        gender_dist = await self.aggregator.group_by(
            "sus_patients",
            "gender",
            {"count": {"type": "count"}}
        )
        gender_distribution = {
            item["_id"]: item["count"]
            for item in gender_dist
            if item["_id"]
        }
        
        # Chronic conditions prevalence
        conditions_pipeline = [
            {"$unwind": "$chronic_conditions"},
            {
                "$group": {
                    "_id": "$chronic_conditions",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        conditions_result = await self.aggregator.aggregate("sus_patients", conditions_pipeline)
        
        chronic_conditions = {}
        if total_patients > 0:
            for item in conditions_result:
                chronic_conditions[item["_id"]] = (item["count"] / total_patients) * 100
        
        # Geographic distribution
        geo_dist = await self.aggregator.group_by(
            "sus_patients",
            "city",
            {"count": {"type": "count"}},
            limit=20
        )
        geographic_distribution = {
            item["_id"]: item["count"]
            for item in geo_dist
            if item["_id"]
        }
        
        return PatientMetrics(
            total_patients=total_patients,
            active_patients=active_patients,
            new_patients_month=new_patients,
            average_age=round(avg_age, 1),
            gender_distribution=gender_distribution,
            chronic_conditions_prevalence=chronic_conditions,
            geographic_distribution=geographic_distribution
        )
    
    async def analyze_readmission_risk(
        self,
        patient_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze patient's readmission risk."""
        # Get patient's admission history
        admissions = await self.db.appointments.count_documents({
            "patient_id": patient_id,
            "appointment_type": "admission",
            "scheduled_date": {"$gte": datetime.now() - timedelta(days=365)}
        })
        
        # Risk factors
        risk_score = 0
        risk_factors = []
        
        # Previous admissions
        if admissions > 2:
            risk_score += 30
            risk_factors.append("Multiple previous admissions")
        elif admissions > 0:
            risk_score += 15
            risk_factors.append("Previous admission")
        
        # Get patient data
        patient = await self.db.sus_patients.find_one({"_id": patient_id})
        if patient:
            # Age factor
            age = (datetime.now() - patient["birth_date"]).days // 365
            if age > 65:
                risk_score += 20
                risk_factors.append("Age > 65")
            
            # Chronic conditions
            conditions = len(patient.get("chronic_conditions", []))
            if conditions > 2:
                risk_score += 25
                risk_factors.append("Multiple chronic conditions")
            elif conditions > 0:
                risk_score += 15
                risk_factors.append("Chronic conditions")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "readmission_probability": min(risk_score, 95) / 100
        }
    
    async def analyze_treatment_adherence(
        self,
        patient_id: str,
        medication_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze patient's medication adherence."""
        # Base query
        query = {"patient_id": patient_id}
        if medication_id:
            query["medication_id"] = medication_id
        
        # Get medication doses
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$medication_id",
                    "total_doses": {"$sum": 1},
                    "taken_doses": {
                        "$sum": {"$cond": [{"$eq": ["$status", "taken"]}, 1, 0]}
                    },
                    "missed_doses": {
                        "$sum": {"$cond": [{"$eq": ["$status", "missed"]}, 1, 0]}
                    }
                }
            }
        ]
        
        results = await self.aggregator.aggregate("medication_doses", pipeline)
        
        if not results:
            return {
                "adherence_rate": 0,
                "status": "no_data",
                "medications": []
            }
        
        # Calculate overall adherence
        total_all = sum(r["total_doses"] for r in results)
        taken_all = sum(r["taken_doses"] for r in results)
        
        adherence_rate = (taken_all / total_all * 100) if total_all > 0 else 0
        
        # Determine status
        if adherence_rate >= 80:
            status = "good"
        elif adherence_rate >= 60:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "adherence_rate": round(adherence_rate, 1),
            "status": status,
            "total_doses": total_all,
            "taken_doses": taken_all,
            "missed_doses": total_all - taken_all,
            "medications": [
                {
                    "medication_id": r["_id"],
                    "adherence_rate": round(
                        r["taken_doses"] / r["total_doses"] * 100, 1
                    ) if r["total_doses"] > 0 else 0
                }
                for r in results
            ]
        }


class FinancialAnalyzer:
    """Analyze financial metrics and trends."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.aggregator = DataAggregator(db)
        self.trend_analyzer = TrendAnalyzer(db)
    
    async def analyze_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze revenue metrics."""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Revenue by source
        revenue_pipeline = [
            {
                "$match": {
                    "date": {"$gte": start_date, "$lte": end_date},
                    "type": "revenue"
                }
            },
            {
                "$group": {
                    "_id": "$source",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        revenue_by_source = await self.aggregator.aggregate(
            "financial_transactions",
            revenue_pipeline
        )
        
        # Total revenue
        total_revenue = sum(item["total"] for item in revenue_by_source)
        
        # Revenue trend
        trend = await self.trend_analyzer.analyze_trend(
            "financial_transactions",
            "date",
            "amount",
            AggregationPeriod.DAILY,
            30
        )
        
        # Average transaction value
        total_transactions = sum(item["count"] for item in revenue_by_source)
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "revenue_by_source": revenue_by_source,
            "average_transaction": avg_transaction,
            "trend": trend.trend,
            "growth_rate": trend.slope * 30,  # Monthly growth
            "forecast_7_days": sum(trend.forecast[:7]) if trend.forecast else 0
        }
    
    async def analyze_costs(
        self,
        category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze cost structure and trends."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = {
            "date": {"$gte": start_date, "$lte": end_date},
            "type": "expense"
        }
        if category:
            query["category"] = category
        
        # Cost by category
        cost_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "avg": {"$avg": "$amount"}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        costs_by_category = await self.aggregator.aggregate(
            "financial_transactions",
            cost_pipeline
        )
        
        # Total costs
        total_costs = sum(item["total"] for item in costs_by_category)
        
        # Cost distribution
        cost_distribution = []
        for item in costs_by_category:
            cost_distribution.append({
                "category": item["_id"],
                "amount": item["total"],
                "percentage": (item["total"] / total_costs * 100) if total_costs > 0 else 0,
                "transactions": item["count"],
                "average": item["avg"]
            })
        
        return {
            "total_costs": total_costs,
            "cost_distribution": cost_distribution,
            "period_days": days,
            "daily_average": total_costs / days if days > 0 else 0
        }


class OperationalAnalyzer:
    """Analyze operational metrics."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.aggregator = DataAggregator(db)
    
    async def analyze_appointment_efficiency(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze appointment scheduling efficiency."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Appointment metrics
        pipeline = [
            {
                "$match": {
                    "scheduled_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_results = await self.aggregator.aggregate("appointments", pipeline)
        
        # Calculate metrics
        status_counts = {item["_id"]: item["count"] for item in status_results}
        total_appointments = sum(status_counts.values())
        
        completed = status_counts.get("completed", 0)
        no_show = status_counts.get("no_show", 0)
        cancelled = status_counts.get("cancelled", 0)
        
        # Efficiency metrics
        completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        no_show_rate = (no_show / total_appointments * 100) if total_appointments > 0 else 0
        cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
        
        # Average wait time
        wait_time_pipeline = [
            {
                "$match": {
                    "scheduled_date": {"$gte": start_date, "$lte": end_date},
                    "status": "completed"
                }
            },
            {
                "$project": {
                    "wait_minutes": {
                        "$divide": [
                            {"$subtract": ["$actual_start", "$scheduled_date"]},
                            60000  # Convert to minutes
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_wait": {"$avg": "$wait_minutes"}
                }
            }
        ]
        
        wait_results = await self.aggregator.aggregate("appointments", wait_time_pipeline)
        avg_wait_time = wait_results[0]["avg_wait"] if wait_results else 0
        
        return {
            "total_appointments": total_appointments,
            "completion_rate": round(completion_rate, 1),
            "no_show_rate": round(no_show_rate, 1),
            "cancellation_rate": round(cancellation_rate, 1),
            "average_wait_time_minutes": round(avg_wait_time, 1),
            "status_breakdown": status_counts,
            "efficiency_score": round(completion_rate - no_show_rate - cancellation_rate, 1)
        }
    
    async def analyze_resource_utilization(
        self,
        resource_type: str = "doctor",
        days: int = 7
    ) -> Dict[str, Any]:
        """Analyze resource utilization rates."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get resource utilization
        pipeline = [
            {
                "$match": {
                    "scheduled_date": {"$gte": start_date, "$lte": end_date},
                    "status": {"$in": ["completed", "in_progress"]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "resource": f"${resource_type}_id",
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$scheduled_date"
                            }
                        }
                    },
                    "appointments": {"$sum": 1},
                    "total_duration": {"$sum": "$duration_minutes"}
                }
            },
            {
                "$group": {
                    "_id": "$_id.resource",
                    "days_worked": {"$sum": 1},
                    "total_appointments": {"$sum": "$appointments"},
                    "total_minutes": {"$sum": "$total_duration"},
                    "avg_daily_appointments": {"$avg": "$appointments"},
                    "avg_daily_minutes": {"$avg": "$total_duration"}
                }
            }
        ]
        
        utilization_results = await self.aggregator.aggregate("appointments", pipeline)
        
        # Calculate utilization metrics
        utilization_data = []
        working_hours_per_day = 8
        working_minutes_per_day = working_hours_per_day * 60
        
        for result in utilization_results:
            utilization_rate = (
                result["avg_daily_minutes"] / working_minutes_per_day * 100
            ) if working_minutes_per_day > 0 else 0
            
            utilization_data.append({
                "resource_id": result["_id"],
                "days_worked": result["days_worked"],
                "total_appointments": result["total_appointments"],
                "avg_appointments_per_day": round(result["avg_daily_appointments"], 1),
                "utilization_rate": round(utilization_rate, 1),
                "efficiency_score": round(
                    utilization_rate * (result["total_appointments"] / result["total_minutes"] * 60)
                    if result["total_minutes"] > 0 else 0,
                    1
                )
            })
        
        # Sort by utilization rate
        utilization_data.sort(key=lambda x: x["utilization_rate"], reverse=True)
        
        # Calculate averages
        if utilization_data:
            avg_utilization = sum(u["utilization_rate"] for u in utilization_data) / len(utilization_data)
            avg_appointments = sum(u["avg_appointments_per_day"] for u in utilization_data) / len(utilization_data)
        else:
            avg_utilization = 0
            avg_appointments = 0
        
        return {
            "resource_type": resource_type,
            "period_days": days,
            "resources_analyzed": len(utilization_data),
            "average_utilization_rate": round(avg_utilization, 1),
            "average_appointments_per_day": round(avg_appointments, 1),
            "utilization_details": utilization_data[:10]  # Top 10
        }