# # pipecat-agent/main.py

# import asyncio
# import os
# import sys
# import logging
# from dotenv import load_dotenv

# # Pipecat core components
# from pipecat.pipeline.pipeline import Pipeline
# from pipecat.pipeline.runner import PipelineRunner
# from pipecat.pipeline.task import PipelineTask
# from pipecat.processors.aggregators.llm_response import LLMUserResponseAggregator # <-- The missing piece

# # The correct, top-level transport class and its parameters
# from pipecat.transports.services.livekit import LiveKitTransport, LiveKitParams

# # The correct VAD analyzer class
# from pipecat.audio.vad.silero import SileroVADAnalyzer

# # Cloud AI services for STT and TTS
# # from pipecat.services.azure import AzureSTTService, AzureTTSService
# from pipecat.services.azure.stt import AzureSTTService
# from pipecat.services.azure.tts import AzureTTSService
# from pipecat.transcriptions.language import Language

# # Our custom service that connects to our local FastAPI backend
# from llm_service import CustomTodoLLMService

# load_dotenv()
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("pipecat-agent")

# # --- Constants ---
# LIVEKIT_ROOM = "ai-voice-room"
# BOT_IDENTITY = "ai-voice-bot"

# def get_env_var(name: str) -> str:
#     var = os.getenv(name)
#     if not var:
#         logger.error(f"FATAL: Environment variable '{name}' is not set. Exiting.")
#         sys.exit(1)
#     return var

# async def main():
#     # --- 1. Load Environment Variables ---
#     livekit_url = get_env_var("LIVEKIT_URL")
#     livekit_api_key = get_env_var("LIVEKIT_API_KEY")
#     livekit_api_secret = get_env_var("LIVEKIT_API_SECRET")
#     azure_speech_key = get_env_var("AZURE_SPEECH_KEY")
#     azure_speech_region = get_env_var("AZURE_SPEECH_REGION")

#     # --- 2. Configure the LiveKit Transport with VAD ---
#     from livekit import api
#     token = api.AccessToken(livekit_api_key, livekit_api_secret) \
#         .with_identity(BOT_IDENTITY) \
#         .with_name("AI Voice Assistant") \
#         .with_grants(api.VideoGrants(room_join=True, room=LIVEKIT_ROOM)) \
#         .to_jwt()

#     livekit_params = LiveKitParams(vad_analyzer=SileroVADAnalyzer())
#     transport = LiveKitTransport(url=livekit_url, token=token, room_name=LIVEKIT_ROOM, params=livekit_params)

#     # --- 3. Configure AI Services ---
#     stt = AzureSTTService(api_key=azure_speech_key, region=azure_speech_region, language=Language.AR_SA)
#     tts = AzureTTSService(api_key=azure_speech_key, region=azure_speech_region, voice_name="ar-SA-HamedNeural")
#     llm = CustomTodoLLMService()
    
#     # --- THIS IS THE KEY FIX ---
#     # The LLMUserResponseAggregator aggregates user transcriptions and prepares them for the LLM.
#     user_aggregator = LLMUserResponseAggregator()

#     # --- 4. Assemble the Pipeline CORRECTLY ---
#     pipeline = Pipeline([
#         transport.input(),
#         stt,
#         user_aggregator, # Aggregates STT frames into a message for the LLM
#         llm,             # Our custom service now receives the correct frame type
#         tts,
#         transport.output(),
#     ])

#     task = PipelineTask(pipeline)

#     # --- 5. Define and Register Event Handlers CORRECTLY ---
#     async def on_join_async(transport, participant_id: str):
#         logger.info(f"Participant joined: {participant_id}")
#         async for frame in tts.run_tts("أهلاً بك، كيف يمكنني المساعدة اليوم؟"):
#             await transport.output().push_frame(frame)

#     async def on_leave_async(transport, participant_id: str, reason: str):
#         logger.info(f"Participant left: {participant_id}")
#         if len(transport.get_participants()) == 0:
#             logger.info("Last participant left, shutting down.")
#             await task.stop_when_done()

#     # Use the public `add_event_handler` method to register the callbacks.
#     transport.add_event_handler("on_participant_joined", on_join_async)
#     transport.add_event_handler("on_participant_left", on_leave_async)
    
#     # --- 6. Run the Pipeline ---
#     logger.info("Starting Pipecat agent...")
#     runner = PipelineRunner()
#     await runner.run(task)
#     logger.info("Pipecat agent stopped.")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Interrupted by user, shutting down.")