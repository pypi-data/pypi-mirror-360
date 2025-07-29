"""
FastAPI application factory and configuration.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from ..core.config import Config
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers


@dataclass
class APISettings:
    """API-specific settings."""
    title: str = "Essencia API"
    description: str = "Medical and Business Application Framework"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS settings
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = field(default_factory=lambda: ["*"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Security settings
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    
    # Static files
    static_enabled: bool = False
    static_path: str = "/static"
    static_directory: str = "static"


@dataclass
class FastAPIConfig:
    """FastAPI application configuration."""
    api_settings: APISettings = field(default_factory=APISettings)
    routers: List[APIRouter] = field(default_factory=list)
    middleware: List[tuple] = field(default_factory=list)
    exception_handlers: Dict[int, Callable] = field(default_factory=dict)
    on_startup: List[Callable] = field(default_factory=list)
    on_shutdown: List[Callable] = field(default_factory=list)
    dependencies: List[Any] = field(default_factory=list)
    
    # Integration with essencia Config
    essencia_config: Optional[Config] = None


def create_app(config: Optional[FastAPIConfig] = None) -> FastAPI:
    """
    Create and configure a FastAPI application.
    
    Args:
        config: FastAPI configuration object
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = FastAPIConfig()
    
    # Create FastAPI instance
    app = FastAPI(
        title=config.api_settings.title,
        description=config.api_settings.description,
        version=config.api_settings.version,
        docs_url=config.api_settings.docs_url,
        redoc_url=config.api_settings.redoc_url,
        openapi_url=config.api_settings.openapi_url,
        dependencies=config.dependencies,
    )
    
    # Store config in app state
    app.state.config = config
    app.state.essencia_config = config.essencia_config
    
    # Setup CORS
    if config.api_settings.allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.api_settings.allow_origins,
            allow_credentials=config.api_settings.allow_credentials,
            allow_methods=config.api_settings.allow_methods,
            allow_headers=config.api_settings.allow_headers,
        )
    
    # Setup session middleware
    if config.api_settings.secret_key:
        app.add_middleware(
            SessionMiddleware,
            secret_key=config.api_settings.secret_key
        )
    
    # Setup custom middleware
    setup_middleware(app, config)
    
    # Setup exception handlers
    setup_exception_handlers(app, config.exception_handlers)
    
    # Add routers
    for router in config.routers:
        app.include_router(router)
    
    # Setup static files
    if config.api_settings.static_enabled:
        app.mount(
            config.api_settings.static_path,
            StaticFiles(directory=config.api_settings.static_directory),
            name="static"
        )
    
    # Register startup handlers
    for handler in config.on_startup:
        app.add_event_handler("startup", handler)
    
    # Register shutdown handlers
    for handler in config.on_shutdown:
        app.add_event_handler("shutdown", handler)
    
    # Add health check endpoint
    @app.get("/health", tags=["system"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": config.api_settings.title}
    
    # Add version endpoint
    @app.get("/version", tags=["system"])
    async def version():
        """Version information endpoint."""
        return {
            "version": config.api_settings.version,
            "api": config.api_settings.title,
            "framework": "essencia",
            "framework_version": "1.5.0"
        }
    
    return app


# Convenience function for creating Flet-compatible FastAPI app
def create_flet_app(
    title: str = "Essencia Flet App",
    essencia_config: Optional[Config] = None,
    **kwargs
) -> FastAPI:
    """
    Create a FastAPI app configured for Flet integration.
    
    Args:
        title: Application title
        essencia_config: Essencia configuration object
        **kwargs: Additional API settings
        
    Returns:
        FastAPI application configured for Flet
    """
    api_settings = APISettings(
        title=title,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        **kwargs
    )
    
    config = FastAPIConfig(
        api_settings=api_settings,
        essencia_config=essencia_config
    )
    
    return create_app(config)