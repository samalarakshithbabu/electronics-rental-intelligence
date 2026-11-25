"""
AI-Powered Electronics Rental and Revenue Intelligence - JWT Authentication Module
Implements secure JWT token generation and validation
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Security configuration
JWT_SECRET = os.getenv("JWT_SECRET", "AI-Powered Electronics Rental-ai-change-in-production-2024!")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))

# Token blacklist for logout
_token_blacklist = set()


class TokenPayload(BaseModel):
    """JWT token payload"""
    user_id: int
    email: str
    role: str
    exp: datetime


class TokenData(BaseModel):
    """Decoded token data for use in endpoints"""
    user_id: int
    email: str
    role: str


def create_access_token(user_id: int, email: str, role: str) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's database ID
        email: User's email address
        role: User's role (customer/admin)
        
    Returns:
        Encoded JWT token string
    """
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": expires,
        "type": "access"
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Created token for user {user_id} (expires: {expires})")
    
    return token


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with decoded information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Check blacklist
        if token in _token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Decode token
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM]
        )
        
        # Validate required fields
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return TokenData(
            user_id=payload["user_id"],
            email=payload["email"],
            role=payload["role"]
        )
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed: expired signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def revoke_token(token: str) -> bool:
    """
    Add a token to the blacklist (logout).
    
    Args:
        token: JWT token to revoke
        
    Returns:
        True if successful
    """
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
        
        # Add to blacklist with expiry
        _token_blacklist.add(token)
        logger.info(f"Revoked token for user {payload.get('user_id')}")
        
        # Clean expired entries periodically
        if len(_token_blacklist) > 1000:
            _clean_blacklist()
        
        return True
    except Exception as e:
        logger.error(f"Token revocation error: {e}")
        return False


def _clean_blacklist():
    """Remove expired tokens from blacklist"""
    now = datetime.utcnow()
    to_remove = []
    
    for token in _token_blacklist:
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=[JWT_ALGORITHM],
                options={"verify_exp": False}
            )
            if payload.get("exp") and datetime.fromtimestamp(payload["exp"]) < now:
                to_remove.append(token)
        except:
            to_remove.append(token)
    
    for token in to_remove:
        _token_blacklist.discard(token)
    
    logger.info(f"Cleaned {len(to_remove)} expired tokens from blacklist")


# FastAPI dependency for protected endpoints
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Returns:
        User data dict with id, email, role
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Get full user data from database
    from database.connection import db
    
    user = db.execute_one(
        "SELECT id, email, first_name, last_name, role FROM users WHERE id = ?",
        (token_data.user_id,)
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return {
        "id": user['id'],
        "email": user['email'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "role": user['role']
    }


async def get_current_user_or_none(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for optional authentication.
    Returns None if no valid token is provided.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based authorization.
    
    Args:
        required_role: Role required to access endpoint
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user.get('role') != required_role and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_role('admin')
require_customer = require_role('customer')