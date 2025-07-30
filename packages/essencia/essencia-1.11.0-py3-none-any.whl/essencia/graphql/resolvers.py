"""
GraphQL resolvers for Essencia.
"""
from typing import List, Optional, Any
from datetime import datetime, date

from essencia.models import User as UserModel
from essencia.integrations.sus import SUSPatient
from essencia.models.vital_signs import BloodPressure, Temperature, HeartRate
from essencia.models.medication import Medication as MedicationModel
from essencia.models.appointment import Appointment as AppointmentModel
from essencia.core import EssenciaException
from essencia.security import verify_password, hash_password

from .types import (
    Patient, PatientInput, PatientFilter,
    VitalSigns, VitalSignsInput,
    Medication, MedicationInput,
    Appointment, AppointmentInput,
    User, LoginResponse
)
from .context import GraphQLContext


class BaseResolver:
    """Base resolver with common functionality."""
    
    def __init__(self, context: GraphQLContext):
        self.context = context
        self.db = context.db
        self.current_user = context.current_user
    
    def require_auth(self):
        """Require authentication."""
        if not self.current_user:
            raise EssenciaException(
                "Authentication required",
                error_code="UNAUTHENTICATED",
                status_code=401
            )
    
    def require_permission(self, permission: str):
        """Require specific permission."""
        self.require_auth()
        if not self.current_user.has_permission(permission):
            raise EssenciaException(
                f"Permission required: {permission}",
                error_code="FORBIDDEN",
                status_code=403
            )


class PatientResolver(BaseResolver):
    """Patient-related resolvers."""
    
    async def list_patients(
        self,
        filter: Optional[PatientFilter],
        limit: int,
        offset: int
    ) -> List[Patient]:
        """List patients with filtering."""
        self.require_permission("patients:read")
        
        # Build query
        query = {}
        if filter:
            if filter.city:
                query["city"] = filter.city
            if filter.state:
                query["state"] = filter.state
            if filter.has_chronic_conditions is not None:
                if filter.has_chronic_conditions:
                    query["chronic_conditions"] = {"$ne": []}
                else:
                    query["chronic_conditions"] = []
        
        # Get patients
        SUSPatient.set_db(self.db)
        patients = await SUSPatient.find_many(query, skip=offset, limit=limit)
        
        # Convert to GraphQL type
        return [self._to_graphql_patient(p) for p in patients]
    
    async def get_patient(self, id: str) -> Optional[Patient]:
        """Get patient by ID."""
        self.require_permission("patients:read")
        
        SUSPatient.set_db(self.db)
        patient = await SUSPatient.find_by_id(id)
        
        if not patient:
            return None
        
        return self._to_graphql_patient(patient)
    
    async def search_patients(self, query: str) -> List[Patient]:
        """Search patients."""
        self.require_permission("patients:read")
        
        SUSPatient.set_db(self.db)
        patients = await SUSPatient.find_many({
            "$or": [
                {"full_name": {"$regex": query, "$options": "i"}},
                {"cpf": query}
            ]
        }, limit=50)
        
        return [self._to_graphql_patient(p) for p in patients]
    
    async def create_patient(self, input: PatientInput) -> Patient:
        """Create new patient."""
        self.require_permission("patients:write")
        
        # Validate CPF
        from essencia.utils.validators import validate_cpf
        if not validate_cpf(input.cpf):
            raise EssenciaException("Invalid CPF", error_code="INVALID_CPF")
        
        # Check if exists
        SUSPatient.set_db(self.db)
        existing = await SUSPatient.find_one({"cpf": input.cpf})
        if existing:
            raise EssenciaException(
                "Patient with this CPF already exists",
                error_code="DUPLICATE_CPF"
            )
        
        # Create patient
        patient = SUSPatient(
            full_name=input.full_name,
            cpf=input.cpf,
            birth_date=input.birth_date,
            birth_city=input.city,
            birth_state=input.state,
            phone=input.phone,
            email=input.email,
            street=input.street,
            number=input.number,
            complement=input.complement,
            neighborhood=input.neighborhood,
            city=input.city,
            state=input.state,
            cep=input.cep,
            blood_type=input.blood_type,
            allergies=input.allergies or [],
            chronic_conditions=input.chronic_conditions or [],
            mother_name=input.mother_name,
            father_name=input.father_name
        )
        
        await patient.save()
        return self._to_graphql_patient(patient)
    
    async def update_patient(self, id: str, input: PatientInput) -> Patient:
        """Update patient."""
        self.require_permission("patients:write")
        
        SUSPatient.set_db(self.db)
        patient = await SUSPatient.find_by_id(id)
        
        if not patient:
            raise EssenciaException("Patient not found", error_code="NOT_FOUND")
        
        # Update fields
        for field, value in input.__dict__.items():
            if value is not None:
                setattr(patient, field, value)
        
        patient.last_update = datetime.now()
        await patient.save()
        
        return self._to_graphql_patient(patient)
    
    async def delete_patient(self, id: str) -> bool:
        """Delete patient."""
        self.require_permission("patients:delete")
        
        SUSPatient.set_db(self.db)
        patient = await SUSPatient.find_by_id(id)
        
        if not patient:
            raise EssenciaException("Patient not found", error_code="NOT_FOUND")
        
        await patient.delete()
        return True
    
    def _to_graphql_patient(self, patient: SUSPatient) -> Patient:
        """Convert database model to GraphQL type."""
        # Calculate age
        today = date.today()
        age = today.year - patient.birth_date.year - (
            (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day)
        )
        
        # Mask CPF for security
        cpf = patient.cpf.get_secret_value() if hasattr(patient.cpf, 'get_secret_value') else patient.cpf
        masked_cpf = f"{cpf[:3]}.***.***-{cpf[-2:]}"
        
        return Patient(
            id=str(patient.id),
            full_name=patient.full_name,
            cpf=masked_cpf,
            birth_date=patient.birth_date,
            age=age,
            phone=patient.phone,
            email=patient.email,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            chronic_conditions=patient.chronic_conditions,
            city=patient.city,
            state=patient.state,
            created_at=patient.registration_date
        )


class VitalSignsResolver(BaseResolver):
    """Vital signs resolvers."""
    
    async def get_patient_vital_signs(
        self,
        patient_id: str,
        limit: int
    ) -> List[VitalSigns]:
        """Get vital signs for patient."""
        self.require_permission("vital_signs:read")
        
        # Get blood pressure readings
        BloodPressure.set_db(self.db)
        bp_readings = await BloodPressure.find_many(
            {"patient_id": patient_id},
            sort=[("recorded_at", -1)],
            limit=limit
        )
        
        # Convert to GraphQL type
        vital_signs = []
        for bp in bp_readings:
            vs = VitalSigns(
                id=str(bp.id),
                patient_id=bp.patient_id,
                recorded_at=bp.recorded_at,
                recorded_by=bp.recorded_by,
                systolic=bp.systolic.get_secret_value() if hasattr(bp.systolic, 'get_secret_value') else bp.systolic,
                diastolic=bp.diastolic.get_secret_value() if hasattr(bp.diastolic, 'get_secret_value') else bp.diastolic,
                heart_rate=bp.pulse,
                blood_pressure_category=bp.categorize().value
            )
            vital_signs.append(vs)
        
        return vital_signs
    
    async def get_latest_vital_signs(self, patient_id: str) -> Optional[VitalSigns]:
        """Get latest vital signs."""
        self.require_permission("vital_signs:read")
        
        vital_signs = await self.get_patient_vital_signs(patient_id, 1)
        return vital_signs[0] if vital_signs else None
    
    async def record_vital_signs(self, input: VitalSignsInput) -> VitalSigns:
        """Record new vital signs."""
        self.require_permission("vital_signs:write")
        
        # Record blood pressure if provided
        if input.systolic and input.diastolic:
            BloodPressure.set_db(self.db)
            bp = BloodPressure(
                patient_id=input.patient_id,
                systolic=input.systolic,
                diastolic=input.diastolic,
                pulse=input.heart_rate,
                recorded_by=str(self.current_user.id),
                notes="Recorded via GraphQL"
            )
            await bp.save()
            
            # Return as vital signs
            return VitalSigns(
                id=str(bp.id),
                patient_id=bp.patient_id,
                recorded_at=bp.recorded_at,
                recorded_by=bp.recorded_by,
                systolic=input.systolic,
                diastolic=input.diastolic,
                heart_rate=input.heart_rate,
                temperature=input.temperature,
                respiratory_rate=input.respiratory_rate,
                oxygen_saturation=input.oxygen_saturation,
                weight=input.weight,
                height=input.height,
                blood_pressure_category=bp.categorize().value
            )
        
        # For now, just return the input as recorded
        return VitalSigns(
            id="temp-id",
            patient_id=input.patient_id,
            recorded_at=datetime.now(),
            recorded_by=str(self.current_user.id),
            **input.__dict__
        )


class MedicationResolver(BaseResolver):
    """Medication resolvers."""
    
    async def get_patient_medications(
        self,
        patient_id: str,
        active_only: bool
    ) -> List[Medication]:
        """Get medications for patient."""
        self.require_permission("medications:read")
        
        MedicationModel.set_db(self.db)
        
        query = {"patient_id": patient_id}
        if active_only:
            query["is_active"] = True
        
        medications = await MedicationModel.find_many(query)
        
        return [self._to_graphql_medication(m) for m in medications]
    
    async def prescribe_medication(self, input: MedicationInput) -> Medication:
        """Prescribe new medication."""
        self.require_permission("medications:write")
        
        MedicationModel.set_db(self.db)
        
        medication = MedicationModel(
            patient_id=input.patient_id,
            name=input.name,
            active_ingredient=input.active_ingredient,
            dosage=input.dosage,
            frequency=input.frequency,
            route=input.route,
            start_date=input.start_date,
            end_date=input.end_date,
            prescribed_by=str(self.current_user.id),
            prescription_notes=input.prescription_notes
        )
        
        await medication.save()
        return self._to_graphql_medication(medication)
    
    async def update_medication(
        self,
        id: str,
        input: MedicationInput
    ) -> Medication:
        """Update medication."""
        self.require_permission("medications:write")
        
        MedicationModel.set_db(self.db)
        medication = await MedicationModel.find_by_id(id)
        
        if not medication:
            raise EssenciaException("Medication not found", error_code="NOT_FOUND")
        
        # Update fields
        for field, value in input.__dict__.items():
            if value is not None and field != "patient_id":
                setattr(medication, field, value)
        
        await medication.save()
        return self._to_graphql_medication(medication)
    
    async def discontinue_medication(self, id: str, reason: str) -> Medication:
        """Discontinue medication."""
        self.require_permission("medications:write")
        
        MedicationModel.set_db(self.db)
        medication = await MedicationModel.find_by_id(id)
        
        if not medication:
            raise EssenciaException("Medication not found", error_code="NOT_FOUND")
        
        medication.discontinue(reason)
        await medication.save()
        
        return self._to_graphql_medication(medication)
    
    async def get_daily_schedule(self, patient_id: str, date: date) -> List[Any]:
        """Get medication schedule for a date."""
        self.require_permission("medications:read")
        
        medications = await self.get_patient_medications(patient_id, True)
        
        # Generate schedule
        schedule = []
        for med in medications:
            # This would use the medication's get_daily_schedule method
            # For now, return a simple schedule
            schedule.append({
                "time": "08:00",
                "medication": med.name,
                "dosage": med.dosage,
                "instructions": f"Take {med.dosage} {med.route}"
            })
        
        return schedule
    
    def _to_graphql_medication(self, medication: MedicationModel) -> Medication:
        """Convert to GraphQL type."""
        return Medication(
            id=str(medication.id),
            patient_id=medication.patient_id,
            name=medication.name,
            active_ingredient=medication.active_ingredient,
            dosage=medication.dosage,
            frequency=medication.frequency,
            route=medication.route,
            start_date=medication.start_date,
            end_date=medication.end_date,
            discontinued_date=medication.discontinued_date,
            prescribed_by=medication.prescribed_by,
            prescribed_at=medication.created_at,
            prescription_notes=medication.prescription_notes,
            is_active=medication.is_active,
            adherence_rate=None  # Would calculate from doses
        )


class AppointmentResolver(BaseResolver):
    """Appointment resolvers."""
    
    async def list_appointments(
        self,
        patient_id: Optional[str],
        doctor_id: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime]
    ) -> List[Appointment]:
        """List appointments with filters."""
        self.require_permission("appointments:read")
        
        AppointmentModel.set_db(self.db)
        
        query = {}
        if patient_id:
            query["patient_id"] = patient_id
        if doctor_id:
            query["doctor_id"] = doctor_id
        if date_from or date_to:
            query["scheduled_date"] = {}
            if date_from:
                query["scheduled_date"]["$gte"] = date_from
            if date_to:
                query["scheduled_date"]["$lte"] = date_to
        
        appointments = await AppointmentModel.find_many(query)
        
        return [self._to_graphql_appointment(a) for a in appointments]
    
    async def get_appointment(self, id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        self.require_permission("appointments:read")
        
        AppointmentModel.set_db(self.db)
        appointment = await AppointmentModel.find_by_id(id)
        
        if not appointment:
            return None
        
        return self._to_graphql_appointment(appointment)
    
    async def schedule_appointment(self, input: AppointmentInput) -> Appointment:
        """Schedule new appointment."""
        self.require_permission("appointments:write")
        
        AppointmentModel.set_db(self.db)
        
        appointment = AppointmentModel(
            patient_id=input.patient_id,
            doctor_id=input.doctor_id,
            scheduled_date=input.scheduled_at,
            duration_minutes=input.duration_minutes,
            appointment_type=input.appointment_type,
            specialty=input.specialty,
            reason=input.reason,
            notes=input.notes,
            status="scheduled",
            created_by=str(self.current_user.id)
        )
        
        await appointment.save()
        return self._to_graphql_appointment(appointment)
    
    async def update_appointment(
        self,
        id: str,
        input: AppointmentInput
    ) -> Appointment:
        """Update appointment."""
        self.require_permission("appointments:write")
        
        AppointmentModel.set_db(self.db)
        appointment = await AppointmentModel.find_by_id(id)
        
        if not appointment:
            raise EssenciaException("Appointment not found", error_code="NOT_FOUND")
        
        # Update fields
        for field, value in input.__dict__.items():
            if value is not None:
                setattr(appointment, field, value)
        
        appointment.updated_at = datetime.now()
        await appointment.save()
        
        return self._to_graphql_appointment(appointment)
    
    async def cancel_appointment(self, id: str, reason: str) -> Appointment:
        """Cancel appointment."""
        self.require_permission("appointments:write")
        
        AppointmentModel.set_db(self.db)
        appointment = await AppointmentModel.find_by_id(id)
        
        if not appointment:
            raise EssenciaException("Appointment not found", error_code="NOT_FOUND")
        
        appointment.cancel(reason, cancelled_by=str(self.current_user.id))
        await appointment.save()
        
        return self._to_graphql_appointment(appointment)
    
    def _to_graphql_appointment(self, appointment: AppointmentModel) -> Appointment:
        """Convert to GraphQL type."""
        from .types import AppointmentStatus
        
        return Appointment(
            id=str(appointment.id),
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            scheduled_at=appointment.scheduled_date,
            duration_minutes=appointment.duration_minutes,
            appointment_type=appointment.appointment_type,
            specialty=appointment.specialty,
            reason=appointment.reason,
            notes=appointment.notes,
            status=AppointmentStatus[appointment.status.upper()],
            confirmed_at=appointment.confirmed_at,
            cancelled_at=appointment.cancelled_at,
            cancellation_reason=appointment.cancellation_reason
        )


class AuthResolver(BaseResolver):
    """Authentication resolvers."""
    
    async def login(self, email: str, password: str) -> LoginResponse:
        """Login user."""
        UserModel.set_db(self.db)
        user = await UserModel.find_one({"email": email.lower()})
        
        if not user or not verify_password(password, user.password_hash):
            raise EssenciaException(
                "Invalid credentials",
                error_code="INVALID_CREDENTIALS"
            )
        
        if not user.is_active:
            raise EssenciaException(
                "Account inactive",
                error_code="ACCOUNT_INACTIVE"
            )
        
        # Generate token
        from jose import jwt
        from datetime import timedelta
        
        expires = datetime.utcnow() + timedelta(hours=24)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expires
        }
        
        access_token = jwt.encode(
            token_data,
            self.context.settings.secret_key,
            algorithm="HS256"
        )
        
        # Update last login
        user.last_login = datetime.now()
        await user.save()
        
        # Convert to GraphQL type
        from .types import UserRole
        graphql_user = User(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=UserRole[user.role.upper()],
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return LoginResponse(
            access_token=access_token,
            expires_in=86400,  # 24 hours
            user=graphql_user
        )
    
    async def logout(self) -> bool:
        """Logout user."""
        self.require_auth()
        # In production, invalidate token
        return True
    
    async def get_current_user(self) -> Optional[User]:
        """Get current user."""
        if not self.current_user:
            return None
        
        from .types import UserRole
        return User(
            id=str(self.current_user.id),
            email=self.current_user.email,
            full_name=self.current_user.full_name,
            role=UserRole[self.current_user.role.upper()],
            is_active=self.current_user.is_active,
            created_at=self.current_user.created_at,
            last_login=self.current_user.last_login
        )
    
    async def get_user(self, id: str) -> Optional[User]:
        """Get user by ID."""
        self.require_permission("users:read")
        
        UserModel.set_db(self.db)
        user = await UserModel.find_by_id(id)
        
        if not user:
            return None
        
        from .types import UserRole
        return User(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=UserRole[user.role.upper()],
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )