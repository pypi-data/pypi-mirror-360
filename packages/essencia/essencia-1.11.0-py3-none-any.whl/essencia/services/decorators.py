"""
Service decorators for common patterns and cross-cutting concerns.
"""

import functools
import asyncio
import time
import logging
from typing import Any, Callable, Optional, Dict, List, Union
from datetime import datetime

from ..models import AuditEventType, AuditOutcome
from .base import ServiceError, ServiceResult

logger = logging.getLogger(__name__)


def service_method(
    name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
    measure_time: bool = True
):
    """
    Decorator for service methods with logging and timing.
    
    Args:
        name: Method name for logging (defaults to function name)
        log_args: Log method arguments
        log_result: Log method result
        measure_time: Measure execution time
    """
    def decorator(func: Callable) -> Callable:
        method_name = name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            start_time = time.time() if measure_time else None
            
            # Log method call
            log_data = {'method': method_name, 'service': self.__class__.__name__}
            if log_args:
                log_data['args'] = args
                log_data['kwargs'] = kwargs
            logger.debug(f"Calling {method_name}", extra=log_data)
            
            try:
                # Execute method
                result = await func(self, *args, **kwargs)
                
                # Log success
                if measure_time:
                    elapsed = time.time() - start_time
                    log_data['elapsed_ms'] = round(elapsed * 1000, 2)
                    
                if log_result:
                    log_data['result'] = result
                    
                logger.info(f"{method_name} completed", extra=log_data)
                return result
                
            except Exception as e:
                # Log failure
                if measure_time:
                    elapsed = time.time() - start_time
                    log_data['elapsed_ms'] = round(elapsed * 1000, 2)
                    
                log_data['error'] = str(e)
                log_data['error_type'] = type(e).__name__
                logger.error(f"{method_name} failed", extra=log_data, exc_info=True)
                raise
                
        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            start_time = time.time() if measure_time else None
            
            # Log method call
            log_data = {'method': method_name, 'service': self.__class__.__name__}
            if log_args:
                log_data['args'] = args
                log_data['kwargs'] = kwargs
            logger.debug(f"Calling {method_name}", extra=log_data)
            
            try:
                # Execute method
                result = func(self, *args, **kwargs)
                
                # Log success
                if measure_time:
                    elapsed = time.time() - start_time
                    log_data['elapsed_ms'] = round(elapsed * 1000, 2)
                    
                if log_result:
                    log_data['result'] = result
                    
                logger.info(f"{method_name} completed", extra=log_data)
                return result
                
            except Exception as e:
                # Log failure
                if measure_time:
                    elapsed = time.time() - start_time
                    log_data['elapsed_ms'] = round(elapsed * 1000, 2)
                    
                log_data['error'] = str(e)
                log_data['error_type'] = type(e).__name__
                logger.error(f"{method_name} failed", extra=log_data, exc_info=True)
                raise
                
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def cached(
    ttl: int = 300,
    cache_key: Optional[Union[str, Callable]] = None,
    force_refresh_param: str = 'force_refresh'
):
    """
    Decorator for caching method results.
    
    Args:
        ttl: Time to live in seconds
        cache_key: Cache key or callable that generates key
        force_refresh_param: Parameter name to force cache refresh
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if force refresh
            force_refresh = kwargs.get(force_refresh_param, False)
            
            # Generate cache key
            if cache_key is None:
                # Auto-generate from method name and args
                key_parts = [self.__class__.__name__, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) 
                                if k != force_refresh_param)
                final_key = ":".join(key_parts)
            elif callable(cache_key):
                final_key = cache_key(self, *args, **kwargs)
            else:
                final_key = cache_key
                
            # Use cache method from service
            return await self.get_with_cache(
                final_key,
                lambda: func(self, *args, **kwargs),
                ttl=ttl,
                force_refresh=force_refresh
            )
            
        return wrapper
    return decorator


def audited(
    action: Optional[Union[str, Callable]] = None,
    event_type: AuditEventType = AuditEventType.DATA_UPDATE,
    resource_type: Optional[Union[str, Callable]] = None,
    resource_id: Optional[Union[str, Callable]] = None,
    include_args: bool = False
):
    """
    Decorator for auditing method calls.
    
    Args:
        action: Audit action or callable to generate it
        event_type: Type of audit event
        resource_type: Resource type or callable
        resource_id: Resource ID or callable to extract it
        include_args: Include method arguments in audit metadata
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generate audit fields
            if action is None:
                audit_action = func.__name__
            elif callable(action):
                audit_action = action(self, *args, **kwargs)
            else:
                audit_action = action
                
            if callable(resource_type):
                audit_resource_type = resource_type(self, *args, **kwargs)
            else:
                audit_resource_type = resource_type
                
            if callable(resource_id):
                audit_resource_id = resource_id(self, *args, **kwargs)
            else:
                audit_resource_id = resource_id
                
            # Build metadata
            metadata = {}
            if include_args:
                metadata['args'] = args
                metadata['kwargs'] = {k: v for k, v in kwargs.items() 
                                     if not k.startswith('_')}
                
            try:
                # Execute method
                result = await func(self, *args, **kwargs)
                
                # Audit success
                if hasattr(self, 'audit_operation'):
                    await self.audit_operation(
                        event_type=event_type,
                        action=audit_action,
                        outcome=AuditOutcome.SUCCESS,
                        resource_type=audit_resource_type,
                        resource_id=str(audit_resource_id) if audit_resource_id else None,
                        metadata=metadata
                    )
                    
                return result
                
            except Exception as e:
                # Audit failure
                metadata['error'] = str(e)
                metadata['error_type'] = type(e).__name__
                
                if hasattr(self, 'audit_operation'):
                    await self.audit_operation(
                        event_type=event_type,
                        action=audit_action,
                        outcome=AuditOutcome.FAILURE,
                        resource_type=audit_resource_type,
                        resource_id=str(audit_resource_id) if audit_resource_id else None,
                        metadata=metadata
                    )
                    
                raise
                
        return wrapper
    return decorator


def authorized(
    required_role: Optional[Union[str, List[str]]] = None,
    required_permission: Optional[Union[str, List[str]]] = None,
    check_ownership: bool = False,
    owner_field: str = 'user_key',
    resource_param: Union[str, int] = 0
):
    """
    Decorator for authorization checks.
    
    Args:
        required_role: Required role(s) for access
        required_permission: Required permission(s)
        check_ownership: Check resource ownership
        owner_field: Field name for owner ID in resource
        resource_param: Parameter containing resource (name or position)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get user from service context
            user = getattr(self, 'current_user', None)
            if not user:
                raise ServiceError("User not authenticated", code="UNAUTHENTICATED")
                
            # Check role
            if required_role:
                roles = required_role if isinstance(required_role, list) else [required_role]
                user_role = user.get('role')
                if user_role not in roles:
                    raise ServiceError(
                        f"Insufficient role. Required: {roles}",
                        code="FORBIDDEN",
                        details={'required_roles': roles, 'user_role': user_role}
                    )
                    
            # Check permission
            if required_permission:
                perms = required_permission if isinstance(required_permission, list) else [required_permission]
                user_perms = user.get('permissions', [])
                if not any(perm in user_perms for perm in perms):
                    raise ServiceError(
                        f"Insufficient permissions. Required: {perms}",
                        code="FORBIDDEN",
                        details={'required_permissions': perms}
                    )
                    
            # Check ownership
            if check_ownership:
                # Get resource
                if isinstance(resource_param, int):
                    resource = args[resource_param] if len(args) > resource_param else None
                else:
                    resource = kwargs.get(resource_param)
                    
                if resource:
                    # Get owner ID from resource
                    if isinstance(resource, dict):
                        owner_id = resource.get(owner_field)
                    else:
                        owner_id = getattr(resource, owner_field, None)
                        
                    # Check ownership
                    user_id = user.get('key') or user.get('_id')
                    if owner_id and str(owner_id) != str(user_id):
                        raise ServiceError(
                            "Access denied. You don't own this resource.",
                            code="FORBIDDEN",
                            details={'owner_id': str(owner_id), 'user_id': str(user_id)}
                        )
                        
            # Execute method
            return await func(self, *args, **kwargs)
            
        return wrapper
    return decorator


def validated(
    schema: Optional[Any] = None,
    validate_args: bool = True,
    validate_kwargs: bool = True,
    arg_schemas: Optional[Dict[int, Any]] = None,
    kwarg_schemas: Optional[Dict[str, Any]] = None
):
    """
    Decorator for input validation.
    
    Args:
        schema: Pydantic model or callable for validation
        validate_args: Validate positional arguments
        validate_kwargs: Validate keyword arguments
        arg_schemas: Schema for specific positional arguments
        kwarg_schemas: Schema for specific keyword arguments
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Validate positional arguments
            if validate_args and arg_schemas:
                for idx, arg_schema in arg_schemas.items():
                    if idx < len(args):
                        try:
                            if hasattr(arg_schema, 'model_validate'):
                                # Pydantic model
                                arg_schema.model_validate(args[idx])
                            elif callable(arg_schema):
                                # Validation function
                                if not arg_schema(args[idx]):
                                    raise ValueError(f"Validation failed for argument {idx}")
                        except Exception as e:
                            raise ServiceError(
                                f"Invalid argument at position {idx}: {e}",
                                code="VALIDATION_ERROR",
                                details={'position': idx, 'error': str(e)}
                            )
                            
            # Validate keyword arguments
            if validate_kwargs and kwarg_schemas:
                for key, kwarg_schema in kwarg_schemas.items():
                    if key in kwargs:
                        try:
                            if hasattr(kwarg_schema, 'model_validate'):
                                # Pydantic model
                                kwargs[key] = kwarg_schema.model_validate(kwargs[key])
                            elif callable(kwarg_schema):
                                # Validation function
                                if not kwarg_schema(kwargs[key]):
                                    raise ValueError(f"Validation failed for {key}")
                        except Exception as e:
                            raise ServiceError(
                                f"Invalid argument '{key}': {e}",
                                code="VALIDATION_ERROR",
                                details={'argument': key, 'error': str(e)}
                            )
                            
            # General schema validation
            if schema:
                try:
                    # Combine args and kwargs for validation
                    data = {'args': args, 'kwargs': kwargs}
                    if hasattr(schema, 'model_validate'):
                        schema.model_validate(data)
                    elif callable(schema):
                        if not schema(data):
                            raise ValueError("Validation failed")
                except Exception as e:
                    raise ServiceError(
                        f"Validation error: {e}",
                        code="VALIDATION_ERROR",
                        details={'error': str(e)}
                    )
                    
            # Execute method
            return await func(self, *args, **kwargs)
            
        return wrapper
    return decorator


def transactional(
    rollback_on: Optional[List[type]] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
):
    """
    Decorator for transactional operations with retry logic.
    
    Args:
        rollback_on: Exception types that trigger rollback
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            rollback_exceptions = rollback_on or [Exception]
            
            for attempt in range(max_retries):
                session = None
                try:
                    # Start transaction if database supports it
                    if hasattr(self.db, 'start_session'):
                        session = await self.db.start_session()
                        session.start_transaction()
                        
                    # Execute method
                    result = await func(self, *args, **kwargs)
                    
                    # Commit transaction
                    if session:
                        await session.commit_transaction()
                        
                    return result
                    
                except Exception as e:
                    # Check if we should rollback
                    should_rollback = any(isinstance(e, exc_type) for exc_type in rollback_exceptions)
                    
                    if session and should_rollback:
                        await session.abort_transaction()
                        
                    # Check if we should retry
                    if attempt < max_retries - 1 and should_rollback:
                        logger.warning(
                            f"Transaction failed on attempt {attempt + 1}, retrying in {retry_delay}s: {e}"
                        )
                        await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise
                        
                finally:
                    if session:
                        await session.end_session()
                        
            # Should never reach here
            raise ServiceError("Transaction failed after all retries", code="TRANSACTION_FAILED")
            
        return wrapper
    return decorator