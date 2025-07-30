"""
Vocals SDK for Python

A Python SDK for voice processing and real-time audio communication,
following functional composition patterns while maintaining backward compatibility.
"""

__version__ = "1.0.6"

# Primary functional interfaces
from .client import create_vocals
from .websocket_client import create_websocket_client
from .audio_processor import create_audio_processor
from .token_manager import create_token_manager

# Utility functions
from .utils import (
    load_audio_file,
    create_default_message_handler,
    create_enhanced_message_handler,
    create_conversation_tracker,
    create_default_connection_handler,
    create_default_error_handler,
    send_audio_in_chunks,
    # Microphone streaming utilities
    create_microphone_stats_tracker,
    create_microphone_message_handler,
    create_microphone_connection_handler,
    create_microphone_audio_data_handler,
    # Performance monitoring
    create_performance_monitor,
    create_realtime_visualizer,
)

# Audio device management
from .audio_processor import (
    list_audio_devices,
    get_default_audio_device,
    test_audio_device,
    validate_audio_device,
    get_audio_device_info,
    print_audio_devices,
    create_audio_device_selector,
)

# Testing framework
from .testing import (
    VocalsSDKTester,
    create_test_suite,
    run_quick_test,
    run_full_test_suite,
    benchmark_performance,
    generate_test_audio_data,
)

# WSToken functionality
from .wstoken import (
    generate_ws_token,
    generate_ws_token_with_user_id,
    generate_ws_token_from_api_key,
    validate_api_key_format,
    is_token_expired,
    get_token_ttl,
    decode_ws_token,
    get_ws_endpoint,
    get_token_expiry_ms,
)

# Configuration and types
from .config import (
    VocalsConfig,
    get_default_config,
    validate_environment,
    create_config_wizard,
)
from .types import (
    VocalsError,
    VocalsSDKException,
    ConnectionState,
    RecordingState,
    PlaybackState,
    TTSAudioSegment,
    WebSocketMessage,
    WebSocketResponse,
    SpeechInterruptionData,
    WSToken,
    ValidatedApiKey,
    Result,
    Ok,
    Err,
)
from .audio_processor import AudioConfig

__all__ = [
    # Primary functional interfaces
    "create_vocals",
    "create_websocket_client",
    "create_audio_processor",
    "create_token_manager",
    # Utility functions
    "load_audio_file",
    "create_default_message_handler",
    "create_enhanced_message_handler",
    "create_conversation_tracker",
    "create_default_connection_handler",
    "create_default_error_handler",
    "send_audio_in_chunks",
    # Microphone streaming utilities
    "create_microphone_stats_tracker",
    "create_microphone_message_handler",
    "create_microphone_connection_handler",
    "create_microphone_audio_data_handler",
    # Performance monitoring
    "create_performance_monitor",
    "create_realtime_visualizer",
    # Audio device management
    "list_audio_devices",
    "get_default_audio_device",
    "test_audio_device",
    "validate_audio_device",
    "get_audio_device_info",
    "print_audio_devices",
    "create_audio_device_selector",
    # Testing framework
    "VocalsSDKTester",
    "create_test_suite",
    "run_quick_test",
    "run_full_test_suite",
    "benchmark_performance",
    "generate_test_audio_data",
    # WSToken functionality
    "generate_ws_token",
    "generate_ws_token_with_user_id",
    "generate_ws_token_from_api_key",
    "validate_api_key_format",
    "is_token_expired",
    "get_token_ttl",
    "decode_ws_token",
    "get_ws_endpoint",
    "get_token_expiry_ms",
    # Legacy class interfaces
    # Configuration and types
    "VocalsConfig",
    "get_default_config",
    "validate_environment",
    "create_config_wizard",
    "AudioConfig",
    "VocalsError",
    "VocalsSDKException",
    "ConnectionState",
    "RecordingState",
    "PlaybackState",
    "TTSAudioSegment",
    "WebSocketMessage",
    "WebSocketResponse",
    "SpeechInterruptionData",
    "WSToken",
    "ValidatedApiKey",
    "Result",
    "Ok",
    "Err",
]
