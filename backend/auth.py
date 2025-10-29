"""
Authentication and authorization utilities for admin endpoints
"""
import os
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Simple token-based authentication for admin endpoints
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev_admin_token_change_in_production")

security = HTTPBearer()


async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify admin token for protected endpoints
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        token: Valid token string
        
    Raises:
        HTTPException: If token is invalid
    """
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin token"
        )
    return credentials.credentials
