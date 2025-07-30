"""
MongoDB Query Validation and Sanitization.
Prevents NoSQL injection attacks by validating and sanitizing query parameters.
"""

import re
import logging
from typing import Dict, Any, Union, List, Set, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class QueryValidator:
    """
    Validates and sanitizes MongoDB queries to prevent NoSQL injection attacks.
    
    This class provides comprehensive validation for MongoDB queries, updates,
    and aggregation pipelines to ensure they don't contain malicious code.
    
    Example:
        >>> validator = QueryValidator()
        >>> safe_query = validator.validate_query({"name": user_input})
        >>> 
        >>> # Or use the decorator
        >>> @validate_query
        >>> def find_users(query):
        >>>     return collection.find(query)
    """
    
    # Allowed MongoDB operators
    ALLOWED_OPERATORS: Set[str] = {
        # Comparison operators
        '$eq', '$ne', '$gt', '$gte', '$lt', '$lte', '$in', '$nin',
        # Logical operators  
        '$and', '$or', '$not', '$nor',
        # Element operators
        '$exists', '$type',
        # Array operators
        '$all', '$elemMatch', '$size',
        # Regex (limited)
        '$regex', '$options'
    }
    
    # Dangerous patterns that should be blocked
    FORBIDDEN_PATTERNS: List[re.Pattern] = [
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'function\s*\(', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'\$where', re.IGNORECASE),
        re.compile(r'\$mapReduce', re.IGNORECASE),
        re.compile(r'\$accumulator', re.IGNORECASE),
        re.compile(r'\$function', re.IGNORECASE),
    ]
    
    # Maximum depth for nested queries
    MAX_QUERY_DEPTH = 10
    
    # Maximum array size for $in/$nin operators
    MAX_ARRAY_SIZE = 1000
    
    def __init__(
        self,
        max_query_depth: int = 10,
        max_array_size: int = 1000,
        additional_forbidden_patterns: Optional[List[str]] = None,
        additional_allowed_operators: Optional[Set[str]] = None
    ):
        """
        Initialize the query validator.
        
        Args:
            max_query_depth: Maximum nesting depth for queries
            max_array_size: Maximum size for array operators
            additional_forbidden_patterns: Extra patterns to block
            additional_allowed_operators: Extra operators to allow
        """
        self.max_query_depth = max_query_depth
        self.max_array_size = max_array_size
        
        self.allowed_operators = self.ALLOWED_OPERATORS.copy()
        if additional_allowed_operators:
            self.allowed_operators.update(additional_allowed_operators)
            
        self.forbidden_patterns = self.FORBIDDEN_PATTERNS.copy()
        if additional_forbidden_patterns:
            for pattern in additional_forbidden_patterns:
                self.forbidden_patterns.append(re.compile(pattern, re.IGNORECASE))
    
    def validate_query(self, query: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        """
        Validates and sanitizes a MongoDB query.
        
        Args:
            query: The MongoDB query to validate
            depth: Current nesting depth (for recursion limit)
            
        Returns:
            Sanitized query dictionary
            
        Raises:
            ValueError: If query contains dangerous patterns or exceeds limits
        """
        if depth > self.max_query_depth:
            raise ValueError(f"Query nesting depth exceeds maximum of {self.max_query_depth}")
            
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")
            
        sanitized_query = {}
        
        for key, value in query.items():
            # Validate key
            sanitized_key = self._validate_key(key)
            
            # Validate value based on type
            if isinstance(value, dict):
                # Recursive validation for nested queries
                sanitized_value = self.validate_query(value, depth + 1)
            elif isinstance(value, list):
                # Validate array values
                sanitized_value = self._validate_array(value, key)
            else:
                # Validate scalar values
                sanitized_value = self._validate_value(value, key)
                
            sanitized_query[sanitized_key] = sanitized_value
            
        return sanitized_query
    
    def _validate_key(self, key: str) -> str:
        """
        Validates a query key (field name or operator).
        
        Args:
            key: The key to validate
            
        Returns:
            Sanitized key
            
        Raises:
            ValueError: If key is invalid or dangerous
        """
        if not isinstance(key, str):
            raise ValueError("Query keys must be strings")
            
        # Check for dangerous patterns in keys
        for pattern in self.forbidden_patterns:
            if pattern.search(key):
                raise ValueError(f"Forbidden pattern detected in key: {key}")
                
        # If it's an operator, check if it's allowed
        if key.startswith('$'):
            if key not in self.allowed_operators:
                raise ValueError(f"Operator '{key}' is not allowed")
                
        # Sanitize field names - only allow alphanumeric, underscore, dot
        if not key.startswith('$'):
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', key):
                raise ValueError(f"Invalid field name: {key}")
                
        return key
    
    def _validate_value(self, value: Any, key: str) -> Any:
        """
        Validates a scalar value in the query.
        
        Args:
            value: The value to validate
            key: The key this value belongs to
            
        Returns:
            Sanitized value
        """
        # Check for dangerous patterns in string values
        if isinstance(value, str):
            for pattern in self.forbidden_patterns:
                if pattern.search(value):
                    raise ValueError(f"Forbidden pattern detected in value: {value}")
                    
            # Handle ObjectId conversion if needed
            if self._looks_like_objectid(value):
                # Return as-is, let the database driver handle conversion
                return value
                    
            # Escape special regex characters if used with $regex
            if key == '$regex':
                # Allow basic regex but escape dangerous characters
                value = self._sanitize_regex(value)
                
        return value
    
    def _validate_array(self, array: List[Any], key: str) -> List[Any]:
        """
        Validates an array value in the query.
        
        Args:
            array: The array to validate
            key: The key this array belongs to
            
        Returns:
            Sanitized array
        """
        if len(array) > self.max_array_size:
            raise ValueError(f"Array size {len(array)} exceeds maximum of {self.max_array_size}")
            
        sanitized_array = []
        for item in array:
            if isinstance(item, dict):
                sanitized_array.append(self.validate_query(item))
            else:
                sanitized_array.append(self._validate_value(item, key))
                
        return sanitized_array
    
    def validate_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates MongoDB update operations.
        
        Args:
            update: The update document to validate
            
        Returns:
            Sanitized update document
        """
        if not isinstance(update, dict):
            raise ValueError("Update must be a dictionary")
            
        # Allowed update operators
        allowed_update_ops = {
            '$set', '$unset', '$inc', '$mul', '$rename', '$min', '$max',
            '$currentDate', '$addToSet', '$pop', '$pull', '$push',
            '$pullAll', '$each', '$slice', '$sort', '$position'
        }
        
        sanitized_update = {}
        
        for key, value in update.items():
            if key.startswith('$'):
                if key not in allowed_update_ops:
                    raise ValueError(f"Update operator '{key}' is not allowed")
                    
            # Validate the update value
            if isinstance(value, dict):
                sanitized_value = {}
                for field, field_value in value.items():
                    # Validate field name
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', field):
                        raise ValueError(f"Invalid field name in update: {field}")
                    sanitized_value[field] = self._validate_value(field_value, field)
                sanitized_update[key] = sanitized_value
            else:
                sanitized_update[key] = self._validate_value(value, key)
                
        return sanitized_update
    
    def validate_aggregation_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitizes MongoDB aggregation pipeline stages.
        
        Args:
            pipeline: List of aggregation pipeline stages
            
        Returns:
            Sanitized pipeline
        """
        # Allowed aggregation stages
        allowed_stages = {
            '$match', '$project', '$sort', '$limit', '$skip', '$unwind',
            '$group', '$lookup', '$addFields', '$replaceRoot', '$facet',
            '$count', '$sortByCount'
        }
        
        sanitized_pipeline = []
        
        for stage in pipeline:
            if not isinstance(stage, dict):
                raise ValueError("Pipeline stage must be a dictionary")
                
            if len(stage) != 1:
                raise ValueError("Pipeline stage must contain exactly one operator")
                
            stage_op = list(stage.keys())[0]
            if stage_op not in allowed_stages:
                raise ValueError(f"Aggregation stage '{stage_op}' is not allowed")
                
            # Validate stage content based on type
            stage_content = stage[stage_op]
            
            if stage_op == '$match':
                # Validate match queries
                sanitized_content = self.validate_query(stage_content)
            elif stage_op in ['$project', '$addFields']:
                # Validate projection fields
                sanitized_content = self._validate_projection(stage_content)
            else:
                # Basic validation for other stages
                sanitized_content = stage_content
                
            sanitized_pipeline.append({stage_op: sanitized_content})
            
        return sanitized_pipeline
    
    def _validate_projection(self, projection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates MongoDB projection specifications.
        
        Args:
            projection: Projection specification
            
        Returns:
            Sanitized projection
        """
        sanitized_projection = {}
        
        for field, value in projection.items():
            # Validate field name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', field):
                raise ValueError(f"Invalid field name in projection: {field}")
                
            # Validate projection value (0, 1, or expression)
            if isinstance(value, (int, bool)):
                sanitized_projection[field] = value
            elif isinstance(value, dict):
                # Expression - basic validation only
                sanitized_projection[field] = value
            else:
                raise ValueError(f"Invalid projection value for field {field}")
                
        return sanitized_projection
    
    def _looks_like_objectid(self, value: str) -> bool:
        """Check if a string looks like a MongoDB ObjectId."""
        return len(value) == 24 and re.match(r'^[a-fA-F0-9]{24}$', value) is not None
    
    def _sanitize_regex(self, pattern: str) -> str:
        """
        Sanitize regex pattern to prevent ReDoS attacks.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            Sanitized pattern
        """
        # Limit pattern length
        if len(pattern) > 1000:
            pattern = pattern[:1000]
            
        # Escape potentially dangerous regex constructs
        # But allow basic regex functionality
        dangerous_constructs = [
            r'(?:.*){',  # Nested quantifiers
            r'(.*)*',    # Catastrophic backtracking
            r'(.+)+',    # Catastrophic backtracking
        ]
        
        for construct in dangerous_constructs:
            if construct in pattern:
                raise ValueError(f"Potentially dangerous regex pattern: {construct}")
                
        return pattern


# Create a default validator instance
_default_validator = QueryValidator()


def validate_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a MongoDB query using the default validator.
    
    Args:
        query: MongoDB query to validate
        
    Returns:
        Sanitized query
    """
    return _default_validator.validate_query(query)


def validate_update(update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a MongoDB update operation using the default validator.
    
    Args:
        update: MongoDB update document
        
    Returns:
        Sanitized update
    """
    return _default_validator.validate_update(update)


def validate_aggregation_pipeline(pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate a MongoDB aggregation pipeline using the default validator.
    
    Args:
        pipeline: Aggregation pipeline stages
        
    Returns:
        Sanitized pipeline
    """
    return _default_validator.validate_aggregation_pipeline(pipeline)


def validate_mongo_operation(operation_type: str = 'query'):
    """
    Decorator to automatically validate MongoDB operations.
    
    Args:
        operation_type: Type of operation ('query', 'update', 'pipeline')
    
    Usage:
        @validate_mongo_operation('query')
        def find_users(query):
            return collection.find(query)
            
        @validate_mongo_operation('update')
        def update_user(query, update):
            return collection.update_one(query, update)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validator = _default_validator
            
            if operation_type == 'query':
                # Validate query parameter
                if 'query' in kwargs:
                    kwargs['query'] = validator.validate_query(kwargs['query'])
                elif len(args) > 0 and isinstance(args[0], dict):
                    args = list(args)
                    args[0] = validator.validate_query(args[0])
                    
            elif operation_type == 'update':
                # Validate both query and update
                if 'query' in kwargs:
                    kwargs['query'] = validator.validate_query(kwargs['query'])
                if 'update' in kwargs:
                    kwargs['update'] = validator.validate_update(kwargs['update'])
                    
                # Handle positional arguments
                args = list(args)
                if len(args) > 0 and isinstance(args[0], dict):
                    args[0] = validator.validate_query(args[0])
                if len(args) > 1 and isinstance(args[1], dict):
                    args[1] = validator.validate_update(args[1])
                    
            elif operation_type == 'pipeline':
                # Validate aggregation pipeline
                if 'pipeline' in kwargs:
                    kwargs['pipeline'] = validator.validate_aggregation_pipeline(kwargs['pipeline'])
                elif len(args) > 0 and isinstance(args[0], list):
                    args = list(args)
                    args[0] = validator.validate_aggregation_pipeline(args[0])
                    
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Utility functions for common sanitization needs

def sanitize_text_search(text: str) -> str:
    """
    Sanitizes text for MongoDB text search.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for $text search
    """
    if not isinstance(text, str):
        raise ValueError("Text search input must be a string")
        
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}$]', '', text)
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
        
    return text.strip()


def sanitize_sort_spec(sort_spec: Union[str, List, Dict]) -> List:
    """
    Sanitizes MongoDB sort specification.
    
    Args:
        sort_spec: Sort specification
        
    Returns:
        Sanitized sort specification as list of tuples
    """
    if isinstance(sort_spec, str):
        # Simple field name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', sort_spec):
            raise ValueError(f"Invalid sort field: {sort_spec}")
        return [(sort_spec, 1)]
        
    elif isinstance(sort_spec, list):
        sanitized_sort = []
        for item in sort_spec:
            if isinstance(item, tuple) and len(item) == 2:
                field, direction = item
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', field):
                    raise ValueError(f"Invalid sort field: {field}")
                if direction not in [1, -1]:
                    raise ValueError(f"Invalid sort direction: {direction}")
                sanitized_sort.append((field, direction))
            else:
                raise ValueError("Sort list items must be (field, direction) tuples")
        return sanitized_sort
        
    elif isinstance(sort_spec, dict):
        sanitized_sort = []
        for field, direction in sort_spec.items():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', field):
                raise ValueError(f"Invalid sort field: {field}")
            if direction not in [1, -1]:
                raise ValueError(f"Invalid sort direction: {direction}")
            sanitized_sort.append((field, direction))
        return sanitized_sort
        
    else:
        raise ValueError("Sort specification must be string, list, or dict")