# live_bot.py (Final Corrected Architecture)
import asyncio
import os
import sys
from dotenv import load_dotenv

# --- Path Fix ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Pipecat Imports ---
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.transports.services.livekit import LiveKitTransport, LiveKitParams
# FIX: Import the VAD and Aggregators
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.tts import AzureTTSService
from pipecat.transcriptions.language import Language
from lm_studio_llm_service import LMStudioLLMService
from livekit import api

load_dotenv()

# --- Configuration (Unchanged) ---
LIVEKIT_URL = "ws://localhost:7880"
LIVEKIT_API_KEY = "devkey"
LIVEKIT_API_SECRET = "secret"
ROOM_NAME = "ai-chat-room"
BOT_IDENTITY = "ai-voice-bot"

def get_env_var(name: str) -> str:
    var = os.getenv(name)
    if not var:
        print(f"FATAL: Environment variable '{name}' is not set. Exiting.")
        sys.exit(1)
    return var

def generate_token() -> str:
    access_token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    access_token.with_identity(BOT_IDENTITY).with_name("AI Assistant").with_grants(
        api.VideoGrants(room_join=True, room=ROOM_NAME)
    )
    return access_token.to_jwt()


async def main():
    azure_speech_key = get_env_var("AZURE_SPEECH_KEY")
    azure_speech_region = get_env_var("AZURE_SPEECH_REGION")

    token = generate_token()
    
    # The VAD is essential for this architecture to work.
    params = LiveKitParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer()
    )
    
    transport = LiveKitTransport(
        url=LIVEKIT_URL,
        token=token,
        room_name=ROOM_NAME,
        params=params
    )

    stt = AzureSTTService(api_key=azure_speech_key, region=azure_speech_region, language=Language.EN_US)
    llm = LMStudioLLMService()
    tts = AzureTTSService(api_key=azure_speech_key, region=azure_speech_region, voice="en-US-JennyNeural")

    # FIX: Create the shared message list and the aggregators to manage conversation state.
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    user_response_aggregator = LLMUserResponseAggregator(messages)
    assistant_response_aggregator = LLMAssistantResponseAggregator(messages)

    # --- 4. Assemble the Final Voice Pipeline with the CORRECT architecture ---
    pipeline = Pipeline([
        transport.input(),
        stt,
        user_response_aggregator,        # Manages the user's turn
        llm,                             # Our full AI logic adapter
        assistant_response_aggregator,   # Captures the LLM's response for context
        tts,
        transport.output(),
    ])

    task = PipelineTask(pipeline)
    runner = PipelineRunner()

    print("\n--- 🚀 LIVE AI VOICE BOT (Corrected Architecture) ---")
    print(f"Bot is connecting to LiveKit room: '{ROOM_NAME}'...")
    print("\nNext Steps:")
    print("1. Join the call from your React app.")
    print("2. Speak a command. The bot should now respond correctly.")
    print("\nPress Ctrl+C here to stop the bot.")
    print("-" * 35)

    await runner.run(task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutting down.")