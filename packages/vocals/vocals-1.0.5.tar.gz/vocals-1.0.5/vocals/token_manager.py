"""
Token management for the Vocals SDK, mirroring the NextJS implementation.
"""

import time
import asyncio
from typing import Optional, Dict, Any, Tuple
import aiohttp
import json


def create_token_manager(endpoint: str, headers: Dict[str, str], refresh_buffer: float):
    """Create a token manager with closures for state management

    Args:
        endpoint: The token endpoint URL
        headers: Headers to include in token requests
        refresh_buffer: Time in seconds before expiry to refresh token

    Returns:
        Dictionary with token management functions
    """
    # State held in closures
    state = {"token": None, "expires_at": 0, "refresh_promise": None}

    async def get_token() -> str:
        """Get a valid token, refreshing if necessary

        Returns:
            A valid token string

        Raises:
            Exception: If token refresh fails
        """
        # Return existing token if still valid
        current_time = time.time()
        if state["token"] and current_time < (state["expires_at"] - refresh_buffer):
            return state["token"]

        # Avoid multiple concurrent refresh requests
        if state["refresh_promise"]:
            return await state["refresh_promise"]

        # Refresh the token
        state["refresh_promise"] = asyncio.create_task(_refresh_token())
        try:
            token = await state["refresh_promise"]
            return token
        finally:
            state["refresh_promise"] = None

    async def _refresh_token() -> str:
        """Refresh the token from the endpoint

        Returns:
            The new token string

        Raises:
            Exception: If token refresh fails
        """
        request_headers = {"Content-Type": "application/json", **headers}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint, headers=request_headers, json={}
            ) as response:
                if not response.ok:
                    try:
                        error_data = await response.json()
                        error_message = error_data.get("error", "Unknown error")
                    except:
                        error_message = f"HTTP {response.status}"
                    raise Exception(
                        f"Failed to refresh WebSocket token: {error_message}"
                    )

                data = await response.json()
                state["token"] = data["token"]
                state["expires_at"] = (
                    data["expiresAt"] / 1000.0
                )  # Convert from milliseconds to seconds

                if not state["token"]:
                    raise Exception("No token received from server")

                return state["token"]

    def clear():
        """Clear the stored token and cancel any pending refresh"""
        state["token"] = None
        state["expires_at"] = 0
        if state["refresh_promise"] and not state["refresh_promise"].done():
            state["refresh_promise"].cancel()
        state["refresh_promise"] = None

    def get_token_info() -> Tuple[Optional[str], Optional[float]]:
        """Get current token info

        Returns:
            Tuple of (token, expires_at_timestamp)
        """
        return (
            state["token"],
            (
                state["expires_at"] * 1000.0 if state["expires_at"] else None
            ),  # Convert to milliseconds
        )

    # Return the token manager interface
    return {
        "get_token": get_token,
        "clear": clear,
        "get_token_info": get_token_info,
    }
