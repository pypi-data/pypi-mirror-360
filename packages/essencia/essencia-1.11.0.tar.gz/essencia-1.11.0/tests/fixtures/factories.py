"""
Test data factories for essencia.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import factory
from faker import Faker

from essencia.models import MongoModel, User
from essencia.security.encryption import FieldEncryptor

fake = Faker("pt_BR")


class MongoModelFactory(factory.Factory):
    """Base factory for MongoDB models."""
    
    class Meta:
        abstract = True
    
    id = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class UserFactory(MongoModelFactory):
    """Factory for User models."""
    
    class Meta:
        model = dict  # Return dict instead of User instance
    
    username = factory.LazyFunction(lambda: fake.user_name())
    email = factory.LazyFunction(lambda: fake.email())
    full_name = factory.LazyFunction(lambda: fake.name())
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # secret
    is_active = True
    is_superuser = False
    is_verified = True
    roles = ["user"]
    permissions = ["read:own_profile"]
    phone = factory.LazyFunction(lambda: fake.phone_number())
    avatar_url = factory.LazyFunction(lambda: fake.image_url())
    preferences = {}
    last_login = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(hours=1))
    login_count = factory.Faker("random_int", min=1, max=100)
    failed_login_count = 0
    locked_until = None
    password_changed_at = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(days=30))
    two_factor_enabled = False
    two_factor_secret = None
    recovery_codes = []


class PatientFactory(MongoModelFactory):
    """Factory for Patient models."""
    
    class Meta:
        model = dict
    
    name = factory.LazyFunction(lambda: fake.name())
    cpf = factory.LazyFunction(lambda: fake.cpf())
    birth_date = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=0, maximum_age=100))
    gender = factory.Faker("random_element", elements=["M", "F"])
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.LazyFunction(lambda: fake.email())
    address = factory.LazyFunction(lambda: {
        "street": fake.street_name(),
        "number": fake.building_number(),
        "complement": fake.random_element(["", f"Apto {fake.random_int(10, 999)}", f"Casa {fake.random_int(1, 9)}"]),
        "neighborhood": fake.neighborhood(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
    })
    medical_record_number = factory.Sequence(lambda n: f"MR{n:06d}")
    blood_type = factory.Faker("random_element", elements=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    allergies = factory.LazyFunction(lambda: fake.random_elements(
        elements=["Penicilina", "Dipirona", "AAS", "Ibuprofeno", "Lactose", "Glúten"],
        length=fake.random_int(0, 3),
        unique=True
    ))
    chronic_conditions = factory.LazyFunction(lambda: fake.random_elements(
        elements=["Hipertensão", "Diabetes", "Asma", "Artrite", "Depressão"],
        length=fake.random_int(0, 2),
        unique=True
    ))
    emergency_contact = factory.LazyFunction(lambda: {
        "name": fake.name(),
        "relationship": fake.random_element(["Cônjuge", "Filho(a)", "Pai", "Mãe", "Irmão(ã)"]),
        "phone": fake.phone_number(),
    })


class VitalSignsFactory(MongoModelFactory):
    """Factory for VitalSigns models."""
    
    class Meta:
        model = dict
    
    patient_id = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    measured_at = factory.LazyFunction(datetime.utcnow)
    blood_pressure_systolic = factory.Faker("random_int", min=90, max=180)
    blood_pressure_diastolic = factory.Faker("random_int", min=60, max=110)
    heart_rate = factory.Faker("random_int", min=50, max=120)
    temperature = factory.Faker("pyfloat", min_value=35.0, max_value=40.0, right_digits=1)
    respiratory_rate = factory.Faker("random_int", min=12, max=30)
    oxygen_saturation = factory.Faker("random_int", min=85, max=100)
    weight = factory.Faker("pyfloat", min_value=40.0, max_value=150.0, right_digits=1)
    height = factory.Faker("random_int", min=150, max=200)
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    measured_by = factory.LazyFunction(lambda: fake.name())


class AppointmentFactory(MongoModelFactory):
    """Factory for Appointment models."""
    
    class Meta:
        model = dict
    
    patient_id = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    doctor_id = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    scheduled_at = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="now", end_date="+30d")
    )
    duration_minutes = factory.Faker("random_element", elements=[30, 45, 60])
    appointment_type = factory.Faker("random_element", elements=[
        "Consulta", "Retorno", "Avaliação", "Procedimento", "Urgência"
    ])
    status = factory.Faker("random_element", elements=[
        "scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"
    ])
    reason = factory.LazyFunction(lambda: fake.text(max_nb_chars=100))
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    location = factory.LazyFunction(lambda: {
        "room": f"Sala {fake.random_int(1, 20)}",
        "floor": f"{fake.random_int(1, 5)}º andar",
        "building": fake.random_element(["Principal", "Anexo A", "Anexo B"]),
    })


class LabTestFactory(MongoModelFactory):
    """Factory for LabTest models."""
    
    class Meta:
        model = dict
    
    patient_key = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    doctor_key = factory.LazyFunction(lambda: str(factory.Faker("uuid4")))
    test_type = factory.LazyFunction(lambda: {
        "name": fake.random_element(["Hemograma", "Glicemia", "Colesterol Total", "TSH", "T4 Livre"]),
        "category": fake.random_element(["Hematologia", "Bioquímica", "Hormônios"]),
        "unit": fake.random_element(["mg/dL", "g/dL", "U/L", "mUI/L"]),
        "reference_range": {"min": 0, "max": 100},
    })
    value = factory.Faker("pyfloat", min_value=0.1, max_value=200.0, right_digits=2)
    collected_at = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(days=fake.random_int(1, 30)))
    reported_at = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(days=fake.random_int(0, 29)))
    laboratory = factory.LazyFunction(lambda: fake.company())
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=100))
    is_abnormal = factory.Faker("boolean", chance_of_getting_true=20)
    critical = factory.Faker("boolean", chance_of_getting_true=5)


class MedicationFactory(MongoModelFactory):
    """Factory for Medication models."""
    
    class Meta:
        model = dict
    
    name = factory.Faker("random_element", elements=[
        "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Metformina",
        "Losartana", "Atenolol", "Sinvastatina", "Dipirona", "Diazepam"
    ])
    active_ingredient = factory.LazyAttribute(lambda obj: obj.name.lower())
    dosage_form = factory.Faker("random_element", elements=[
        "Comprimido", "Cápsula", "Solução oral", "Injetável", "Pomada"
    ])
    strength = factory.LazyFunction(lambda: f"{fake.random_int(100, 1000)}mg")
    manufacturer = factory.LazyFunction(lambda: fake.company())
    category = factory.Faker("random_element", elements=[
        "Analgésico", "Anti-inflamatório", "Antibiótico", "Anti-hipertensivo",
        "Antidiabético", "Ansiolítico"
    ])
    requires_prescription = factory.Faker("boolean", chance_of_getting_true=70)
    controlled_substance = factory.Faker("boolean", chance_of_getting_true=10)


def create_test_user(**kwargs) -> Dict[str, Any]:
    """Create a test user with optional overrides."""
    return UserFactory(**kwargs)


def create_test_patient(**kwargs) -> Dict[str, Any]:
    """Create a test patient with optional overrides."""
    return PatientFactory(**kwargs)


def create_test_vital_signs(**kwargs) -> Dict[str, Any]:
    """Create test vital signs with optional overrides."""
    return VitalSignsFactory(**kwargs)


def create_test_appointment(**kwargs) -> Dict[str, Any]:
    """Create a test appointment with optional overrides."""
    return AppointmentFactory(**kwargs)


def create_test_lab_test(**kwargs) -> Dict[str, Any]:
    """Create a test lab result with optional overrides."""
    return LabTestFactory(**kwargs)


def create_test_medication(**kwargs) -> Dict[str, Any]:
    """Create a test medication with optional overrides."""
    return MedicationFactory(**kwargs)