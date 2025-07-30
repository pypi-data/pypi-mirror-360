#!/usr/bin/env python3
"""
Enhanced example script demonstrating real-time microphone streaming through Vocals SDK.
This version uses the new SDK abstractions with enhanced text handling for both 
transcription and LLM responses.
"""

import asyncio
import logging
import signal

# Configure logging (can be overridden per example)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Vocals SDK with new utilities
from vocals import (
    create_vocals,
    get_default_config,
    AudioConfig,
    create_microphone_stats_tracker,
    create_microphone_message_handler,
    create_microphone_connection_handler,
    create_microphone_audio_data_handler,
    create_conversation_tracker,
    create_enhanced_message_handler,
)

# Global shutdown event
shutdown_event = asyncio.Event()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        if not shutdown_event.is_set():
            logger.info(f"📡 Received signal {signum}, shutting down...")
            shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """
    Main function demonstrating enhanced microphone streaming with beautiful text display.
    """
    sdk = None
    try:
        # Set logging to WARNING level for cleaner output
        logging.getLogger("vocals").setLevel(logging.WARNING)
        logging.getLogger("websockets").setLevel(logging.WARNING)

        logger.info("🎤 Starting Enhanced Vocals SDK Microphone Streaming Example")

        # Setup signal handlers
        setup_signal_handlers()

        # Create SDK configuration
        config = get_default_config()
        audio_config = AudioConfig(sample_rate=24000, channels=1, format="pcm_f32le")

        # Create SDK instance
        sdk = create_vocals(config, audio_config)

        try:
            print("\n" + "=" * 60)
            print("🎤 ENHANCED MICROPHONE STREAMING")
            print("=" * 60)
            print("Speak into your microphone!")
            print("You'll see:")
            print("  🎤 Real-time transcription (with partial updates)")
            print("  💭 Streaming AI responses")
            print("  🤖 AI speaking (with TTS audio)")
            print("Recording for 30 seconds...")
            print("=" * 60)

            # Create microphone streaming task
            async def stream_task():
                return await sdk["stream_microphone"](
                    duration=30.0,  # Record for 30 seconds
                    auto_connect=True,  # Auto-connect if needed
                    auto_playback=True,  # Auto-play received audio
                    verbose=False,  # Clean output, no debug messages
                    stats_tracking=True,  # Track session statistics
                    amplitude_threshold=0.01,  # Voice activity detection threshold
                )

            # Create streaming task
            streaming_task = asyncio.create_task(stream_task())

            # Wait for either completion or shutdown signal
            shutdown_task = asyncio.create_task(shutdown_event.wait())

            try:
                done, pending = await asyncio.wait(
                    [streaming_task, shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Get stats if streaming completed
                stats = None
                if streaming_task in done and not streaming_task.cancelled():
                    try:
                        stats = streaming_task.result()
                    except Exception:
                        stats = None

            finally:
                # Clean cancellation without recursion
                if not streaming_task.done():
                    streaming_task.cancel()
                if not shutdown_task.done():
                    shutdown_task.cancel()

                # Wait briefly for cancellation to complete
                await asyncio.sleep(0.1)

            # Print final statistics
            print("\n" + "=" * 60)
            print("🎉 MICROPHONE STREAMING COMPLETED!")
            print("=" * 60)
            if stats:
                print("📊 Session Statistics:")
                print(f"   • Transcriptions: {stats.get('transcriptions', 0)}")
                print(f"   • AI Responses: {stats.get('responses', 0)}")
                print(f"   • TTS Segments: {stats.get('tts_segments_received', 0)}")
                print(f"   • Speech Interruptions: {stats.get('interruptions', 0)}")
                print(f"   • Recording Time: {stats.get('recording_time', 0):.1f}s")
            print("=" * 60)

        finally:
            # Cleanup will be handled in the outer finally block
            pass

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user - shutting down gracefully...")
        logger.info("👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        # Ensure proper cleanup
        if sdk:
            try:
                # Stop recording first
                try:
                    await asyncio.wait_for(sdk["stop_recording"](), timeout=2.0)
                except (asyncio.TimeoutError, Exception):
                    pass

                # Then disconnect and cleanup
                await asyncio.wait_for(sdk["disconnect"](), timeout=3.0)
                sdk["cleanup"]()

            except Exception as e:
                logger.debug(f"Error during cleanup: {e}")
        shutdown_event.set()


async def conversation_tracking_example():
    """
    Example with conversation tracking and enhanced text display.
    """
    try:
        logger.info("📜 Starting Conversation Tracking Example")

        # Create SDK
        sdk = create_vocals()

        # Create conversation tracker and stats tracker
        conversation_tracker = create_conversation_tracker()
        stats_tracker = create_microphone_stats_tracker(verbose=True)

        # Create enhanced message handler with conversation tracking
        message_handler = create_microphone_message_handler(
            stats_tracker=stats_tracker,
            verbose=False,
            conversation_tracker=conversation_tracker,
            show_text=True,  # Show beautiful text display
        )
        connection_handler = create_microphone_connection_handler(
            stats_tracker, verbose=False
        )
        audio_handler = create_microphone_audio_data_handler(
            amplitude_threshold=0.02, verbose=False
        )

        # Set up handlers
        sdk["on_message"](message_handler)
        sdk["on_connection_change"](connection_handler)
        sdk["on_audio_data"](audio_handler)

        try:
            print("\n" + "=" * 60)
            print("📜 CONVERSATION TRACKING EXAMPLE")
            print("=" * 60)
            print("This example tracks your full conversation with the AI.")
            print("Features:")
            print("  🎤 Partial & final transcriptions")
            print("  💭 Streaming LLM responses")
            print("  🤖 TTS audio segments")
            print("  📊 Detailed conversation history")
            print("Speak for 20 seconds and see the full history!")
            print("=" * 60)

            # Stream microphone with enhanced features
            await sdk["stream_microphone"](
                duration=20.0,
                auto_connect=True,
                auto_playback=True,
                verbose=False,
                stats_tracking=False,
            )

            # Print detailed conversation history
            conversation_tracker["print_conversation"]()

            # Print session statistics
            stats_tracker["print"]()

            # Print conversation stats
            conv_stats = conversation_tracker["get_stats"]()
            print(f"\n📈 Conversation lasted {conv_stats['duration']:.1f} seconds")
            print(
                f"🗣️  Total dialogue exchanges: {conv_stats['transcriptions'] + conv_stats['responses']}"
            )

        finally:
            await sdk["disconnect"]()
            sdk["cleanup"]()

    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


async def minimal_example():
    """
    Minimal example - just one line to stream microphone!
    """
    try:
        logger.info("🎤 Starting Minimal Example")

        # Create SDK and stream microphone in one go
        sdk = create_vocals()
        await sdk["stream_microphone"](duration=10.0)

        logger.info("🎉 Minimal example completed!")

    except Exception as e:
        logger.error(f"Error in minimal example: {e}")
        raise


async def infinite_streaming_example():
    """
    Example showing infinite streaming until interrupted.
    """
    try:
        logger.info("🎤 Starting Infinite Streaming Example")

        # Create SDK
        sdk = create_vocals()

        # Create a task to handle the infinite streaming
        async def stream_task():
            await sdk["stream_microphone"](
                duration=0,  # 0 = infinite streaming
                auto_connect=True,
                auto_playback=True,
                verbose=False,
                stats_tracking=True,
            )

        # Run streaming task
        stream_task_handle = asyncio.create_task(stream_task())

        try:
            # Wait for shutdown signal
            await shutdown_event.wait()

            # Stop recording gracefully
            await sdk["stop_recording"]()

            # Wait a bit for final processing
            await asyncio.sleep(2)

            # Cancel the streaming task
            stream_task_handle.cancel()

            try:
                await stream_task_handle
            except asyncio.CancelledError:
                pass

        finally:
            await sdk["disconnect"]()
            sdk["cleanup"]()

        logger.info("🎉 Infinite streaming example completed!")

    except Exception as e:
        logger.error(f"Error in infinite streaming example: {e}")
        raise


if __name__ == "__main__":
    print("Choose an example:")
    print("1. Enhanced microphone streaming (30s)")
    print("2. Conversation tracking example (20s)")
    print("3. Minimal example (10s)")
    print("4. Infinite streaming example (until Ctrl+C)")

    choice = input("Enter choice (1-4): ").strip()

    try:
        if choice == "1":
            asyncio.run(main())
        elif choice == "2":
            asyncio.run(conversation_tracking_example())
        elif choice == "3":
            asyncio.run(minimal_example())
        elif choice == "4":
            asyncio.run(infinite_streaming_example())
        else:
            print("Invalid choice, running enhanced example")
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import sys

        sys.exit(1)
