"""
WebSocket token management for the Vocals SDK, mirroring the NextJS implementation.
"""

import os
import time
from typing import Optional, Dict, Any, cast

try:
    import jwt
except ImportError:
    raise ImportError(
        "PyJWT is required for WebSocket token functionality. Install with: pip install PyJWT"
    )

try:
    from dotenv import load_dotenv

    # Load environment variables from .env file in the root directory
    load_dotenv()
except ImportError:
    # python-dotenv is optional, continue without it
    pass

from .types import Result, Ok, Err, WSToken, ValidatedApiKey, VocalsError

# Constants
VOCALS_WS_ENDPOINT = "ws://192.168.1.46:8000/v1/stream/conversation"
TOKEN_EXPIRY_MS = 10 * 60 * 1000  # 10 minutes
API_KEY_MIN_LENGTH = 32


def validate_api_key_format(api_key: str) -> Result[ValidatedApiKey, VocalsError]:
    """
    Validate API key format.

    Args:
        api_key: The API key to validate

    Returns:
        Result containing validated API key or error
    """
    if len(api_key) >= API_KEY_MIN_LENGTH and api_key.startswith("vdev_"):
        return Ok(api_key)
    else:
        return Err(
            VocalsError(
                message='Invalid API key format. Must be at least 32 characters and start with "vdev_"',
                code="INVALID_API_KEY_FORMAT",
            )
        )


def get_vocals_api_key() -> Result[str, VocalsError]:
    """
    Get the Vocals API key from environment variables.

    Returns:
        Result containing API key or error
    """
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if api_key:
        return Ok(api_key)
    else:
        return Err(
            VocalsError(
                message="VOCALS_DEV_API_KEY environment variable not set",
                code="MISSING_API_KEY",
            )
        )


def generate_ws_token_from_api_key(
    api_key: ValidatedApiKey, user_id: Optional[str] = None
) -> Result[WSToken, VocalsError]:
    """
    Generate WebSocket token from API key using JWT.

    Args:
        api_key: Validated API key
        user_id: Optional user ID to include in token

    Returns:
        Result containing WSToken or error
    """
    try:
        expires_at = int(time.time() * 1000) + TOKEN_EXPIRY_MS
        expires_in = TOKEN_EXPIRY_MS // 1000  # Convert to seconds for JWT

        # Create JWT payload with userId if provided
        payload: Dict[str, Any] = {
            "apiKey": api_key[:8] + "...",  # Only include partial key for security
        }

        if user_id:
            payload["userId"] = user_id

        # Use the API key as the JWT secret
        # Let JWT library handle the exp claim via exp parameter
        token = jwt.encode(payload, api_key, algorithm="HS256")

        # Add exp claim manually since we want to control the exact timestamp
        payload["exp"] = expires_at // 1000  # JWT expects seconds
        token = jwt.encode(payload, api_key, algorithm="HS256")

        return Ok(WSToken(token=token, expires_at=expires_at))

    except Exception as error:
        return Err(
            VocalsError(
                message=f"Failed to generate WebSocket token: {str(error)}",
                code="TOKEN_GENERATION_FAILED",
            )
        )


def generate_ws_token() -> Result[WSToken, VocalsError]:
    """
    Generate WebSocket token using environment API key.

    Returns:
        Result containing WSToken or error
    """
    api_key_result = get_vocals_api_key()

    if isinstance(api_key_result, Err):
        return Err(api_key_result.error)

    validated_api_key_result = validate_api_key_format(api_key_result.data)

    if isinstance(validated_api_key_result, Err):
        return Err(validated_api_key_result.error)

    return generate_ws_token_from_api_key(validated_api_key_result.data)


def generate_ws_token_with_user_id(user_id: str) -> Result[WSToken, VocalsError]:
    """
    Generate WebSocket token with user ID using environment API key.

    Args:
        user_id: User ID to include in token

    Returns:
        Result containing WSToken or error
    """
    api_key_result = get_vocals_api_key()

    if isinstance(api_key_result, Err):
        return Err(api_key_result.error)

    validated_api_key_result = validate_api_key_format(api_key_result.data)

    if isinstance(validated_api_key_result, Err):
        return Err(validated_api_key_result.error)

    return generate_ws_token_from_api_key(validated_api_key_result.data, user_id)


def is_token_expired(token: WSToken) -> bool:
    """
    Check if token is expired.

    Args:
        token: WSToken to check

    Returns:
        True if token is expired, False otherwise
    """
    return int(time.time() * 1000) > token.expires_at


def get_token_ttl(token: WSToken) -> int:
    """
    Get token TTL in seconds.

    Args:
        token: WSToken to check

    Returns:
        TTL in seconds, 0 if expired
    """
    return max(0, (token.expires_at - int(time.time() * 1000)) // 1000)


def decode_ws_token(token: str, api_key: str) -> Result[Dict[str, Any], VocalsError]:
    """
    Decode JWT token and extract payload.

    Args:
        token: JWT token to decode
        api_key: API key used to sign the token

    Returns:
        Result containing decoded payload or error
    """
    try:
        decoded = jwt.decode(token, api_key, algorithms=["HS256"])
        return Ok(decoded)
    except Exception as error:
        return Err(
            VocalsError(
                message=f"Failed to decode WebSocket token: {str(error)}",
                code="TOKEN_DECODE_FAILED",
            )
        )


def get_ws_endpoint() -> str:
    """Get WebSocket endpoint URL."""
    return VOCALS_WS_ENDPOINT


def get_token_expiry_ms() -> int:
    """Get token expiry time in milliseconds."""
    return TOKEN_EXPIRY_MS
