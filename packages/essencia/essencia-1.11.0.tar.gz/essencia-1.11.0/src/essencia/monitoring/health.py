"""
Health check system for monitoring application components.
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import psutil
import httpx

from essencia.database import MongoDB, Database
from essencia.cache import AsyncCache


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a component."""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    last_check: datetime = None
    response_time_ms: Optional[float] = None
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = datetime.now()


class HealthCheck:
    """Health check system for application monitoring."""
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._results: Dict[str, ComponentHealth] = {}
        self._check_interval = timedelta(seconds=30)
        self._last_full_check = datetime.min
    
    def register(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self._checks[name] = check_func
    
    async def check_component(self, name: str) -> ComponentHealth:
        """Check health of a specific component."""
        if name not in self._checks:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"No health check registered for {name}"
            )
        
        start_time = datetime.now()
        try:
            check_func = self._checks[name]
            
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = None
                details = None
            elif isinstance(result, dict):
                status = result.get("status", HealthStatus.HEALTHY)
                message = result.get("message")
                details = result.get("details")
            else:
                status = HealthStatus.HEALTHY
                message = str(result) if result else None
                details = None
            
            return ComponentHealth(
                name=name,
                status=status,
                message=message,
                details=details,
                response_time_ms=response_time
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time
            )
    
    async def check_all(self, force: bool = False) -> Dict[str, ComponentHealth]:
        """Check health of all registered components."""
        # Use cached results if recent enough
        if not force and (datetime.now() - self._last_full_check) < self._check_interval:
            return self._results
        
        # Run all health checks concurrently
        tasks = []
        for name in self._checks:
            tasks.append(self.check_component(name))
        
        results = await asyncio.gather(*tasks)
        
        # Update results
        self._results = {result.name: result for result in results}
        self._last_full_check = datetime.now()
        
        return self._results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self._results:
            return HealthStatus.UNHEALTHY
        
        statuses = [result.status for result in self._results.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check results to dictionary."""
        return {
            "status": self.get_overall_status(),
            "timestamp": datetime.now().isoformat(),
            "components": {
                name: {
                    "status": health.status,
                    "message": health.message,
                    "details": health.details,
                    "last_check": health.last_check.isoformat(),
                    "response_time_ms": health.response_time_ms
                }
                for name, health in self._results.items()
            }
        }


# Global health check instance
_health_check = HealthCheck()


# Default health checks
async def check_database_health() -> Dict[str, Any]:
    """Check MongoDB health."""
    try:
        import os
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Ping database
        await client.admin.command('ping')
        
        # Get server info
        info = await client.server_info()
        
        return {
            "status": HealthStatus.HEALTHY,
            "details": {
                "version": info.get("version"),
                "uptime": info.get("uptime")
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


def check_redis_health() -> Dict[str, Any]:
    """Check Redis health."""
    try:
        import os
        import redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        client = redis.from_url(redis_url, socket_connect_timeout=5)
        
        # Ping Redis
        client.ping()
        
        # Get info
        info = client.info()
        
        return {
            "status": HealthStatus.HEALTHY,
            "details": {
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human")
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


def check_disk_space() -> Dict[str, Any]:
    """Check disk space usage."""
    try:
        usage = psutil.disk_usage('/')
        
        # Determine status based on usage
        if usage.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Disk usage critical: {usage.percent}%"
        elif usage.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Disk usage high: {usage.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = None
        
        return {
            "status": status,
            "message": message,
            "details": {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        
        # Determine status based on usage
        if memory.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Memory usage critical: {memory.percent}%"
        elif memory.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"Memory usage high: {memory.percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = None
        
        return {
            "status": status,
            "message": message,
            "details": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


def check_cpu_usage() -> Dict[str, Any]:
    """Check CPU usage."""
    try:
        # Get CPU usage over 1 second
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Determine status
        if cpu_percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"CPU usage critical: {cpu_percent}%"
        elif cpu_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"CPU usage high: {cpu_percent}%"
        else:
            status = HealthStatus.HEALTHY
            message = None
        
        return {
            "status": status,
            "message": message,
            "details": {
                "percent": cpu_percent,
                "core_count": psutil.cpu_count()
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


async def check_external_service(url: str, timeout: int = 5) -> Dict[str, Any]:
    """Check external service availability."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return {
                    "status": HealthStatus.HEALTHY,
                    "details": {
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"Service returned {response.status_code}",
                    "details": {
                        "status_code": response.status_code
                    }
                }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": str(e)
        }


# Register default health checks
_health_check.register("database", check_database_health)
_health_check.register("redis", check_redis_health)
_health_check.register("disk_space", check_disk_space)
_health_check.register("memory", check_memory_usage)
_health_check.register("cpu", check_cpu_usage)


# Public API
def register_health_check(name: str, check_func: Callable):
    """Register a custom health check."""
    _health_check.register(name, check_func)


async def get_health_status(force: bool = False) -> Dict[str, Any]:
    """Get current health status."""
    await _health_check.check_all(force=force)
    return _health_check.to_dict()


# FastAPI integration
def setup_health_endpoints(app):
    """Setup health check endpoints for FastAPI."""
    from fastapi import Response, status
    
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        health_data = await get_health_status()
        
        # Determine HTTP status based on health
        overall_status = health_data["status"]
        if overall_status == HealthStatus.HEALTHY:
            http_status = status.HTTP_200_OK
        elif overall_status == HealthStatus.DEGRADED:
            http_status = status.HTTP_200_OK  # Still return 200 for degraded
        else:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(
            content=health_data,
            status_code=http_status,
            media_type="application/json"
        )
    
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe endpoint."""
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe endpoint."""
        health_data = await get_health_status()
        
        if health_data["status"] == HealthStatus.HEALTHY:
            return {"status": "ready"}
        else:
            return Response(
                content={"status": "not ready"},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )