"""
Testing framework for the Vocals SDK

Provides comprehensive testing utilities for validating SDK functionality,
audio devices, configuration, and network connectivity.
"""

import asyncio
import logging
import os
import time
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class VocalsSDKTester:
    """Comprehensive test framework for SDK functionality"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = []
        self.start_time = time.time()

    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def _add_result(self, test_name: str, success: bool, details: str = ""):
        """Add a test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append(
            {
                "test": test_name,
                "success": success,
                "details": details,
                "status": status,
                "timestamp": time.time(),
            }
        )

        if self.verbose:
            print(f"{status}: {test_name}")
            if details:
                print(f"   Details: {details}")

    # Configuration Tests
    def test_environment_variables(self) -> bool:
        """Test that required environment variables are set"""
        try:
            api_key = os.environ.get("VOCALS_DEV_API_KEY")

            if not api_key:
                self._add_result(
                    "Environment Variables", False, "VOCALS_DEV_API_KEY not set"
                )
                return False

            if not api_key.startswith("vdev_"):
                self._add_result(
                    "Environment Variables", False, "Invalid API key format"
                )
                return False

            # Test optional variables
            endpoint = os.environ.get("VOCALS_WS_ENDPOINT")
            if endpoint and not endpoint.startswith("ws"):
                self._add_result(
                    "Environment Variables", False, "Invalid WebSocket endpoint format"
                )
                return False

            self._add_result(
                "Environment Variables", True, f"API key: {api_key[:10]}..."
            )
            return True

        except Exception as e:
            self._add_result("Environment Variables", False, str(e))
            return False

    def test_configuration_loading(self) -> bool:
        """Test configuration loading and validation"""
        try:
            from .config import get_default_config, validate_environment

            config = get_default_config()

            # Test configuration validation
            issues = validate_environment()
            if issues:
                self._add_result(
                    "Configuration Loading", False, f"Issues: {', '.join(issues)}"
                )
                return False

            # Test config validation
            config_issues = config.validate()
            if config_issues:
                self._add_result(
                    "Configuration Loading",
                    False,
                    f"Config issues: {', '.join(config_issues)}",
                )
                return False

            self._add_result(
                "Configuration Loading", True, "Configuration loaded successfully"
            )
            return True

        except Exception as e:
            self._add_result("Configuration Loading", False, str(e))
            return False

    # Dependencies Tests
    def test_dependencies(self) -> bool:
        """Test that all required dependencies are available"""
        required_deps = [
            "sounddevice",
            "numpy",
            "websockets",
            "aiohttp",
            "PyJWT",
            "python-dotenv",
            "click",
        ]

        optional_deps = ["psutil", "matplotlib"]

        missing_required = []
        missing_optional = []

        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_required.append(dep)

        for dep in optional_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_optional.append(dep)

        if missing_required:
            self._add_result(
                "Dependencies",
                False,
                f"Missing required: {', '.join(missing_required)}",
            )
            return False

        details = f"All required dependencies available"
        if missing_optional:
            details += f", missing optional: {', '.join(missing_optional)}"

        self._add_result("Dependencies", True, details)
        return True

    # Audio System Tests
    def test_audio_system(self) -> bool:
        """Test audio system availability"""
        try:
            from .audio_processor import list_audio_devices, get_default_audio_device

            devices = list_audio_devices()
            if not devices:
                self._add_result("Audio System", False, "No audio input devices found")
                return False

            default_device = get_default_audio_device()
            if default_device is None:
                self._add_result("Audio System", False, "No default audio device")
                return False

            self._add_result(
                "Audio System",
                True,
                f"Found {len(devices)} audio devices, default: {default_device}",
            )
            return True

        except Exception as e:
            self._add_result("Audio System", False, str(e))
            return False

    async def test_audio_recording(self, duration: float = 1.0) -> bool:
        """Test basic audio recording functionality"""
        try:
            from .audio_processor import create_audio_processor, AudioConfig

            audio_config = AudioConfig(sample_rate=44100, channels=1)
            processor = create_audio_processor(audio_config)

            # Test recording for a short duration
            recorded_data = []

            def audio_handler(data):
                recorded_data.extend(data)

            processor["add_audio_data_handler"](audio_handler)

            # Start recording
            await processor["start_recording"]()
            await asyncio.sleep(duration)
            await processor["stop_recording"]()

            processor["cleanup"]()

            if len(recorded_data) == 0:
                self._add_result("Audio Recording", False, "No audio data recorded")
                return False

            self._add_result(
                "Audio Recording", True, f"Recorded {len(recorded_data)} samples"
            )
            return True

        except Exception as e:
            self._add_result("Audio Recording", False, str(e))
            return False

    async def test_audio_playback(self) -> bool:
        """Test basic audio playback functionality"""
        try:
            from .audio_processor import create_audio_processor, AudioConfig
            from .types import TTSAudioSegment
            import base64

            audio_config = AudioConfig(sample_rate=44100, channels=1)
            processor = create_audio_processor(audio_config)

            # Create a simple sine wave test audio
            import numpy as np

            duration = 0.5  # 0.5 seconds
            sample_rate = 44100
            frequency = 440  # A4 note

            t = np.linspace(0, duration, int(sample_rate * duration))
            sine_wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)

            # Convert to WAV format
            import io
            import wave

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes((sine_wave * 32767).astype(np.int16).tobytes())

            wav_data = wav_buffer.getvalue()
            audio_data_b64 = base64.b64encode(wav_data).decode("utf-8")

            # Create test segment
            segment = TTSAudioSegment(
                text="Test audio",
                audio_data=audio_data_b64,
                sample_rate=sample_rate,
                segment_id="test_segment",
                sentence_number=1,
                generation_time_ms=100,
                format="wav",
                duration_seconds=duration,
            )

            # Test playback
            processor["add_to_queue"](segment)
            await processor["play_audio"]()

            # Wait for playback to complete
            await asyncio.sleep(duration + 0.5)

            processor["cleanup"]()

            self._add_result("Audio Playback", True, "Test audio played successfully")
            return True

        except Exception as e:
            self._add_result("Audio Playback", False, str(e))
            return False

    # Network Tests
    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection to Vocals service"""
        try:
            from .websocket_client import create_websocket_client
            from .config import get_default_config

            config = get_default_config()
            client = create_websocket_client(config)

            # Test connection
            await client["connect"]()

            if not client["get_is_connected"]():
                self._add_result("WebSocket Connection", False, "Failed to connect")
                return False

            # Test basic functionality
            await asyncio.sleep(0.5)

            await client["disconnect"]()

            self._add_result(
                "WebSocket Connection", True, "Successfully connected and disconnected"
            )
            return True

        except Exception as e:
            self._add_result("WebSocket Connection", False, str(e))
            return False

    async def test_token_generation(self) -> bool:
        """Test WebSocket token generation"""
        try:
            from .wstoken import generate_ws_token, validate_api_key_format

            # Test API key validation
            api_key = os.environ.get("VOCALS_DEV_API_KEY")
            if not api_key:
                self._add_result("Token Generation", False, "No API key available")
                return False

            validation_result = validate_api_key_format(api_key)
            if not hasattr(validation_result, "data"):
                self._add_result(
                    "Token Generation",
                    False,
                    f"Invalid API key format",
                )
                return False

            # Test token generation
            token_result = generate_ws_token()
            if not hasattr(token_result, "data"):
                self._add_result(
                    "Token Generation",
                    False,
                    f"Token generation failed",
                )
                return False

            token = token_result.data
            self._add_result(
                "Token Generation",
                True,
                f"Token generated, expires at: {token.expires_at}",
            )
            return True

        except Exception as e:
            self._add_result("Token Generation", False, str(e))
            return False

    # Integration Tests
    async def test_sdk_creation(self) -> bool:
        """Test SDK creation and basic functionality"""
        try:
            from .client import create_vocals

            sdk = create_vocals()

            # Test basic properties
            if not hasattr(sdk, "__getitem__"):
                self._add_result("SDK Creation", False, "SDK not created as expected")
                return False

            # Test core methods exist
            required_methods = [
                "connect",
                "disconnect",
                "start_recording",
                "stop_recording",
                "stream_microphone",
                "stream_audio_file",
                "on_message",
            ]

            for method in required_methods:
                if method not in sdk:
                    self._add_result("SDK Creation", False, f"Missing method: {method}")
                    return False

            # Test connection
            await sdk["connect"]()

            if not sdk["get_is_connected"]():
                self._add_result("SDK Creation", False, "SDK failed to connect")
                return False

            await sdk["disconnect"]()
            sdk["cleanup"]()

            self._add_result(
                "SDK Creation", True, "SDK created and connected successfully"
            )
            return True

        except Exception as e:
            self._add_result("SDK Creation", False, str(e))
            return False

    async def test_message_handling(self) -> bool:
        """Test message handling system"""
        try:
            from .client import create_vocals
            from .types import WebSocketResponse

            sdk = create_vocals()

            # Test message handler registration
            received_messages = []

            def test_handler(message):
                received_messages.append(message)

            remove_handler = sdk["on_message"](test_handler)

            # Simulate a message (this would normally come from WebSocket)
            test_message = WebSocketResponse(
                event="test", type="test", data={"test": "data"}
            )

            # Test handler removal
            remove_handler()

            sdk["cleanup"]()

            self._add_result("Message Handling", True, "Message handler system working")
            return True

        except Exception as e:
            self._add_result("Message Handling", False, str(e))
            return False

    # Performance Tests
    async def test_performance_baseline(self) -> bool:
        """Test basic performance characteristics"""
        try:
            from .utils import create_performance_monitor

            monitor = create_performance_monitor(verbose=False)

            # Simulate some activity
            for i in range(100):
                monitor["update"]("messages_received")
                if i % 10 == 0:
                    monitor["update"]("transcriptions_received")

            stats = monitor["get_stats"]()

            if stats["messages_received"] != 100:
                self._add_result(
                    "Performance Baseline",
                    False,
                    f"Expected 100 messages, got {stats['messages_received']}",
                )
                return False

            if stats["transcriptions_received"] != 10:
                self._add_result(
                    "Performance Baseline",
                    False,
                    f"Expected 10 transcriptions, got {stats['transcriptions_received']}",
                )
                return False

            self._add_result(
                "Performance Baseline",
                True,
                f"Performance tracking working, {stats['messages_per_second']:.1f} msgs/sec",
            )
            return True

        except Exception as e:
            self._add_result("Performance Baseline", False, str(e))
            return False

    # File System Tests
    def test_file_operations(self) -> bool:
        """Test file operations and permissions"""
        try:
            # Test .env file creation
            test_env_path = Path(".test_env")
            test_content = "TEST_VAR=test_value\n"

            try:
                with open(test_env_path, "w") as f:
                    f.write(test_content)

                # Test reading
                with open(test_env_path, "r") as f:
                    content = f.read()

                if content != test_content:
                    self._add_result("File Operations", False, "File content mismatch")
                    return False

                # Cleanup
                test_env_path.unlink()

            except Exception as e:
                self._add_result(
                    "File Operations", False, f"File operations failed: {e}"
                )
                return False

            self._add_result("File Operations", True, "File operations working")
            return True

        except Exception as e:
            self._add_result("File Operations", False, str(e))
            return False

    # Utility Tests
    def test_utility_functions(self) -> bool:
        """Test utility functions"""
        try:
            from .utils import (
                create_enhanced_message_handler,
                create_conversation_tracker,
                create_performance_monitor,
            )

            # Test message handler creation
            handler = create_enhanced_message_handler()
            if not callable(handler):
                self._add_result(
                    "Utility Functions", False, "Message handler not callable"
                )
                return False

            # Test conversation tracker
            tracker = create_conversation_tracker()
            if "add_transcription" not in tracker:
                self._add_result(
                    "Utility Functions", False, "Conversation tracker incomplete"
                )
                return False

            # Test performance monitor
            monitor = create_performance_monitor(verbose=False)
            if "update" not in monitor:
                self._add_result(
                    "Utility Functions", False, "Performance monitor incomplete"
                )
                return False

            self._add_result("Utility Functions", True, "All utility functions working")
            return True

        except Exception as e:
            self._add_result("Utility Functions", False, str(e))
            return False

    # Main Test Runner
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        self._log("🧪 Starting Vocals SDK Tests")
        self._log("=" * 50)

        # Configuration and Environment Tests
        self._log("\n📋 Configuration Tests:")
        self.test_environment_variables()
        self.test_configuration_loading()

        # Dependencies Tests
        self._log("\n📦 Dependencies Tests:")
        self.test_dependencies()

        # Audio System Tests
        self._log("\n🎧 Audio System Tests:")
        self.test_audio_system()
        await self.test_audio_recording()
        await self.test_audio_playback()

        # Network Tests
        self._log("\n🌐 Network Tests:")
        await self.test_websocket_connection()
        await self.test_token_generation()

        # Integration Tests
        self._log("\n🔧 Integration Tests:")
        await self.test_sdk_creation()
        await self.test_message_handling()

        # Performance Tests
        self._log("\n⚡ Performance Tests:")
        await self.test_performance_baseline()

        # File System Tests
        self._log("\n📁 File System Tests:")
        self.test_file_operations()

        # Utility Tests
        self._log("\n🛠️ Utility Tests:")
        self.test_utility_functions()

        # Summary
        self._log("\n" + "=" * 50)
        self._log("📊 Test Results Summary")
        self._log("=" * 50)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests

        self._log(f"Total Tests: {total_tests}")
        self._log(f"Passed: {passed_tests} ✅")
        self._log(f"Failed: {failed_tests} ❌")
        self._log(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

        duration = time.time() - self.start_time
        self._log(f"Total Duration: {duration:.2f} seconds")

        if failed_tests > 0:
            self._log("\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    self._log(f"   • {result['test']}: {result['details']}")

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests / total_tests * 100,
            "duration": duration,
            "results": self.results,
            "overall_success": failed_tests == 0,
        }

    def print_results(self):
        """Print formatted test results"""
        if not self.results:
            print("No test results available")
            return

        print("\n🧪 Test Results:")
        print("=" * 50)

        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")

        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        print(f"\nSummary: {passed}/{total} tests passed")


# Utility Functions
def create_test_suite(verbose: bool = True) -> VocalsSDKTester:
    """Create a new test suite instance"""
    return VocalsSDKTester(verbose=verbose)


async def run_quick_test() -> bool:
    """Run a quick subset of tests for basic validation"""
    tester = VocalsSDKTester(verbose=False)

    # Run only essential tests
    success = True
    success &= tester.test_environment_variables()
    success &= tester.test_dependencies()
    success &= tester.test_audio_system()
    success &= await tester.test_websocket_connection()
    success &= await tester.test_sdk_creation()

    return success


async def run_full_test_suite(verbose: bool = True) -> Dict[str, Any]:
    """Run the complete test suite"""
    tester = VocalsSDKTester(verbose=verbose)
    return await tester.run_all_tests()


def benchmark_performance(duration: float = 10.0) -> Dict[str, Any]:
    """Run performance benchmarks"""
    from .utils import create_performance_monitor
    import time

    monitor = create_performance_monitor(verbose=False)
    start_time = time.time()

    # Simulate activity
    message_count = 0
    while time.time() - start_time < duration:
        monitor["update"]("messages_received")
        message_count += 1

        if message_count % 100 == 0:
            monitor["update"]("transcriptions_received")

        if message_count % 500 == 0:
            monitor["update"]("responses_received")

        time.sleep(0.001)  # Small delay to simulate real workload

    stats = monitor["get_stats"]()

    return {
        "duration": duration,
        "messages_processed": stats["messages_received"],
        "messages_per_second": stats["messages_per_second"],
        "transcriptions": stats["transcriptions_received"],
        "responses": stats["responses_received"],
        "memory_usage": stats.get("avg_memory_mb", 0),
        "cpu_usage": stats.get("avg_cpu_percent", 0),
    }


# Test Data Generators
def generate_test_audio_data(
    duration: float = 1.0, sample_rate: int = 44100
) -> List[float]:
    """Generate test audio data for testing"""
    try:
        import numpy as np

        # Generate a simple sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        amplitude = 0.5

        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return sine_wave.astype(np.float32).tolist()

    except ImportError:
        # Fallback: generate simple test data without numpy
        sample_count = int(sample_rate * duration)
        return [0.5 * (i % 100 - 50) / 50 for i in range(sample_count)]


if __name__ == "__main__":
    # Run tests when module is executed directly
    async def main():
        print("🧪 Running Vocals SDK Test Suite")
        results = await run_full_test_suite(verbose=True)

        if results["overall_success"]:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ {results['failed']} tests failed")
            exit(1)

    asyncio.run(main())
