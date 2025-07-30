"""
Data aggregation utilities for analytics.
"""
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime, date, timedelta
from enum import Enum
from dataclasses import dataclass
import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase

from essencia.models import MongoModel


class AggregationPeriod(str, Enum):
    """Time periods for aggregation."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AggregationFunction(str, Enum):
    """Aggregation functions."""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    DISTINCT = "distinct"
    STDDEV = "stddev"
    PERCENTILE = "percentile"


@dataclass
class AggregationResult:
    """Result of an aggregation operation."""
    period: str
    value: Union[float, int, Dict[str, Any]]
    count: int
    metadata: Optional[Dict[str, Any]] = None


class DataAggregator:
    """Base data aggregator for MongoDB collections."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        cursor = self.db[collection].aggregate(pipeline)
        return await cursor.to_list(None)
    
    async def count_documents(
        self,
        collection: str,
        filter_query: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents in collection."""
        filter_query = filter_query or {}
        return await self.db[collection].count_documents(filter_query)
    
    async def distinct_values(
        self,
        collection: str,
        field: str,
        filter_query: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Get distinct values for a field."""
        filter_query = filter_query or {}
        return await self.db[collection].distinct(field, filter_query)
    
    async def group_by(
        self,
        collection: str,
        group_fields: Union[str, List[str]],
        aggregations: Dict[str, Dict[str, Any]],
        filter_query: Optional[Dict[str, Any]] = None,
        sort_by: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Group documents and aggregate."""
        # Build pipeline
        pipeline = []
        
        # Match stage
        if filter_query:
            pipeline.append({"$match": filter_query})
        
        # Group stage
        if isinstance(group_fields, str):
            group_id = f"${group_fields}"
        else:
            group_id = {field: f"${field}" for field in group_fields}
        
        group_stage = {"$group": {"_id": group_id}}
        
        # Add aggregations
        for field_name, agg_spec in aggregations.items():
            agg_type = agg_spec.get("type", "sum")
            source_field = agg_spec.get("field")
            
            if agg_type == "sum":
                group_stage["$group"][field_name] = {"$sum": f"${source_field}"}
            elif agg_type == "avg":
                group_stage["$group"][field_name] = {"$avg": f"${source_field}"}
            elif agg_type == "min":
                group_stage["$group"][field_name] = {"$min": f"${source_field}"}
            elif agg_type == "max":
                group_stage["$group"][field_name] = {"$max": f"${source_field}"}
            elif agg_type == "count":
                group_stage["$group"][field_name] = {"$sum": 1}
            elif agg_type == "distinct":
                group_stage["$group"][field_name] = {"$addToSet": f"${source_field}"}
        
        pipeline.append(group_stage)
        
        # Sort stage
        if sort_by:
            pipeline.append({"$sort": sort_by})
        
        # Limit stage
        if limit:
            pipeline.append({"$limit": limit})
        
        return await self.aggregate(collection, pipeline)


class TimeSeriesAggregator(DataAggregator):
    """Aggregator for time-series data."""
    
    async def aggregate_by_time(
        self,
        collection: str,
        date_field: str,
        value_field: str,
        period: AggregationPeriod,
        function: AggregationFunction,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filter_query: Optional[Dict[str, Any]] = None
    ) -> List[AggregationResult]:
        """Aggregate data by time period."""
        # Build date filter
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        
        # Build match stage
        match_stage = filter_query or {}
        if date_filter:
            match_stage[date_field] = date_filter
        
        # Build date grouping based on period
        date_grouping = self._get_date_grouping(date_field, period)
        
        # Build aggregation
        agg_expression = self._get_aggregation_expression(value_field, function)
        
        # Build pipeline
        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": date_grouping,
                    "value": agg_expression,
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        # Execute aggregation
        results = await self.aggregate(collection, pipeline)
        
        # Convert to AggregationResult
        return [
            AggregationResult(
                period=self._format_period(r["_id"], period),
                value=r["value"],
                count=r["count"]
            )
            for r in results
        ]
    
    def _get_date_grouping(self, date_field: str, period: AggregationPeriod) -> Dict[str, Any]:
        """Get date grouping expression for period."""
        if period == AggregationPeriod.HOURLY:
            return {
                "year": {"$year": f"${date_field}"},
                "month": {"$month": f"${date_field}"},
                "day": {"$dayOfMonth": f"${date_field}"},
                "hour": {"$hour": f"${date_field}"}
            }
        elif period == AggregationPeriod.DAILY:
            return {
                "year": {"$year": f"${date_field}"},
                "month": {"$month": f"${date_field}"},
                "day": {"$dayOfMonth": f"${date_field}"}
            }
        elif period == AggregationPeriod.WEEKLY:
            return {
                "year": {"$year": f"${date_field}"},
                "week": {"$week": f"${date_field}"}
            }
        elif period == AggregationPeriod.MONTHLY:
            return {
                "year": {"$year": f"${date_field}"},
                "month": {"$month": f"${date_field}"}
            }
        elif period == AggregationPeriod.QUARTERLY:
            return {
                "year": {"$year": f"${date_field}"},
                "quarter": {
                    "$ceil": {"$divide": [{"$month": f"${date_field}"}, 3]}
                }
            }
        else:  # YEARLY
            return {"year": {"$year": f"${date_field}"}}
    
    def _get_aggregation_expression(
        self,
        value_field: str,
        function: AggregationFunction
    ) -> Dict[str, Any]:
        """Get aggregation expression for function."""
        if function == AggregationFunction.SUM:
            return {"$sum": f"${value_field}"}
        elif function == AggregationFunction.AVG:
            return {"$avg": f"${value_field}"}
        elif function == AggregationFunction.MIN:
            return {"$min": f"${value_field}"}
        elif function == AggregationFunction.MAX:
            return {"$max": f"${value_field}"}
        elif function == AggregationFunction.COUNT:
            return {"$sum": 1}
        elif function == AggregationFunction.DISTINCT:
            return {"$addToSet": f"${value_field}"}
        elif function == AggregationFunction.STDDEV:
            return {"$stdDevPop": f"${value_field}"}
        else:
            return {"$sum": f"${value_field}"}
    
    def _format_period(self, period_id: Dict[str, int], period: AggregationPeriod) -> str:
        """Format period ID to string."""
        if period == AggregationPeriod.HOURLY:
            return f"{period_id['year']}-{period_id['month']:02d}-{period_id['day']:02d} {period_id['hour']:02d}:00"
        elif period == AggregationPeriod.DAILY:
            return f"{period_id['year']}-{period_id['month']:02d}-{period_id['day']:02d}"
        elif period == AggregationPeriod.WEEKLY:
            return f"{period_id['year']}-W{period_id['week']:02d}"
        elif period == AggregationPeriod.MONTHLY:
            return f"{period_id['year']}-{period_id['month']:02d}"
        elif period == AggregationPeriod.QUARTERLY:
            return f"{period_id['year']}-Q{period_id['quarter']}"
        else:  # YEARLY
            return str(period_id['year'])
    
    async def calculate_moving_average(
        self,
        collection: str,
        date_field: str,
        value_field: str,
        window_size: int,
        period: AggregationPeriod = AggregationPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Calculate moving average over time."""
        # Get time series data
        data = await self.aggregate_by_time(
            collection,
            date_field,
            value_field,
            period,
            AggregationFunction.AVG,
            start_date,
            end_date
        )
        
        # Calculate moving average
        if len(data) < window_size:
            return []
        
        values = [d.value for d in data]
        periods = [d.period for d in data]
        
        moving_avg = []
        for i in range(window_size - 1, len(values)):
            window = values[i - window_size + 1:i + 1]
            avg = sum(window) / window_size
            moving_avg.append({
                "period": periods[i],
                "value": values[i],
                "moving_average": avg
            })
        
        return moving_avg


class MetricsAggregator(DataAggregator):
    """Aggregator for business metrics."""
    
    async def calculate_growth_rate(
        self,
        collection: str,
        date_field: str,
        value_field: str,
        period: AggregationPeriod,
        comparison_periods: int = 1
    ) -> Dict[str, Any]:
        """Calculate growth rate between periods."""
        # Get current period data
        end_date = datetime.now()
        
        # Calculate period duration
        if period == AggregationPeriod.DAILY:
            period_delta = timedelta(days=1)
        elif period == AggregationPeriod.WEEKLY:
            period_delta = timedelta(weeks=1)
        elif period == AggregationPeriod.MONTHLY:
            period_delta = timedelta(days=30)
        elif period == AggregationPeriod.QUARTERLY:
            period_delta = timedelta(days=90)
        else:  # YEARLY
            period_delta = timedelta(days=365)
        
        # Current period
        current_start = end_date - period_delta
        current_data = await self.aggregate_by_time(
            collection,
            date_field,
            value_field,
            period,
            AggregationFunction.SUM,
            current_start,
            end_date
        )
        
        # Previous period
        previous_end = current_start
        previous_start = previous_end - (period_delta * comparison_periods)
        previous_data = await self.aggregate_by_time(
            collection,
            date_field,
            value_field,
            period,
            AggregationFunction.SUM,
            previous_start,
            previous_end
        )
        
        # Calculate growth
        current_value = sum(d.value for d in current_data) if current_data else 0
        previous_value = sum(d.value for d in previous_data) if previous_data else 0
        
        if previous_value > 0:
            growth_rate = ((current_value - previous_value) / previous_value) * 100
        else:
            growth_rate = 100 if current_value > 0 else 0
        
        return {
            "current_value": current_value,
            "previous_value": previous_value,
            "growth_rate": growth_rate,
            "period": period.value,
            "comparison_periods": comparison_periods
        }
    
    async def calculate_percentiles(
        self,
        collection: str,
        value_field: str,
        percentiles: List[float] = [25, 50, 75, 90, 95, 99],
        filter_query: Optional[Dict[str, Any]] = None
    ) -> Dict[float, float]:
        """Calculate percentiles for a numeric field."""
        # Get all values
        pipeline = []
        if filter_query:
            pipeline.append({"$match": filter_query})
        
        pipeline.extend([
            {"$group": {"_id": None, "values": {"$push": f"${value_field}"}}},
            {"$project": {"values": 1}}
        ])
        
        results = await self.aggregate(collection, pipeline)
        
        if not results or not results[0].get("values"):
            return {p: 0.0 for p in percentiles}
        
        values = sorted(results[0]["values"])
        n = len(values)
        
        percentile_values = {}
        for p in percentiles:
            index = int(n * p / 100)
            if index >= n:
                index = n - 1
            percentile_values[p] = values[index]
        
        return percentile_values
    
    async def calculate_distribution(
        self,
        collection: str,
        field: str,
        bins: Optional[int] = None,
        filter_query: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate distribution of values."""
        # Get distinct values or numeric range
        distinct_values = await self.distinct_values(collection, field, filter_query)
        
        if not distinct_values:
            return {"distribution": [], "total": 0}
        
        # Check if numeric
        if all(isinstance(v, (int, float)) for v in distinct_values):
            # Numeric distribution
            min_val = min(distinct_values)
            max_val = max(distinct_values)
            
            if bins:
                # Create histogram bins
                bin_size = (max_val - min_val) / bins
                distribution = []
                
                for i in range(bins):
                    bin_start = min_val + (i * bin_size)
                    bin_end = bin_start + bin_size
                    
                    count = await self.count_documents(
                        collection,
                        {
                            **filter_query,
                            field: {"$gte": bin_start, "$lt": bin_end}
                        }
                    )
                    
                    distribution.append({
                        "range": f"{bin_start:.2f}-{bin_end:.2f}",
                        "count": count
                    })
            else:
                # Count each distinct value
                distribution = []
                for value in sorted(distinct_values):
                    count = await self.count_documents(
                        collection,
                        {**filter_query, field: value}
                    )
                    distribution.append({
                        "value": value,
                        "count": count
                    })
        else:
            # Categorical distribution
            distribution = []
            for value in distinct_values:
                count = await self.count_documents(
                    collection,
                    {**filter_query, field: value}
                )
                distribution.append({
                    "value": str(value),
                    "count": count
                })
        
        total = sum(item["count"] for item in distribution)
        
        # Add percentages
        for item in distribution:
            item["percentage"] = (item["count"] / total * 100) if total > 0 else 0
        
        return {
            "distribution": sorted(distribution, key=lambda x: x["count"], reverse=True),
            "total": total,
            "unique_values": len(distinct_values)
        }