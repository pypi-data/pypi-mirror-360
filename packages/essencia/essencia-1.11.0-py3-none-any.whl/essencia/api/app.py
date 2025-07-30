"""
FastAPI application factory with OpenAPI documentation.
"""
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from essencia.core import Config, EssenciaException
from essencia.middleware import (
    SecurityMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    MetricsMiddleware
)
from essencia.monitoring import setup_metrics_endpoint, setup_health_endpoints
from essencia.monitoring.tracing import setup_fastapi_tracing


class AppSettings(BaseModel):
    """Application settings."""
    title: str = "Essencia Medical API"
    description: str = """
    ## Essencia Medical Framework API
    
    A comprehensive REST API for medical applications built with the Essencia framework.
    
    ### Features
    - 🔒 **Secure**: Field-level encryption, RBAC, and comprehensive security
    - 🏥 **Medical Domain**: Complete support for healthcare workflows
    - 🇧🇷 **Brazilian Ready**: CPF/CNPJ validation, SUS integration, ANVISA data
    - 📊 **Monitoring**: Prometheus metrics and OpenTelemetry tracing
    - 🚀 **Performance**: Async operations, intelligent caching
    
    ### Authentication
    Use Bearer token authentication. Get a token from `/auth/login` endpoint.
    
    ### Rate Limiting
    API endpoints are rate-limited. Check `X-RateLimit-*` headers for limits.
    """
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    cors_credentials: bool = True
    cors_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_headers: list[str] = Field(default_factory=lambda: ["*"])
    
    # API settings
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    mongodb_url: str = Field(..., description="MongoDB connection URL")
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_prefix = "ESSENCIA_"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Essencia API...")
    
    # Initialize database connections
    from essencia.database import MongoDB
    app.state.db = MongoDB(app.state.settings.mongodb_url)
    
    # Initialize cache if Redis is configured
    if app.state.settings.redis_url:
        from essencia.cache import AsyncCache
        app.state.cache = AsyncCache()
    
    # Initialize monitoring
    if hasattr(app.state.settings, "monitoring_enabled") and app.state.settings.monitoring_enabled:
        from essencia.monitoring.tracing import init_tracing
        init_tracing(
            service_name="essencia-api",
            service_version=app.state.settings.version,
            exporter_type="otlp",
            endpoint=getattr(app.state.settings, "otlp_endpoint", None)
        )
    
    yield
    
    # Shutdown
    print("Shutting down Essencia API...")
    
    # Close database connections
    if hasattr(app.state, "db"):
        app.state.db.client.close()
    
    # Close cache connections
    if hasattr(app.state, "cache"):
        await app.state.cache.close()


def create_app(settings: Optional[AppSettings] = None) -> FastAPI:
    """Create FastAPI application."""
    if not settings:
        settings = get_app_settings()
    
    # Create app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "auth",
                "description": "Authentication and authorization endpoints"
            },
            {
                "name": "patients",
                "description": "Patient management endpoints"
            },
            {
                "name": "appointments",
                "description": "Appointment scheduling and management"
            },
            {
                "name": "medications",
                "description": "Medication and prescription management"
            },
            {
                "name": "vital-signs",
                "description": "Vital signs recording and monitoring"
            },
            {
                "name": "mental-health",
                "description": "Mental health assessments and tracking"
            },
            {
                "name": "laboratory",
                "description": "Laboratory tests and results"
            },
            {
                "name": "monitoring",
                "description": "System monitoring and health checks"
            },
            {
                "name": "admin",
                "description": "Administrative functions"
            }
        ],
        servers=[
            {
                "url": "https://api.essencia.health",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.essencia.health",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ]
    )
    
    # Store settings
    app.state.settings = settings
    
    # Add middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.rate_limit_requests
        )
    
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)
    
    # Setup monitoring
    setup_metrics_endpoint(app)
    setup_health_endpoints(app)
    setup_fastapi_tracing(app)
    
    # Exception handlers
    @app.exception_handler(EssenciaException)
    async def essencia_exception_handler(request: Request, exc: EssenciaException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.debug else None
            }
        )
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """API root endpoint."""
        return {
            "name": settings.title,
            "version": settings.version,
            "docs": settings.docs_url,
            "health": "/health",
            "metrics": "/metrics"
        }
    
    # Include routers
    from .routers import (
        auth_router,
        patients_router,
        appointments_router,
        medications_router,
        vital_signs_router,
        mental_health_router,
        laboratory_router,
        admin_router
    )
    
    app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(patients_router, prefix=f"{settings.api_prefix}/patients", tags=["patients"])
    app.include_router(appointments_router, prefix=f"{settings.api_prefix}/appointments", tags=["appointments"])
    app.include_router(medications_router, prefix=f"{settings.api_prefix}/medications", tags=["medications"])
    app.include_router(vital_signs_router, prefix=f"{settings.api_prefix}/vital-signs", tags=["vital-signs"])
    app.include_router(mental_health_router, prefix=f"{settings.api_prefix}/mental-health", tags=["mental-health"])
    app.include_router(laboratory_router, prefix=f"{settings.api_prefix}/laboratory", tags=["laboratory"])
    app.include_router(admin_router, prefix=f"{settings.api_prefix}/admin", tags=["admin"])
    
    return app


def get_app_settings() -> AppSettings:
    """Get application settings from environment."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    return AppSettings(
        secret_key=os.getenv("ESSENCIA_SECRET_KEY", "your-secret-key-here"),
        mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017/essencia"),
        redis_url=os.getenv("REDIS_URL"),
        cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )