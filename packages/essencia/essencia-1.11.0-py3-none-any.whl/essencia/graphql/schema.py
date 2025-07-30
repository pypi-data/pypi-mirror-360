"""
GraphQL schema definition for Essencia.
"""
import strawberry
from typing import List, Optional, Any
from datetime import datetime, date
from strawberry.types import Info

from .types import (
    Patient, PatientInput, PatientFilter,
    VitalSigns, VitalSignsInput,
    Medication, MedicationInput,
    Appointment, AppointmentInput,
    User, LoginInput, LoginResponse
)
from .resolvers import (
    PatientResolver,
    VitalSignsResolver,
    MedicationResolver,
    AppointmentResolver,
    AuthResolver
)


@strawberry.type
class Query:
    """GraphQL Query root."""
    
    # Patient queries
    @strawberry.field
    async def patients(
        self,
        info: Info,
        filter: Optional[PatientFilter] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Patient]:
        """List patients with optional filtering."""
        resolver = PatientResolver(info.context)
        return await resolver.list_patients(filter, limit, offset)
    
    @strawberry.field
    async def patient(self, info: Info, id: str) -> Optional[Patient]:
        """Get patient by ID."""
        resolver = PatientResolver(info.context)
        return await resolver.get_patient(id)
    
    @strawberry.field
    async def search_patients(self, info: Info, query: str) -> List[Patient]:
        """Search patients by name or CPF."""
        resolver = PatientResolver(info.context)
        return await resolver.search_patients(query)
    
    # Vital signs queries
    @strawberry.field
    async def vital_signs(
        self,
        info: Info,
        patient_id: str,
        limit: int = 100
    ) -> List[VitalSigns]:
        """Get vital signs for a patient."""
        resolver = VitalSignsResolver(info.context)
        return await resolver.get_patient_vital_signs(patient_id, limit)
    
    @strawberry.field
    async def latest_vital_signs(
        self,
        info: Info,
        patient_id: str
    ) -> Optional[VitalSigns]:
        """Get latest vital signs for a patient."""
        resolver = VitalSignsResolver(info.context)
        return await resolver.get_latest_vital_signs(patient_id)
    
    # Medication queries
    @strawberry.field
    async def medications(
        self,
        info: Info,
        patient_id: str,
        active_only: bool = True
    ) -> List[Medication]:
        """Get medications for a patient."""
        resolver = MedicationResolver(info.context)
        return await resolver.get_patient_medications(patient_id, active_only)
    
    @strawberry.field
    async def medication_schedule(
        self,
        info: Info,
        patient_id: str,
        date: date
    ) -> List[Any]:
        """Get medication schedule for a specific date."""
        resolver = MedicationResolver(info.context)
        return await resolver.get_daily_schedule(patient_id, date)
    
    # Appointment queries
    @strawberry.field
    async def appointments(
        self,
        info: Info,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get appointments with filters."""
        resolver = AppointmentResolver(info.context)
        return await resolver.list_appointments(
            patient_id, doctor_id, date_from, date_to
        )
    
    @strawberry.field
    async def appointment(self, info: Info, id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        resolver = AppointmentResolver(info.context)
        return await resolver.get_appointment(id)
    
    # User queries
    @strawberry.field
    async def me(self, info: Info) -> Optional[User]:
        """Get current authenticated user."""
        resolver = AuthResolver(info.context)
        return await resolver.get_current_user()
    
    @strawberry.field
    async def user(self, info: Info, id: str) -> Optional[User]:
        """Get user by ID (requires permission)."""
        resolver = AuthResolver(info.context)
        return await resolver.get_user(id)


@strawberry.type
class Mutation:
    """GraphQL Mutation root."""
    
    # Authentication mutations
    @strawberry.mutation
    async def login(self, info: Info, input: LoginInput) -> LoginResponse:
        """Authenticate user and get access token."""
        resolver = AuthResolver(info.context)
        return await resolver.login(input.email, input.password)
    
    @strawberry.mutation
    async def logout(self, info: Info) -> bool:
        """Logout current user."""
        resolver = AuthResolver(info.context)
        return await resolver.logout()
    
    # Patient mutations
    @strawberry.mutation
    async def create_patient(
        self,
        info: Info,
        input: PatientInput
    ) -> Patient:
        """Create a new patient."""
        resolver = PatientResolver(info.context)
        return await resolver.create_patient(input)
    
    @strawberry.mutation
    async def update_patient(
        self,
        info: Info,
        id: str,
        input: PatientInput
    ) -> Patient:
        """Update patient information."""
        resolver = PatientResolver(info.context)
        return await resolver.update_patient(id, input)
    
    @strawberry.mutation
    async def delete_patient(self, info: Info, id: str) -> bool:
        """Delete a patient."""
        resolver = PatientResolver(info.context)
        return await resolver.delete_patient(id)
    
    # Vital signs mutations
    @strawberry.mutation
    async def record_vital_signs(
        self,
        info: Info,
        input: VitalSignsInput
    ) -> VitalSigns:
        """Record new vital signs."""
        resolver = VitalSignsResolver(info.context)
        return await resolver.record_vital_signs(input)
    
    # Medication mutations
    @strawberry.mutation
    async def prescribe_medication(
        self,
        info: Info,
        input: MedicationInput
    ) -> Medication:
        """Prescribe a new medication."""
        resolver = MedicationResolver(info.context)
        return await resolver.prescribe_medication(input)
    
    @strawberry.mutation
    async def update_medication(
        self,
        info: Info,
        id: str,
        input: MedicationInput
    ) -> Medication:
        """Update medication details."""
        resolver = MedicationResolver(info.context)
        return await resolver.update_medication(id, input)
    
    @strawberry.mutation
    async def discontinue_medication(
        self,
        info: Info,
        id: str,
        reason: str
    ) -> Medication:
        """Discontinue a medication."""
        resolver = MedicationResolver(info.context)
        return await resolver.discontinue_medication(id, reason)
    
    # Appointment mutations
    @strawberry.mutation
    async def schedule_appointment(
        self,
        info: Info,
        input: AppointmentInput
    ) -> Appointment:
        """Schedule a new appointment."""
        resolver = AppointmentResolver(info.context)
        return await resolver.schedule_appointment(input)
    
    @strawberry.mutation
    async def update_appointment(
        self,
        info: Info,
        id: str,
        input: AppointmentInput
    ) -> Appointment:
        """Update appointment details."""
        resolver = AppointmentResolver(info.context)
        return await resolver.update_appointment(id, input)
    
    @strawberry.mutation
    async def cancel_appointment(
        self,
        info: Info,
        id: str,
        reason: str
    ) -> Appointment:
        """Cancel an appointment."""
        resolver = AppointmentResolver(info.context)
        return await resolver.cancel_appointment(id, reason)


@strawberry.type
class Subscription:
    """GraphQL Subscription root for real-time updates."""
    
    @strawberry.subscription
    async def vital_signs_updates(
        self,
        info: Info,
        patient_id: str
    ) -> VitalSigns:
        """Subscribe to vital signs updates for a patient."""
        # Implementation would use WebSockets
        # This is a placeholder for the subscription
        import asyncio
        while True:
            await asyncio.sleep(5)
            # In real implementation, yield new vital signs when recorded
            yield VitalSigns(
                id="sample",
                patient_id=patient_id,
                recorded_at=datetime.now(),
                systolic=120,
                diastolic=80,
                heart_rate=72,
                temperature=36.5,
                oxygen_saturation=98
            )
    
    @strawberry.subscription
    async def appointment_updates(
        self,
        info: Info,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> Appointment:
        """Subscribe to appointment updates."""
        # Placeholder for appointment updates
        pass


# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[
        # Add extensions for performance monitoring
    ]
)