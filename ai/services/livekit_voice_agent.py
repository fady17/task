# ai/services/livekit_voice_agent.py

import asyncio
import os
import json
import logging
from typing import Optional, Dict, Any
from livekit import rtc, api
import numpy as np

# Pipecat imports
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.tts import AzureTTSService
from pipecat.transcriptions.language import Language

# Import your existing AI logic
from .ai_processor import process_chat_request
from ..dependencies import get_todo_api_client
from .. import db_utils

# Import our custom processors
from .livekit_stt_processor import LiveKitSTTProcessor
from .livekit_tts_processor import LiveKitTTSProcessor

logger = logging.getLogger(__name__)

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
BOT_IDENTITY = "ai-voice-assistant"

class LiveKitVoiceAgent:
    """
    A LiveKit participant that processes voice using Pipecat pipeline
    and integrates with your existing AI processor.
    """
    
    def __init__(self, user_id: int = 1):
        self.room: Optional[rtc.Room] = None
        self.user_id = user_id
        self.session_id: Optional[int] = None
        self.todo_api_client = get_todo_api_client()
        
        # Audio processing
        self.audio_source: Optional[rtc.AudioSource] = None
        self.audio_track: Optional[rtc.LocalAudioTrack] = None
        
        # Audio processing components
        self.stt_processor: Optional[LiveKitSTTProcessor] = None
        self.tts_processor: Optional[LiveKitTTSProcessor] = None
        
        # Conversation state
        self.conversation_history = []
        self.is_processing = False
        
        logger.info(f"LiveKitVoiceAgent initialized for user {user_id}")

    async def _initialize_services(self):
        """Initialize Pipecat STT and TTS services"""
        try:
            azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
            azure_speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if not azure_speech_key or not azure_speech_region:
                raise ValueError("Azure Speech credentials not found in environment")
            
            # Initialize STT service
            stt_service = AzureSTTService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                language=Language.EN_US
            )
            
            # Initialize TTS service
            tts_service = AzureTTSService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                voice="en-US-JennyNeural"
            )
            
            # Create processors (audio_source will be set later)
            self.stt_processor = LiveKitSTTProcessor(stt_service)
            self.stt_processor.set_transcription_callback(self._handle_transcription)
            
            # TTS processor will be created after audio source is available
            
            logger.info("Pipecat services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pipecat services: {e}")
            raised in environment")
            
            # Initialize STT service
            self.stt_service = AzureSTTService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                language=Language.EN_US
            )
            
            # Initialize TTS service
            self.tts_service = AzureTTSService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                voice="en-US-JennyNeural"
            )
            
            logger.info("Pipecat services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pipecat services: {e}")
            raise

    async def _ensure_session(self):
        """Create a database session if it doesn't exist"""
        if self.session_id is None:
            try:
                session_record = await db_utils.create_new_session(self.user_id)
                self.session_id = session_record['id']
                await db_utils.update_session_title(
                    self.session_id, 
                    f"Voice Chat - LiveKit Room"
                )
                logger.info(f"Created new voice session with ID: {self.session_id}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                # Fallback: use a dummy session ID
                self.session_id = 1

    async def connect(self, room_name: str):
        """Connect to LiveKit room as voice agent"""
        logger.info(f"Voice Agent attempting to join LiveKit room: {room_name}")
        
        # Initialize services first
        await self._initialize_services()
        await self._ensure_session()
        
        # Create LiveKit token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(BOT_IDENTITY) \
            .with_name("AI Voice Assistant") \
            .with_grants(api.VideoGrants(
                room_join=True, 
                room=room_name,
                can_publish=True,
                can_subscribe=True
            )) \
            .to_jwt()

        self.room = rtc.Room()
        
        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")
            # Subscribe to their audio tracks
            asyncio.create_task(self._subscribe_to_participant_audio(participant))
        
        @self.room.on("participant_disconnected") 
        def on_participant_disconnected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant disconnected: {participant.identity}")

        @self.room.on("track_published")
        def on_track_published(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            logger.info(f"Track published: {publication.sid} by {participant.identity}")
            if publication.kind == rtc.TrackKind.KIND_AUDIO:
                asyncio.create_task(self._handle_audio_track(publication, participant))

        # Connect to room
        await self.room.connect(LIVEKIT_URL, token)
        
        # Create and publish our audio track for TTS output
        await self._setup_audio_output()
        
        logger.info(f"Voice Agent connected successfully to room: {room_name}")

    async def _setup_audio_output(self):
        """Set up audio source and track for TTS output"""
        try:
            # Create audio source (16kHz, mono, 16-bit)
            self.audio_source = rtc.AudioSource(16000, 1)
            self.audio_track = rtc.LocalAudioTrack.create_audio_track(
                "ai-voice", self.audio_source
            )
            
            # Now create TTS processor with audio source
            azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
            azure_speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            tts_service = AzureTTSService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                voice="en-US-JennyNeural"
            )
            
            self.tts_processor = LiveKitTTSProcessor(tts_service, self.audio_source)
            
            # Publish the audio track
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            
            await self.room.local_participant.publish_track(self.audio_track, options)
            logger.info("Audio output track published successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup audio output: {e}")

    async def _subscribe_to_participant_audio(self, participant: rtc.RemoteParticipant):
        """Subscribe to a participant's audio tracks"""
        for publication in participant.track_publications.values():
            if publication.kind == rtc.TrackKind.KIND_AUDIO and not publication.subscribed:
                await publication.set_subscribed(True)
                logger.info(f"Subscribed to audio from {participant.identity}")

    async def _handle_audio_track(self, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        """Handle incoming audio track from participant"""
        if participant.identity == BOT_IDENTITY:
            return  # Don't process our own audio
            
        track = publication.track
        if not track:
            return
            
        logger.info(f"Processing audio from {participant.identity}")
        
        # Create audio stream
        audio_stream = rtc.AudioStream(track)
        
        # Process audio frames
        async for audio_frame_event in audio_stream:
            if self.is_processing:
                continue  # Skip if we're already processing
                
            await self._process_audio_frame(audio_frame_event.frame, participant)

    async def _process_audio_frame(self, frame: rtc.AudioFrame, participant: rtc.RemoteParticipant):
        """Process individual audio frame through STT pipeline"""
        try:
            if not self.stt_processor:
                return
                
            # Convert LiveKit audio frame to bytes
            audio_bytes = bytes(frame.data)
            
            # Process through our STT processor
            await self.stt_processor.process_audio_frame(
                audio_bytes, 
                frame.sample_rate, 
                frame.channels_per_frame
            )
            
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")

    async def _handle_transcription(self, transcribed_text: str):
        """Handle transcription and generate AI response"""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            logger.info(f"Processing transcription: {transcribed_text}")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": transcribed_text
            })
            
            # Process through your existing AI processor
            ai_response = ""
            async for response_chunk in process_chat_request(
                prompt=transcribed_text,
                session_id=self.session_id,
                todo_api=self.todo_api_client
            ):
                if response_chunk.get("type") == "chat_message":
                    content = response_chunk.get("content", "")
                    if content:
                        ai_response += content
                elif response_chunk.get("type") == "error":
                    ai_response = f"I encountered an error: {response_chunk.get('content', 'Unknown error')}"
                    break
            
            if ai_response:
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                # Convert to speech and play
                if self.tts_processor:
                    await self.tts_processor.speak_text(ai_response)
                
                # Also send as data message for any text-based clients
                await self._send_data_message({
                    "type": "voice_response",
                    "content": ai_response,
                    "transcription": transcribed_text
                })
            
        except Exception as e:
            logger.error(f"Error handling transcription: {e}")
            error_message = "I'm sorry, I encountered an error processing your request."
            if self.tts_processor:
                await self.tts_processor.speak_text(error_message)
        finally:
            self.is_processing = False

    async def _send_data_message(self, payload: Dict[str, Any]):
        """Send data message to room participants"""
        if self.room:
            try:
                await self.room.local_participant.publish_data(
                    json.dumps(payload), 
                    reliable=True
                )
            except Exception as e:
                logger.error(f"Error sending data message: {e}")

    async def disconnect(self):
        """Disconnect from LiveKit room"""
        if self.room:
            await self.room.disconnect()
            logger.info("Voice Agent disconnected from LiveKit room")


# Singleton instance
livekit_voice_agent = LiveKitVoiceAgent()
VOICE_CHAT_ROOM_NAME = "voice-ai-chat-room"