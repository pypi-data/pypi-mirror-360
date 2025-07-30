#!/usr/bin/env python3
"""
Enhanced example script demonstrating file-based audio playback through Vocals SDK.
This version uses the new SDK abstractions and enhanced text handling for both 
transcription and LLM responses.
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Vocals SDK with new utilities
from vocals import (
    create_vocals,
    get_default_config,
    AudioConfig,
    create_default_message_handler,
    create_enhanced_message_handler,
    create_conversation_tracker,
    create_default_connection_handler,
    create_default_error_handler,
)

# Audio file path
AUDIO_FILE = Path(__file__).parent / "test_audio.wav"


async def main():
    """
    Main function demonstrating enhanced file-based audio playback with text display.
    """
    try:
        logger.info("🎵 Starting Enhanced Vocals SDK File Playback Example")

        # Create SDK configuration
        config = get_default_config()
        audio_config = AudioConfig(sample_rate=24000, channels=1, format="pcm_f32le")

        # Create SDK instance
        sdk = create_vocals(config, audio_config)

        # Set up enhanced message handler to beautifully display text
        remove_message_handler = sdk["on_message"](
            create_enhanced_message_handler(
                verbose=False,
                show_transcription=True,  # Show transcription text prominently
                show_responses=True,  # Show LLM responses prominently
                show_streaming=True,  # Show streaming LLM responses
                show_detection=False,  # Don't show detection for file playback
            )
        )
        remove_connection_handler = sdk["on_connection_change"](
            create_default_connection_handler()
        )
        remove_error_handler = sdk["on_error"](create_default_error_handler())

        try:
            print("\n" + "=" * 60)
            print("🎵 STARTING AUDIO FILE PLAYBACK")
            print("=" * 60)
            print("The audio file will be streamed to the AI.")
            print("Watch for transcription and AI responses below...")
            print("=" * 60)

            # Stream the audio file - this handles everything automatically!
            await sdk["stream_audio_file"](
                file_path=str(AUDIO_FILE),
                chunk_size=1024,
                verbose=False,
                auto_connect=True,
            )

            print("\n" + "=" * 60)
            print("🎉 FILE PLAYBACK COMPLETED SUCCESSFULLY!")
            print("=" * 60)

        finally:
            # Cleanup handlers
            remove_message_handler()
            remove_connection_handler()
            remove_error_handler()

            # Disconnect and cleanup
            await sdk["disconnect"]()
            sdk["cleanup"]()

    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


async def conversation_tracking_example():
    """
    Example with conversation tracking to maintain dialogue history.
    """
    try:
        logger.info("📜 Starting Conversation Tracking Example")

        # Create SDK configuration
        config = get_default_config()
        audio_config = AudioConfig(sample_rate=24000, channels=1, format="pcm_f32le")

        # Create SDK instance
        sdk = create_vocals(config, audio_config)

        # Create conversation tracker
        conversation_tracker = create_conversation_tracker()

        # Set up enhanced message handler that automatically tracks conversation
        def enhanced_tracking_handler(message):
            """Enhanced handler with automatic conversation tracking"""
            try:
                # Handle display first
                enhanced_handler = create_enhanced_message_handler(
                    verbose=True,
                    show_transcription=True,
                    show_responses=True,
                    show_streaming=True,
                    show_detection=False,
                )
                enhanced_handler(message)

                # Then handle conversation tracking for all message types
                if message.type == "transcription" and message.data:
                    text = message.data.get("text", "")
                    is_partial = message.data.get("is_partial", False)
                    segment_id = message.data.get("segment_id", "unknown")
                    if text:
                        conversation_tracker["add_transcription"](
                            text, is_partial, segment_id
                        )

                elif message.type == "llm_response_streaming" and message.data:
                    token = message.data.get("token", "")
                    accumulated = message.data.get("accumulated_response", "")
                    is_complete = message.data.get("is_complete", False)
                    segment_id = message.data.get("segment_id", "unknown")
                    text = accumulated or token
                    if text:
                        conversation_tracker["add_response"](
                            text,
                            is_streaming=True,
                            is_complete=is_complete,
                            segment_id=segment_id,
                        )

                elif message.type == "llm_response" and message.data:
                    response_text = message.data.get("response", "")
                    segment_id = message.data.get("segment_id", "unknown")
                    if response_text:
                        conversation_tracker["add_response"](
                            response_text, segment_id=segment_id
                        )

                elif message.type == "tts_audio" and message.data:
                    text = message.data.get("text", "")
                    segment_id = message.data.get("segment_id", "unknown")
                    if text:
                        conversation_tracker["add_tts_segment"](text, segment_id)

                elif message.event == "transcription" and message.data:
                    # Legacy format
                    conversation_tracker["add_transcription"](str(message.data))

                elif message.event == "response" and message.data:
                    # Legacy format
                    conversation_tracker["add_response"](str(message.data))

            except Exception as e:
                logger.error(f"Error in enhanced tracking handler: {e}")

        remove_message_handler = sdk["on_message"](enhanced_tracking_handler)
        remove_connection_handler = sdk["on_connection_change"](
            create_default_connection_handler()
        )
        remove_error_handler = sdk["on_error"](create_default_error_handler())

        try:
            print("\n" + "=" * 60)
            print("📜 CONVERSATION TRACKING EXAMPLE")
            print("=" * 60)
            print("This example tracks the full conversation history.")
            print("You'll see a summary at the end!")
            print("=" * 60)

            # Stream the audio file
            await sdk["stream_audio_file"](str(AUDIO_FILE))

            # Print conversation history
            conversation_tracker["print_conversation"]()

            # Print conversation stats
            stats = conversation_tracker["get_stats"]()
            print(f"\n📈 Session lasted {stats['duration']:.1f} seconds")

        finally:
            # Cleanup handlers
            remove_message_handler()
            remove_connection_handler()
            remove_error_handler()

            # Cleanup SDK
            await sdk["disconnect"]()
            sdk["cleanup"]()

    except KeyboardInterrupt:
        logger.info("👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


async def minimal_example():
    """
    Minimal example - just one line to stream an audio file!
    """
    try:
        logger.info("🎵 Starting Minimal Example")

        # Create SDK and stream file in one go
        sdk = create_vocals()
        await sdk["stream_audio_file"](str(AUDIO_FILE))

        logger.info("🎉 Minimal example completed!")

    except Exception as e:
        logger.error(f"Error in minimal example: {e}")
        raise


if __name__ == "__main__":
    print("Choose an example:")
    print("1. Enhanced file playback with text display")
    print("2. Conversation tracking example")
    print("3. Minimal example")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(conversation_tracking_example())
    elif choice == "3":
        asyncio.run(minimal_example())
    else:
        print("Invalid choice, running enhanced example")
        asyncio.run(main())
