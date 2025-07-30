"""
Type definitions for the Vocals SDK, mirroring the NextJS implementation.
"""

from typing import Dict, List, Optional, Any, Callable, Union, Literal, Generic, TypeVar
from dataclasses import dataclass
from enum import Enum
import time

# Result type pattern for error handling
T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Ok(Generic[T]):
    """Success result wrapper"""

    data: T
    success: bool = True


@dataclass
class Err(Generic[E]):
    """Error result wrapper"""

    error: E
    success: bool = False


# Result type union
Result = Union[Ok[T], Err[E]]

# Type aliases for API key validation
ValidatedApiKey = str


@dataclass
class WSToken:
    """WebSocket token with expiration information"""

    token: str
    expires_at: int  # Unix timestamp in milliseconds


# Connection states
class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


# Recording states
class RecordingState(str, Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


# Playback states
class PlaybackState(str, Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class VocalsError:
    """Error class for Vocals SDK exceptions"""

    message: str
    code: str = "VOCALS_ERROR"
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time() * 1000  # milliseconds


class VocalsSDKException(Exception):
    """Exception class for Vocals SDK errors"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        self.timestamp = time.time() * 1000  # milliseconds
        super().__init__(f"[{code}] {message}")


@dataclass
class TTSAudioSegment:
    """TTS Audio segment interface"""

    text: str
    audio_data: str  # Base64 encoded WAV
    sample_rate: int
    segment_id: str
    sentence_number: int
    generation_time_ms: int
    format: str
    duration_seconds: float


@dataclass
class SpeechInterruptionData:
    """Speech interruption data interface"""

    segment_id: str
    start_time: float
    reason: str  # "new_speech_segment", "speech_segment_merged", etc.
    connection_id: Optional[int] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time() * 1000  # milliseconds


@dataclass
class WebSocketMessage:
    """WebSocket message format"""

    event: str
    data: Optional[Any] = None
    format: Optional[str] = None
    sample_rate: Optional[int] = None


@dataclass
class WebSocketResponse:
    """WebSocket response format"""

    event: str
    data: Optional[Any] = None
    type: Optional[str] = None


@dataclass
class AudioProcessorMessage:
    """Audio processor message format"""

    data: List[float]
    format: str
    sample_rate: int


@dataclass
class TTSAudioMessage:
    """TTS Audio message interface"""

    type: Literal["tts_audio"]
    data: TTSAudioSegment


@dataclass
class SpeechInterruptionMessage:
    """Speech interruption message interface"""

    type: Literal["speech_interruption"]
    data: SpeechInterruptionData


# Event handler types
MessageHandler = Callable[[WebSocketResponse], None]
ConnectionHandler = Callable[[ConnectionState], None]
ErrorHandler = Callable[[VocalsError], None]
AudioDataHandler = Callable[[List[float]], None]
