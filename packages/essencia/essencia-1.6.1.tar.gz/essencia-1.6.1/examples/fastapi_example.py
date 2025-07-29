"""
Example FastAPI application using Essencia framework.

This example demonstrates:
- FastAPI app factory pattern
- CRUD routers for models
- Authentication and authorization
- WebSocket support
- Integration with Essencia services
"""

import asyncio
from typing import List

from fastapi import FastAPI, Depends, WebSocket, HTTPException
from pydantic import BaseModel

# Import from essencia
from essencia import (
    create_app,
    FastAPIConfig,
    APISettings,
    CRUDRouter,
    AuthRouter,
    WebSocketManager,
    get_current_user,
    require_role,
)
from essencia.web.dependencies import get_model_service
from essencia.models import User
from essencia.core import Config


# Example Pydantic models for API
class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    priority: str = None
    completed: bool = None


# Example custom router
class TaskRouter(CRUDRouter):
    """Custom router for tasks with additional endpoints."""
    
    def setup_routes(self):
        # Call parent to setup standard CRUD routes
        super().setup_routes()
        
        # Add custom routes
        @self.router.get("/my-tasks")
        async def get_my_tasks(
            user=Depends(get_current_user),
            service=Depends(get_model_service(self.model_class))
        ):
            """Get current user's tasks."""
            tasks = await service.find_many({"creator": str(user.id)})
            return [task.model_dump() for task in tasks]
        
        @self.router.post("/{task_id}/complete")
        async def complete_task(
            task_id: str,
            user=Depends(get_current_user),
            service=Depends(get_model_service(self.model_class))
        ):
            """Mark task as completed."""
            task = await service.update(
                {"_id": task_id, "creator": str(user.id)},
                {"completed": True}
            )
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task.model_dump()


def create_example_app() -> FastAPI:
    """Create example FastAPI application with Essencia."""
    
    # Configure API settings
    api_settings = APISettings(
        title="Essencia Example API",
        description="Example API using Essencia framework",
        version="1.0.0",
        # Security
        secret_key="your-secret-key-here",
        access_token_expire_minutes=60,
        # CORS
        allow_origins=["http://localhost:3000", "http://localhost:8080"],
        # Rate limiting
        rate_limit_enabled=True,
        rate_limit_calls=100,
        rate_limit_period=60,
    )
    
    # Create routers
    auth_router = AuthRouter(prefix="/api/auth", tags=["authentication"])
    
    # Example: CRUD router for a Task model
    # task_router = TaskRouter(
    #     Task,  # Your Task model
    #     prefix="/api/tasks",
    #     create_schema=TaskCreate,
    #     update_schema=TaskUpdate,
    # )
    
    # User management (admin only)
    user_router = CRUDRouter(
        User,
        prefix="/api/users",
        tags=["users"],
        dependencies=[Depends(require_role(["admin"]))]
    )
    
    # WebSocket manager
    ws_manager = WebSocketManager()
    
    # Configure app
    config = FastAPIConfig(
        api_settings=api_settings,
        routers=[
            auth_router.get_router(),
            # task_router.get_router(),
            user_router.get_router(),
        ],
        essencia_config=Config(),  # Essencia configuration
    )
    
    # Create app
    app = create_app(config)
    
    # Add WebSocket endpoint
    @app.websocket("/ws/{channel}")
    async def websocket_endpoint(
        websocket: WebSocket,
        channel: str,
        token: str = None
    ):
        """WebSocket endpoint for real-time communication."""
        from essencia.web.websocket import websocket_endpoint as ws_handler
        await ws_handler(websocket, ws_manager, channel, token)
    
    # Add custom startup/shutdown handlers
    @app.on_event("startup")
    async def startup():
        """Initialize services on startup."""
        print("Starting Essencia Example API...")
        # Initialize database connections, etc.
    
    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup on shutdown."""
        print("Shutting down Essencia Example API...")
        # Close database connections, etc.
    
    # Add custom endpoints
    @app.get("/api/stats", tags=["monitoring"])
    async def get_stats(user=Depends(require_role(["admin"]))):
        """Get application statistics (admin only)."""
        return {
            "websocket_stats": ws_manager.get_stats(),
            "api_version": api_settings.version,
            # Add more stats here
        }
    
    return app


# For running with uvicorn
app = create_example_app()


if __name__ == "__main__":
    # Run with uvicorn
    import uvicorn
    
    uvicorn.run(
        "fastapi_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )