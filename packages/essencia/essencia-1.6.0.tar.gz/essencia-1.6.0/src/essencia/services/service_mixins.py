"""
Service mixins providing common functionality patterns.
"""

import abc
from typing import Dict, Any, List, Optional, Type, Callable, TYPE_CHECKING
from datetime import datetime, date, timedelta
import asyncio

from essencia.services.base_service import BaseService
from essencia.core.exceptions import ValidationError, ServiceError, NotFoundError

if TYPE_CHECKING:
    from essencia.models.base import MongoModel


class SearchMixin:
    """Mixin for search functionality"""
    
    def build_search_query(self, model_class: Type['MongoModel'], 
                          search_term: str, search_fields: List[str]) -> Dict[str, Any]:
        """Build MongoDB search query"""
        if not search_term:
            return {}
        
        # Create regex search for multiple fields
        search_conditions = []
        for field in search_fields:
            search_conditions.append({
                field: {"$regex": search_term, "$options": "i"}
            })
        
        return {"$or": search_conditions} if search_conditions else {}
    
    async def search_with_pagination(self, model_class: Type['MongoModel'],
                                   query: Dict[str, Any], page: int = 1, 
                                   limit: int = 20, sort_field: str = "created",
                                   sort_direction: int = -1) -> Dict[str, Any]:
        """Search with pagination support"""
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get total count
        total = await self.count_documents(model_class, query)
        
        # Get results
        results = await self.find_many(
            model_class, 
            query, 
            sort=[(sort_field, sort_direction)],
            limit=limit
        )
        
        # Apply manual skip (since our find_many doesn't support it yet)
        results = results[skip:skip + limit]
        
        return {
            "data": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1
            }
        }


class AuditMixin:
    """Mixin for audit trail functionality"""
    
    def create_audit_entry(self, action: str, resource_type: str, 
                          resource_id: str, user_id: str, 
                          changes: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create audit trail entry"""
        return {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "changes": changes or {},
            "timestamp": datetime.now(),
            "ip_address": None,  # Could be populated from request context
            "user_agent": None   # Could be populated from request context
        }
    
    async def log_action(self, action: str, resource_type: str, 
                        resource_id: str, user_id: str, 
                        changes: Dict[str, Any] = None):
        """Log an action to audit trail"""
        try:
            # This assumes an AuditLog model exists in the implementing project
            # The implementing project should override this method if needed
            self.logger.info(f"Audit: {action} on {resource_type}:{resource_id} by {user_id}")
        except Exception as e:
            self.logger.warning(f"Failed to create audit log: {e}")


class ValidationMixin:
    """Mixin for advanced validation functionality"""
    
    def validate_business_rules(self, model_class: Type['MongoModel'], 
                               data: Dict[str, Any], 
                               instance: Optional['MongoModel'] = None) -> List[str]:
        """Validate business rules - override in specific services"""
        errors = []
        
        # Common validations can go here
        # Specific services should override this method
        
        return errors
    
    def validate_unique_fields(self, model_class: Type['MongoModel'],
                              data: Dict[str, Any], unique_fields: List[str],
                              instance: Optional['MongoModel'] = None) -> List[str]:
        """Validate unique field constraints"""
        errors = []
        
        for field in unique_fields:
            if field in data:
                query = {field: data[field]}
                
                # Exclude current instance if updating
                if instance:
                    query["_id"] = {"$ne": instance._id}
                
                existing = model_class.find_one(query)
                if existing:
                    errors.append(f"{field.title()} já está em uso")
        
        return errors
    
    async def validate_references(self, data: Dict[str, Any], 
                                 reference_fields: Dict[str, Type['MongoModel']]) -> List[str]:
        """Validate foreign key references"""
        errors = []
        
        for field, ref_model in reference_fields.items():
            if field in data and data[field]:
                ref_key = data[field]
                ref_instance = await self.find_by_key(ref_model, ref_key)
                if not ref_instance:
                    errors.append(f"{field.title()} não encontrado")
        
        return errors


class CacheMixin:
    """Mixin for caching functionality"""
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key"""
        key_parts = [str(prefix)] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    async def get_or_cache(self, cache_key: str, fetch_func: Callable,
                          ttl: int = 300) -> Any:
        """Get data from cache or fetch and cache"""
        return await self.get_with_cache(cache_key, fetch_func, ttl)
    
    def invalidate_model_cache(self, model_class: Type['MongoModel'], instance_key: str = None):
        """Invalidate cache for a model"""
        model_name = model_class.__name__.lower()
        
        if instance_key:
            # Invalidate specific instance
            patterns = [
                f"{model_name}:{instance_key}:*",
                f"list:{model_name}:*",
                f"search:{model_name}:*"
            ]
        else:
            # Invalidate all model cache
            patterns = [f"{model_name}:*", f"list:{model_name}:*", f"search:{model_name}:*"]
        
        for pattern in patterns:
            self.invalidate_cache(pattern)


class BulkOperationMixin:
    """Mixin for bulk operations"""
    
    async def bulk_create(self, model_class: Type['MongoModel'], 
                         data_list: List[Dict[str, Any]], 
                         batch_size: int = 100) -> Dict[str, Any]:
        """Create multiple instances in batches"""
        total = len(data_list)
        created = []
        errors = []
        
        for i in range(0, total, batch_size):
            batch = data_list[i:i + batch_size]
            batch_results = await self._process_batch_create(model_class, batch)
            created.extend(batch_results["success"])
            errors.extend(batch_results["errors"])
        
        return {
            "total": total,
            "created": len(created),
            "errors": len(errors),
            "success_data": created,
            "error_data": errors
        }
    
    async def _process_batch_create(self, model_class: Type['MongoModel'],
                                   batch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a single batch for creation"""
        success = []
        errors = []
        
        for data in batch_data:
            try:
                instance = await self.create(model_class, data)
                success.append(instance)
            except Exception as e:
                errors.append({"data": data, "error": str(e)})
        
        return {"success": success, "errors": errors}
    
    async def bulk_update(self, model_class: Type['MongoModel'],
                         updates: List[Dict[str, Any]],
                         batch_size: int = 100) -> Dict[str, Any]:
        """Update multiple instances in batches"""
        total = len(updates)
        updated = []
        errors = []
        
        for i in range(0, total, batch_size):
            batch = updates[i:i + batch_size]
            batch_results = await self._process_batch_update(model_class, batch)
            updated.extend(batch_results["success"])
            errors.extend(batch_results["errors"])
        
        return {
            "total": total,
            "updated": len(updated),
            "errors": len(errors),
            "success_data": updated,
            "error_data": errors
        }
    
    async def _process_batch_update(self, model_class: Type['MongoModel'],
                                   batch_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a single batch for updates"""
        success = []
        errors = []
        
        for update_data in batch_updates:
            try:
                instance_id = update_data.pop("_id")
                instance = await self.update(model_class, instance_id, update_data)
                success.append(instance)
            except Exception as e:
                errors.append({"data": update_data, "error": str(e)})
        
        return {"success": success, "errors": errors}


class AnalyticsMixin:
    """Mixin for analytics and reporting functionality"""
    
    async def get_model_stats(self, model_class: Type['MongoModel'],
                             date_field: str = "created",
                             period_days: int = 30) -> Dict[str, Any]:
        """Get basic statistics for a model"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # Total count
        total = await self.count_documents(model_class, {})
        
        # Period count
        period_query = {
            date_field: {
                "$gte": start_date.isoformat(),
                "$lt": end_date.isoformat()
            }
        }
        period_count = await self.count_documents(model_class, period_query)
        
        # Daily breakdown
        daily_stats = await self._get_daily_breakdown(
            model_class, date_field, start_date, end_date
        )
        
        return {
            "total": total,
            "period_count": period_count,
            "period_days": period_days,
            "daily_breakdown": daily_stats,
            "average_per_day": period_count / period_days if period_days > 0 else 0
        }
    
    async def _get_daily_breakdown(self, model_class: Type['MongoModel'],
                                  date_field: str, start_date: date,
                                  end_date: date) -> List[Dict[str, Any]]:
        """Get daily breakdown of records"""
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            query = {
                date_field: {
                    "$gte": current_date.isoformat(),
                    "$lt": next_date.isoformat()
                }
            }
            
            count = await self.count_documents(model_class, query)
            daily_stats.append({
                "date": current_date.isoformat(),
                "count": count
            })
            
            current_date = next_date
        
        return daily_stats
    
    async def count_documents(self, model_class: Type['MongoModel'], 
                             query: Dict[str, Any]) -> int:
        """Count documents matching query"""
        # This would need to be implemented based on your MongoDB setup
        # For now, using find and len as fallback
        results = await self.find_many(model_class, query)
        return len(results)


class EnhancedBaseService(BaseService, SearchMixin, AuditMixin, 
                         ValidationMixin, CacheMixin, BulkOperationMixin, 
                         AnalyticsMixin):
    """
    Enhanced base service with all mixins applied.
    """
    
    def __init__(self, model_class: Type['MongoModel'] = None, **kwargs):
        super().__init__(**kwargs)
        self.model_class = model_class
        
        # Service configuration
        self.search_fields: List[str] = []
        self.unique_fields: List[str] = []
        self.reference_fields: Dict[str, Type['MongoModel']] = {}
        self.cache_ttl = 300  # 5 minutes default
    
    async def create_with_validation(self, data: Dict[str, Any], 
                                   user_id: str = None) -> 'MongoModel':
        """Create instance with full validation"""
        # Validate required fields
        if hasattr(self.model_class, '__annotations__'):
            required_fields = [
                field for field, annotation in self.model_class.__annotations__.items()
                if not hasattr(annotation, '__origin__') or 
                annotation.__origin__ is not Optional
            ]
            self.validate_required_fields(data, required_fields)
        
        # Business rule validation
        business_errors = self.validate_business_rules(self.model_class, data)
        if business_errors:
            raise ValidationError("; ".join(business_errors))
        
        # Unique field validation
        unique_errors = self.validate_unique_fields(
            self.model_class, data, self.unique_fields
        )
        if unique_errors:
            raise ValidationError("; ".join(unique_errors))
        
        # Reference validation
        ref_errors = await self.validate_references(data, self.reference_fields)
        if ref_errors:
            raise ValidationError("; ".join(ref_errors))
        
        # Create instance
        instance = await self.create(self.model_class, data, user_id)
        
        # Audit log
        if user_id:
            await self.log_action("CREATE", self.model_class.__name__, 
                                 instance.key, user_id, data)
        
        # Invalidate cache
        self.invalidate_model_cache(self.model_class)
        
        return instance
    
    async def update_with_validation(self, instance_id: str, data: Dict[str, Any],
                                   user_id: str = None) -> 'MongoModel':
        """Update instance with full validation"""
        # Get existing instance
        instance = await self.find_by_key(self.model_class, instance_id)
        if not instance:
            raise NotFoundError(f"{self.model_class.__name__} não encontrado")
        
        # Business rule validation
        business_errors = self.validate_business_rules(
            self.model_class, data, instance
        )
        if business_errors:
            raise ValidationError("; ".join(business_errors))
        
        # Unique field validation
        unique_errors = self.validate_unique_fields(
            self.model_class, data, self.unique_fields, instance
        )
        if unique_errors:
            raise ValidationError("; ".join(unique_errors))
        
        # Reference validation
        ref_errors = await self.validate_references(data, self.reference_fields)
        if ref_errors:
            raise ValidationError("; ".join(ref_errors))
        
        # Store original data for audit
        original_data = instance.model_dump() if hasattr(instance, 'model_dump') else {}
        
        # Update instance
        updated_instance = await self.update(self.model_class, instance_id, data, user_id)
        
        # Audit log
        if user_id:
            changes = {
                "before": original_data,
                "after": data
            }
            await self.log_action("UPDATE", self.model_class.__name__,
                                 instance.key, user_id, changes)
        
        # Invalidate cache
        self.invalidate_model_cache(self.model_class, instance.key)
        
        return updated_instance
    
    async def delete_with_audit(self, instance_id: str, user_id: str = None) -> bool:
        """Delete instance with audit trail"""
        # Get instance for audit
        instance = await self.find_by_key(self.model_class, instance_id)
        if not instance:
            raise NotFoundError(f"{self.model_class.__name__} não encontrado")
        
        # Store data for audit
        instance_data = instance.model_dump() if hasattr(instance, 'model_dump') else {}
        
        # Delete
        await self.delete(self.model_class, instance_id)
        
        # Audit log
        if user_id:
            await self.log_action("DELETE", self.model_class.__name__,
                                 instance.key, user_id, instance_data)
        
        # Invalidate cache
        self.invalidate_model_cache(self.model_class, instance.key)
        
        return True
    
    async def search_cached(self, search_term: str, page: int = 1, 
                           limit: int = 20) -> Dict[str, Any]:
        """Search with caching"""
        cache_key = self.get_cache_key(
            "search", self.model_class.__name__.lower(), 
            search_term, page, limit
        )
        
        async def fetch_search_results():
            query = self.build_search_query(
                self.model_class, search_term, self.search_fields
            )
            return await self.search_with_pagination(
                self.model_class, query, page, limit
            )
        
        return await self.get_or_cache(cache_key, fetch_search_results, self.cache_ttl)
    
    async def get_stats_cached(self, period_days: int = 30) -> Dict[str, Any]:
        """Get statistics with caching"""
        cache_key = self.get_cache_key(
            "stats", self.model_class.__name__.lower(), period_days
        )
        
        async def fetch_stats():
            return await self.get_model_stats(
                self.model_class, period_days=period_days
            )
        
        return await self.get_or_cache(cache_key, fetch_stats, self.cache_ttl)