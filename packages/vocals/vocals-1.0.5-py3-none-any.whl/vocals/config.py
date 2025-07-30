"""
Configuration management for the Vocals SDK, mirroring the NextJS implementation.
"""

import os
import logging
from dataclasses import dataclass
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VocalsConfig:
    """Configuration options for the Vocals SDK"""

    # Custom endpoint for token fetching (defaults to /api/wstoken)
    token_endpoint: Optional[str] = None

    # Custom headers for token requests
    headers: Optional[Dict[str, str]] = None

    # Auto-connect on initialization (defaults to True)
    auto_connect: bool = True

    # Reconnection attempts (defaults to 3)
    max_reconnect_attempts: int = 3

    # Reconnection delay in seconds (defaults to 1.0)
    reconnect_delay: float = 1.0

    # Token refresh buffer in seconds - refresh token this many seconds before expiry (defaults to 60)
    token_refresh_buffer: float = 60.0

    # WebSocket endpoint URL (if not provided, will try to get from token or use default)
    ws_endpoint: Optional[str] = None

    # Whether to use token authentication (defaults to True)
    use_token_auth: bool = True

    # Debug configuration
    debug_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    debug_websocket: bool = False
    debug_audio: bool = False

    # Audio device configuration
    audio_device_id: Optional[int] = None

    def __post_init__(self):
        """Initialize default values based on environment variables"""
        if self.token_endpoint is None:
            self.token_endpoint = "/api/wstoken"

        if self.headers is None:
            self.headers = {}

        if self.ws_endpoint is None:
            self.ws_endpoint = (
                os.environ.get("VOCALS_WS_ENDPOINT")
                or "ws://192.168.1.46:8000/v1/stream/conversation"
            )

        # Set debug settings from environment
        self.debug_level = os.environ.get("VOCALS_DEBUG_LEVEL", "INFO").upper()
        self.debug_websocket = (
            os.environ.get("VOCALS_DEBUG_WEBSOCKET", "false").lower() == "true"
        )
        self.debug_audio = (
            os.environ.get("VOCALS_DEBUG_AUDIO", "false").lower() == "true"
        )

        # Set audio device from environment
        device_id = os.environ.get("VOCALS_AUDIO_DEVICE_ID")
        if device_id and device_id.isdigit():
            self.audio_device_id = int(device_id)

    def setup_logging(self):
        """Setup logging based on debug configuration"""
        level = getattr(logging, self.debug_level.upper(), logging.INFO)
        logging.basicConfig(
            level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        if self.debug_websocket:
            logging.getLogger("websockets").setLevel(logging.DEBUG)
        else:
            logging.getLogger("websockets").setLevel(logging.WARNING)

        if self.debug_audio:
            logging.getLogger("sounddevice").setLevel(logging.DEBUG)
        else:
            logging.getLogger("sounddevice").setLevel(logging.WARNING)

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        # Check API key
        api_key = os.environ.get("VOCALS_DEV_API_KEY")
        if not api_key:
            issues.append("VOCALS_DEV_API_KEY environment variable not set")
        elif not api_key.startswith("vdev_"):
            issues.append("Invalid API key format (should start with 'vdev_')")

        # Check WebSocket endpoint
        if self.ws_endpoint and not self.ws_endpoint.startswith("ws"):
            issues.append(
                "Invalid WebSocket endpoint format (should start with 'ws' or 'wss')"
            )

        # Check debug level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.debug_level not in valid_levels:
            issues.append(
                f"Invalid debug level: {self.debug_level}. Must be one of {valid_levels}"
            )

        # Check audio device
        if self.audio_device_id is not None:
            try:
                import sounddevice as sd

                devices = sd.query_devices()
                if self.audio_device_id >= len(devices):
                    issues.append(f"Invalid audio device ID: {self.audio_device_id}")
            except ImportError:
                issues.append("sounddevice not installed, cannot validate audio device")
            except Exception as e:
                issues.append(f"Error checking audio device: {e}")

        return issues

    def print_config(self):
        """Print current configuration"""
        print("🎤 Vocals SDK Configuration")
        print("=" * 50)

        # Safe API key display
        api_key = os.environ.get("VOCALS_DEV_API_KEY")
        if api_key:
            print(f"API Key: {api_key[:10]}...")
        else:
            print("API Key: NOT SET")

        print(f"WebSocket Endpoint: {self.ws_endpoint}")
        print(f"Auto Connect: {self.auto_connect}")
        print(f"Max Reconnect Attempts: {self.max_reconnect_attempts}")
        print(f"Reconnect Delay: {self.reconnect_delay}s")
        print(f"Token Refresh Buffer: {self.token_refresh_buffer}s")
        print(f"Use Token Auth: {self.use_token_auth}")
        print(f"Debug Level: {self.debug_level}")
        print(f"Debug WebSocket: {self.debug_websocket}")
        print(f"Debug Audio: {self.debug_audio}")

        if self.audio_device_id is not None:
            print(f"Audio Device ID: {self.audio_device_id}")
        else:
            print("Audio Device: Default")


# Default configuration instance
DEFAULT_CONFIG = VocalsConfig()


def get_default_config() -> VocalsConfig:
    """Get the default configuration with environment variable overrides"""
    return VocalsConfig(
        token_endpoint=os.environ.get("VOCALS_TOKEN_ENDPOINT", "/api/wstoken"),
        ws_endpoint=os.environ.get(
            "VOCALS_WS_ENDPOINT", "ws://192.168.1.46:8000/v1/stream/conversation"
        ),
        auto_connect=os.environ.get("VOCALS_AUTO_CONNECT", "true").lower() == "true",
        max_reconnect_attempts=int(
            os.environ.get("VOCALS_MAX_RECONNECT_ATTEMPTS", "3")
        ),
        reconnect_delay=float(os.environ.get("VOCALS_RECONNECT_DELAY", "1.0")),
        token_refresh_buffer=float(
            os.environ.get("VOCALS_TOKEN_REFRESH_BUFFER", "60.0")
        ),
        use_token_auth=os.environ.get("VOCALS_USE_TOKEN_AUTH", "true").lower()
        == "true",
    )


def validate_environment() -> List[str]:
    """Validate environment variables and return list of issues"""
    issues = []

    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            issues.append("python-dotenv not installed but .env file exists")

    # Check API key
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if not api_key:
        issues.append("VOCALS_DEV_API_KEY environment variable not set")
    elif not api_key.startswith("vdev_"):
        issues.append("Invalid API key format (should start with 'vdev_')")

    # Check WebSocket endpoint
    endpoint = os.environ.get("VOCALS_WS_ENDPOINT")
    if endpoint and not endpoint.startswith("ws"):
        issues.append(
            "Invalid WebSocket endpoint format (should start with 'ws' or 'wss')"
        )

    # Check audio system
    try:
        import sounddevice as sd

        sd.query_devices()
    except ImportError:
        issues.append("sounddevice not installed")
    except Exception as e:
        issues.append(f"Audio system error: {e}")

    return issues


def create_config_wizard():
    """Interactive configuration wizard"""
    print("🎤 Vocals SDK Configuration Wizard")
    print("=" * 50)

    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists.")
        overwrite = input("Overwrite existing configuration? (y/n): ").lower().strip()
        if overwrite != "y":
            print("Configuration wizard cancelled.")
            return

    # API Key setup
    print("\n1. API Key Configuration")
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if api_key:
        print(f"Current API key: {api_key[:10]}...")
        keep = input("Keep current API key? (y/n): ").lower().strip()
        if keep == "y":
            pass  # Keep current
        else:
            api_key = input("Enter your Vocals API key: ").strip()
    else:
        api_key = input("Enter your Vocals API key: ").strip()

    if not api_key.startswith("vdev_"):
        print("⚠️  Warning: API key should start with 'vdev_'")

    # WebSocket endpoint
    print("\n2. WebSocket Configuration")
    current_endpoint = os.environ.get(
        "VOCALS_WS_ENDPOINT", "ws://192.168.1.46:8000/v1/stream/conversation"
    )
    print(f"Current endpoint: {current_endpoint}")

    custom = input("Use custom WebSocket endpoint? (y/n): ").lower().strip()
    if custom == "y":
        endpoint = input(f"WebSocket endpoint [{current_endpoint}]: ").strip()
        if not endpoint:
            endpoint = current_endpoint
    else:
        endpoint = current_endpoint

    # Audio device selection
    print("\n3. Audio Device Selection")
    try:
        from .cli import list_audio_devices

        devices = list_audio_devices()

        if devices:
            print("Available audio devices:")
            for device in devices:
                print(
                    f"  {device['id']}: {device['name']} ({device['channels']} channels)"
                )

            device_input = input(
                "Select device ID (or press Enter for default): "
            ).strip()
            if device_input and device_input.isdigit():
                device_id = int(device_input)
            else:
                device_id = None
        else:
            print("No audio input devices found")
            device_id = None
    except Exception as e:
        print(f"⚠️  Could not list audio devices: {e}")
        device_id = None

    # Debug configuration
    print("\n4. Debug Configuration")
    debug_level = input("Debug level [INFO/DEBUG/WARNING/ERROR]: ").upper().strip()
    if debug_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        debug_level = "INFO"

    debug_websocket = (
        input("Enable WebSocket debugging? (y/n): ").lower().strip() == "y"
    )
    debug_audio = input("Enable audio debugging? (y/n): ").lower().strip() == "y"

    # Write configuration
    env_content = f"""# Vocals SDK Configuration
# Generated by configuration wizard

# API Configuration
VOCALS_DEV_API_KEY={api_key}
VOCALS_WS_ENDPOINT={endpoint}

# Connection Configuration
VOCALS_AUTO_CONNECT=true
VOCALS_MAX_RECONNECT_ATTEMPTS=3
VOCALS_RECONNECT_DELAY=1.0
VOCALS_TOKEN_REFRESH_BUFFER=60.0

# Debug Configuration
VOCALS_DEBUG_LEVEL={debug_level}
VOCALS_DEBUG_WEBSOCKET={'true' if debug_websocket else 'false'}
VOCALS_DEBUG_AUDIO={'true' if debug_audio else 'false'}
"""

    if device_id is not None:
        env_content += f"VOCALS_AUDIO_DEVICE_ID={device_id}\n"

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n✅ Configuration saved to .env")
    print("You can now use the Vocals SDK!")

    # Validate configuration
    issues = validate_environment()
    if issues:
        print("\n⚠️  Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Configuration validated successfully!")


if __name__ == "__main__":
    create_config_wizard()
