"""
Main Vocals SDK client, following functional composition pattern while mirroring the NextJS implementation.
"""

import asyncio
import logging
from typing import Optional, List, Callable, Dict, Any, Tuple

from .config import VocalsConfig, get_default_config
from .types import (
    ConnectionState,
    RecordingState,
    PlaybackState,
    VocalsError,
    VocalsSDKException,
    TTSAudioSegment,
    WebSocketMessage,
    WebSocketResponse,
    MessageHandler,
    ConnectionHandler,
    ErrorHandler,
    AudioDataHandler,
)
from .websocket_client import create_websocket_client
from .audio_processor import create_audio_processor, AudioConfig

logger = logging.getLogger(__name__)


def create_vocals(
    config: Optional[VocalsConfig] = None,
    audio_config: Optional[AudioConfig] = None,
    user_id: Optional[str] = None,
):
    """
    Create a Vocals SDK instance for voice processing and real-time audio communication.

    This function provides the same functionality as the NextJS useVocals hook
    but using functional composition instead of class-based structure.

    Args:
        config: Configuration options for the SDK
        audio_config: Audio processing configuration
        user_id: Optional user ID for token generation

    Returns:
        Dictionary with SDK functions and properties
    """
    # Initialize configurations
    config = config or get_default_config()
    audio_config = audio_config or AudioConfig()

    # Setup logging based on configuration
    config.setup_logging()

    # Create components using functional approach
    websocket_client = create_websocket_client(config, user_id)
    audio_processor = create_audio_processor(audio_config)

    # Store event loop reference for audio callback thread
    event_loop = None
    # Flag to track if microphone streaming is active (to avoid duplicate TTS processing)
    microphone_streaming_active = False

    def _handle_websocket_message(message: WebSocketResponse) -> None:
        """Handle incoming WebSocket messages"""
        try:
            # Handle TTS audio messages (skip if microphone streaming is handling it)
            if (
                message.type == "tts_audio"
                and message.data
                and not microphone_streaming_active
            ):
                # Convert to TTSAudioSegment
                segment_data = message.data
                segment = TTSAudioSegment(
                    text=segment_data.get("text", ""),
                    audio_data=segment_data.get("audio_data", ""),
                    sample_rate=segment_data.get("sample_rate", 24000),
                    segment_id=segment_data.get("segment_id", ""),
                    sentence_number=segment_data.get("sentence_number", 0),
                    generation_time_ms=segment_data.get("generation_time_ms", 0),
                    format=segment_data.get("format", "wav"),
                    duration_seconds=segment_data.get("duration_seconds", 0.0),
                )

                # Add to audio queue
                audio_processor["add_to_queue"](segment)

                # Auto-start playback if not already playing
                if not audio_processor["get_is_playing"]():
                    asyncio.create_task(audio_processor["play_audio"]())

            # Handle speech interruption messages
            elif message.type == "speech_interruption":
                logger.info(f"Speech interruption received: {message.data}")

                # Fade out current audio and clear queue for new speech
                asyncio.create_task(_handle_speech_interruption())

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def _handle_speech_interruption() -> None:
        """Handle speech interruption events"""
        try:
            # Fade out current audio
            await audio_processor["fade_out_audio"](0.3)

            # Clear the queue
            audio_processor["clear_queue"]()

        except Exception as e:
            logger.error(f"Error handling speech interruption: {e}")

    def _handle_audio_data(audio_data: List[float]) -> None:
        """Handle audio data from processor"""
        # Send audio data to WebSocket if connected and recording
        if (
            websocket_client["get_is_connected"]()
            and audio_processor["get_recording_state"]() == RecordingState.RECORDING
        ):
            message = WebSocketMessage(
                event="media",
                data=audio_data,
                format=audio_config.format,
                sample_rate=audio_config.sample_rate,
            )

            # Schedule the coroutine in the main event loop since we're in a callback thread
            if event_loop:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        websocket_client["send_message"](message), event_loop
                    )

                    # Add a callback to handle any errors
                    def handle_send_result(fut):
                        try:
                            fut.result()  # This will raise any exceptions
                        except Exception as e:
                            logger.error(f"Error sending audio data: {e}")

                    future.add_done_callback(handle_send_result)
                except Exception as e:
                    logger.error(f"Error scheduling audio data send: {e}")
            else:
                logger.warning("No event loop available for audio data sending")

    def _handle_error(error: VocalsError) -> None:
        """Handle errors from components"""
        logger.error(f"SDK Error: {error.message} ({error.code})")
        # Additional error handling can be added here

    # Set up event handlers between components
    websocket_client["add_message_handler"](_handle_websocket_message)
    audio_processor["add_audio_data_handler"](_handle_audio_data)
    websocket_client["add_error_handler"](_handle_error)
    audio_processor["add_error_handler"](_handle_error)

    # Connection methods
    async def connect() -> None:
        """Connect to the WebSocket server"""
        await websocket_client["connect"]()

    async def disconnect() -> None:
        """Disconnect from the WebSocket server"""
        await websocket_client["disconnect"]()
        audio_processor["cleanup"]()

    async def reconnect() -> None:
        """Reconnect to the WebSocket server"""
        await disconnect()
        await connect()

    # Voice recording methods
    async def start_recording() -> None:
        """Start voice recording"""
        nonlocal event_loop

        # Capture the event loop for audio callback thread
        try:
            event_loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No event loop running when starting recording")

        # Ensure we're connected
        if not websocket_client["get_is_connected"]():
            await connect()

        # Send start event
        start_message = WebSocketMessage(event="start")
        await websocket_client["send_message"](start_message)

        # Start audio recording
        await audio_processor["start_recording"]()

        # Send settings event with sample rate
        settings_message = WebSocketMessage(
            event="settings", data={"sampleRate": audio_config.sample_rate}
        )
        await websocket_client["send_message"](settings_message)

    async def stop_recording() -> None:
        """Stop voice recording"""
        # Stop audio recording
        await audio_processor["stop_recording"]()

        # Send stop event
        stop_message = WebSocketMessage(event="stop")
        await websocket_client["send_message"](stop_message)

    # Audio playback methods
    async def play_audio() -> None:
        """Start or resume audio playback"""
        await audio_processor["play_audio"]()

    async def pause_audio() -> None:
        """Pause audio playback"""
        await audio_processor["pause_audio"]()

    async def stop_audio() -> None:
        """Stop audio playback"""
        await audio_processor["stop_audio"]()

    async def fade_out_audio(duration: float = 0.5) -> None:
        """Fade out current audio over specified duration"""
        await audio_processor["fade_out_audio"](duration)

    def clear_queue() -> None:
        """Clear the audio playback queue"""
        audio_processor["clear_queue"]()

    def add_to_queue(segment: TTSAudioSegment) -> None:
        """Add an audio segment to the playback queue"""
        audio_processor["add_to_queue"](segment)

    # Messaging methods
    async def send_message(message: WebSocketMessage) -> None:
        """Send a message to the WebSocket server"""
        await websocket_client["send_message"](message)

    # High-level audio file streaming
    async def stream_audio_file(
        file_path: str,
        chunk_size: int = 1024,
        verbose: bool = True,
        auto_connect: bool = True,
    ) -> None:
        """
        High-level method to stream an audio file to the WebSocket server.

        This method handles the entire flow:
        1. Loads the audio file
        2. Connects to WebSocket if not connected
        3. Sends start and settings messages
        4. Streams audio in chunks
        5. Sends stop message
        6. Handles any received audio playback

        Args:
            file_path: Path to the audio file to stream
            chunk_size: Size of each chunk to send
            verbose: Whether to log detailed progress
            auto_connect: Whether to automatically connect if not connected

        Raises:
            VocalsError: If there's an error streaming the file
        """
        try:
            from .utils import load_audio_file, send_audio_in_chunks

            if verbose:
                logger.info(f"🎵 Starting to stream audio file: {file_path}")

            # Load audio file
            audio_data = load_audio_file(file_path)
            if not audio_data:
                raise VocalsSDKException(
                    "AUDIO_LOAD_ERROR", f"Failed to load audio file: {file_path}"
                )

            if verbose:
                logger.info(f"✅ Loaded {len(audio_data)} audio samples")

            # Connect if not connected
            if auto_connect and not websocket_client["get_is_connected"]():
                if verbose:
                    logger.info("Connecting to WebSocket...")
                await connect()
                # Give it a moment to establish connection
                await asyncio.sleep(1)

            # Verify connection
            if not websocket_client["get_is_connected"]():
                raise VocalsSDKException(
                    "CONNECTION_ERROR", "Not connected to WebSocket server"
                )

            # Send start message
            if verbose:
                logger.info("Sending start message...")
            start_message = WebSocketMessage(event="start")
            await websocket_client["send_message"](start_message)

            # Send settings message
            if verbose:
                logger.info("Sending settings message...")
            settings_message = WebSocketMessage(
                event="settings", data={"sampleRate": audio_config.sample_rate}
            )
            await websocket_client["send_message"](settings_message)

            # Stream audio in chunks
            if verbose:
                logger.info("Starting audio chunk streaming...")
            await send_audio_in_chunks(
                websocket_client["send_message"],
                audio_data,
                chunk_size=chunk_size,
                sample_rate=audio_config.sample_rate,
                verbose=verbose,
            )

            # Send stop message
            if verbose:
                logger.info("Sending stop message...")
            stop_message = WebSocketMessage(event="stop")
            await websocket_client["send_message"](stop_message)

            # Wait for any final responses
            if verbose:
                logger.info("Waiting for responses...")
            await asyncio.sleep(2)

            # Check for any audio in queue and play it
            audio_queue = audio_processor["get_audio_queue"]()
            if audio_queue:
                if verbose:
                    logger.info(f"Playing {len(audio_queue)} audio segments...")
                await audio_processor["play_audio"]()

                # Wait for playback to complete
                while audio_processor["get_is_playing"]():
                    await asyncio.sleep(0.1)

                if verbose:
                    logger.info("✅ Playback completed")

            if verbose:
                logger.info("🎉 Audio file streaming completed successfully")

        except Exception as e:
            error_msg = f"Error streaming audio file: {e}"
            logger.error(error_msg)
            raise VocalsSDKException("AUDIO_STREAM_ERROR", error_msg)

    # High-level microphone streaming
    async def stream_microphone(
        duration: float = 30.0,
        auto_connect: bool = True,
        auto_playback: bool = True,
        verbose: bool = True,
        stats_tracking: bool = True,
        amplitude_threshold: float = 0.01,
    ) -> Optional[dict]:
        """
        High-level method to stream from microphone for a specified duration.

        This method handles the entire microphone streaming flow:
        1. Connects to WebSocket if not connected
        2. Sets up optimized handlers for microphone streaming
        3. Starts recording for the specified duration
        4. Automatically plays back received audio
        5. Tracks statistics and provides session summary

        Args:
            duration: Recording duration in seconds (0 for infinite)
            auto_connect: Whether to automatically connect if not connected
            auto_playback: Whether to automatically play received audio
            verbose: Whether to log detailed progress
            stats_tracking: Whether to track and return statistics
            amplitude_threshold: Minimum amplitude to consider as speech

        Returns:
            Optional dictionary with session statistics if stats_tracking is True

        Raises:
            VocalsSDKException: If there's an error during streaming
        """
        try:
            from .utils import (
                create_microphone_stats_tracker,
                create_microphone_message_handler,
                create_microphone_connection_handler,
                create_microphone_audio_data_handler,
            )

            # Set flag to prevent default handler from processing TTS messages
            nonlocal microphone_streaming_active
            microphone_streaming_active = True

            if verbose:
                logger.info(f"🎤 Starting microphone streaming for {duration}s...")

            # Initialize statistics tracker
            stats_tracker = None
            if stats_tracking:
                stats_tracker = create_microphone_stats_tracker(verbose)

            # Connect if not connected
            if auto_connect and not websocket_client["get_is_connected"]():
                if verbose:
                    logger.info("Connecting to WebSocket...")
                await connect()
                # Give it a moment to establish connection
                await asyncio.sleep(1)

            # Verify connection
            if not websocket_client["get_is_connected"]():
                raise VocalsSDKException(
                    "CONNECTION_ERROR", "Not connected to WebSocket server"
                )

            # Set up optimized handlers
            message_handler = create_microphone_message_handler(
                stats_tracker, verbose, audio_processor=audio_processor
            )
            connection_handler = create_microphone_connection_handler(
                stats_tracker, verbose
            )
            audio_data_handler = create_microphone_audio_data_handler(
                amplitude_threshold, verbose
            )

            # Register microphone-specific handlers (they'll handle TTS display)
            remove_message_handler = websocket_client["add_message_handler"](
                message_handler
            )
            remove_connection_handler = websocket_client["add_connection_handler"](
                connection_handler
            )
            remove_audio_handler = audio_processor["add_audio_data_handler"](
                audio_data_handler
            )

            # Start playback monitoring if enabled
            playback_monitor_task = None
            if auto_playback:

                async def monitor_playback():
                    try:
                        while True:
                            # Check if there's audio in queue and we're not playing
                            audio_queue = audio_processor["get_audio_queue"]()
                            is_playing = audio_processor["get_is_playing"]()

                            if audio_queue and not is_playing:
                                if verbose:
                                    logger.info(
                                        f"🎶 Auto-playing {len(audio_queue)} queued audio segments"
                                    )
                                await audio_processor["play_audio"]()

                            await asyncio.sleep(0.1)  # Check every 100ms

                    except asyncio.CancelledError:
                        if verbose:
                            logger.debug("Playback monitor cancelled")
                        raise
                    except Exception as e:
                        logger.error(f"Error in playback monitor: {e}")
                        raise

                playback_monitor_task = asyncio.create_task(monitor_playback())

            try:
                # Start recording
                if verbose:
                    logger.info("🎙️ Starting recording session...")
                await start_recording()

                # Record for specified duration
                if duration > 0:
                    start_time = asyncio.get_event_loop().time()
                    while (asyncio.get_event_loop().time() - start_time) < duration:
                        # Show recording status
                        if verbose:
                            recording_state = audio_processor["get_recording_state"]()
                            amplitude = audio_processor["get_current_amplitude"]()

                            if (
                                recording_state.name == "RECORDING"
                                and amplitude > amplitude_threshold
                            ):
                                logger.debug(
                                    f"🎤 Recording... amplitude: {amplitude:.4f}"
                                )

                        await asyncio.sleep(0.5)

                        # Update recording time stats
                        if stats_tracker:
                            stats_tracker["update"]("recording_time", duration)

                else:
                    # Infinite recording - wait for external stop
                    if verbose:
                        logger.info(
                            "🎙️ Recording indefinitely... (use stop_recording() to stop)"
                        )
                    while audio_processor["get_recording_state"]().name == "RECORDING":
                        await asyncio.sleep(0.5)

                # Stop recording
                if verbose:
                    logger.info("🛑 Stopping recording session...")
                await stop_recording()

                # Wait for any final responses
                if verbose:
                    logger.info("Waiting for final responses...")
                await asyncio.sleep(2)

                # Wait for playback to complete if auto_playback is enabled
                if auto_playback:
                    while audio_processor["get_is_playing"]():
                        if verbose:
                            current_segment = audio_processor["get_current_segment"]()
                            if current_segment:
                                logger.debug(f"🎵 Playing: {current_segment.text}")
                        await asyncio.sleep(0.1)

                    if verbose:
                        logger.info("✅ Playback completed")

                # Print final statistics
                if stats_tracker and verbose:
                    stats_tracker["print"]()

                if verbose:
                    logger.info("🎉 Microphone streaming completed successfully")

                return stats_tracker["stats"] if stats_tracker else None

            finally:
                # Cancel playback monitor
                if playback_monitor_task:
                    playback_monitor_task.cancel()
                    try:
                        await playback_monitor_task
                    except asyncio.CancelledError:
                        pass

                # Cleanup handlers
                remove_message_handler()
                remove_connection_handler()
                remove_audio_handler()

        except Exception as e:
            error_msg = f"Error during microphone streaming: {e}"
            logger.error(error_msg)
            raise VocalsSDKException("MICROPHONE_STREAM_ERROR", error_msg)
        finally:
            # Reset flag to allow default handler to process TTS messages again
            microphone_streaming_active = False

    # Event handler registration methods
    def on_message(handler: MessageHandler) -> Callable[[], None]:
        """Register a message handler"""
        return websocket_client["add_message_handler"](handler)

    def on_connection_change(handler: ConnectionHandler) -> Callable[[], None]:
        """Register a connection state change handler"""
        return websocket_client["add_connection_handler"](handler)

    def on_error(handler: ErrorHandler) -> Callable[[], None]:
        """Register an error handler"""
        return websocket_client["add_error_handler"](handler)

    def on_audio_data(handler: AudioDataHandler) -> Callable[[], None]:
        """Register an audio data handler"""
        return audio_processor["add_audio_data_handler"](handler)

    # Property getters
    def get_connection_state() -> ConnectionState:
        """Get the current connection state"""
        return websocket_client["get_connection_state"]()

    def get_is_connected() -> bool:
        """Check if connected to the WebSocket server"""
        return websocket_client["get_is_connected"]()

    def get_is_connecting() -> bool:
        """Check if connecting or reconnecting to the WebSocket server"""
        return websocket_client["get_is_connecting"]()

    def get_recording_state() -> RecordingState:
        """Get the current recording state"""
        return audio_processor["get_recording_state"]()

    def get_is_recording() -> bool:
        """Check if currently recording"""
        return audio_processor["get_is_recording"]()

    def get_playback_state() -> PlaybackState:
        """Get the current playback state"""
        return audio_processor["get_playback_state"]()

    def get_is_playing() -> bool:
        """Check if currently playing audio"""
        return audio_processor["get_is_playing"]()

    def get_audio_queue() -> List[TTSAudioSegment]:
        """Get the current audio queue"""
        return audio_processor["get_audio_queue"]()

    def get_current_segment() -> Optional[TTSAudioSegment]:
        """Get the currently playing audio segment"""
        return audio_processor["get_current_segment"]()

    def get_current_amplitude() -> float:
        """Get the current audio amplitude for visualization"""
        return audio_processor["get_current_amplitude"]()

    def get_token() -> Optional[str]:
        """Get the current token"""
        token_info = websocket_client["get_token_info"]()
        return token_info[0]

    def get_token_expires_at() -> Optional[float]:
        """Get the token expiration timestamp"""
        token_info = websocket_client["get_token_info"]()
        return token_info[1]

    def set_user_id(user_id: str) -> None:
        """Set user ID for token generation"""
        websocket_client["set_user_id"](user_id)

    # Context manager support
    async def __aenter__():
        """Async context manager entry"""
        await connect()
        return {
            "connect": connect,
            "disconnect": disconnect,
            "reconnect": reconnect,
            "start_recording": start_recording,
            "stop_recording": stop_recording,
            "play_audio": play_audio,
            "pause_audio": pause_audio,
            "stop_audio": stop_audio,
            "fade_out_audio": fade_out_audio,
            "clear_queue": clear_queue,
            "add_to_queue": add_to_queue,
            "send_message": send_message,
            "on_message": on_message,
            "on_connection_change": on_connection_change,
            "on_error": on_error,
            "on_audio_data": on_audio_data,
            "get_connection_state": get_connection_state,
            "get_is_connected": get_is_connected,
            "get_is_connecting": get_is_connecting,
            "get_recording_state": get_recording_state,
            "get_is_recording": get_is_recording,
            "get_playback_state": get_playback_state,
            "get_is_playing": get_is_playing,
            "get_audio_queue": get_audio_queue,
            "get_current_segment": get_current_segment,
            "get_current_amplitude": get_current_amplitude,
            "get_token": get_token,
            "get_token_expires_at": get_token_expires_at,
            "set_user_id": set_user_id,
            "cleanup": cleanup,
        }

    async def __aexit__(exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await disconnect()

    # Cleanup
    def cleanup() -> None:
        """Clean up resources"""
        audio_processor["cleanup"]()
        # WebSocket client cleanup is handled by disconnect

    # Auto-connect if configured
    if config.auto_connect:
        asyncio.create_task(connect())

    # Return the SDK interface
    return {
        "connect": connect,
        "disconnect": disconnect,
        "reconnect": reconnect,
        "start_recording": start_recording,
        "stop_recording": stop_recording,
        "play_audio": play_audio,
        "pause_audio": pause_audio,
        "stop_audio": stop_audio,
        "fade_out_audio": fade_out_audio,
        "clear_queue": clear_queue,
        "add_to_queue": add_to_queue,
        "send_message": send_message,
        "stream_audio_file": stream_audio_file,
        "stream_microphone": stream_microphone,
        "on_message": on_message,
        "on_connection_change": on_connection_change,
        "on_error": on_error,
        "on_audio_data": on_audio_data,
        "get_connection_state": get_connection_state,
        "get_is_connected": get_is_connected,
        "get_is_connecting": get_is_connecting,
        "get_recording_state": get_recording_state,
        "get_is_recording": get_is_recording,
        "get_playback_state": get_playback_state,
        "get_is_playing": get_is_playing,
        "get_audio_queue": get_audio_queue,
        "get_current_segment": get_current_segment,
        "get_current_amplitude": get_current_amplitude,
        "get_token": get_token,
        "get_token_expires_at": get_token_expires_at,
        "set_user_id": set_user_id,
        "cleanup": cleanup,
        "__aenter__": __aenter__,
        "__aexit__": __aexit__,
    }
