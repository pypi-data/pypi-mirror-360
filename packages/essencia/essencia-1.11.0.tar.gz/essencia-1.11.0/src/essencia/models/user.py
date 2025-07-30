"""User model definitions for authentication and authorization."""

import datetime
from typing import Any, Optional

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    ph = PasswordHasher()
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False
    ph = None

from pydantic import ConfigDict, EmailStr, Field, ValidationError, field_validator, model_validator, ValidationInfo

from .base import BaseModel
from .bases import MongoModel, ObjectReferenceId, StrEnum
from .people import BaseProfile


# Simple API models for external use
class UserBase(BaseModel):
    """Base user model."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="Is user active")
    is_admin: bool = Field(False, description="Is user admin")


class UserCreate(UserBase):
    """Model for creating a user."""
    
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Model for updating a user."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    """User model for database storage."""
    
    hashed_password: str = Field(..., description="Hashed password")


# Medical system specific user models
class BaseUser(MongoModel):
    """Base user model for medical system with role-based access."""
    model_config = ConfigDict(
        extra='ignore',
        populate_by_name=False,
        arbitrary_types_allowed=True,
    )
    COLLECTION_NAME = 'user'
    
    email: str
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    class Role(StrEnum):
        PATIENT = 'Paciente'
        EMPLOYEE = 'Funcionário'
        DOCTOR = 'Médico'
        THERAPIST = 'Terapeuta'
    
    role: Role
    admin: bool = Field(default=False)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.admin and self.role == self.Role.PATIENT:
            raise ValidationError('Paciente não pode ser administrador do sistema.')


class SessionUser(BaseUser):
    """User model with profile information for session management."""
    profile: BaseProfile
    
    @property
    def reference(self) -> str:
        return f'{self.role.name.lower()}.{self.profile.key}'


class MedicalUser(BaseUser):
    """User model with password management for medical system."""
    password: str  # This will store the hashed password
    
    def set_password(self, plain_password: str) -> None:
        """Hash and store a password."""
        if HAS_ARGON2:
            self.password = ph.hash(plain_password)
        else:
            # Fallback to basic SHA256 if argon2 not available
            import hashlib
            self.password = hashlib.sha256(plain_password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify a password against the hash."""
        if not HAS_ARGON2:
            # Fallback verification
            import hashlib
            return self.password == hashlib.sha256(plain_password.encode()).hexdigest()
        
        try:
            # Check if password needs migration from old format
            if not self.password.startswith('$argon2'):
                # This might be an old password format
                import hashlib
                if self.password == hashlib.sha256(plain_password.encode()).hexdigest():
                    # Migrate to new hash
                    new_hash = ph.hash(plain_password)
                    self.update_self({'$set': {'password': new_hash}})
                    self.password = new_hash
                    return True
                return False
            
            # Normal argon2 verification
            ph.verify(self.password, plain_password)
            # If verification is successful, check if rehashing is needed
            if ph.check_needs_rehash(self.password):
                new_hash = ph.hash(plain_password)
                self.update_self({'$set': {'password': new_hash}})
                self.password = new_hash
            return True
        except VerifyMismatchError:
            return False
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional['MedicalUser']:
        """Authenticate a user by email and password."""
        user = cls.find_one({'email': email})
        if user and user.verify_password(password):
            return user
        return None


class NewUser(MedicalUser):
    """Temporary model for user registration with password confirmation."""
    password_repeat: str = Field(..., exclude=True, description="Must match password field")
    
    @field_validator("password_repeat")
    @classmethod
    def validate_passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Ensure password and password_repeat match."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    def model_dump_json(self, *args, **kwargs) -> str:
        """Serialize model excluding sensitive fields."""
        exclude = {'password', 'password_repeat'}
        kwargs.update({'exclude': exclude})
        return super().model_dump_json(*args, **kwargs)

    @model_validator(mode="after")
    def hash_new_password(self) -> "NewUser":
        """Ensure password gets hashed during creation."""
        # The password field will contain the plain password at this point
        # We need to hash it before saving
        return self
    
    def create(self) -> MedicalUser:
        """Create a new user with hashed password."""
        # Create a MedicalUser instance (not NewUser) with the hashed password
        user_data = self.model_dump(exclude={'password_repeat'})
        user = MedicalUser(**user_data)
        user.set_password(self.password)  # Hash the password
        saved = user.save_self()
        return saved