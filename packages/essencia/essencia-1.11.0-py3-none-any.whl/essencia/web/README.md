# Essencia Web Module

The `essencia.web` module provides FastAPI integration for building modern web APIs with the Essencia framework. It includes app factory patterns, automatic CRUD routers, WebSocket support, and comprehensive security features.

## Features

- **FastAPI App Factory**: Create configured FastAPI applications with a single function call
- **CRUD Routers**: Automatic REST API generation for MongoModel subclasses
- **WebSocket Support**: Real-time communication with channel-based WebSocket management
- **Authentication & Authorization**: Built-in JWT authentication with role-based access control
- **Middleware Stack**: Logging, security headers, rate limiting, and performance monitoring
- **Dependency Injection**: Reusable dependencies for database, cache, and authentication
- **Exception Handling**: Comprehensive error handling with standardized responses

## Quick Start

```python
from essencia import create_app, FastAPIConfig, APISettings, CRUDRouter
from essencia.models import User

# Configure API
api_settings = APISettings(
    title="My API",
    secret_key="your-secret-key",
    rate_limit_enabled=True
)

# Create CRUD router for User model
user_router = CRUDRouter(User, prefix="/api/users")

# Configure app
config = FastAPIConfig(
    api_settings=api_settings,
    routers=[user_router.get_router()]
)

# Create FastAPI app
app = create_app(config)
```

## CRUD Router

The `CRUDRouter` automatically generates RESTful endpoints for any MongoModel:

```python
from essencia import CRUDRouter
from myapp.models import Task

# Basic CRUD router
task_router = CRUDRouter(Task, prefix="/api/tasks")

# With authentication required
task_router = CRUDRouter(
    Task,
    prefix="/api/tasks",
    require_authentication=True
)

# With custom schemas
task_router = CRUDRouter(
    Task,
    create_schema=TaskCreate,
    update_schema=TaskUpdate,
    response_schema=TaskResponse
)
```

Generated endpoints:
- `GET /api/tasks` - List tasks with pagination
- `GET /api/tasks/{id}` - Get single task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## WebSocket Support

Real-time communication with channel-based WebSocket management:

```python
from essencia import WebSocketManager

# Create WebSocket manager
ws_manager = WebSocketManager()

# Add WebSocket endpoint
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_message(websocket, data, channel)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
```

## Authentication

Built-in JWT authentication with customizable OAuth2 flow:

```python
from essencia import require_auth, require_role, get_current_user

# Require authentication
@app.get("/protected")
async def protected_route(user=Depends(require_auth)):
    return {"user": user.email}

# Require specific role
@app.get("/admin")
async def admin_route(user=Depends(require_role(["admin"]))):
    return {"message": "Admin access granted"}

# Optional authentication
@app.get("/public")
async def public_route(user=Depends(get_current_user)):
    if user:
        return {"message": f"Hello {user.name}"}
    return {"message": "Hello anonymous"}
```

## Middleware

The web module includes several middleware components:

### Security Middleware
```python
# Automatically adds security headers:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection: 1; mode=block
# - Strict-Transport-Security (HSTS)
```

### Rate Limiting
```python
api_settings = APISettings(
    rate_limit_enabled=True,
    rate_limit_calls=100,  # 100 calls
    rate_limit_period=60   # per 60 seconds
)
```

### Logging & Performance
```python
# Automatic request/response logging
# Performance monitoring for slow requests
# Audit trail for API access
```

## Flet Integration

Special support for Flet applications:

```python
from essencia import create_flet_app

# Create FastAPI app configured for Flet
app = create_flet_app(
    title="My Flet App",
    essencia_config=config
)

# Use with Flet
import flet as ft

def main(page: ft.Page):
    # Your Flet app code
    pass

ft.app(target=main, fastapi_app=app)
```

## Custom Routers

Extend `BaseRouter` or `CRUDRouter` for custom functionality:

```python
from essencia import CRUDRouter

class TaskRouter(CRUDRouter):
    def setup_routes(self):
        # Include standard CRUD routes
        super().setup_routes()
        
        # Add custom endpoints
        @self.router.get("/my-tasks")
        async def get_my_tasks(user=Depends(get_current_user)):
            tasks = await self.service.find_many({"creator": user.id})
            return tasks
        
        @self.router.post("/{id}/complete")
        async def complete_task(id: str):
            return await self.service.update(id, {"completed": True})
```

## Error Handling

Standardized error responses with custom exception types:

```python
from essencia.web import ValidationException, PermissionException

@app.post("/items")
async def create_item(data: dict):
    if not data.get("name"):
        raise ValidationException("Name is required")
    
    if not user.can_create_items:
        raise PermissionException("You cannot create items")
```

## Configuration

Full configuration options:

```python
api_settings = APISettings(
    # Basic settings
    title="My API",
    description="API Description",
    version="1.0.0",
    
    # Documentation
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    
    # CORS
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
    # Security
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    
    # Rate limiting
    rate_limit_enabled=True,
    rate_limit_calls=100,
    rate_limit_period=60,
    
    # Static files
    static_enabled=True,
    static_path="/static",
    static_directory="static"
)
```

## Running the Application

```python
# Development
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# Production
uvicorn.run("myapp:app", host="0.0.0.0", port=8000, workers=4)
```

## Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_item():
    response = client.post("/api/items", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```