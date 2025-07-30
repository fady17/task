# import asyncio
# import os
# from dotenv import load_dotenv

# from pipecat.frames.frames import EndFrame
# from pipecat.pipeline.pipeline import Pipeline
# from pipecat.pipeline.runner import PipelineRunner
# from pipecat.pipeline.task import PipelineTask
# from pipecat.processors.aggregators.llm_response import LLMUserResponseAggregator
# from pipecat.services.ai_services import OpenAILLMService
# from pipecat.transports.services.livekit import LiveKitParams, LiveKitSource, LiveKitSink
# from pipecat.services.vad.silero import SileroVADService
# from pipecat.services.stt.deepgram import DeepgramSTTService
# from pipecat.services.tts.deepgram import DeepgramTTSService

# # This is a placeholder for now. You will need a Deepgram API key.
# # Add DEEPGRAM_API_KEY="your_key" to your .env file
# load_dotenv()

# # The room the bot will join. This must match the frontend.
# LIVEKIT_ROOM = "ai-voice-room"
# BOT_IDENTITY = "ai-voice-bot"

# async def main():
#     livekit_source = LiveKitSource(
#         url=os.getenv("LIVEKIT_URL"),
#         token=LiveKitParams.access_token(
#             api_key=os.getenv("LIVEKIT_API_KEY"),
#             api_secret=os.getenv("LIVEKIT_API_SECRET"),
#             room_name=LIVEKIT_ROOM,
#             participant_identity=BOT_IDENTITY,
#         ),
#     )

#     livekit_sink = LiveKitSink(
#         url=os.getenv("LIVEKIT_URL"),
#         token=LiveKitParams.access_token(
#             api_key=os.getenv("LIVEKIT_API_KEY"),
#             api_secret=os.getenv("LIVEKIT_API_SECRET"),
#             room_name=LIVEKIT_ROOM,
#             participant_identity=BOT_IDENTITY,
#         ),
#     )

#     # For this simple echo bot, we don't need the LLM yet.
#     # We will just use STT and TTS.
#     stt = DeepgramSTTService()
#     tts = DeepgramTTSService()

#     pipeline = Pipeline([
#         livekit_source,
#         SileroVADService(), # Voice Activity Detection
#         stt,
#         # In the future, the LLM will go here. For now, the STT output
#         # (TranscriptionFrame) will pass directly to the TTS input.
#         tts,
#         livekit_sink,
#     ])

#     task = PipelineTask(pipeline)

#     @livekit_source.on("participant_joined")
#     async def on_join(room, participant):
#         print(f"Participant joined: {participant.identity}")

#     @livekit_source.on("participant_left")
#     async def on_leave(room, participant):
#         print(f"Participant left: {participant.identity}")
#         # If the last user leaves, shut down the pipeline
#         if len(room.participants) == 0:
#             print("Last participant left, shutting down.")
#             await task.stop_when_done()

#     print("Starting Pipecat agent...")
#     runner = PipelineRunner()
#     await runner.run(task)
#     print("Pipecat agent stopped.")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Interrupted, shutting down.")