"""
Security utilities for FastAPI web applications.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    OAuth2 password bearer that also checks cookies.
    Useful for supporting both API tokens and session cookies.
    """
    
    def __init__(
        self,
        tokenUrl: str,
        cookie_name: str = "access_token",
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            scopes=scopes,
            description=description,
            auto_error=auto_error,
        )
        self.cookie_name = cookie_name
        
    async def __call__(self, request: Request) -> Optional[str]:
        """
        Extract token from Authorization header or cookie.
        
        Args:
            request: FastAPI request
            
        Returns:
            Token string or None
        """
        # Try Authorization header first
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        
        if scheme.lower() == "bearer" and token:
            return token
            
        # Try cookie
        token = request.cookies.get(self.cookie_name)
        if token:
            return token
            
        # No token found
        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None


def create_access_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Token payload data
        secret_key: Secret key for signing
        algorithm: JWT algorithm
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Encode token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Token payload data
        secret_key: Secret key for signing
        algorithm: JWT algorithm
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    # Set expiration (default 7 days for refresh tokens)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
        
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    # Encode token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
    token_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        secret_key: Secret key for verification
        algorithm: JWT algorithm
        token_type: Expected token type (access/refresh)
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        
        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}"
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


class SecurityUtils:
    """
    Additional security utilities for web applications.
    """
    
    @staticmethod
    def check_csrf_token(
        request: Request,
        csrf_token: Optional[str] = None,
        header_name: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token"
    ) -> bool:
        """
        Verify CSRF token.
        
        Args:
            request: FastAPI request
            csrf_token: CSRF token from form/header
            header_name: Header name for CSRF token
            cookie_name: Cookie name for CSRF token
            
        Returns:
            True if CSRF token is valid
        """
        # Get token from request
        if not csrf_token:
            csrf_token = request.headers.get(header_name)
            
        if not csrf_token:
            return False
            
        # Compare with cookie
        cookie_token = request.cookies.get(cookie_name)
        return csrf_token == cookie_token
        
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token."""
        import secrets
        return secrets.token_urlsafe(32)
        
    @staticmethod
    def is_safe_url(
        url: str,
        allowed_hosts: Optional[list] = None
    ) -> bool:
        """
        Check if URL is safe for redirects.
        
        Args:
            url: URL to check
            allowed_hosts: List of allowed hosts
            
        Returns:
            True if URL is safe
        """
        from urllib.parse import urlparse
        
        if not url:
            return False
            
        # Parse URL
        parsed = urlparse(url)
        
        # Reject if scheme is present and not http/https
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            return False
            
        # Check host if allowed_hosts specified
        if allowed_hosts and parsed.netloc:
            return parsed.netloc in allowed_hosts
            
        # Allow relative URLs
        return not parsed.netloc
        
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        import re
        
        # Remove path components
        filename = filename.replace("..", "").replace("/", "").replace("\\", "")
        
        # Keep only safe characters
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
        
        # Limit length
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        if len(name) > 100:
            name = name[:100]
            
        return f"{name}.{ext}" if ext else name