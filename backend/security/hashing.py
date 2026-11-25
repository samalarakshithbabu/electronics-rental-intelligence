"""
ElectroRent AI - Password Security Module
Implements bcrypt password hashing for secure credential storage
"""
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with automatic salt generation.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string (includes salt)
    """
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def migrate_password(user_record: dict) -> Optional[str]:
    """
    Migrate a plaintext password hash to bcrypt.
    This should only be called during user migration from legacy systems.
    
    Args:
        user_record: User record with plaintext password_hash
        
    Returns:
        New bcrypt hash if migration successful, None otherwise
    """
    try:
        current_hash = user_record.get('password_hash', '')
        
        # Skip if already bcrypt hashed (bcrypt hashes start with $2)
        if current_hash.startswith('$2'):
            logger.info(f"User {user_record.get('email')} already uses bcrypt")
            return None
        
        # Migrate plaintext password to bcrypt
        if len(current_hash) > 0:
            new_hash = hash_password(current_hash)
            logger.info(f"Migrated password for user {user_record.get('email')}")
            return new_hash
        
        return None
    except Exception as e:
        logger.error(f"Password migration error: {e}")
        return None


# Password strength validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']
    if password.lower() in weak_passwords:
        return False, "Password is too common"
    
    return True, ""


def generate_reset_token() -> str:
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)


def validate_token_expiry(created_at: datetime, expiry_hours: int = 24) -> bool:
    """Check if a token has expired"""
    expiry = created_at + timedelta(hours=expiry_hours)
    return datetime.now() < expiry