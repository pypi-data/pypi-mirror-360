"""
Audio processing for the Vocals SDK, mirroring the NextJS implementation.
"""

import asyncio
import base64
import logging
import threading
import time
from typing import Optional, List, Callable, Any
from collections import deque
from dataclasses import dataclass

try:
    import sounddevice as sd
    import numpy as np
    import wave
    import io
except ImportError:
    # Will be handled in requirements.txt
    pass

from .types import (
    TTSAudioSegment,
    RecordingState,
    PlaybackState,
    VocalsError,
)

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio configuration settings"""

    sample_rate: int = 24000
    channels: int = 1
    format: str = "pcm_f32le"
    buffer_size: int = 1024


def create_audio_processor(config: Optional[AudioConfig] = None):
    """Create an audio processor with closures for state management

    Args:
        config: Audio configuration settings

    Returns:
        Dictionary with audio processing functions
    """
    # Initialize configuration
    config = config or AudioConfig()

    # State held in closures
    state = {
        "recording_state": RecordingState.IDLE,
        "playback_state": PlaybackState.IDLE,
        "recording_stream": None,
        "is_recording": False,
        "current_amplitude": 0.0,
        "playback_stream": None,
        "is_playing": False,
        "audio_queue": deque(),
        "current_segment": None,
        "playback_thread": None,
        "stop_playback_event": threading.Event(),
        "audio_data_handlers": [],
        "error_handlers": [],
    }

    def _create_error(message: str, code: str = "AUDIO_ERROR") -> VocalsError:
        """Create an error object"""
        return VocalsError(message=message, code=code)

    def _handle_error(error: VocalsError) -> None:
        """Handle error and notify handlers"""
        logger.error(f"Audio error: {error.message} ({error.code})")

        # Notify handlers
        for handler in state["error_handlers"]:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")

    def _audio_callback(
        indata: np.ndarray, frames: int, time_info: Any, status: Any
    ) -> None:
        """Callback for audio input stream"""
        if status:
            logger.warning(f"Audio input status: {status}")

        if not state["is_recording"]:
            return

        # Convert to float32 and flatten
        audio_data = indata.flatten().astype(np.float32)

        # Calculate amplitude for visualization
        state["current_amplitude"] = float(np.mean(np.abs(audio_data)))

        # Convert to list and notify handlers
        audio_list = audio_data.tolist()

        for handler in state["audio_data_handlers"]:
            try:
                handler(audio_list)
            except Exception as e:
                logger.error(f"Error in audio data handler: {e}")

    async def start_recording() -> None:
        """Start audio recording"""
        try:
            if state["recording_state"] == RecordingState.RECORDING:
                return

            state["recording_state"] = RecordingState.RECORDING
            state["is_recording"] = True

            # Create input stream
            state["recording_stream"] = sd.InputStream(
                samplerate=config.sample_rate,
                channels=config.channels,
                dtype=np.float32,
                callback=_audio_callback,
                blocksize=config.buffer_size,
            )

            # Start the stream
            state["recording_stream"].start()

            logger.info("Audio recording started")

        except Exception as e:
            error = _create_error(
                f"Failed to start recording: {str(e)}", "RECORDING_FAILED"
            )
            _handle_error(error)
            state["recording_state"] = RecordingState.ERROR
            state["is_recording"] = False

    async def stop_recording() -> None:
        """Stop audio recording"""
        try:
            state["is_recording"] = False
            state["recording_state"] = RecordingState.IDLE

            if state["recording_stream"]:
                state["recording_stream"].stop()
                state["recording_stream"].close()
                state["recording_stream"] = None

            logger.info("Audio recording stopped")

        except Exception as e:
            error = _create_error(
                f"Failed to stop recording: {str(e)}", "RECORDING_STOP_FAILED"
            )
            _handle_error(error)
            state["recording_state"] = RecordingState.ERROR

    def add_to_queue(segment: TTSAudioSegment) -> None:
        """Add an audio segment to the playback queue"""
        # Check for duplicates
        for existing in state["audio_queue"]:
            if (
                existing.segment_id == segment.segment_id
                and existing.sentence_number == segment.sentence_number
            ):
                logger.warning(
                    f"Duplicate audio segment detected, skipping: {segment.segment_id}"
                )
                return

        state["audio_queue"].append(segment)
        logger.debug(f"Added audio segment to queue: {segment.segment_id}")

        # Auto-start playback if not already playing
        if not state["is_playing"]:
            _start_playback_thread()

    def clear_queue() -> None:
        """Clear the audio playback queue"""
        state["audio_queue"].clear()
        state["current_segment"] = None
        state["stop_playback_event"].set()

        if state["playback_stream"]:
            state["playback_stream"].stop()
            state["playback_stream"].close()
            state["playback_stream"] = None

        state["playback_state"] = PlaybackState.IDLE
        state["is_playing"] = False

        logger.info("Audio queue cleared")

    def _start_playback_thread() -> None:
        """Start the playback thread"""
        if state["playback_thread"] and state["playback_thread"].is_alive():
            return

        state["stop_playback_event"].clear()
        state["playback_thread"] = threading.Thread(target=_playback_worker)
        state["playback_thread"].daemon = True
        state["playback_thread"].start()

    def _playback_worker() -> None:
        """Worker thread for audio playback"""
        try:
            while not state["stop_playback_event"].is_set():
                if not state["audio_queue"]:
                    time.sleep(0.1)
                    continue

                # Get next segment
                segment = state["audio_queue"].popleft()
                state["current_segment"] = segment
                state["playback_state"] = PlaybackState.PLAYING
                state["is_playing"] = True

                # Decode and play audio
                _play_segment(segment)

                # Brief pause between segments
                time.sleep(0.05)

        except Exception as e:
            error = _create_error(
                f"Playback worker error: {str(e)}", "PLAYBACK_WORKER_ERROR"
            )
            _handle_error(error)
            state["playback_state"] = PlaybackState.ERROR

        finally:
            state["is_playing"] = False
            state["current_segment"] = None
            if not state["audio_queue"]:
                state["playback_state"] = PlaybackState.IDLE

    def _play_segment(segment: TTSAudioSegment) -> None:
        """Play a single audio segment"""
        try:
            # Decode base64 audio data
            audio_data = base64.b64decode(segment.audio_data)

            # Parse WAV data
            with io.BytesIO(audio_data) as wav_io:
                with wave.open(wav_io, "rb") as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())

                    # Convert to numpy array
                    if wav_file.getsampwidth() == 2:
                        audio_array = (
                            np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                            / 32768.0
                        )
                    else:
                        audio_array = np.frombuffer(frames, dtype=np.float32)

                    # Play using sounddevice
                    sd.play(audio_array, samplerate=segment.sample_rate)
                    sd.wait()  # Wait for playback to complete

            logger.debug(f"Played audio segment: {segment.segment_id}")

        except Exception as e:
            error = _create_error(
                f"Failed to play segment: {str(e)}", "SEGMENT_PLAYBACK_FAILED"
            )
            _handle_error(error)

    async def play_audio() -> None:
        """Start or resume audio playback"""
        if state["audio_queue"] and not state["is_playing"]:
            _start_playback_thread()

    async def pause_audio() -> None:
        """Pause audio playback"""
        state["stop_playback_event"].set()
        if state["playback_stream"]:
            state["playback_stream"].stop()
        state["playback_state"] = PlaybackState.PAUSED

    async def stop_audio() -> None:
        """Stop audio playback"""
        state["stop_playback_event"].set()
        if state["playback_stream"]:
            state["playback_stream"].stop()
            state["playback_stream"].close()
            state["playback_stream"] = None
        state["playback_state"] = PlaybackState.IDLE
        state["is_playing"] = False
        state["current_segment"] = None

    async def fade_out_audio(duration: float = 0.5) -> None:
        """Fade out current audio over specified duration"""
        # For simplicity, just stop the audio
        # In a more advanced implementation, we would gradually reduce volume
        await stop_audio()

        # Wait for fade duration
        await asyncio.sleep(duration)

    def add_audio_data_handler(
        handler: Callable[[List[float]], None]
    ) -> Callable[[], None]:
        """Add an audio data handler"""
        state["audio_data_handlers"].append(handler)
        return lambda: (
            state["audio_data_handlers"].remove(handler)
            if handler in state["audio_data_handlers"]
            else None
        )

    def add_error_handler(handler: Callable[[VocalsError], None]) -> Callable[[], None]:
        """Add an error handler"""
        state["error_handlers"].append(handler)
        return lambda: (
            state["error_handlers"].remove(handler)
            if handler in state["error_handlers"]
            else None
        )

    def cleanup() -> None:
        """Clean up audio resources"""
        state["is_recording"] = False
        state["is_playing"] = False
        state["stop_playback_event"].set()

        if state["recording_stream"]:
            state["recording_stream"].stop()
            state["recording_stream"].close()
            state["recording_stream"] = None

        if state["playback_stream"]:
            state["playback_stream"].stop()
            state["playback_stream"].close()
            state["playback_stream"] = None

        if state["playback_thread"] and state["playback_thread"].is_alive():
            state["playback_thread"].join(timeout=1.0)

        state["audio_queue"].clear()
        state["current_segment"] = None
        state["recording_state"] = RecordingState.IDLE
        state["playback_state"] = PlaybackState.IDLE

        logger.info("Audio processor cleanup completed")

    # Property getters
    def get_recording_state() -> RecordingState:
        return state["recording_state"]

    def get_is_recording() -> bool:
        return state["is_recording"]

    def get_playback_state() -> PlaybackState:
        return state["playback_state"]

    def get_is_playing() -> bool:
        return state["is_playing"]

    def get_audio_queue() -> List[TTSAudioSegment]:
        return list(state["audio_queue"])

    def get_current_segment() -> Optional[TTSAudioSegment]:
        return state["current_segment"]

    def get_current_amplitude() -> float:
        return state["current_amplitude"]

    # Return the audio processor interface
    return {
        "start_recording": start_recording,
        "stop_recording": stop_recording,
        "add_to_queue": add_to_queue,
        "clear_queue": clear_queue,
        "play_audio": play_audio,
        "pause_audio": pause_audio,
        "stop_audio": stop_audio,
        "fade_out_audio": fade_out_audio,
        "add_audio_data_handler": add_audio_data_handler,
        "add_error_handler": add_error_handler,
        "cleanup": cleanup,
        "get_recording_state": get_recording_state,
        "get_is_recording": get_is_recording,
        "get_playback_state": get_playback_state,
        "get_is_playing": get_is_playing,
        "get_audio_queue": get_audio_queue,
        "get_current_segment": get_current_segment,
        "get_current_amplitude": get_current_amplitude,
    }


# Audio device management functions
def _is_default_input_device(device_id: int, sd_module) -> bool:
    """Check if a device is the default input device"""
    try:
        default_device = sd_module.default.device
        if (
            default_device
            and isinstance(default_device, (list, tuple))
            and len(default_device) > 0
        ):
            return device_id == default_device[0]
        return False
    except Exception:
        return False


def _is_default_output_device(device_id: int, sd_module) -> bool:
    """Check if a device is the default output device"""
    try:
        default_device = sd_module.default.device
        if (
            default_device
            and isinstance(default_device, (list, tuple))
            and len(default_device) > 1
        ):
            return device_id == default_device[1]
        return False
    except Exception:
        return False


def list_audio_devices():
    """List available audio devices for user selection"""
    try:
        import sounddevice as sd

        devices = sd.query_devices()

        input_devices = []
        for i, device in enumerate(devices):
            # sounddevice returns a DeviceList of dictionaries
            if isinstance(device, dict):
                max_input_channels = device.get("max_input_channels", 0)
                device_name = device.get("name", "Unknown")
                sample_rate = device.get("default_samplerate", 44100)
                hostapi = device.get("hostapi", 0)
            else:
                # Fallback for unexpected types
                max_input_channels = 0
                device_name = str(device)
                sample_rate = 44100
                hostapi = 0

            if max_input_channels > 0:
                input_devices.append(
                    {
                        "id": i,
                        "name": device_name,
                        "channels": max_input_channels,
                        "sample_rate": sample_rate,
                        "hostapi": hostapi,
                        "is_default": _is_default_input_device(i, sd),
                    }
                )

        return input_devices
    except ImportError:
        logger.error("sounddevice not installed")
        return []
    except Exception as e:
        logger.error(f"Error listing audio devices: {e}")
        return []


def get_default_audio_device():
    """Get the default audio input device"""
    try:
        import sounddevice as sd

        default_device = sd.default.device
        if (
            default_device
            and isinstance(default_device, (list, tuple))
            and len(default_device) > 0
            and default_device[0] is not None
        ):
            return default_device[0]
        else:
            # Find first available input device
            devices = list_audio_devices()
            if devices:
                return devices[0]["id"]
            return None
    except Exception as e:
        logger.error(f"Error getting default audio device: {e}")
        return None


def test_audio_device(
    device_id: Optional[int] = None, duration: float = 5.0, verbose: bool = True
):
    """Test an audio device with visual feedback"""
    try:
        import sounddevice as sd
        import numpy as np
        import time

        if device_id is None:
            device_id = get_default_audio_device()

        if device_id is None:
            raise Exception("No audio device available")

        if verbose:
            print(f"Testing audio device {device_id} for {duration} seconds...")
            print("Speak into your microphone!")

        # Test variables
        max_volume = 0.0
        volume_readings = []

        def callback(indata, frames, time, status):
            nonlocal max_volume
            if status:
                if verbose:
                    print(f"Audio status: {status}")

            volume = np.sqrt(np.mean(indata**2))
            max_volume = max(max_volume, volume)
            volume_readings.append(volume)

            if verbose:
                # Visual volume meter
                bar_length = int(volume * 50)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"\rVolume: [{bar}] {volume:.3f}", end="", flush=True)

        # Start recording
        with sd.InputStream(
            callback=callback,
            device=device_id,
            channels=1,
            samplerate=44100,
            blocksize=1024,
        ):
            time.sleep(duration)

        if verbose:
            print(f"\n✅ Device test completed")
            print(f"Max volume: {max_volume:.3f}")
            print(f"Average volume: {np.mean(volume_readings):.3f}")

        return {
            "device_id": device_id,
            "max_volume": max_volume,
            "average_volume": np.mean(volume_readings) if volume_readings else 0.0,
            "readings_count": len(volume_readings),
            "success": True,
        }

    except Exception as e:
        error_msg = f"Error testing audio device {device_id}: {e}"
        if verbose:
            print(f"\n❌ {error_msg}")
        logger.error(error_msg)
        return {"device_id": device_id, "success": False, "error": str(e)}


def validate_audio_device(device_id: int):
    """Validate that an audio device exists and can be used"""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        if device_id >= len(devices):
            return False, f"Device ID {device_id} not found"

        device = devices[device_id]  # type: ignore

        # Handle device as dictionary
        if isinstance(device, dict):
            max_input_channels = device.get("max_input_channels", 0)
        else:
            max_input_channels = 0

        if max_input_channels == 0:
            return False, f"Device {device_id} has no input channels"

        return True, f"Device {device_id} is valid"

    except Exception as e:
        return False, f"Error validating device {device_id}: {e}"


def get_audio_device_info(device_id: int):
    """Get detailed information about an audio device"""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        if device_id >= len(devices):
            return None

        device = devices[device_id]  # type: ignore

        # Handle device as dictionary
        if isinstance(device, dict):
            device_name = device.get("name", "Unknown")
            hostapi = device.get("hostapi", 0)
            max_input_channels = device.get("max_input_channels", 0)
            max_output_channels = device.get("max_output_channels", 0)
            default_low_input_latency = device.get("default_low_input_latency", 0.0)
            default_low_output_latency = device.get("default_low_output_latency", 0.0)
            default_high_input_latency = device.get("default_high_input_latency", 0.0)
            default_high_output_latency = device.get("default_high_output_latency", 0.0)
            default_samplerate = device.get("default_samplerate", 44100)
        else:
            # Fallback for unexpected types
            device_name = str(device)
            hostapi = 0
            max_input_channels = 0
            max_output_channels = 0
            default_low_input_latency = 0.0
            default_low_output_latency = 0.0
            default_high_input_latency = 0.0
            default_high_output_latency = 0.0
            default_samplerate = 44100

        return {
            "id": device_id,
            "name": device_name,
            "hostapi": hostapi,
            "max_input_channels": max_input_channels,
            "max_output_channels": max_output_channels,
            "default_low_input_latency": default_low_input_latency,
            "default_low_output_latency": default_low_output_latency,
            "default_high_input_latency": default_high_input_latency,
            "default_high_output_latency": default_high_output_latency,
            "default_samplerate": default_samplerate,
            "is_default_input": _is_default_input_device(device_id, sd),
            "is_default_output": _is_default_output_device(device_id, sd),
        }

    except Exception as e:
        logger.error(f"Error getting device info for {device_id}: {e}")
        return None


def print_audio_devices():
    """Print a formatted list of available audio devices"""
    devices = list_audio_devices()

    if not devices:
        print("No audio input devices found")
        return

    print("🎧 Available Audio Input Devices:")
    print("=" * 60)

    for device in devices:
        status = "⭐ DEFAULT" if device["is_default"] else ""
        print(f"ID {device['id']}: {device['name']} {status}")
        print(f"  Channels: {device['channels']}")
        print(f"  Sample Rate: {device['sample_rate']} Hz")
        print(f"  Host API: {device['hostapi']}")
        print()


def create_audio_device_selector():
    """Interactive audio device selector"""
    devices = list_audio_devices()

    if not devices:
        print("❌ No audio input devices found")
        return None

    print("🎧 Audio Device Selection")
    print("=" * 40)

    # Show devices
    for device in devices:
        status = " (DEFAULT)" if device["is_default"] else ""
        print(f"{device['id']}: {device['name']}{status}")

    print()

    # Get user selection
    while True:
        try:
            selection = input("Select device ID (or press Enter for default): ").strip()

            if not selection:
                # Use default device
                default_device = get_default_audio_device()
                if default_device is not None:
                    return default_device
                else:
                    return devices[0]["id"]

            device_id = int(selection)

            # Validate selection
            if any(d["id"] == device_id for d in devices):
                return device_id
            else:
                print(f"❌ Invalid device ID: {device_id}")

        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Selection cancelled")
            return None
