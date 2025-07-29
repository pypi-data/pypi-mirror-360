"""
Service mixins providing reusable functionality.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import hashlib
import json
from abc import abstractmethod

from ..models import AuditLog, AuditEventType, AuditOutcome
from .base import ServiceResult, ServiceError


class CacheMixin:
    """Mixin for advanced caching functionality."""
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate consistent cache key from arguments.
        
        Args:
            prefix: Cache key prefix
            *args: Arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            Generated cache key
        """
        # Create a consistent string from args and kwargs
        key_parts = [prefix]
        
        # Add args
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                key_parts.append(json.dumps(sorted(arg), sort_keys=True))
            elif isinstance(arg, dict):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                # For complex objects, use repr or str
                key_parts.append(str(arg))
                
        # Add sorted kwargs
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if v is not None:
                key_parts.append(f"{k}:{v}")
                
        # Join and hash if too long
        key = ":".join(key_parts)
        if len(key) > 250:  # Redis key limit
            # Use hash for long keys
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:hash:{key_hash}"
            
        return key
        
    def invalidate_related_cache(self, entity_type: str, entity_id: str) -> None:
        """
        Invalidate all cache entries related to an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'patient', 'user')
            entity_id: Entity identifier
        """
        patterns = [
            f"{entity_type}:{entity_id}:*",
            f"*:{entity_type}:{entity_id}",
            f"list:{entity_type}:*",  # Lists might need refresh
        ]
        
        for pattern in patterns:
            self.invalidate_cache(pattern)
            
    def cache_aside_pattern(self, cache_key: str, ttl: int = 300):
        """
        Decorator for cache-aside pattern.
        
        Args:
            cache_key: Cache key or callable that generates key
            ttl: Time to live in seconds
        """
        def decorator(func):
            async def wrapper(self, *args, **kwargs):
                # Generate cache key
                if callable(cache_key):
                    key = cache_key(self, *args, **kwargs)
                else:
                    key = cache_key
                    
                # Try cache first
                result = await self.get_with_cache(
                    key,
                    lambda: func(self, *args, **kwargs),
                    ttl=ttl
                )
                return result
            return wrapper
        return decorator


class AuditMixin:
    """Mixin for audit trail functionality."""
    
    @abstractmethod
    def get_audit_user_info(self) -> Dict[str, Optional[str]]:
        """Get current user information for audit."""
        pass
        
    async def audit_operation(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: AuditOutcome,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create audit log entry for operation.
        
        Args:
            event_type: Type of event
            action: Action performed
            outcome: Operation outcome
            resource_type: Type of resource accessed
            resource_id: Resource identifier
            metadata: Additional metadata
        """
        user_info = self.get_audit_user_info()
        
        audit_data = {
            **user_info,
            'event_type': event_type,
            'action': action,
            'outcome': outcome,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow()
        }
        
        try:
            # Create audit log
            AuditLog.create_log(**audit_data)
            self.logger.info(f"Audit log created: {action}")
        except Exception as e:
            # Don't fail operation due to audit failure
            self.logger.error(f"Failed to create audit log: {e}")
            
    def audit_data_access(self, resource_type: str, resource_id: str, action: str = "view"):
        """
        Decorator to audit data access.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier or callable
            action: Action being performed
        """
        def decorator(func):
            async def wrapper(self, *args, **kwargs):
                # Get resource ID
                if callable(resource_id):
                    rid = resource_id(*args, **kwargs)
                else:
                    rid = resource_id
                    
                # Audit the access
                await self.audit_operation(
                    AuditEventType.DATA_ACCESS,
                    f"{action} {resource_type}",
                    AuditOutcome.SUCCESS,
                    resource_type=resource_type,
                    resource_id=str(rid)
                )
                
                # Execute function
                return await func(self, *args, **kwargs)
            return wrapper
        return decorator


class ValidationMixin:
    """Mixin for advanced validation functionality."""
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        import re
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        # Check if it's a valid phone number (10-15 digits)
        return bool(re.match(r'^\+?\d{10,15}$', cleaned))
        
    def validate_cpf(self, cpf: str) -> bool:
        """Validate Brazilian CPF."""
        # Remove non-digits
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        # Check for known invalid patterns
        if cpf in ['00000000000', '11111111111', '22222222222', '33333333333',
                   '44444444444', '55555555555', '66666666666', '77777777777',
                   '88888888888', '99999999999']:
            return False
            
        # Validate check digits
        def calculate_digit(cpf_partial):
            sum_digit = 0
            for i, digit in enumerate(cpf_partial):
                sum_digit += int(digit) * (len(cpf_partial) + 1 - i)
            remainder = sum_digit % 11
            return '0' if remainder < 2 else str(11 - remainder)
            
        # Validate first check digit
        if cpf[9] != calculate_digit(cpf[:9]):
            return False
            
        # Validate second check digit
        if cpf[10] != calculate_digit(cpf[:10]):
            return False
            
        return True
        
    def validate_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """
        Validate date range.
        
        Raises:
            ServiceError: If date range is invalid
        """
        if start_date > end_date:
            raise ServiceError(
                "Start date must be before end date",
                code="INVALID_DATE_RANGE"
            )
            
        # Check if range is too large (e.g., more than 1 year)
        if (end_date - start_date).days > 365:
            raise ServiceError(
                "Date range cannot exceed 365 days",
                code="DATE_RANGE_TOO_LARGE"
            )


class PaginationMixin:
    """Mixin for pagination functionality."""
    
    def paginate_results(
        self,
        items: List[Any],
        page: int = 1,
        page_size: int = 20,
        total_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Paginate a list of items.
        
        Args:
            items: List of items to paginate
            page: Current page number (1-indexed)
            page_size: Items per page
            total_count: Total count if known (otherwise uses len(items))
            
        Returns:
            Pagination metadata with items
        """
        if page < 1:
            page = 1
            
        if page_size < 1:
            page_size = 20
        elif page_size > 100:
            page_size = 100
            
        total = total_count or len(items)
        total_pages = (total + page_size - 1) // page_size
        
        # Calculate slice indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page items
        if total_count is None:
            # Items is the full list
            page_items = items[start_idx:end_idx]
        else:
            # Items is already the page items
            page_items = items
            
        return {
            'items': page_items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_items': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'previous_page': page - 1 if page > 1 else None,
            }
        }
        
    def parse_pagination_params(self, params: Dict[str, Any]) -> Tuple[int, int, Dict[str, Any]]:
        """
        Parse pagination parameters from request.
        
        Args:
            params: Request parameters
            
        Returns:
            Tuple of (page, page_size, filters)
        """
        # Extract pagination params
        page = int(params.pop('page', 1))
        page_size = int(params.pop('page_size', 20))
        
        # Validate
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        
        # Remaining params are filters
        filters = params
        
        return page, page_size, filters


class SearchMixin:
    """Mixin for search functionality."""
    
    def build_search_query(
        self,
        search_term: str,
        search_fields: List[str],
        use_regex: bool = True
    ) -> Dict[str, Any]:
        """
        Build MongoDB search query.
        
        Args:
            search_term: Term to search for
            search_fields: Fields to search in
            use_regex: Use regex for partial matching
            
        Returns:
            MongoDB query dict
        """
        if not search_term or not search_fields:
            return {}
            
        if use_regex:
            # Case-insensitive regex search
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            or_conditions = [{field: regex_pattern} for field in search_fields]
        else:
            # Exact match
            or_conditions = [{field: search_term} for field in search_fields]
            
        return {'$or': or_conditions}
        
    def build_text_search_query(self, search_term: str) -> Dict[str, Any]:
        """
        Build MongoDB text search query.
        
        Args:
            search_term: Term to search for
            
        Returns:
            MongoDB text search query
        """
        return {'$text': {'$search': search_term}}
        
    def rank_search_results(
        self,
        results: List[Dict[str, Any]],
        search_term: str,
        boost_fields: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank search results by relevance.
        
        Args:
            results: Search results
            search_term: Original search term
            boost_fields: Fields to boost with weights
            
        Returns:
            Ranked results
        """
        if not boost_fields:
            boost_fields = {}
            
        search_lower = search_term.lower()
        
        def calculate_score(item):
            score = 0.0
            
            for field, boost in boost_fields.items():
                value = item.get(field, '')
                if isinstance(value, str):
                    value_lower = value.lower()
                    # Exact match
                    if value_lower == search_lower:
                        score += boost * 2
                    # Starts with
                    elif value_lower.startswith(search_lower):
                        score += boost * 1.5
                    # Contains
                    elif search_lower in value_lower:
                        score += boost
                        
            return score
            
        # Add scores to results
        for item in results:
            item['_search_score'] = calculate_score(item)
            
        # Sort by score descending
        return sorted(results, key=lambda x: x['_search_score'], reverse=True)


class ExportMixin:
    """Mixin for data export functionality."""
    
    def export_to_dict(
        self,
        data: List[Any],
        fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Export data to list of dictionaries.
        
        Args:
            data: Data to export
            fields: Fields to include (None for all)
            exclude_fields: Fields to exclude
            
        Returns:
            List of dictionaries
        """
        result = []
        exclude_fields = exclude_fields or []
        
        for item in data:
            # Convert to dict
            if hasattr(item, 'model_dump'):
                item_dict = item.model_dump()
            elif hasattr(item, 'to_dict'):
                item_dict = item.to_dict()
            elif isinstance(item, dict):
                item_dict = item.copy()
            else:
                item_dict = item.__dict__.copy()
                
            # Filter fields
            if fields:
                item_dict = {k: v for k, v in item_dict.items() if k in fields}
            
            # Exclude fields
            for field in exclude_fields:
                item_dict.pop(field, None)
                
            result.append(item_dict)
            
        return result
        
    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        include_headers: bool = True
    ) -> str:
        """
        Export data to CSV format.
        
        Args:
            data: Data to export (list of dicts)
            include_headers: Include header row
            
        Returns:
            CSV string
        """
        import csv
        import io
        
        if not data:
            return ""
            
        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        headers = sorted(all_keys)
        
        # Write CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        
        if include_headers:
            writer.writeheader()
            
        for item in data:
            writer.writerow(item)
            
        return output.getvalue()
        
    def export_to_json(
        self,
        data: List[Dict[str, Any]],
        pretty: bool = True
    ) -> str:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export
            pretty: Pretty print JSON
            
        Returns:
            JSON string
        """
        import json
        from datetime import datetime
        
        def json_serializer(obj):
            """Handle special types."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'model_dump'):
                return obj.model_dump()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
                
        if pretty:
            return json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, default=json_serializer, ensure_ascii=False)