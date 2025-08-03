# ai/services/lm_studio_llm_service.py
import logging
import os
import sys
from typing import AsyncGenerator, List, Dict, Optional
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Pipecat Imports
from pipecat.frames.frames import Frame, LLMFullResponseStartFrame, TextFrame, LLMFullResponseEndFrame, LLMMessagesFrame, ErrorFrame
from pipecat.services.llm_service import LLMService
from pipecat.processors.frame_processor import FrameDirection

# Import your existing AI logic
from ai.services.ai_processor import process_chat_request
from ai.dependencies import get_todo_api_client
from ai import db_utils

logger = logging.getLogger("pipecat.lmstudio")

class LMStudioLLMService(LLMService):
    def __init__(self, user_id: int = 1, session_name: str = None): # type: ignore
        super().__init__()
        self.user_id = user_id
        self.session_name = session_name or f"voice-session-{user_id}"
        self.session_id: Optional[int] = None
        self.todo_api_client = get_todo_api_client()
        logger.info(f"Initialized LM Studio service for user {user_id}, session: {self.session_name}")

    async def _ensure_session(self):
        """Create a database session if it doesn't exist"""
        if self.session_id is None:
            try:
                session_record = await db_utils.create_new_session(self.user_id)
                self.session_id = session_record['id']
                # Update the session title to reflect it's a voice session
                await db_utils.update_session_title(self.session_id, f"Voice Chat - {self.session_name}") # type: ignore
                logger.info(f"Created new voice session with ID: {self.session_id}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                # Fallback: use a dummy session ID for testing
                self.session_id = 1

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, LLMMessagesFrame):
            messages: List[Dict] = frame.messages
            # Extract the last user message for processing
            user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if user_message:
                # Ensure we have a valid session before processing
                await self._ensure_session()
                self.create_task(self._run_llm_task(user_message))
        else:
            await self.push_frame(frame, direction)

    async def _run_llm_task(self, user_prompt: str):
        async for yielded_frame in self.run_llm(user_prompt):
            await self.push_frame(yielded_frame)

    async def run_llm(self, user_prompt: str) -> AsyncGenerator[Frame, None]:
        yield LLMFullResponseStartFrame()
        
        logger.info(f"Processing voice input: {user_prompt[:100]}...")

        try:
            # Ensure we have a valid session ID
            if self.session_id is None:
                await self._ensure_session()

            # Use your existing AI processor directly - no wrapper needed!
            async for response_chunk in process_chat_request(
                prompt=user_prompt,
                session_id=self.session_id, # type: ignore
                todo_api=self.todo_api_client
            ):
                if response_chunk.get("type") == "chat_message":
                    content = response_chunk.get("content", "")
                    if content:
                        # Stream the content as it comes
                        yield TextFrame(content)
                elif response_chunk.get("type") == "state_change":
                    # Handle state changes if needed (like session updates)
                    logger.info(f"State change: {response_chunk.get('resource')}")
                elif response_chunk.get("type") == "error":
                    error_msg = response_chunk.get("content", "Unknown error")
                    logger.error(f"AI processing error: {error_msg}")
                    yield ErrorFrame(error_msg)
                    return

            logger.info("Voice response completed")

        except Exception as e:
            error_text = f"Error in AI processing: {e}"
            logger.error(error_text, exc_info=True)
            yield ErrorFrame(error_text)
        finally:
            yield LLMFullResponseEndFrame()
# # lm_studio_llm_service.py 
# import aiohttp
# import logging
# import os
# from typing import AsyncGenerator, List, Dict

# # Pipecat Imports
# from pipecat.frames.frames import Frame, LLMFullResponseStartFrame, TextFrame, LLMFullResponseEndFrame, LLMMessagesFrame, ErrorFrame
# from pipecat.services.llm_service import LLMService
# from pipecat.processors.frame_processor import FrameDirection

# logger = logging.getLogger("pipecat.lmstudio")

# class LMStudioLLMService(LLMService):
#     def __init__(self):
#         super().__init__()
#         self.api_url = os.getenv("LM_STUDIO_API_URL", "http://127.0.0.1:1234/v1")
#         logger.info(f"Initialized MINIMAL LM Studio service. URL: {self.api_url}")

#     async def process_frame(self, frame: Frame, direction: FrameDirection):
#         await super().process_frame(frame, direction)
#         if isinstance(frame, LLMMessagesFrame):
#             messages: List[Dict] = frame.messages
#             self.create_task(self._run_llm_generator_task(messages))
#         else:
#             await self.push_frame(frame, direction)

#     async def _run_llm_generator_task(self, messages: List[Dict]):
#         async for yielded_frame in self.run_llm(messages):
#             await self.push_frame(yielded_frame)

#     async def run_llm(self, messages: List[Dict]) -> AsyncGenerator[Frame, None]:
#         yield LLMFullResponseStartFrame()
        
#         logger.info(f"🤖 Calling LM Studio with {len(messages)} messages...")

#         # FIX: Remove the 'model' parameter. Let LM Studio use the model loaded in the UI.
#         payload = {
#             "messages": messages, 
#             "temperature": 0.7,
#             "stream": False,
#         }

#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(f"{self.api_url}/chat/completions", json=payload, timeout=30) as response:
#                     response.raise_for_status()
#                     result = await response.json()
                    
#                     content = result["choices"][0]["message"]["content"]
#                     logger.info(f"🤖 AI responds: {content[:100]}...")
#                     yield TextFrame(content.strip())

#         except Exception as e:
#             error_text = f"Error communicating with LM Studio: {e}"
#             logger.error(error_text, exc_info=True)
#             # FIX: Yield a proper ErrorFrame to signal failure.
#             yield ErrorFrame(error_text)
#         finally:
#             yield LLMFullResponseEndFrame()