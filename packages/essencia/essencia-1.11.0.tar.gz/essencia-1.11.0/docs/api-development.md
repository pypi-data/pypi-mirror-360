# API Development Guide

Build robust REST APIs with Essencia's FastAPI integration, complete with automatic OpenAPI documentation, security, and monitoring.

## Table of Contents

1. [Creating Your First API](#creating-your-first-api)
2. [Authentication & Authorization](#authentication--authorization)
3. [Building Endpoints](#building-endpoints)
4. [OpenAPI Documentation](#openapi-documentation)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Monitoring & Metrics](#monitoring--metrics)
8. [Testing APIs](#testing-apis)

## Creating Your First API

### Basic Setup

```python
# main.py
from essencia.api import create_app

# Create FastAPI app with Essencia features
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Custom Configuration

```python
from essencia.api import create_app, AppSettings

# Configure your API
settings = AppSettings(
    title="My Medical API",
    description="Secure medical data API",
    version="2.0.0",
    
    # Security
    secret_key="your-secret-key",
    access_token_expire_minutes=60,
    
    # Database
    mongodb_url="mongodb://localhost:27017/medical_db",
    redis_url="redis://localhost:6379",
    
    # CORS
    cors_origins=["https://app.example.com"],
    
    # Rate limiting
    rate_limit_requests=100,
    rate_limit_window=60
)

app = create_app(settings)
```

## Authentication & Authorization

### JWT Authentication

Essencia uses JWT tokens for authentication:

```python
from fastapi import APIRouter, Depends
from essencia.api.dependencies import get_current_user, require_permission
from essencia.models import User

router = APIRouter()

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """This route requires authentication."""
    return {"user": current_user.email}

@router.get("/admin-only")
async def admin_route(
    current_user: User = Depends(require_permission("admin:read"))
):
    """This route requires admin permission."""
    return {"message": "Admin access granted"}
```

### Login Implementation

```python
# Already included in essencia.api.routers.auth
# POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "securepassword"
}

# Response
{
    "access_token": "eyJ0eXAiOiJKV1Q...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "507f1f77bcf86cd799439011",
        "email": "user@example.com",
        "role": "doctor"
    }
}
```

### Role-Based Access Control

```python
from essencia.api.dependencies import require_role

@router.get("/doctors-only")
async def doctors_only(
    current_user: User = Depends(require_role("doctor"))
):
    """Only doctors can access this."""
    return {"message": "Doctor access granted"}
```

## Building Endpoints

### CRUD Operations

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from essencia.models import MongoModel
from essencia.api.dependencies import get_db, pagination_params

# Define your model
class Patient(MongoModel):
    name: str
    cpf: str
    email: str
    
    class Settings:
        collection_name = "patients"

# Define request/response schemas
class PatientCreate(BaseModel):
    name: str
    cpf: str
    email: str

class PatientResponse(BaseModel):
    id: str
    name: str
    email: str

# Create router
router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    db = Depends(get_db),
    pagination = Depends(pagination_params)
):
    """List all patients with pagination."""
    Patient.set_db(db)
    patients = await Patient.find_many(
        {},
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    return [
        PatientResponse(
            id=str(p.id),
            name=p.name,
            email=p.email
        )
        for p in patients
    ]

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db = Depends(get_db)
):
    """Create a new patient."""
    Patient.set_db(db)
    
    # Check if exists
    existing = await Patient.find_one({"cpf": patient_data.cpf})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient with this CPF already exists"
        )
    
    # Create patient
    patient = Patient(**patient_data.dict())
    await patient.save()
    
    return PatientResponse(
        id=str(patient.id),
        name=patient.name,
        email=patient.email
    )

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db = Depends(get_db)
):
    """Get patient by ID."""
    Patient.set_db(db)
    patient = await Patient.find_by_id(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientResponse(
        id=str(patient.id),
        name=patient.name,
        email=patient.email
    )
```

### Advanced Queries

```python
from essencia.api.dependencies import sorting_params, create_filter_dependency

# Create filter dependency
patient_filters = create_filter_dependency(["city", "state", "has_insurance"])

@router.get("/search", response_model=List[PatientResponse])
async def search_patients(
    q: str = Query(..., description="Search query"),
    filters = Depends(patient_filters),
    sorting = Depends(sorting_params),
    db = Depends(get_db)
):
    """Search patients with filters."""
    Patient.set_db(db)
    
    # Build query
    query = {
        "$and": [
            {"$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}}
            ]},
            filters  # Apply additional filters
        ]
    }
    
    patients = await Patient.find_many(query, sort=sorting.get("sort"))
    return [PatientResponse.from_orm(p) for p in patients]
```

## OpenAPI Documentation

### Automatic Documentation

Essencia automatically generates OpenAPI documentation accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Customizing Documentation

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/medical",
    tags=["medical"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"}
    }
)

@router.post(
    "/vital-signs",
    summary="Record vital signs",
    description="""
    Record patient vital signs including:
    - Blood pressure
    - Temperature
    - Heart rate
    - Oxygen saturation
    
    All measurements are encrypted at rest.
    """,
    response_description="The created vital signs record",
    responses={
        201: {
            "description": "Vital signs recorded",
            "content": {
                "application/json": {
                    "example": {
                        "id": "507f1f77bcf86cd799439011",
                        "patient_id": "507f1f77bcf86cd799439012",
                        "systolic": 120,
                        "diastolic": 80,
                        "temperature": 36.5,
                        "recorded_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def record_vital_signs(data: VitalSignsCreate):
    """Record patient vital signs."""
    pass
```

### Schema Examples

```python
class MedicationCreate(BaseModel):
    """Medication creation schema."""
    name: str = Field(..., example="Losartana")
    dosage: str = Field(..., example="50mg")
    frequency: str = Field(..., example="2x ao dia")
    patient_id: str = Field(..., example="507f1f77bcf86cd799439011")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Losartana",
                "dosage": "50mg",
                "frequency": "2x ao dia",
                "patient_id": "507f1f77bcf86cd799439011"
            }
        }
```

## Error Handling

### Standard Error Responses

```python
from essencia.core import EssenciaException

class PatientNotFound(EssenciaException):
    def __init__(self, patient_id: str):
        super().__init__(
            message=f"Patient {patient_id} not found",
            error_code="PATIENT_NOT_FOUND",
            status_code=404
        )

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    patient = await Patient.find_by_id(patient_id)
    if not patient:
        raise PatientNotFound(patient_id)
    return patient
```

### Global Error Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "VALIDATION_ERROR",
            "message": str(exc),
            "path": request.url.path
        }
    )
```

## Rate Limiting

### Endpoint Rate Limiting

```python
from essencia.api.dependencies import rate_limit

@router.post(
    "/appointments",
    dependencies=[rate_limit(max_requests=5, window_seconds=60)]
)
async def create_appointment(data: AppointmentCreate):
    """Create appointment - limited to 5 per minute."""
    pass
```

### Custom Rate Limits

```python
from essencia.api.dependencies import RateLimitDep

# Different limits for different user types
class CustomRateLimit(RateLimitDep):
    async def __call__(self, request, current_user, cache):
        if current_user.role == "admin":
            self.max_requests = 1000
        elif current_user.role == "doctor":
            self.max_requests = 100
        else:
            self.max_requests = 50
        
        return await super().__call__(request, current_user, cache)
```

## Monitoring & Metrics

### Prometheus Metrics

Metrics are automatically exposed at `/metrics`:

```python
# Custom business metrics
from essencia.monitoring import track_business_metric

@router.post("/appointments")
async def create_appointment(data: AppointmentCreate):
    # Create appointment...
    
    # Track metric
    track_business_metric("appointment_created", {
        "type": data.appointment_type,
        "specialty": data.specialty
    })
```

### OpenTelemetry Tracing

```python
from essencia.monitoring.tracing import trace_async

@trace_async("appointment_creation")
async def create_appointment_with_notifications(data: AppointmentCreate):
    # Create appointment
    appointment = await create_appointment(data)
    
    # Send notifications (traced separately)
    await send_email_notification(appointment)
    await send_sms_notification(appointment)
    
    return appointment
```

### Health Checks

```python
from essencia.monitoring import register_health_check

async def check_external_api():
    """Check if external API is available."""
    try:
        response = await httpx.get("https://api.example.com/health")
        return response.status_code == 200
    except:
        return False

register_health_check("external_api", check_external_api)
```

## Testing APIs

### Unit Testing

```python
import pytest
from httpx import AsyncClient
from essencia.api import create_app

@pytest.fixture
async def client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_patient(client, mock_db):
    response = await client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "cpf": "123.456.789-00",
            "email": "test@example.com"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Patient"
```

### Integration Testing

```python
@pytest.mark.integration
async def test_patient_workflow(client, test_db):
    # 1. Create patient
    create_response = await client.post("/api/v1/patients", json={...})
    patient_id = create_response.json()["id"]
    
    # 2. Record vital signs
    vitals_response = await client.post(
        f"/api/v1/patients/{patient_id}/vital-signs",
        json={"systolic": 120, "diastolic": 80}
    )
    
    # 3. Get patient timeline
    timeline_response = await client.get(
        f"/api/v1/patients/{patient_id}/timeline"
    )
    
    assert len(timeline_response.json()["events"]) == 1
```

## Best Practices

1. **Use Dependency Injection**: Leverage FastAPI's dependency system
2. **Validate Everything**: Use Pydantic models for request/response validation
3. **Document Thoroughly**: Add descriptions and examples to your endpoints
4. **Handle Errors Gracefully**: Use appropriate HTTP status codes
5. **Version Your API**: Include version in URL (e.g., `/api/v1/`)
6. **Use Async**: Take advantage of async/await for better performance
7. **Monitor Everything**: Use metrics and tracing for observability
8. **Test Comprehensively**: Write both unit and integration tests

## Next Steps

- [Security Guide](./security.md) - Deep dive into API security
- [Deployment Guide](./deployment.md) - Deploy your API to production
- [Performance Guide](./performance.md) - Optimize API performance
- [Examples](./examples/api-examples.md) - Complete API examples