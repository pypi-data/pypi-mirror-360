"""
Patient management endpoints.
"""
from typing import Annotated, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

from essencia.models import User
from essencia.api.dependencies import (
    get_db,
    get_current_user,
    require_permission,
    pagination_params,
    sorting_params,
    rate_limit
)
from essencia.integrations.sus import SUSPatient


router = APIRouter()


class PatientCreate(BaseModel):
    """Patient creation request."""
    full_name: str = Field(..., example="Maria Santos")
    cpf: str = Field(..., example="123.456.789-00")
    birth_date: date = Field(..., example="1990-01-15")
    phone: Optional[str] = Field(None, example="(11) 98765-4321")
    email: Optional[str] = Field(None, example="maria@example.com")
    
    # Address
    street: str = Field(..., example="Rua das Flores")
    number: str = Field(..., example="123")
    complement: Optional[str] = Field(None, example="Apto 45")
    neighborhood: str = Field(..., example="Centro")
    city: str = Field(..., example="São Paulo")
    state: str = Field(..., example="SP")
    cep: str = Field(..., example="01234-567")
    
    # Medical info
    blood_type: Optional[str] = Field(None, example="O+")
    allergies: List[str] = Field(default_factory=list, example=["Penicilina"])
    chronic_conditions: List[str] = Field(default_factory=list, example=["Hipertensão"])
    
    # SUS info
    cns: Optional[str] = Field(None, example="123456789012345")
    mother_name: str = Field(..., example="Ana Santos")
    father_name: Optional[str] = Field(None, example="José Santos")


class PatientUpdate(BaseModel):
    """Patient update request."""
    phone: Optional[str] = None
    email: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    cep: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None


class PatientResponse(BaseModel):
    """Patient response model."""
    id: str
    full_name: str
    cpf: str
    birth_date: date
    age: int
    phone: Optional[str]
    email: Optional[str]
    city: str
    state: str
    blood_type: Optional[str]
    allergies: List[str]
    chronic_conditions: List[str]
    cns: Optional[str]
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@router.get("/", response_model=List[PatientResponse], summary="List patients")
async def list_patients(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:read"))],
    pagination: Annotated[dict, Depends(pagination_params)],
    sorting: Annotated[dict, Depends(sorting_params)],
    search: Optional[str] = Query(None, description="Search by name or CPF"),
    city: Optional[str] = Query(None, description="Filter by city"),
    has_chronic_conditions: Optional[bool] = Query(None, description="Filter by chronic conditions")
) -> List[PatientResponse]:
    """
    List patients with pagination and filters.
    
    Requires `patients:read` permission.
    
    **Search options:**
    - `search`: Search by name or CPF
    - `city`: Filter by city
    - `has_chronic_conditions`: Filter patients with chronic conditions
    """
    SUSPatient.set_db(db)
    
    # Build filter
    filter_query = {}
    
    if search:
        filter_query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"cpf": search}
        ]
    
    if city:
        filter_query["city"] = city
    
    if has_chronic_conditions is not None:
        if has_chronic_conditions:
            filter_query["chronic_conditions"] = {"$ne": []}
        else:
            filter_query["chronic_conditions"] = []
    
    # Get patients
    patients = await SUSPatient.find_many(
        filter_query,
        skip=pagination["skip"],
        limit=pagination["limit"],
        sort=sorting.get("sort")
    )
    
    # Convert to response
    return [
        PatientResponse(
            id=str(patient.id),
            full_name=patient.full_name,
            cpf=patient.cpf.get_secret_value() if hasattr(patient.cpf, 'get_secret_value') else patient.cpf,
            birth_date=patient.birth_date,
            age=patient.get_age(),
            phone=patient.phone,
            email=patient.email,
            city=patient.city,
            state=patient.state,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            chronic_conditions=patient.chronic_conditions,
            cns=patient.cns.get_secret_value() if patient.cns and hasattr(patient.cns, 'get_secret_value') else patient.cns,
            created_at=patient.registration_date
        )
        for patient in patients
    ]


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, summary="Create patient")
@rate_limit(max_requests=10, window_seconds=60)
async def create_patient(
    patient_data: PatientCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:write"))]
) -> PatientResponse:
    """
    Create a new patient record.
    
    Requires `patients:write` permission.
    Rate limited to 10 requests per minute.
    """
    from essencia.utils.validators import validate_cpf
    from essencia.integrations.sus import SUSCardStatus
    
    # Validate CPF
    if not validate_cpf(patient_data.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CPF"
        )
    
    # Check if patient already exists
    SUSPatient.set_db(db)
    existing = await SUSPatient.find_one({"cpf": patient_data.cpf})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient with this CPF already exists"
        )
    
    # Create patient
    patient = SUSPatient(
        full_name=patient_data.full_name,
        cpf=patient_data.cpf,
        cns=patient_data.cns,
        cns_status=SUSCardStatus.ACTIVE if patient_data.cns else None,
        birth_date=patient_data.birth_date,
        birth_city=patient_data.city,
        birth_state=patient_data.state,
        mother_name=patient_data.mother_name,
        father_name=patient_data.father_name,
        phone=patient_data.phone,
        email=patient_data.email,
        street=patient_data.street,
        number=patient_data.number,
        complement=patient_data.complement,
        neighborhood=patient_data.neighborhood,
        city=patient_data.city,
        state=patient_data.state,
        cep=patient_data.cep,
        blood_type=patient_data.blood_type,
        allergies=patient_data.allergies,
        chronic_conditions=patient_data.chronic_conditions
    )
    
    await patient.save()
    
    return PatientResponse(
        id=str(patient.id),
        full_name=patient.full_name,
        cpf=patient.cpf.get_secret_value(),
        birth_date=patient.birth_date,
        age=patient.get_age(),
        phone=patient.phone,
        email=patient.email,
        city=patient.city,
        state=patient.state,
        blood_type=patient.blood_type,
        allergies=patient.allergies,
        chronic_conditions=patient.chronic_conditions,
        cns=patient.cns.get_secret_value() if patient.cns else None,
        created_at=patient.registration_date
    )


@router.get("/{patient_id}", response_model=PatientResponse, summary="Get patient by ID")
async def get_patient(
    patient_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:read"))]
) -> PatientResponse:
    """
    Get patient details by ID.
    
    Requires `patients:read` permission.
    """
    SUSPatient.set_db(db)
    patient = await SUSPatient.find_by_id(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientResponse(
        id=str(patient.id),
        full_name=patient.full_name,
        cpf=patient.cpf.get_secret_value(),
        birth_date=patient.birth_date,
        age=patient.get_age(),
        phone=patient.phone,
        email=patient.email,
        city=patient.city,
        state=patient.state,
        blood_type=patient.blood_type,
        allergies=patient.allergies,
        chronic_conditions=patient.chronic_conditions,
        cns=patient.cns.get_secret_value() if patient.cns else None,
        created_at=patient.registration_date
    )


@router.put("/{patient_id}", response_model=PatientResponse, summary="Update patient")
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:write"))]
) -> PatientResponse:
    """
    Update patient information.
    
    Requires `patients:write` permission.
    """
    SUSPatient.set_db(db)
    patient = await SUSPatient.find_by_id(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update fields
    update_data = patient_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    patient.last_update = datetime.now()
    await patient.save()
    
    return PatientResponse(
        id=str(patient.id),
        full_name=patient.full_name,
        cpf=patient.cpf.get_secret_value(),
        birth_date=patient.birth_date,
        age=patient.get_age(),
        phone=patient.phone,
        email=patient.email,
        city=patient.city,
        state=patient.state,
        blood_type=patient.blood_type,
        allergies=patient.allergies,
        chronic_conditions=patient.chronic_conditions,
        cns=patient.cns.get_secret_value() if patient.cns else None,
        created_at=patient.registration_date
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete patient")
async def delete_patient(
    patient_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:delete"))]
):
    """
    Delete patient record.
    
    Requires `patients:delete` permission.
    
    **Warning**: This action cannot be undone.
    """
    SUSPatient.set_db(db)
    patient = await SUSPatient.find_by_id(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    await patient.delete()


@router.get("/{patient_id}/timeline", summary="Get patient timeline")
async def get_patient_timeline(
    patient_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("patients:read"))],
    days: int = Query(30, description="Number of days to include")
) -> dict:
    """
    Get patient's medical timeline including appointments, medications, and vital signs.
    
    Requires `patients:read` permission.
    """
    # This would aggregate data from multiple collections
    # For now, return a sample structure
    return {
        "patient_id": patient_id,
        "period_days": days,
        "timeline": [
            {
                "date": "2024-01-15",
                "events": [
                    {
                        "type": "appointment",
                        "time": "09:00",
                        "description": "Consulta com Dr. Silva",
                        "specialty": "Cardiologia"
                    },
                    {
                        "type": "medication",
                        "time": "08:00",
                        "description": "Losartana 50mg",
                        "action": "administered"
                    }
                ]
            }
        ],
        "summary": {
            "total_appointments": 5,
            "medications_administered": 45,
            "vital_signs_recorded": 15
        }
    }


from datetime import datetime

# Add method to SUSPatient model
def get_age(self) -> int:
    """Calculate patient age."""
    today = date.today()
    return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

# Monkey patch the method (in production, add to the model directly)
SUSPatient.get_age = get_age