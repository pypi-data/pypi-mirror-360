"""
WebSocket client for the Vocals SDK, mirroring the NextJS implementation.
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Callable, Set, Dict, Any
from urllib.parse import urlencode

from .types import (
    ConnectionState,
    VocalsError,
    WebSocketMessage,
    WebSocketResponse,
    TTSAudioMessage,
    SpeechInterruptionMessage,
    MessageHandler,
    ConnectionHandler,
    ErrorHandler,
    AudioDataHandler,
    Ok,
    Err,
)
from .config import VocalsConfig

logger = logging.getLogger(__name__)


def create_websocket_client(config: VocalsConfig, user_id: Optional[str] = None):
    """Create a WebSocket client with closures for state management

    Args:
        config: Configuration object
        user_id: Optional user ID for token generation

    Returns:
        Dictionary with WebSocket client functions
    """
    # State held in closures
    state = {
        "websocket": None,
        "connection_state": ConnectionState.DISCONNECTED,
        "reconnect_attempts": 0,
        "reconnect_task": None,
        "message_task": None,
        "current_token": None,
        "token_expires_at": None,
        "user_id": user_id,
        "message_handlers": set(),
        "connection_handlers": set(),
        "error_handlers": set(),
        "audio_data_handlers": set(),
    }

    def _update_connection_state(new_state: ConnectionState) -> None:
        """Update connection state and notify handlers"""
        state["connection_state"] = new_state
        logger.info(f"Connection state changed to: {new_state}")

        # Notify handlers
        for handler in state["connection_handlers"]:
            try:
                handler(new_state)
            except Exception as e:
                logger.error(f"Error in connection handler: {e}")

    def _handle_error(error: VocalsError) -> None:
        """Handle error and notify handlers"""
        logger.error(f"WebSocket error: {error.message} ({error.code})")

        # Notify handlers
        for handler in state["error_handlers"]:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")

    def _create_error(message: str, code: str = "VOCALS_ERROR") -> VocalsError:
        """Create an error object"""
        return VocalsError(message=message, code=code)

    async def _get_token() -> Optional[str]:
        """Get a valid token using WSToken generation"""
        if not config.use_token_auth:
            return None

        try:
            # Import WSToken functions dynamically to avoid circular imports
            from .wstoken import (
                generate_ws_token,
                generate_ws_token_with_user_id,
                is_token_expired,
                WSToken,
            )

            # Check if current token is still valid
            if state["current_token"] and state["token_expires_at"]:
                # Create WSToken object to check expiration
                ws_token = WSToken(
                    token=state["current_token"], expires_at=state["token_expires_at"]
                )
                if not is_token_expired(ws_token):
                    return state["current_token"]

            # Generate new token
            if state["user_id"]:
                token_result = generate_ws_token_with_user_id(state["user_id"])
            else:
                token_result = generate_ws_token()

            if isinstance(token_result, Ok):
                ws_token = token_result.data
                state["current_token"] = ws_token.token
                state["token_expires_at"] = ws_token.expires_at
                logger.info("Successfully generated new WSToken")
                return ws_token.token
            else:
                logger.error(
                    f"Failed to generate WSToken: {token_result.error.message}"
                )
                return None

        except Exception as e:
            logger.error(f"Error generating WSToken: {e}")
            return None

    async def connect() -> None:
        """Connect to the WebSocket server"""
        try:
            _update_connection_state(ConnectionState.CONNECTING)

            # Build WebSocket URL
            ws_url = await _build_websocket_url()

            # Connect to WebSocket
            state["websocket"] = await websockets.connect(ws_url)

            _update_connection_state(ConnectionState.CONNECTED)
            state["reconnect_attempts"] = 0

            # Start message handling as a background task
            state["message_task"] = asyncio.create_task(_handle_messages())

        except Exception as e:
            error = _create_error(f"Failed to connect: {str(e)}", "CONNECTION_FAILED")
            _handle_error(error)
            _update_connection_state(ConnectionState.ERROR)

            # Attempt reconnection if configured
            if state["reconnect_attempts"] < config.max_reconnect_attempts:
                _update_connection_state(ConnectionState.RECONNECTING)
                state["reconnect_attempts"] += 1

                # Schedule reconnection
                state["reconnect_task"] = asyncio.create_task(_reconnect_after_delay())
            else:
                _update_connection_state(ConnectionState.DISCONNECTED)

    async def _build_websocket_url() -> str:
        """Build the WebSocket URL with token if needed"""
        ws_url = config.ws_endpoint or "ws://192.168.1.46:8000/v1/stream/conversation"

        if config.use_token_auth:
            # Get fresh token using WSToken generation
            token = await _get_token()

            if token:
                # Add token as query parameter
                if "?" in ws_url:
                    ws_url += f"&token={token}"
                else:
                    ws_url += f"?token={token}"
            else:
                logger.warning("No token available for WebSocket connection")

        return ws_url

    async def _reconnect_after_delay() -> None:
        """Reconnect after configured delay"""
        await asyncio.sleep(config.reconnect_delay)
        await connect()

    async def _handle_messages() -> None:
        """Handle incoming WebSocket messages"""
        try:
            if not state["websocket"]:
                return
            async for message in state["websocket"]:
                try:
                    data = json.loads(message)
                    response = WebSocketResponse(
                        event=data.get("event", ""),
                        data=data.get("data"),
                        type=data.get("type"),
                    )

                    # Handle specific message types
                    await _process_message(response, data)

                    # Notify message handlers
                    for handler in state["message_handlers"]:
                        try:
                            handler(response)
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}")

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            _update_connection_state(ConnectionState.DISCONNECTED)

            # Attempt reconnection if configured
            if state["reconnect_attempts"] < config.max_reconnect_attempts:
                _update_connection_state(ConnectionState.RECONNECTING)
                state["reconnect_attempts"] += 1
                state["reconnect_task"] = asyncio.create_task(_reconnect_after_delay())

        except Exception as e:
            error = _create_error(
                f"Message handling error: {str(e)}", "MESSAGE_HANDLING_ERROR"
            )
            _handle_error(error)
            _update_connection_state(ConnectionState.ERROR)

    async def _process_message(
        response: WebSocketResponse, raw_data: Dict[str, Any]
    ) -> None:
        """Process specific message types"""
        # Handle speech interruption events
        if raw_data.get("type") == "speech_interruption":
            logger.info(f"Speech interruption received: {raw_data.get('data', {})}")
            # Additional processing can be added here

        # Handle TTS audio messages
        elif raw_data.get("type") == "tts_audio" and raw_data.get("data"):
            logger.info(
                f"TTS audio segment received: {raw_data['data'].get('segment_id', 'unknown')}"
            )
            # Additional processing can be added here

        # Handle audio data for visualization
        elif (
            response.event == "media"
            and response.data
            and isinstance(response.data, list)
        ):
            audio_data = response.data

            # Notify audio data handlers
            for handler in state["audio_data_handlers"]:
                try:
                    handler(audio_data)
                except Exception as e:
                    logger.error(f"Error in audio data handler: {e}")

    async def disconnect() -> None:
        """Disconnect from the WebSocket server"""
        # Cancel reconnection task if running
        if state["reconnect_task"] and not state["reconnect_task"].done():
            state["reconnect_task"].cancel()

        # Cancel message handling task if running
        if state["message_task"] and not state["message_task"].done():
            state["message_task"].cancel()
            try:
                await state["message_task"]
            except asyncio.CancelledError:
                pass

        # Close WebSocket connection
        if state["websocket"]:
            try:
                # Try to check if closed (different websockets versions have different attributes)
                is_closed = getattr(state["websocket"], "closed", False)
                if not is_closed:
                    await state["websocket"].close()
            except Exception as e:
                logger.debug(f"Error closing websocket: {e}")
                try:
                    await state["websocket"].close()
                except:
                    pass

        state["websocket"] = None
        state["message_task"] = None
        _update_connection_state(ConnectionState.DISCONNECTED)
        state["reconnect_attempts"] = 0

        # Clear token state
        state["current_token"] = None
        state["token_expires_at"] = None

    async def send_message(message: WebSocketMessage) -> None:
        """Send a message to the WebSocket server"""
        if not state["websocket"]:
            error = _create_error("WebSocket is not connected", "WS_NOT_CONNECTED")
            _handle_error(error)
            return

        # Check if websocket is closed
        try:
            is_closed = getattr(state["websocket"], "closed", False)
            if is_closed:
                error = _create_error("WebSocket is closed", "WS_CLOSED")
                _handle_error(error)
                return
        except Exception:
            # If we can't check the closed state, assume it's still open
            pass

        try:
            # Convert message to dict
            message_dict = {
                "event": message.event,
                "data": message.data,
                "format": message.format,
                "sampleRate": message.sample_rate,
            }

            # Remove None values
            message_dict = {k: v for k, v in message_dict.items() if v is not None}

            # Send message
            await state["websocket"].send(json.dumps(message_dict))

        except Exception as e:
            error = _create_error(
                f"Failed to send message: {str(e)}", "MESSAGE_SEND_FAILED"
            )
            _handle_error(error)

    # Event handler registration methods
    def add_message_handler(handler: MessageHandler) -> Callable[[], None]:
        """Add a message handler"""
        state["message_handlers"].add(handler)
        return lambda: state["message_handlers"].discard(handler)

    def add_connection_handler(handler: ConnectionHandler) -> Callable[[], None]:
        """Add a connection state handler"""
        state["connection_handlers"].add(handler)
        return lambda: state["connection_handlers"].discard(handler)

    def add_error_handler(handler: ErrorHandler) -> Callable[[], None]:
        """Add an error handler"""
        state["error_handlers"].add(handler)
        return lambda: state["error_handlers"].discard(handler)

    def add_audio_data_handler(handler: AudioDataHandler) -> Callable[[], None]:
        """Add an audio data handler"""
        state["audio_data_handlers"].add(handler)
        return lambda: state["audio_data_handlers"].discard(handler)

    # Property getters
    def get_connection_state() -> ConnectionState:
        return state["connection_state"]

    def get_is_connected() -> bool:
        """Check if WebSocket is connected"""
        return state["connection_state"] == ConnectionState.CONNECTED

    def get_is_connecting() -> bool:
        """Check if WebSocket is connecting or reconnecting"""
        return state["connection_state"] in [
            ConnectionState.CONNECTING,
            ConnectionState.RECONNECTING,
        ]

    def get_token_info() -> tuple:
        """Get current token info"""
        return (state["current_token"], state["token_expires_at"])

    def set_user_id(user_id: str) -> None:
        """Set user ID for token generation"""
        state["user_id"] = user_id
        # Clear current token to force regeneration with new user ID
        state["current_token"] = None
        state["token_expires_at"] = None

    # Return the websocket client interface
    return {
        "connect": connect,
        "disconnect": disconnect,
        "send_message": send_message,
        "add_message_handler": add_message_handler,
        "add_connection_handler": add_connection_handler,
        "add_error_handler": add_error_handler,
        "add_audio_data_handler": add_audio_data_handler,
        "get_connection_state": get_connection_state,
        "get_is_connected": get_is_connected,
        "get_is_connecting": get_is_connecting,
        "get_token_info": get_token_info,
        "set_user_id": set_user_id,
    }
