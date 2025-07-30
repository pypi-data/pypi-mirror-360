"""
Vocals SDK Command Line Interface

Provides convenient command-line tools for setup, testing, and demos.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import List, Optional

try:
    import click
except ImportError:
    print("Click is required for CLI functionality. Install with: pip install click")
    sys.exit(1)

from .config import VocalsConfig, get_default_config
from .audio_processor import AudioConfig
from .client import create_vocals_sdk


@click.group()
def cli():
    """🎤 Vocals SDK Command Line Interface"""
    pass


@cli.command()
@click.option(
    "--duration", default=30, help="Recording duration in seconds (0 for infinite)"
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--stats", is_flag=True, default=True, help="Show session statistics")
@click.option("--device", type=int, help="Audio device ID to use")
def demo(duration, verbose, stats, device):
    """Run a microphone streaming demo"""

    async def run_demo():
        print("🎤 Vocals SDK Demo")
        print("=" * 50)

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.getLogger("vocals_sdk").setLevel(logging.WARNING)

        try:
            # Create configuration
            config = get_default_config()
            audio_config = AudioConfig(
                sample_rate=24000, channels=1, format="pcm_f32le"
            )

            # Override audio device if specified
            if device is not None:
                print(f"Using audio device ID: {device}")
                # This would need to be implemented in audio_processor

            # Create SDK
            sdk = create_vocals_sdk(config, audio_config)

            print(f"Starting microphone streaming for {duration}s...")
            print("Speak into your microphone!")
            print("Press Ctrl+C to stop early")

            # Stream microphone
            session_stats = await sdk["stream_microphone"](
                duration=duration,
                auto_connect=True,
                auto_playback=True,
                verbose=verbose,
                stats_tracking=stats,
            )

            # Show results
            if stats and session_stats:
                print("\n📊 Session Statistics:")
                print(f"   • Transcriptions: {session_stats.get('transcriptions', 0)}")
                print(f"   • AI Responses: {session_stats.get('responses', 0)}")
                print(
                    f"   • TTS Segments: {session_stats.get('tts_segments_received', 0)}"
                )

        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if "sdk" in locals():
                try:
                    await sdk["disconnect"]()
                    sdk["cleanup"]()
                except:
                    pass

    asyncio.run(run_demo())


@cli.command()
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
def setup(force):
    """Interactive setup wizard"""

    print("🎤 Vocals SDK Setup Wizard")
    print("=" * 50)

    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists() and not force:
        print("⚠️  .env file already exists. Use --force to overwrite.")
        if not click.confirm("Continue with existing configuration?"):
            return

    # API Key setup
    print("\n1. API Key Configuration")
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if api_key:
        print(f"Current API key: {api_key[:10]}...")
        if not click.confirm("Keep current API key?"):
            api_key = None

    if not api_key:
        api_key = click.prompt("Enter your Vocals API key", hide_input=True)
        if not api_key.startswith("vdev_"):
            print("⚠️  API key should start with 'vdev_'")

    # WebSocket endpoint
    print("\n2. WebSocket Configuration")
    current_endpoint = os.environ.get(
        "VOCALS_WS_ENDPOINT", "ws://192.168.1.46:8000/v1/stream/conversation"
    )
    print(f"Current endpoint: {current_endpoint}")

    if click.confirm("Use custom WebSocket endpoint?"):
        endpoint = click.prompt("WebSocket endpoint", default=current_endpoint)
    else:
        endpoint = current_endpoint

    # Audio device selection
    print("\n3. Audio Device Selection")
    try:
        devices = list_audio_devices()
        if devices:
            print("Available audio devices:")
            for device in devices:
                print(
                    f"  {device['id']}: {device['name']} ({device['channels']} channels)"
                )

            device_id = click.prompt(
                "Select device ID (or press Enter for default)",
                type=int,
                default=None,
                show_default=False,
            )
        else:
            device_id = None
    except Exception as e:
        print(f"⚠️  Could not list audio devices: {e}")
        device_id = None

    # Write configuration
    env_content = f"""# Vocals SDK Configuration
VOCALS_DEV_API_KEY={api_key}
VOCALS_WS_ENDPOINT={endpoint}
"""

    if device_id is not None:
        env_content += f"VOCALS_AUDIO_DEVICE_ID={device_id}\n"

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n✅ Configuration saved to .env")
    print("You can now run: vocals-demo")


@cli.command()
@click.option("--verbose", is_flag=True, help="Show detailed test output")
def test(verbose):
    """Run SDK functionality tests"""

    async def run_tests():
        print("🧪 Vocals SDK Tests")
        print("=" * 50)

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.getLogger("vocals_sdk").setLevel(logging.WARNING)

        tester = VocalsSDKTester()

        # Run tests
        print("Testing connection...")
        await tester.test_connection()

        print("Testing audio recording...")
        await tester.test_audio_recording()

        print("Testing configuration...")
        tester.test_configuration()

        print("Testing audio devices...")
        tester.test_audio_devices()

        # Show results
        tester.print_results()

    asyncio.run(run_tests())


@cli.command()
def devices():
    """List available audio devices"""

    print("🎧 Available Audio Devices")
    print("=" * 50)

    try:
        devices = list_audio_devices()
        if devices:
            for device in devices:
                print(f"ID {device['id']}: {device['name']}")
                print(f"  Input channels: {device['channels']}")
                print(f"  Sample rate: {device.get('sample_rate', 'Unknown')}")
                print()
        else:
            print("No audio input devices found")
    except Exception as e:
        print(f"❌ Error listing devices: {e}")


@cli.command()
@click.argument("device_id", type=int)
@click.option("--duration", default=5, help="Test duration in seconds")
def test_device(device_id, duration):
    """Test a specific audio device"""

    print(f"🎤 Testing Audio Device {device_id}")
    print("=" * 50)

    try:
        print(f"Testing device for {duration} seconds...")
        print("Speak into your microphone!")
        print("Volume meter will show below:")

        test_audio_device(device_id, duration)

    except Exception as e:
        print(f"❌ Error testing device: {e}")


@cli.command()
@click.argument("template_name")
@click.option("--output", "-o", default=None, help="Output file name")
def create_template(template_name, output):
    """Create a template file for quick start"""

    templates = get_available_templates()

    if template_name not in templates:
        print(f"❌ Template '{template_name}' not found")
        print(f"Available templates: {', '.join(templates.keys())}")
        return

    if output is None:
        output = f"{template_name}_example.py"

    if Path(output).exists():
        if not click.confirm(f"File {output} exists. Overwrite?"):
            return

    with open(output, "w") as f:
        f.write(templates[template_name])

    print(f"✅ Template created: {output}")


@cli.command()
@click.option(
    "--output", "-o", default="config_report.txt", help="Output file for report"
)
def diagnose(output):
    """Generate diagnostic report"""

    print("🔍 Generating Diagnostic Report")
    print("=" * 50)

    report = generate_diagnostic_report()

    with open(output, "w") as f:
        f.write(report)

    print(f"✅ Diagnostic report saved to: {output}")
    print("\nSummary:")
    print(report.split("\n")[:10])  # Show first 10 lines


# Helper functions
def list_audio_devices():
    """List available audio devices"""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        result = []
        for i, device in enumerate(devices):
            max_input_channels = device.get("max_input_channels", 0)
            if max_input_channels > 0:
                result.append(
                    {
                        "id": i,
                        "name": device.get("name", "Unknown"),
                        "channels": max_input_channels,
                        "sample_rate": device.get("default_samplerate", "Unknown"),
                    }
                )
        return result
    except ImportError:
        raise Exception("sounddevice not installed")
    except Exception as e:
        raise Exception(f"Error querying audio devices: {e}")


def test_audio_device(device_id: int, duration: int = 5):
    """Test audio device with visual feedback"""
    try:
        import sounddevice as sd
        import numpy as np
        import time

        print(f"Testing device {device_id} for {duration} seconds...")

        def callback(indata, frames, time, status):
            volume = np.sqrt(np.mean(indata**2))
            bar_length = int(volume * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"\rVolume: [{bar}] {volume:.3f}", end="", flush=True)

        with sd.InputStream(callback=callback, device=device_id, channels=1):
            time.sleep(duration)

        print("\n✅ Device test completed")

    except Exception as e:
        print(f"\n❌ Error testing device: {e}")


def get_available_templates():
    """Get available code templates"""
    return {
        "voice_assistant": '''#!/usr/bin/env python3
"""
Voice Assistant Template
A simple voice assistant using Vocals SDK
"""

import asyncio
import logging
from vocals_sdk import create_vocals_sdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def voice_assistant():
    """Main voice assistant function"""
    
    # Create SDK instance
    sdk = create_vocals_sdk()
    
    # Custom message handlers
    def on_transcription(message):
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            
            if not is_partial and text:
                print(f"🎤 You said: {text}")
    
    def on_ai_response(message):
        if message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                print(f"🤖 AI: {response}")
    
    # Register handlers
    sdk["on_message"](on_transcription)
    sdk["on_message"](on_ai_response)
    
    try:
        print("🎤 Voice Assistant Started")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")
        
        # Stream microphone (30 seconds)
        await sdk["stream_microphone"](
            duration=30,
            auto_connect=True,
            auto_playback=True,
            verbose=True
        )
        
    except KeyboardInterrupt:
        print("\\n👋 Voice assistant stopped")
    finally:
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    asyncio.run(voice_assistant())
''',
        "file_processor": '''#!/usr/bin/env python3
"""
Audio File Processor Template
Process audio files with Vocals SDK
"""

import asyncio
import sys
from pathlib import Path
from vocals_sdk import create_vocals_sdk

async def process_audio_file(file_path: str):
    """Process an audio file and get AI responses"""
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Create SDK instance
    sdk = create_vocals_sdk()
    
    # Handler for responses
    def on_response(message):
        if message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                print(f"🤖 AI Response: {response}")
    
    sdk["on_message"](on_response)
    
    try:
        print(f"🎵 Processing file: {file_path}")
        
        # Stream audio file
        await sdk["stream_audio_file"](
            file_path=file_path,
            verbose=True,
            auto_connect=True
        )
        
        # Wait for TTS playback to complete
        print("⏳ Waiting for AI response playback...")
        while sdk["get_is_playing"]():
            await asyncio.sleep(0.1)
        
        print("✅ File processing completed")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
    finally:
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_processor.py <audio_file.wav>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    asyncio.run(process_audio_file(file_path))
''',
        "conversation_tracker": '''#!/usr/bin/env python3
"""
Conversation Tracker Template
Track and analyze conversation with AI
"""

import asyncio
from vocals_sdk import (
    create_vocals_sdk,
    create_conversation_tracker,
    create_enhanced_message_handler
)

async def conversation_session():
    """Run a conversation session with tracking"""
    
    # Create SDK and tracker
    sdk = create_vocals_sdk()
    tracker = create_conversation_tracker()
    
    # Enhanced message handler
    handler = create_enhanced_message_handler(
        verbose=True,
        show_transcription=True,
        show_responses=True,
        show_streaming=True
    )
    
    # Tracking handler
    def track_conversation(message):
        handler(message)  # Display message
        
        # Track conversation
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if text:
                tracker["add_transcription"](text, is_partial)
                
        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                tracker["add_response"](response)
    
    sdk["on_message"](track_conversation)
    
    try:
        print("💬 Conversation Session Started")
        print("Have a conversation with the AI...")
        print("Press Ctrl+C to stop and see analysis")
        
        # Run conversation
        await sdk["stream_microphone"](
            duration=60,  # 1 minute
            auto_connect=True,
            auto_playback=True,
            verbose=False
        )
        
    except KeyboardInterrupt:
        print("\\n📊 Conversation Analysis:")
        
    finally:
        # Print conversation history
        tracker["print_conversation"]()
        
        # Print statistics
        stats = tracker["get_stats"]()
        print(f"\\n📈 Session Statistics:")
        print(f"   Duration: {stats['duration']:.1f} seconds")
        print(f"   Exchanges: {stats['transcriptions'] + stats['responses']}")
        
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    asyncio.run(conversation_session())
''',
    }


def generate_diagnostic_report():
    """Generate a diagnostic report"""
    import platform
    import sys

    report = f"""Vocals SDK Diagnostic Report
Generated: {__import__('datetime').datetime.now()}

System Information:
- Platform: {platform.platform()}
- Python Version: {sys.version}
- Python Path: {sys.executable}

Environment Variables:
- VOCALS_DEV_API_KEY: {'SET' if os.environ.get('VOCALS_DEV_API_KEY') else 'NOT SET'}
- VOCALS_WS_ENDPOINT: {os.environ.get('VOCALS_WS_ENDPOINT', 'NOT SET')}

Dependencies:
"""

    # Check dependencies
    deps_to_check = [
        "sounddevice",
        "numpy",
        "websockets",
        "aiohttp",
        "PyJWT",
        "python-dotenv",
        "click",
    ]

    for dep in deps_to_check:
        try:
            __import__(dep)
            report += f"- {dep}: ✅ Installed\n"
        except ImportError:
            report += f"- {dep}: ❌ Missing\n"

    # Check audio devices
    report += "\nAudio Devices:\n"
    try:
        devices = list_audio_devices()
        for device in devices:
            report += (
                f"- {device['id']}: {device['name']} ({device['channels']} channels)\n"
            )
    except Exception as e:
        report += f"- Error: {e}\n"

    return report


class VocalsSDKTester:
    """Test framework for SDK functionality"""

    def __init__(self):
        self.results = []

    async def test_connection(self):
        """Test WebSocket connection"""
        try:
            from .client import create_vocals_sdk

            sdk = create_vocals_sdk()
            await sdk["connect"]()
            connected = sdk["get_is_connected"]()
            await sdk["disconnect"]()

            self.results.append(
                ("WebSocket Connection", "✅ PASS" if connected else "❌ FAIL")
            )
            return connected
        except Exception as e:
            self.results.append(("WebSocket Connection", f"❌ ERROR: {e}"))
            return False

    async def test_audio_recording(self):
        """Test audio recording functionality"""
        try:
            from .client import create_vocals_sdk

            sdk = create_vocals_sdk()
            await sdk["start_recording"]()
            await asyncio.sleep(0.5)
            recording = sdk["get_is_recording"]()
            await sdk["stop_recording"]()

            self.results.append(
                ("Audio Recording", "✅ PASS" if recording else "❌ FAIL")
            )
            return recording
        except Exception as e:
            self.results.append(("Audio Recording", f"❌ ERROR: {e}"))
            return False

    def test_configuration(self):
        """Test configuration"""
        try:
            issues = validate_config()
            if not issues:
                self.results.append(("Configuration", "✅ PASS"))
                return True
            else:
                self.results.append(
                    ("Configuration", f"❌ ISSUES: {', '.join(issues)}")
                )
                return False
        except Exception as e:
            self.results.append(("Configuration", f"❌ ERROR: {e}"))
            return False

    def test_audio_devices(self):
        """Test audio device availability"""
        try:
            devices = list_audio_devices()
            if devices:
                self.results.append(
                    ("Audio Devices", f"✅ {len(devices)} devices found")
                )
                return True
            else:
                self.results.append(("Audio Devices", "❌ No input devices found"))
                return False
        except Exception as e:
            self.results.append(("Audio Devices", f"❌ ERROR: {e}"))
            return False

    def print_results(self):
        """Print test results"""
        print("\n🧪 Test Results:")
        print("=" * 50)
        for test, result in self.results:
            print(f"{test}: {result}")


def validate_config() -> List[str]:
    """Validate configuration and return issues"""
    issues = []

    # Check API key
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if not api_key:
        issues.append("VOCALS_DEV_API_KEY not set")
    elif not api_key.startswith("vdev_"):
        issues.append("Invalid API key format")

    # Check audio system
    try:
        import sounddevice as sd

        sd.query_devices()
    except ImportError:
        issues.append("sounddevice not installed")
    except Exception as e:
        issues.append(f"Audio system error: {e}")

    # Check WebSocket endpoint
    endpoint = os.environ.get("VOCALS_WS_ENDPOINT")
    if endpoint and not endpoint.startswith("ws"):
        issues.append("Invalid WebSocket endpoint format")

    return issues


if __name__ == "__main__":
    cli()
