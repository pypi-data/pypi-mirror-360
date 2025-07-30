"""Authentication utilities for Grasp SDK Python implementation.

This module provides authentication and key verification functionality
for the Grasp platform.
"""

import asyncio
from typing import Dict, Any, Optional, TYPE_CHECKING
from urllib.parse import quote

try:
    import aiohttp
except ImportError:
    aiohttp = None

if TYPE_CHECKING:
    from aiohttp import ClientSession

from ..models import ISandboxConfig


class AuthError(Exception):
    """Exception raised for authentication errors."""
    pass


class KeyVerificationError(AuthError):
    """Exception raised when key verification fails."""
    pass


async def login(token: str) -> Dict[str, Any]:
    """Authenticates with the Grasp platform using a token.
    
    Args:
        token: Authentication token to verify
        
    Returns:
        Dict[str, Any]: Response from the authentication API
        
    Raises:
        AuthError: If authentication fails
        ImportError: If aiohttp is not installed
    """
    if aiohttp is None:
        raise ImportError("aiohttp is required for authentication. Install with: pip install aiohttp")
    
    url = f"https://d1toyru2btfpfr.cloudfront.net/api/key/verify?token={quote(token)}"
    
    try:
        if aiohttp is None:
            raise ImportError("aiohttp is required for authentication. Install with: pip install aiohttp")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise AuthError("Invalid authentication token")
                elif response.status == 403:
                    raise AuthError("Access forbidden - token may be expired")
                else:
                    response.raise_for_status()
                    return await response.json()
    except Exception as e:
        if aiohttp is not None and isinstance(e, aiohttp.ClientError):
            raise AuthError(f"Network error during authentication: {str(e)}")
        else:
            raise AuthError(f"Unexpected error during authentication: {str(e)}")


async def verify(config: ISandboxConfig) -> Dict[str, Any]:
    """Verifies the sandbox configuration and authenticates.
    
    Args:
        config: Sandbox configuration containing the API key
        
    Returns:
        Dict[str, Any]: Authentication response
        
    Raises:
        KeyVerificationError: If the key is missing or invalid
        AuthError: If authentication fails
    """
    if not config['key']:
        raise KeyVerificationError('Grasp key is required')
    
    try:
        return await login(config['key'])
    except AuthError:
        raise
    except Exception as e:
        raise KeyVerificationError(f"Key verification failed: {str(e)}")


def verify_sync(config: ISandboxConfig) -> Dict[str, Any]:
    """Synchronous wrapper for the verify function.
    
    Args:
        config: Sandbox configuration containing the API key
        
    Returns:
        Dict[str, Any]: Authentication response
        
    Raises:
        KeyVerificationError: If the key is missing or invalid
        AuthError: If authentication fails
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(verify(config))


async def validate_token(token: str) -> bool:
    """Validates a token without raising exceptions.
    
    Args:
        token: Token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        await login(token)
        return True
    except (AuthError, Exception):
        return False


def validate_token_sync(token: str) -> bool:
    """Synchronous wrapper for token validation.
    
    Args:
        token: Token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(validate_token(token))


class AuthManager:
    """Authentication manager for handling multiple tokens and sessions."""
    
    def __init__(self):
        """Initialize the authentication manager."""
        if aiohttp is None:
            raise ImportError("aiohttp is required for AuthManager. Install with: pip install aiohttp")
        self._verified_tokens: Dict[str, Dict[str, Any]] = {}
        self._session: Optional['ClientSession'] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        if aiohttp is None:
            raise ImportError("aiohttp is required for AuthManager. Install with: pip install aiohttp")
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def verify_token(self, token: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Verify a token with caching support.
        
        Args:
            token: Token to verify
            force_refresh: Whether to force a new verification
            
        Returns:
            Dict[str, Any]: Verification response
            
        Raises:
            AuthError: If verification fails
        """
        if not force_refresh and token in self._verified_tokens:
            return self._verified_tokens[token]
        
        url = f"https://d1toyru2btfpfr.cloudfront.net/api/key/verify?token={quote(token)}"
        
        if not self._session:
            raise AuthError("AuthManager not properly initialized. Use as async context manager.")
        
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self._verified_tokens[token] = result
                    return result
                elif response.status == 401:
                    raise AuthError("Invalid authentication token")
                elif response.status == 403:
                    raise AuthError("Access forbidden - token may be expired")
                else:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            if aiohttp is not None and isinstance(e, aiohttp.ClientError):
                raise AuthError(f"Network error during authentication: {str(e)}")
            else:
                raise AuthError(f"Unexpected error during authentication: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the token verification cache."""
        self._verified_tokens.clear()
    
    def is_token_cached(self, token: str) -> bool:
        """Check if a token is cached.
        
        Args:
            token: Token to check
            
        Returns:
            bool: True if token is cached
        """
        return token in self._verified_tokens