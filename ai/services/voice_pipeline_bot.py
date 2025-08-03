# ai/services/voice_pipeline_bot.py
import asyncio
import os
import logging
from typing import Optional

# Pipecat Imports
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.transports.services.livekit import LiveKitTransport, LiveKitParams
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.tts import AzureTTSService
from pipecat.transcriptions.language import Language
from livekit import api

# Import your LLM service (no more "enhanced" naming)
from ai.routers import sessions
from pipecatAgent.lm_studio_llm_service import LMStudioLLMService
from ..config import logger

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
BOT_IDENTITY = "ai-voice-assistant"

class VoicePipelineBot:
    def __init__(self):
        self.room_name: Optional[str] = None
        self.runner: Optional[PipelineRunner] = None
        self.task: Optional[PipelineTask] = None
        self._running = False
        logger.info("VoicePipelineBot initialized")

    def _generate_token(self, room_name: str) -> str:
        """Generate LiveKit access token for the bot"""
        access_token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        access_token.with_identity(BOT_IDENTITY).with_name("AI Voice Assistant").with_grants(
            api.VideoGrants(room_join=True, room=room_name)
        )
        return access_token.to_jwt()

    async def connect(self, room_name: str, user_id: int = 1, session_name: str = None): # type: ignore
        """Connect the voice bot to a LiveKit room"""
        if self._running:
            logger.warning("Voice bot is already running")
            return

        self.room_name = room_name
        logger.info(f"Voice bot connecting to room: {room_name}")

        try:
            # Get Azure credentials
            azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
            azure_speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if not azure_speech_key or not azure_speech_region:
                raise ValueError("Azure Speech credentials not configured")

            # Generate token
            token = self._generate_token(room_name)
            
            # Configure transport with VAD
            params = LiveKitParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer()
            )
            
            transport = LiveKitTransport(
                url=LIVEKIT_URL,
                token=token,
                room_name=room_name,
                params=params
            )

            # Configure services
            stt = AzureSTTService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                language=Language.EN_US
            )
            
            # Use your enhanced LLM service with session context
            llm = LMStudioLLMService(
                user_id=1,  # You might want to pass actual user_id from session
                session_name=f"voice-{room_name}-{sessions or 'default'}"
            )
            
            tts = AzureTTSService(
                api_key=azure_speech_key,
                region=azure_speech_region,
                voice="en-US-JennyNeural"
            )

            # Set up conversation context
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant with access to todo management capabilities. Keep responses concise for voice interaction."
                }
            ]
            user_response_aggregator = LLMUserResponseAggregator(messages)
            assistant_response_aggregator = LLMAssistantResponseAggregator(messages)

            # Build the pipeline
            pipeline = Pipeline([
                transport.input(),
                stt,
                user_response_aggregator,
                llm,
                assistant_response_aggregator,
                tts,
                transport.output(),
            ])

            self.task = PipelineTask(pipeline)
            self.runner = PipelineRunner()
            
            # Start the pipeline in background
            self._running = True
            asyncio.create_task(self._run_pipeline())
            
            logger.info(f"Voice bot successfully connected to room: {room_name}")

        except Exception as e:
            logger.error(f"Failed to connect voice bot: {e}", exc_info=True)
            self._running = False
            raise

    async def _run_pipeline(self):
        """Run the pipeline"""
        try:
            if self.runner and self.task:
                await self.runner.run(self.task)
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
        finally:
            self._running = False

    async def disconnect(self):
        """Disconnect the voice bot"""
        if not self._running:
            return

        logger.info("Disconnecting voice bot...")
        self._running = False
        
        if self.runner:
            try:
                await self.runner.cancel()
            except Exception as e:
                logger.error(f"Error canceling runner: {e}")
        
        self.runner = None
        self.task = None
        self.room_name = None
        logger.info("Voice bot disconnected")

    @property
    def is_running(self) -> bool:
        return self._running

# Singleton instance
voice_pipeline_bot = VoicePipelineBot()