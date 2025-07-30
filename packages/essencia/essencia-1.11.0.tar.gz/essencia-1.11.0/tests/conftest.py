"""
Global pytest configuration and fixtures for essencia tests.
"""
import asyncio
import os
from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database

from essencia.core.config import Config
from essencia.database import AsyncDatabase, Database as SyncDatabase
from essencia.models import MongoModel
from essencia.security.encryption import FieldEncryptor


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Test configuration with test database."""
    return Config(
        app_name="essencia_test",
        mongodb_url=os.getenv("TEST_MONGODB_URL", "mongodb://localhost:27017/essencia_test"),
        redis_url=os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1"),
        encryption_key=FieldEncryptor.generate_key(),
        debug=True,
        testing=True,
    )


@pytest.fixture
def sync_db(test_config) -> Generator[Database, None, None]:
    """Synchronous database connection for testing."""
    client = MongoClient(test_config.mongodb_url)
    database = client.get_database()
    
    # Clean database before tests
    for collection_name in database.list_collection_names():
        database[collection_name].delete_many({})
    
    yield database
    
    # Cleanup after tests
    for collection_name in database.list_collection_names():
        database[collection_name].delete_many({})
    client.close()


@pytest_asyncio.fixture
async def async_db(test_config) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Asynchronous database connection for testing."""
    client = AsyncIOMotorClient(test_config.mongodb_url)
    database = client.get_database()
    
    # Clean database before tests
    for collection_name in await database.list_collection_names():
        await database[collection_name].delete_many({})
    
    yield database
    
    # Cleanup after tests
    for collection_name in await database.list_collection_names():
        await database[collection_name].delete_many({})
    client.close()


@pytest.fixture
def field_encryptor(test_config):
    """Field encryptor for testing."""
    return FieldEncryptor(test_config.encryption_key)


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = Mock()
    mock.get = Mock(return_value=None)
    mock.set = Mock(return_value=True)
    mock.delete = Mock(return_value=True)
    mock.exists = Mock(return_value=False)
    mock.expire = Mock(return_value=True)
    mock.ttl = Mock(return_value=-1)
    return mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "roles": ["user"],
        "permissions": ["read:own_profile"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "name": "João da Silva",
        "cpf": "123.456.789-00",
        "birth_date": datetime(1990, 5, 15),
        "gender": "M",
        "phone": "(11) 98765-4321",
        "email": "joao.silva@example.com",
        "address": {
            "street": "Rua das Flores",
            "number": "123",
            "complement": "Apto 45",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567",
        },
        "medical_record_number": "MR001",
        "blood_type": "O+",
        "allergies": ["Penicilina", "Dipirona"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_vital_signs_data():
    """Sample vital signs data for testing."""
    return {
        "patient_id": "patient_123",
        "measured_at": datetime.utcnow(),
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "temperature": 36.5,
        "respiratory_rate": 16,
        "oxygen_saturation": 98,
        "weight": 70.5,
        "height": 175,
        "notes": "Patient feeling well",
    }


@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {
        "Authorization": "Bearer test_token_123",
        "X-CSRF-Token": "csrf_token_456",
    }


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    return {
        "user_id": "user_123",
        "username": "test_user",
        "roles": ["user"],
        "permissions": ["read:own_profile"],
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture(autouse=True)
def reset_mongo_model_db():
    """Reset MongoModel database connection before each test."""
    MongoModel._db = None
    yield
    MongoModel._db = None


@pytest.mark.asyncio
async def async_test_wrapper(test_func):
    """Wrapper for async tests to ensure proper cleanup."""
    try:
        await test_func()
    finally:
        # Ensure all async operations are completed
        await asyncio.sleep(0.01)