"""
Utilities for Vocals SDK - common helper functions for audio processing and file handling.
"""

import logging
import wave
import asyncio
from pathlib import Path
from typing import List, Optional, Union

logger = logging.getLogger(__name__)


def load_audio_file(file_path: Union[str, Path]) -> Optional[List[float]]:
    """
    Load audio file and convert to float32 list.

    Args:
        file_path: Path to the audio file (supports .wav files)

    Returns:
        List of audio samples normalized to float32 or None if failed
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"Audio file not found: {file_path}")
            return None

        with wave.open(str(file_path), "rb") as wav_file:
            # Get audio properties
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frames = wav_file.getnframes()

            logger.info(
                f"Audio file properties: {sample_rate}Hz, {channels}ch, {sample_width}B, {frames} frames"
            )

            # Read audio data
            audio_data = wav_file.readframes(frames)

            # Convert to float32 based on sample width
            if sample_width == 2:  # 16-bit
                import numpy as np

                audio_array = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            elif sample_width == 4:  # 32-bit float
                import numpy as np

                audio_array = np.frombuffer(audio_data, dtype=np.float32)
            else:
                logger.error(f"Unsupported sample width: {sample_width}")
                return None

            # Convert to mono if stereo
            if channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1)

            return audio_array.tolist()

    except Exception as e:
        logger.error(f"Error loading audio file: {e}")
        return None


def create_default_message_handler(verbose: bool = True):
    """
    Create a simple default message handler for common use cases.

    Args:
        verbose: Whether to log detailed message information

    Returns:
        Message handler function
    """

    def handle_message(message) -> None:
        """Handle incoming WebSocket messages with basic logging"""
        try:
            if verbose:
                logger.info(f"Received message: {message.type} - {message.event}")

            if message.type == "tts_audio" and message.data:
                if verbose:
                    logger.info(
                        f"Received TTS audio segment: {message.data.get('segment_id', 'unknown')}"
                    )

            elif message.type == "speech_interruption":
                if verbose:
                    logger.info("Speech interruption detected")

            elif message.event == "transcription":
                if message.data and verbose:
                    logger.info(f"Transcription: {message.data}")

            elif message.event == "response":
                if message.data and verbose:
                    logger.info(f"Response: {message.data}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    return handle_message


def create_enhanced_message_handler(
    verbose: bool = True,
    show_transcription: bool = True,
    show_responses: bool = True,
    show_streaming: bool = True,
    show_detection: bool = False,
):
    """
    Create an enhanced message handler that beautifully displays all message types including
    transcription with partial updates, streaming LLM responses, detection, and status messages.

    Args:
        verbose: Whether to log detailed message information
        show_transcription: Whether to highlight transcription text
        show_responses: Whether to highlight LLM responses
        show_streaming: Whether to show streaming LLM responses in real-time
        show_detection: Whether to show real-time detection/interim results

    Returns:
        Enhanced message handler function
    """
    # Track streaming state
    streaming_responses = {}
    current_transcripts = {}

    def handle_message(message) -> None:
        """Handle incoming WebSocket messages with enhanced text display"""
        try:
            if message.type == "transcription" and message.data:
                # Handle structured transcription messages with partial updates
                text = message.data.get("text", "")
                is_partial = message.data.get("is_partial", False)
                segment_id = message.data.get("segment_id", "unknown")

                if verbose:
                    logger.info(
                        f"📝 Transcription [{segment_id}]: '{text}' (partial: {is_partial})"
                    )

                # Show transcription with partial indicator
                if show_transcription and text:
                    if is_partial:
                        print(f"\r🎤 You're saying: {text}...", end="", flush=True)
                        current_transcripts[segment_id] = text
                    else:
                        # Final transcription
                        if segment_id in current_transcripts:
                            print()  # New line after partial updates
                        print(f"\n🎤 You said: {text}")
                        current_transcripts.pop(segment_id, None)

            elif message.type == "llm_response_streaming" and message.data:
                # Handle streaming LLM responses
                token = message.data.get("token", "")
                accumulated = message.data.get("accumulated_response", "")
                is_complete = message.data.get("is_complete", False)
                segment_id = message.data.get("segment_id", "unknown")

                if verbose:
                    logger.info(
                        f"💭 LLM Streaming [{segment_id}]: token='{token}', complete={is_complete}"
                    )

                # Show streaming response
                if show_streaming and show_responses:
                    if segment_id not in streaming_responses:
                        print(f"\n💭 AI Thinking: ", end="", flush=True)
                        streaming_responses[segment_id] = ""

                    if token:
                        print(token, end="", flush=True)
                        streaming_responses[segment_id] += token

                    if is_complete:
                        print()  # New line when complete
                        final_text = accumulated or streaming_responses[segment_id]
                        if verbose:
                            logger.info(
                                f"💬 LLM Complete [{segment_id}]: '{final_text}'"
                            )
                        streaming_responses.pop(segment_id, None)

            elif message.type == "llm_response" and message.data:
                # Handle complete LLM responses (non-streaming)
                response_text = message.data.get("response", "")
                original_text = message.data.get("original_text", "")
                segment_id = message.data.get("segment_id", "unknown")

                if verbose:
                    logger.info(f"💬 LLM Response [{segment_id}]: '{response_text}'")

                # Show complete response
                if show_responses and response_text:
                    print(f"\n💭 AI Response: {response_text}")

            elif message.type == "tts_audio" and message.data:
                # Extract text from TTS audio data
                text = message.data.get("text", "")
                segment_id = message.data.get("segment_id", "unknown")
                duration = message.data.get("duration_seconds", 0)

                if verbose:
                    logger.info(
                        f"🎵 TTS Audio [{segment_id}]: '{text}' ({duration:.2f}s)"
                    )

                # Show TTS audio text
                if show_responses and text:
                    print(f"\n🤖 AI Speaking: {text}")

            elif message.type == "detection":
                # Handle real-time detection/interim results
                detection_text = getattr(message, "text", "")
                confidence = getattr(message, "confidence", 0)

                if verbose:
                    logger.debug(
                        f"🔍 Detection: '{detection_text}' (confidence: {confidence})"
                    )

                # Show real-time detection if enabled
                if show_detection and detection_text:
                    print(f"\r🔍 Detecting: {detection_text}", end="", flush=True)

            elif message.type == "transcription_status" and message.data:
                # Handle transcription status messages
                status = message.data
                if verbose:
                    logger.info(f"📊 Transcription Status: {status}")

            elif message.type == "audio_saved" and hasattr(message, "filename"):
                # Handle audio saved notifications
                filename = message.filename
                if verbose:
                    logger.info(f"💾 Audio Saved: {filename}")
                if show_transcription:
                    print(f"\n💾 Audio saved to: {filename}")

            elif message.type == "speech_interruption":
                if verbose:
                    logger.info("🛑 Speech interruption detected")
                if show_transcription:
                    print(f"\n🛑 Speech interrupted - processing...")

            elif message.event == "transcription":
                # Handle legacy transcription format
                if message.data:
                    transcription_text = str(message.data)
                    if verbose:
                        logger.info(f"📝 Legacy Transcription: {transcription_text}")
                    if show_transcription:
                        print(f"\n🎤 You said: {transcription_text}")

            elif message.event == "response":
                # Handle legacy response format
                if message.data:
                    response_text = str(message.data)
                    if verbose:
                        logger.info(f"💬 Legacy Response: {response_text}")
                    if show_responses:
                        print(f"\n💭 AI Response: {response_text}")

            elif message.event == "error":
                if verbose:
                    logger.error(f"❌ Server Error: {message.data}")
                print(f"\n❌ Error: {message.data}")

            elif verbose:
                # Log other message types
                logger.debug(
                    f"📨 Other message: {message.type or 'unknown'} - {message.event}"
                )

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    return handle_message


def create_conversation_tracker():
    """
    Create a conversation tracker that maintains the dialogue history including
    partial transcriptions, streaming responses, and all message types.

    Returns:
        Dictionary with conversation tracking functions
    """
    conversation = {
        "transcriptions": [],
        "responses": [],
        "tts_segments": [],
        "streaming_responses": [],
        "detections": [],
        "status_updates": [],
        "start_time": None,
    }

    def add_transcription(
        text: str, is_partial: bool = False, segment_id: Optional[str] = None
    ):
        """Add a transcription to the conversation"""
        import time

        entry = {
            "text": text,
            "timestamp": time.time(),
            "is_partial": is_partial,
            "segment_id": segment_id,
        }

        # For partial transcriptions, update existing entry or add new one
        if is_partial and segment_id:
            # Find existing partial transcription with same segment_id
            for i, trans in enumerate(conversation["transcriptions"]):
                if trans.get("segment_id") == segment_id and trans.get("is_partial"):
                    conversation["transcriptions"][i] = entry
                    return

        # Add new transcription
        conversation["transcriptions"].append(entry)
        if conversation["start_time"] is None:
            conversation["start_time"] = time.time()

    def add_response(
        text: str,
        is_streaming: bool = False,
        is_complete: bool = True,
        segment_id: Optional[str] = None,
    ):
        """Add an LLM response to the conversation"""
        import time

        if is_streaming:
            # Handle streaming responses
            entry = {
                "text": text,
                "timestamp": time.time(),
                "is_complete": is_complete,
                "segment_id": segment_id,
            }

            if not is_complete and segment_id:
                # Update existing streaming response
                for i, resp in enumerate(conversation["streaming_responses"]):
                    if resp.get("segment_id") == segment_id:
                        conversation["streaming_responses"][i] = entry
                        return
                # Add new streaming response
                conversation["streaming_responses"].append(entry)
            else:
                # Complete response - move from streaming to regular responses
                conversation["responses"].append(
                    {"text": text, "timestamp": time.time(), "segment_id": segment_id}
                )
                # Remove from streaming responses
                conversation["streaming_responses"] = [
                    r
                    for r in conversation["streaming_responses"]
                    if r.get("segment_id") != segment_id
                ]
        else:
            # Regular complete response
            conversation["responses"].append(
                {"text": text, "timestamp": time.time(), "segment_id": segment_id}
            )

    def add_tts_segment(text: str, segment_id: str):
        """Add a TTS segment to the conversation"""
        import time

        conversation["tts_segments"].append(
            {"text": text, "segment_id": segment_id, "timestamp": time.time()}
        )

    def add_detection(text: str, confidence: float = 0):
        """Add a detection/interim result to the conversation"""
        import time

        conversation["detections"].append(
            {"text": text, "confidence": confidence, "timestamp": time.time()}
        )

    def add_status_update(status: str, message_type: str = "status"):
        """Add a status update to the conversation"""
        import time

        conversation["status_updates"].append(
            {"status": status, "type": message_type, "timestamp": time.time()}
        )

    def print_conversation():
        """Print the full conversation history"""
        print("\n" + "=" * 60)
        print("📜 CONVERSATION HISTORY")
        print("=" * 60)

        all_events = []

        # Add all events with timestamps
        for t in conversation["transcriptions"]:
            if not t.get("is_partial", False):  # Only show final transcriptions
                all_events.append(("transcription", t["text"], t["timestamp"]))

        for r in conversation["responses"]:
            all_events.append(("response", r["text"], r["timestamp"]))

        for tts in conversation["tts_segments"]:
            all_events.append(("tts", tts["text"], tts["timestamp"]))

        for s in conversation["streaming_responses"]:
            if s.get("is_complete", True):  # Only show completed streaming responses
                all_events.append(("streaming", s["text"], s["timestamp"]))

        # Sort by timestamp
        all_events.sort(key=lambda x: x[2])

        # Print in chronological order
        for event_type, text, timestamp in all_events:
            if event_type == "transcription":
                print(f"\n🎤 YOU: {text}")
            elif event_type == "response":
                print(f"\n💭 AI (thinking): {text}")
            elif event_type == "streaming":
                print(f"\n💭 AI (streaming): {text}")
            elif event_type == "tts":
                print(f"\n🤖 AI (speaking): {text}")

        print("\n" + "=" * 60)

        # Show statistics
        final_transcriptions = [
            t for t in conversation["transcriptions"] if not t.get("is_partial", False)
        ]
        completed_streaming = [
            s for s in conversation["streaming_responses"] if s.get("is_complete", True)
        ]

        print(
            f"📊 Total: {len(final_transcriptions)} transcriptions, "
            f"{len(conversation['responses'])} responses, "
            f"{len(completed_streaming)} streaming responses, "
            f"{len(conversation['tts_segments'])} TTS segments"
        )

        if conversation["detections"]:
            print(f"🔍 {len(conversation['detections'])} detection events")

        if conversation["status_updates"]:
            print(f"📊 {len(conversation['status_updates'])} status updates")

        print("=" * 60)

    def get_stats():
        """Get conversation statistics"""
        import time

        # Count only final (non-partial) transcriptions
        final_transcriptions = [
            t for t in conversation["transcriptions"] if not t.get("is_partial", False)
        ]

        return {
            "transcriptions": len(final_transcriptions),
            "partial_transcriptions": len(
                [
                    t
                    for t in conversation["transcriptions"]
                    if t.get("is_partial", False)
                ]
            ),
            "responses": len(conversation["responses"]),
            "streaming_responses": len(conversation["streaming_responses"]),
            "tts_segments": len(conversation["tts_segments"]),
            "detections": len(conversation["detections"]),
            "status_updates": len(conversation["status_updates"]),
            "duration": (
                time.time() - conversation["start_time"]
                if conversation["start_time"]
                else 0
            ),
        }

    return {
        "add_transcription": add_transcription,
        "add_response": add_response,
        "add_tts_segment": add_tts_segment,
        "add_detection": add_detection,
        "add_status_update": add_status_update,
        "print_conversation": print_conversation,
        "get_stats": get_stats,
        "conversation": conversation,
    }


def create_default_connection_handler(verbose: bool = True):
    """
    Create a simple default connection handler for common use cases.

    Args:
        verbose: Whether to log connection state changes

    Returns:
        Connection handler function
    """

    def handle_connection(state) -> None:
        """Handle connection state changes with basic logging"""
        if verbose:
            logger.info(f"Connection state changed: {state}")

            if state.name == "CONNECTED":
                logger.info("✅ Connected to Vocals WebSocket")
            elif state.name == "DISCONNECTED":
                logger.info("❌ Disconnected from Vocals WebSocket")
            elif state.name == "RECONNECTING":
                logger.info("🔄 Reconnecting to Vocals WebSocket...")

    return handle_connection


def create_default_error_handler(verbose: bool = True):
    """
    Create a simple default error handler for common use cases.

    Args:
        verbose: Whether to log errors

    Returns:
        Error handler function
    """

    def handle_error(error) -> None:
        """Handle SDK errors with basic logging"""
        if verbose:
            logger.error(f"SDK Error [{error.code}]: {error.message}")

    return handle_error


async def send_audio_in_chunks(
    send_message_func,
    audio_data: List[float],
    chunk_size: int = 1024,
    sample_rate: int = 24000,
    verbose: bool = True,
) -> None:
    """
    Send audio data in chunks with proper timing simulation.

    Args:
        send_message_func: Function to send WebSocket messages
        audio_data: List of audio samples
        chunk_size: Size of each chunk to send
        sample_rate: Sample rate for timing calculations
        verbose: Whether to log progress

    Raises:
        Exception: If there's an error sending chunks
    """
    try:
        if verbose:
            logger.info(
                f"Sending {len(audio_data)} audio samples in chunks of {chunk_size}"
            )

        total_chunks = len(audio_data) // chunk_size
        if verbose:
            logger.info(f"Total chunks to send: {total_chunks}")

        from .types import WebSocketMessage

        # Send audio chunks
        for i in range(0, len(audio_data), chunk_size):
            chunk_num = i // chunk_size + 1
            chunk = audio_data[i : i + chunk_size]

            if verbose:
                logger.info(
                    f"Sending chunk {chunk_num}/{total_chunks} (size: {len(chunk)})"
                )

            # Create media message
            message = WebSocketMessage(
                event="media", data=chunk, format="pcm_f32le", sample_rate=sample_rate
            )

            # Send chunk with timeout
            try:
                await asyncio.wait_for(send_message_func(message), timeout=5.0)
                if verbose:
                    logger.info(f"✅ Chunk {chunk_num} sent successfully")
            except asyncio.TimeoutError:
                logger.error(f"Timeout sending chunk {chunk_num}")
                raise
            except Exception as e:
                logger.error(f"Error sending chunk {chunk_num}: {e}")
                raise

            # Small delay to simulate real-time streaming
            sleep_time = chunk_size / sample_rate
            if verbose:
                logger.debug(f"Sleeping for {sleep_time:.4f} seconds...")
            await asyncio.sleep(sleep_time)

        if verbose:
            logger.info("✅ Finished sending audio chunks")

    except Exception as e:
        logger.error(f"Error sending audio chunks: {e}")
        raise


def create_microphone_stats_tracker(verbose: bool = True):
    """
    Create a statistics tracker for microphone streaming sessions.

    Args:
        verbose: Whether to log statistics updates

    Returns:
        Dictionary with stats and update functions
    """
    stats = {
        "connection_state": "disconnected",
        "transcriptions": 0,
        "responses": 0,
        "tts_segments_received": 0,
        "interruptions": 0,
        "errors": 0,
        "sdk_errors": 0,
        "recording_time": 0.0,
        "playback_time": 0.0,
    }

    def update_stat(key: str, value=None):
        """Update a statistic"""
        if value is not None:
            stats[key] = value
        else:
            stats[key] += 1

        if verbose:
            logger.debug(f"Stats updated: {key} = {stats[key]}")

    def print_stats():
        """Print current statistics"""
        logger.info("📊 Session Statistics:")
        logger.info(f"   Connection: {stats['connection_state']}")
        logger.info(f"   Transcriptions: {stats['transcriptions']}")
        logger.info(f"   Responses: {stats['responses']}")
        logger.info(f"   TTS Segments: {stats['tts_segments_received']}")
        logger.info(f"   Interruptions: {stats['interruptions']}")
        logger.info(f"   Errors: {stats['errors']}")
        logger.info(f"   SDK Errors: {stats['sdk_errors']}")
        logger.info(f"   Recording time: {stats['recording_time']:.1f}s")
        logger.info(f"   Playback time: {stats['playback_time']:.1f}s")

    return {
        "stats": stats,
        "update": update_stat,
        "print": print_stats,
    }


def create_microphone_message_handler(
    stats_tracker=None,
    verbose: bool = True,
    conversation_tracker=None,
    show_text: bool = True,
    show_streaming: bool = True,
    show_detection: bool = False,
    audio_processor=None,
):
    """
    Create a message handler optimized for microphone streaming with support for all message types.

    Args:
        stats_tracker: Optional stats tracker from create_microphone_stats_tracker
        verbose: Whether to log detailed message information
        conversation_tracker: Optional conversation tracker for dialogue history
        show_text: Whether to display transcription and response text prominently
        show_streaming: Whether to show streaming LLM responses in real-time
        show_detection: Whether to show real-time detection/interim results

    Returns:
        Message handler function
    """
    # Use the enhanced message handler as a base
    enhanced_handler = create_enhanced_message_handler(
        verbose=verbose,
        show_transcription=show_text,
        show_responses=show_text,
        show_streaming=show_streaming,
        show_detection=show_detection,
    )

    def handle_message(message) -> None:
        """Handle incoming WebSocket messages for microphone streaming with stats and conversation tracking"""
        try:
            # First, let the enhanced handler process the message for display
            enhanced_handler(message)

            # Then handle stats and conversation tracking
            if message.type == "transcription" and message.data:
                text = message.data.get("text", "")
                is_partial = message.data.get("is_partial", False)
                segment_id = message.data.get("segment_id", "unknown")

                if stats_tracker:
                    stats_tracker["update"]("transcriptions")

                if conversation_tracker and text:
                    conversation_tracker["add_transcription"](
                        text, is_partial, segment_id
                    )

            elif message.type == "llm_response_streaming" and message.data:
                token = message.data.get("token", "")
                accumulated = message.data.get("accumulated_response", "")
                is_complete = message.data.get("is_complete", False)
                segment_id = message.data.get("segment_id", "unknown")

                if stats_tracker:
                    stats_tracker["update"]("responses")

                if conversation_tracker:
                    text = accumulated or token
                    conversation_tracker["add_response"](
                        text,
                        is_streaming=True,
                        is_complete=is_complete,
                        segment_id=segment_id,
                    )

            elif message.type == "llm_response" and message.data:
                response_text = message.data.get("response", "")
                segment_id = message.data.get("segment_id", "unknown")

                if stats_tracker:
                    stats_tracker["update"]("responses")

                if conversation_tracker and response_text:
                    conversation_tracker["add_response"](
                        response_text, segment_id=segment_id
                    )

            elif message.type == "tts_audio" and message.data:
                segment_id = message.data.get("segment_id", "unknown")
                text = message.data.get("text", "")

                if stats_tracker:
                    stats_tracker["update"]("tts_segments_received")

                if conversation_tracker and text:
                    conversation_tracker["add_tts_segment"](text, segment_id)

                # Handle TTS audio playback during microphone streaming
                if audio_processor:
                    from .types import TTSAudioSegment
                    import asyncio

                    # Convert to TTSAudioSegment
                    segment = TTSAudioSegment(
                        text=text,
                        audio_data=message.data.get("audio_data", ""),
                        sample_rate=message.data.get("sample_rate", 24000),
                        segment_id=segment_id,
                        sentence_number=message.data.get("sentence_number", 0),
                        generation_time_ms=message.data.get("generation_time_ms", 0),
                        format=message.data.get("format", "wav"),
                        duration_seconds=message.data.get("duration_seconds", 0.0),
                    )

                    # Add to audio queue
                    audio_processor["add_to_queue"](segment)

                    # Auto-start playback if not already playing
                    if not audio_processor["get_is_playing"]():
                        try:
                            # Create a task for playback
                            loop = asyncio.get_running_loop()
                            loop.create_task(audio_processor["play_audio"]())
                        except RuntimeError:
                            # No event loop running
                            pass

            elif message.type == "detection":
                detection_text = getattr(message, "text", "")
                confidence = getattr(message, "confidence", 0)

                if conversation_tracker and detection_text:
                    conversation_tracker["add_detection"](detection_text, confidence)

            elif message.type == "transcription_status" and message.data:
                if conversation_tracker:
                    conversation_tracker["add_status_update"](
                        str(message.data), "transcription_status"
                    )

            elif message.type == "audio_saved" and hasattr(message, "filename"):
                if conversation_tracker:
                    conversation_tracker["add_status_update"](
                        f"Audio saved: {message.filename}", "audio_saved"
                    )

            elif message.type == "speech_interruption":
                if stats_tracker:
                    stats_tracker["update"]("interruptions")

            elif message.event == "transcription":
                # Legacy transcription format
                if message.data:
                    transcription_text = str(message.data)

                    if stats_tracker:
                        stats_tracker["update"]("transcriptions")

                    if conversation_tracker:
                        conversation_tracker["add_transcription"](transcription_text)

            elif message.event == "response":
                # Legacy response format
                if message.data:
                    response_text = str(message.data)

                    if stats_tracker:
                        stats_tracker["update"]("responses")

                    if conversation_tracker:
                        conversation_tracker["add_response"](response_text)

            elif message.event == "error":
                if stats_tracker:
                    stats_tracker["update"]("errors")

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    return handle_message


def create_microphone_connection_handler(stats_tracker=None, verbose: bool = True):
    """
    Create a connection handler optimized for microphone streaming.

    Args:
        stats_tracker: Optional stats tracker from create_microphone_stats_tracker
        verbose: Whether to log connection state changes

    Returns:
        Connection handler function
    """

    def handle_connection(state) -> None:
        """Handle connection state changes for microphone streaming"""
        if verbose:
            logger.info(f"🔌 Connection: {state}")

        if stats_tracker:
            stats_tracker["update"]("connection_state", str(state))

        if verbose:
            if state.name == "CONNECTED":
                logger.info("✅ Connected to Vocals WebSocket")
            elif state.name == "DISCONNECTED":
                logger.info("❌ Disconnected from Vocals WebSocket")
            elif state.name == "RECONNECTING":
                logger.info("🔄 Reconnecting to Vocals WebSocket...")
            elif state.name == "ERROR":
                logger.error("⚠️ Connection error occurred")

    return handle_connection


def create_microphone_audio_data_handler(
    amplitude_threshold: float = 0.01, verbose: bool = True
):
    """
    Create an audio data handler optimized for microphone streaming.

    Args:
        amplitude_threshold: Minimum amplitude to consider as speech
        verbose: Whether to log audio data information

    Returns:
        Audio data handler function
    """

    def handle_audio_data(audio_data: List[float]) -> None:
        """Handle audio data from microphone with voice activity detection"""
        try:
            # Calculate amplitude for voice activity detection
            amplitude = sum(abs(sample) for sample in audio_data) / len(audio_data)

            # Only log if above threshold to avoid spam
            if amplitude > amplitude_threshold and verbose:
                logger.debug(f"🎤 Audio amplitude: {amplitude:.4f}")

        except Exception as e:
            logger.error(f"Error processing audio data: {e}")

    return handle_audio_data


def create_performance_monitor(verbose: bool = True):
    """
    Create a performance monitor for tracking SDK metrics.

    Args:
        verbose: Whether to log periodic performance updates

    Returns:
        Dictionary with performance monitoring functions
    """
    import time

    try:
        import psutil

        process = psutil.Process()
        psutil_available = True
    except ImportError:
        psutil_available = False
        logger.warning("psutil not available, performance monitoring limited")

    stats = {
        "start_time": time.time(),
        "messages_received": 0,
        "audio_chunks_processed": 0,
        "transcriptions_received": 0,
        "responses_received": 0,
        "tts_segments_received": 0,
        "errors": 0,
        "memory_usage": [],
        "cpu_usage": [],
        "network_bytes_sent": 0,
        "network_bytes_received": 0,
        "connection_events": 0,
        "reconnections": 0,
        "last_report_time": time.time(),
    }

    def update_stats(metric: str, value: int = 1):
        """Update a performance metric"""
        stats[metric] += value

        # Collect system metrics if available
        if psutil_available:
            try:
                stats["memory_usage"].append(
                    process.memory_info().rss / 1024 / 1024
                )  # MB
                stats["cpu_usage"].append(process.cpu_percent())

                # Keep only last 1000 samples to avoid memory growth
                if len(stats["memory_usage"]) > 1000:
                    stats["memory_usage"] = stats["memory_usage"][-1000:]
                    stats["cpu_usage"] = stats["cpu_usage"][-1000:]

            except Exception as e:
                logger.debug(f"Error collecting system metrics: {e}")

        # Log periodic updates
        current_time = time.time()
        if (
            verbose and current_time - stats["last_report_time"] > 30
        ):  # Every 30 seconds
            print_performance_stats()
            stats["last_report_time"] = current_time

    def print_performance_stats():
        """Print current performance statistics"""
        current_time = time.time()
        duration = current_time - stats["start_time"]

        print(f"\n📊 Performance Stats (Running for {duration:.1f}s):")
        print(f"   Messages: {stats['messages_received']}")
        print(f"   Audio chunks: {stats['audio_chunks_processed']}")
        print(f"   Transcriptions: {stats['transcriptions_received']}")
        print(f"   Responses: {stats['responses_received']}")
        print(f"   TTS segments: {stats['tts_segments_received']}")
        print(f"   Errors: {stats['errors']}")
        print(f"   Reconnections: {stats['reconnections']}")

        if psutil_available and stats["memory_usage"]:
            avg_memory = sum(stats["memory_usage"]) / len(stats["memory_usage"])
            max_memory = max(stats["memory_usage"])

            if stats["cpu_usage"]:
                avg_cpu = sum(stats["cpu_usage"]) / len(stats["cpu_usage"])
                max_cpu = max(stats["cpu_usage"])
                print(f"   Memory: {avg_memory:.1f}MB avg, {max_memory:.1f}MB max")
                print(f"   CPU: {avg_cpu:.1f}% avg, {max_cpu:.1f}% max")

    def create_message_handler():
        """Create a message handler that tracks performance"""

        def handle_message(message):
            update_stats("messages_received")

            if message.type == "transcription":
                update_stats("transcriptions_received")
            elif message.type == "llm_response":
                update_stats("responses_received")
            elif message.type == "tts_audio":
                update_stats("tts_segments_received")

        return handle_message

    def create_audio_handler():
        """Create an audio handler that tracks performance"""

        def handle_audio(audio_data):
            update_stats("audio_chunks_processed")

        return handle_audio

    def create_connection_handler():
        """Create a connection handler that tracks performance"""

        def handle_connection(state):
            update_stats("connection_events")

            if state == "RECONNECTING":
                update_stats("reconnections")

        return handle_connection

    def create_error_handler():
        """Create an error handler that tracks performance"""

        def handle_error(error):
            update_stats("errors")
            if verbose:
                logger.warning(f"Error tracked: {error}")

        return handle_error

    def get_stats():
        """Get current performance statistics"""
        current_time = time.time()
        duration = current_time - stats["start_time"]

        result = dict(stats)
        result["duration"] = duration
        result["messages_per_second"] = (
            stats["messages_received"] / duration if duration > 0 else 0
        )
        result["audio_chunks_per_second"] = (
            stats["audio_chunks_processed"] / duration if duration > 0 else 0
        )

        if psutil_available and stats["memory_usage"]:
            result["avg_memory_mb"] = sum(stats["memory_usage"]) / len(
                stats["memory_usage"]
            )
            result["max_memory_mb"] = max(stats["memory_usage"])

            if stats["cpu_usage"]:
                result["avg_cpu_percent"] = sum(stats["cpu_usage"]) / len(
                    stats["cpu_usage"]
                )
                result["max_cpu_percent"] = max(stats["cpu_usage"])

        return result

    return {
        "update": update_stats,
        "print_stats": print_performance_stats,
        "create_message_handler": create_message_handler,
        "create_audio_handler": create_audio_handler,
        "create_connection_handler": create_connection_handler,
        "create_error_handler": create_error_handler,
        "get_stats": get_stats,
    }


def create_realtime_visualizer(enable_plot: bool = True):
    """
    Create a real-time audio visualizer.

    Args:
        enable_plot: Whether to enable matplotlib plotting

    Returns:
        Audio handler function for visualization
    """
    from collections import deque

    # Audio buffer for visualization
    audio_buffer = deque(maxlen=1000)
    amplitude_buffer = deque(maxlen=100)

    if enable_plot:
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            plt.ion()  # Turn on interactive mode
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

            # Initialize plots
            ax1.set_title("Real-time Audio Waveform")
            ax1.set_ylabel("Amplitude")
            ax1.set_ylim(-1, 1)

            ax2.set_title("Volume Level")
            ax2.set_ylabel("Volume")
            ax2.set_ylim(0, 1)

            (line1,) = ax1.plot([], [])
            (line2,) = ax2.plot([], [])

            matplotlib_available = True
        except ImportError:
            matplotlib_available = False
            logger.warning("matplotlib not available, visualization disabled")
    else:
        matplotlib_available = False

    def audio_handler(audio_data: List[float]):
        """Handle audio data for visualization"""
        if not audio_data:
            return

        # Add to buffer
        audio_buffer.extend(audio_data)

        # Calculate amplitude
        amplitude = sum(abs(sample) for sample in audio_data) / len(audio_data)
        amplitude_buffer.append(amplitude)

        # Update plot if available
        if matplotlib_available:
            try:
                # Update waveform
                if len(audio_buffer) > 0:
                    line1.set_data(range(len(audio_buffer)), list(audio_buffer))
                    ax1.set_xlim(0, len(audio_buffer))

                # Update volume
                if len(amplitude_buffer) > 0:
                    line2.set_data(range(len(amplitude_buffer)), list(amplitude_buffer))
                    ax2.set_xlim(0, len(amplitude_buffer))

                # Redraw
                fig.canvas.draw()
                fig.canvas.flush_events()

            except Exception as e:
                logger.debug(f"Visualization error: {e}")

        # Simple text-based visualization
        if not matplotlib_available:
            bar_length = int(amplitude * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"\rVolume: [{bar}] {amplitude:.3f}", end="", flush=True)

    return audio_handler
