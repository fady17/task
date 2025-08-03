# # pipecat-agent/custom_llm_service.py

# import aiohttp
# import json
# from pipecat.frames.frames import TextFrame, LLMMessagesFrame
# # from pipecat.services.ai_services import LLMService
# from pipecat.services.llm_service import LLMService

# # Point to the simple, non-streaming endpoint for now
# API_ENDPOINT = "http://localhost:8000/ai/voice/query"

# class CustomTodoLLMService(LLMService):
#     def __init__(self):
#         super().__init__()
    
#     async def run_llm(self, messages: list[LLMMessagesFrame]):
#         # Your corrected logic for extracting the user prompt is perfect.
#         user_prompt = ""
#         if messages:
#             frame = messages[-1]
#             if frame.messages:
#                 last_message = frame.messages[-1]
#                 if isinstance(last_message, dict) and last_message.get("role") == "user":
#                     user_prompt = last_message.get("content", "")
        
#         if not user_prompt:
#             print("Pipecat Agent: No user prompt found.")
#             return
        
#         print(f"Pipecat Agent: Sending prompt to backend: '{user_prompt}'")
#         payload = {
#             "prompt": user_prompt,
#             "session_id": 1  # Using a hardcoded session ID for now
#         }
        
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(API_ENDPOINT, json=payload) as response:
#                     response.raise_for_status()
#                     result = await response.json()
                    
#                     if result and result.get("content"):
#                         print(f"Pipecat Agent: Received response from backend: '{result['content']}'")
#                         yield TextFrame(result["content"])

#         except aiohttp.ClientError as e:
#             print(f"Error calling backend API: {e}")
#             yield TextFrame("I'm having trouble connecting to my brain. Please try again later.")