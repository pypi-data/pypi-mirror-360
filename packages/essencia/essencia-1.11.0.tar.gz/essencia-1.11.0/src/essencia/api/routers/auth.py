"""
Authentication and authorization endpoints.
"""
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from essencia.models import User, Session
from essencia.api.dependencies import get_db, get_current_user
from essencia.security import verify_password, hash_password


router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="password123")


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RegisterRequest(BaseModel):
    """User registration request."""
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="securepassword123")
    full_name: str = Field(..., example="João Silva")
    cpf: str = Field(..., example="123.456.789-00")
    phone: Optional[str] = Field(None, example="(11) 98765-4321")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "joao.silva@example.com",
                "password": "minhasenha123",
                "full_name": "João Silva",
                "cpf": "123.456.789-00",
                "phone": "(11) 98765-4321"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


@router.post("/login", response_model=LoginResponse, summary="User login")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> LoginResponse:
    """
    Authenticate user and return access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token for authenticated requests.
    """
    # Find user
    User.set_db(db)
    user = await User.find_one({"email": login_data.email.lower()})
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    settings = request.app.state.settings
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expire
    }
    
    access_token = jwt.encode(
        token_data,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Create session
    Session.set_db(db)
    session = Session(
        user_id=str(user.id),
        token=access_token,
        expires_at=expire,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    await session.save()
    
    # Update last login
    user.last_login = datetime.now()
    await user.save()
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    )


@router.post("/login/oauth", response_model=LoginResponse, summary="OAuth2 login")
async def oauth_login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> LoginResponse:
    """
    OAuth2 compatible login endpoint.
    
    Use this endpoint for OAuth2 password flow compatibility.
    """
    login_data = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    return await login(request, login_data, db)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Register new user")
async def register(
    register_data: RegisterRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> dict:
    """
    Register a new user account.
    
    - **email**: Valid email address (will be used for login)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    - **cpf**: Valid Brazilian CPF
    - **phone**: Optional phone number
    """
    from essencia.utils.validators import validate_cpf
    
    # Validate CPF
    if not validate_cpf(register_data.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CPF"
        )
    
    # Check if user exists
    User.set_db(db)
    existing_user = await User.find_one({"email": register_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Check if CPF exists
    existing_cpf = await User.find_one({"cpf": register_data.cpf})
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF already registered"
        )
    
    # Create user
    user = User(
        email=register_data.email.lower(),
        password_hash=hash_password(register_data.password),
        full_name=register_data.full_name,
        cpf=register_data.cpf,
        phone=register_data.phone,
        role="patient",  # Default role
        permissions=["own_profile:read", "own_profile:write"]
    )
    
    await user.save()
    
    return {
        "message": "User registered successfully",
        "user_id": str(user.id)
    }


@router.post("/logout", summary="User logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> dict:
    """
    Logout current user and invalidate session.
    """
    # In a real implementation, you would:
    # 1. Invalidate the current token
    # 2. Remove the session from database
    # 3. Add token to a blacklist if using JWT
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=dict, summary="Get current user")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Get current authenticated user information.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "permissions": current_user.permissions,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }


@router.put("/me/password", summary="Change password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> dict:
    """
    Change current user's password.
    
    Requires current password for verification.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    await current_user.save()
    
    # Invalidate all sessions (in production)
    # await Session.delete_many({"user_id": str(current_user.id)})
    
    return {"message": "Password changed successfully"}


@router.post("/refresh", response_model=LoginResponse, summary="Refresh access token")
async def refresh_token(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
) -> LoginResponse:
    """
    Refresh access token for authenticated user.
    
    Use this endpoint to get a new token before the current one expires.
    """
    # Create new token
    settings = request.app.state.settings
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    
    token_data = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "exp": expire
    }
    
    access_token = jwt.encode(
        token_data,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user={
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role
        }
    )


from typing import Optional