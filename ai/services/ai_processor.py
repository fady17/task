# ai/services/ai_processor.py 
import json
import httpx
from typing import AsyncGenerator, Dict, List, Tuple

from .todo_client import TodoAPIClient
from .. import db_utils
from ..config import logger, LM_STUDIO_API_URL, MODEL_NAME, SYSTEM_PROMPT, TOOLS

# --- WORKER FUNCTIONS ---

async def _call_llm(messages: List[Dict]) -> Dict:
    """
    Worker: Prepares the payload and calls the LLM API.

    Args:
        messages: The current list of conversation messages.

    Returns:
        The assistant's message dictionary from the API response.
    """
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "model": MODEL_NAME, "messages": messages, "tools": TOOLS, "tool_choice": "auto",
            "temperature": 0.1, "top_p": 0.9, "repetition_penalty": 1.1, "max_tokens": 8192,
        }
        response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]

async def _execute_function(function_name: str, arguments: dict, todo_api: TodoAPIClient) -> dict:
    """Worker: Executes a single tool function on the TodoAPIClient."""
    try:
        if hasattr(todo_api, function_name):
            method = getattr(todo_api, function_name)
            result = await method(**arguments)
            logger.info(f"Function '{function_name}' succeeded.")
            return {"success": True, "result": result}
        else:
            raise AttributeError(f"Unknown function: {function_name}")
    except Exception as e:
        logger.error(f"Function '{function_name}' failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

async def _handle_tool_calls(
    tool_calls: List[Dict],
    todo_api: TodoAPIClient
) -> Tuple[List[Dict], List[Dict]]:
    """
    Worker: Processes a list of tool calls from the LLM.

    Args:
        tool_calls: The list of tool_calls from the assistant's message.
        todo_api: The client for the todo API.

    Returns:
        A tuple containing:
        - A list of tool result messages to be appended to the conversation.
        - A list of state change events to be yielded to the client.
    """
    tool_result_messages = []
    state_change_events = []

    logger.info(f"Processing {len(tool_calls)} tool calls.")
    for tool_call in tool_calls:
        func_name = tool_call["function"]["name"]
        try:
            func_args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in function args: {tool_call['function']['arguments']}")
            continue

        result = await _execute_function(func_name, func_args, todo_api)

        tool_result_messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": func_name,
            "content": json.dumps(result)
        })

        if result.get("success") and func_name not in ["get_all_todo_lists", "get_todo_list"]:
            state_change_events.append({"type": "state_change", "resource": "todos"})

    return tool_result_messages, state_change_events


async def _generate_title(prompt: str) -> str:
    """Worker: Generates a short title for a new chat session."""
    try:
        title_prompt = f"Create a 2-4 word title for this todo request: '{prompt}'"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{LM_STUDIO_API_URL}/chat/completions",
                json={"model": MODEL_NAME, "messages": [{"role": "user", "content": title_prompt}], "temperature": 0.3, "max_tokens": 15}
            )
            response.raise_for_status()
            title = response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
            return title if title else "New Chat"
    except Exception as e:
        logger.error(f"Title generation failed: {e}")
        return "New Chat"


# --- ORCHESTRATOR FUNCTION ---
async def process_chat_request(prompt: str, session_id: int, todo_api: TodoAPIClient) -> AsyncGenerator[Dict, None]:
    """
    Orchestrator: Manages the conversation flow with the LLM.
    This function implements "Strategic Amnesia" to keep the context clean.
    """
    logger.info(f"Processing chat request for session {session_id}: '{prompt}'")

    # 1. Save the new user message to the database for long-term record keeping.
    await db_utils.save_message(session_id, "user", prompt)

    # --- NEW: RESTORED CHAT NAMING LOGIC ---
    # Check if this is the first user message in the session to generate a title.
    user_count = await db_utils.count_user_messages_in_session(session_id)
    if user_count == 1:
        logger.info(f"First user message in session {session_id}. Generating title.")
        title = await _generate_title(prompt)
        await db_utils.update_session_title(session_id, title)
        # Yield a state change event so the UI updates the session list immediately.
        yield {"type": "state_change", "resource": "sessions"}
    # --- END OF NEW LOGIC ---


    # Always start with the unbreakable rules.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Provide the absolute latest state of the world as context.
    # This is more valuable than old conversation.
    try:
        current_state = await _execute_function("get_all_todo_lists", {}, todo_api)
        context_message = {
            "role": "system",
            "content": f"## Current Database State (as of right now):\n```json\n{json.dumps(current_state['result'], indent=2)}\n```"
        }
        messages.append(context_message)
    except Exception as e:
        logger.error(f"Failed to get initial state for context: {e}")
        # If we can't get the state, we can't proceed reliably.
        yield {"type": "chat_message", "content": f"Critical error: Could not retrieve database state. {e}"}
        return

    # Add ONLY the most recent user request. This is the mission.
    messages.append({"role": "user", "content": prompt})

    # --- END OF STRATEGIC AMNESIA IMPLEMENTATION ---


    # The rest of the loop remains the same, but it now operates on the clean 'messages' list.
    turn_count = 0
    max_turns_safety_limit = 20 # Can be lower now as context is cleaner

    while turn_count < max_turns_safety_limit:
        turn_count += 1
        try:
            logger.info(f"Turn {turn_count}: Calling LLM with a clean, focused context of {len(messages)} messages.")
            assistant_msg = await _call_llm(messages)
            messages.append(assistant_msg)

            if tool_calls := assistant_msg.get("tool_calls"):
                tool_results, state_changes = await _handle_tool_calls(tool_calls, todo_api)
                messages.extend(tool_results)
                for event in state_changes:
                    yield event
                continue

            if content := assistant_msg.get("content"):
                # Save the final assistant response to the DB for the record.
                await db_utils.save_message(session_id, "assistant", content)
                yield {"type": "chat_message", "content": content}

            return

        except Exception as e:
            logger.error(f"Error in chat processing loop: {e}", exc_info=True)
            error_msg = f"I encountered an error: {e}. Please try again."
            await db_utils.save_message(session_id, "assistant", error_msg)
            yield {"type": "chat_message", "content": error_msg}
            return

    timeout_msg = f"Safety limit of {max_turns_safety_limit} turns reached. Please simplify the request."
    await db_utils.save_message(session_id, "assistant", timeout_msg)
    yield {"type": "chat_message", "content": timeout_msg}
# # ai/services/ai_processor.py (Corrected and Final Version)
# import json
# import httpx
# from typing import AsyncGenerator, Dict

# from .todo_client import TodoAPIClient # <<<--- FIX: Import the type for type hinting
# from .. import db_utils
# from ..config import logger, LM_STUDIO_API_URL, MODEL_NAME, SYSTEM_PROMPT, TOOLS

# async def _execute_function(function_name: str, arguments: dict, todo_api: TodoAPIClient) -> dict: # <<<--- FIX 2: Accept todo_api
#     """Dynamically executes a function on the provided TodoAPIClient."""
#     try:
#         logger.info(f"Executing function: {function_name} with args: {arguments}")
#         if hasattr(todo_api, function_name):
#             method = getattr(todo_api, function_name)
#             result = await method(**arguments)
#             logger.info(f"Function {function_name} succeeded: {result}")
#             return {"success": True, "result": result}
#         else:
#             raise AttributeError(f"Unknown function: {function_name}")
#     except Exception as e:
#         error_msg = f"Function {function_name} failed: {str(e)}"
#         logger.error(error_msg, exc_info=True)
#         return {"success": False, "error": error_msg}

# async def _generate_title(prompt: str) -> str:
#     """Generate a short title for the chat session"""
#     try:
#         title_prompt = f"Create a 2-4 word title for this todo request: '{prompt}'"
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.post(
#                 f"{LM_STUDIO_API_URL}/chat/completions",
#                 json={"model": MODEL_NAME, "messages": [{"role": "user", "content": title_prompt}], "temperature": 0.3, "max_tokens": 15}
#             )
#             response.raise_for_status()
#             title = response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
#             return title if title else "New Chat"
#     except Exception as e:
#         logger.error(f"Title generation failed: {e}")
#         return "New Chat"

# # <<<--- FIX 1: The service now accepts the dependency it needs ---<<<
# async def process_chat_request(prompt: str, session_id: int, todo_api: TodoAPIClient) -> AsyncGenerator[Dict, None]:
#     """Processes a chat request, yielding dictionaries for network transmission."""
#     logger.info(f"Processing chat request for session {session_id}: {prompt}")

#     await db_utils.save_message(session_id, "user", prompt)

#     user_count = await db_utils.count_user_messages_in_session(session_id)
#     if user_count == 1:
#         title = await _generate_title(prompt)
#         await db_utils.update_session_title(session_id, title)
#         yield {"type": "state_change", "resource": "sessions"}

#     history = await db_utils.fetch_session_messages(session_id)
#     messages = [{"role": record["role"], "content": record["content"]} for record in history]
#     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
#     messages.append({"role": "user", "content": prompt})

#     turn_count = 0
#     max_turns_safety_limit = 20 # Keep this as a safety net

#     while turn_count < max_turns_safety_limit:
#         turn_count += 1
#         try:
#             logger.info(f"Turn {turn_count}: Calling LLM with {len(messages)} messages.")
#             async with httpx.AsyncClient(timeout=90.0) as client:
#                 payload = {
#                     "model": MODEL_NAME, "messages": messages, "tools": TOOLS, "tool_choice": "auto",
#                     "temperature": 0.1, "top_p": 0.9, "repetition_penalty": 1.1, "max_tokens": 8192,
#                 }
#                 response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=payload)
#                 response.raise_for_status()
#                 data = response.json()
#                 assistant_msg = data["choices"][0]["message"]
#                 messages.append(assistant_msg)

#                 if assistant_msg.get("tool_calls"):
#                     logger.info(f"Processing {len(assistant_msg['tool_calls'])} tool calls")
#                     for tool_call in assistant_msg["tool_calls"]:
#                         func_name = tool_call["function"]["name"]
#                         try:
#                             func_args = json.loads(tool_call["function"]["arguments"])
#                         except json.JSONDecodeError:
#                             logger.error(f"Invalid JSON in function args: {tool_call['function']['arguments']}")
#                             continue

#                         # <<<--- FIX 3: Pass the received dependency to the helper ---<<<
#                         result = await _execute_function(func_name, func_args, todo_api)

#                         messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": func_name, "content": json.dumps(result)})
#                         if result.get("success") and func_name != "get_all_todo_lists":
#                             yield {"type": "state_change", "resource": "todos"}
#                     continue # Loop back to let the LLM react to the tool results

#                 if content := assistant_msg.get("content"):
#                     await db_utils.save_message(session_id, "assistant", content)
#                     yield {"type": "chat_message", "content": content}
#                 return # End the process once the LLM gives a final text response

#         except Exception as e:
#             logger.error(f"Error in chat processing: {e}", exc_info=True)
#             error_msg = f"I encountered an error: {str(e)}. Please try again."
#             await db_utils.save_message(session_id, "assistant", error_msg)
#             yield {"type": "chat_message", "content": error_msg}
#             return

#     timeout_msg = f"Safety limit of {max_turns_safety_limit} turns reached. Please simplify the request."
#     await db_utils.save_message(session_id, "assistant", timeout_msg)
#     yield {"type": "chat_message", "content": timeout_msg}
# # # ai/services/ai_processor.py
# # """
# # Core AI processing logic. Handles chat requests, function execution, and interaction
# # with the language model, but is completely independent of FastAPI.
# # """
# # import json
# # import httpx
# # import re
# # from typing import Any

# # from .todo_client import TodoAPIClient
# # from ..config import logger, LM_STUDIO_API_URL, MODEL_NAME, SYSTEM_PROMPT, TOOLS
# # from .. import db_utils

# # def _safe_send_channel(channel: Any, message: str):
# #     """Safely send a message through a WebRTC data channel."""
# #     try:
# #         if channel and hasattr(channel, 'readyState') and channel.readyState == "open":
# #             channel.send(message)
# #         else:
# #             logger.warning("Data channel is not open or available. Cannot send message.")
# #     except Exception as e:
# #         logger.error(f"Failed to send message via data channel: {e}")

# # async def _execute_function(function_name: str, arguments: dict, todo_api: TodoAPIClient) -> dict:
# #     """Execute a tool function and return the result."""
# #     try:
# #         logger.info(f"Executing function: {function_name} with args: {arguments}")
# #         if hasattr(todo_api, function_name):
# #             method = getattr(todo_api, function_name)
# #             result = await method(**arguments)
# #             logger.info(f"Function {function_name} succeeded: {result}")
# #             return {"success": True, "result": result}
# #         else:
# #             error_msg = f"Unknown function: {function_name}"
# #             logger.error(error_msg)
# #             return {"success": False, "error": error_msg}
# #     except Exception as e:
# #         error_msg = f"Function {function_name} failed: {str(e)}"
# #         logger.error(error_msg, exc_info=True)
# #         return {"success": False, "error": str(e)}

# # async def _generate_title(prompt: str) -> str:
# #     """Generate a short title for the chat session using the language model."""
# #     try:
# #         title_prompt = f"Create a 2-4 word title for this todo request: '{prompt}'"
# #         async with httpx.AsyncClient(timeout=15.0) as client:
# #             response = await client.post(
# #                 f"{LM_STUDIO_API_URL}/chat/completions",
# #                 json={
# #                     "model": MODEL_NAME,
# #                     "messages": [{"role": "user", "content": title_prompt}],
# #                     "temperature": 0.3, "max_tokens": 15
# #                 }
# #             )
# #             response.raise_for_status()
# #             title = response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
# #             return title if title else "New Chat"
# #     except Exception as e:
# #         logger.error(f"Title generation failed: {e}")
# #         return "New Chat"

# # async def process_chat_request(prompt: str, session_id: int, channel: Any, todo_api: TodoAPIClient):
# #     """Main logic to process a chat request, interact with the AI, and call tools."""
# #     logger.info(f"Processing chat request for session {session_id}: {prompt}")
# #     await db_utils.save_message(session_id, "user", prompt)

# #     user_count = await db_utils.count_user_messages_in_session(session_id)
# #     if user_count == 1:
# #         title = await _generate_title(prompt)
# #         await db_utils.update_session_title(session_id, title)
# #         _safe_send_channel(channel, json.dumps({"type": "state_change", "resource": "sessions"}))

# #     history = await db_utils.fetch_session_messages(session_id)
# #     messages = [{"role": record["role"], "content": record["content"]} for record in history]
# #     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
# #     messages.append({"role": "user", "content": prompt})

# #     # TODO: Replac the fixed `for` loop with a `while` loop to allow the agent
# #     # to take as many turns as its logic requires. The `max_turns` variable now
# #     # acts as a safety break to prevent infinite loops, not as a hard limit on AI reasoning.
    
# #     # max_turns = 10
  
# #     turn_count = 0
# #     max_turns_safety_limit = 20 
# #     while turn_count < max_turns_safety_limit:
# #         turn_count += 1
# #     # for turn in range(max_turns):
# #         try:
# #             # logger.info(f"Turn {turn + 1}: Calling LM Studio with {len(messages)} messages.")
# #             logger.info(f"Turn {turn_count}: Calling LM Studio")

# #             async with httpx.AsyncClient(timeout=90.0) as client:
# #                 payload = {
# #                     "model": MODEL_NAME, "messages": messages,
# #                     "tools": TOOLS, "tool_choice": "auto",
# #                     "temperature": 0.1, "max_tokens": 15000
# #                 }
# #                 response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=payload)
# #                 response.raise_for_status()
# #                 data = response.json()
# #                 assistant_msg = data["choices"][0]["message"]
# #                 messages.append(assistant_msg)

# #                 if assistant_msg.get("tool_calls"):
# #                     logger.info(f"Processing {len(assistant_msg['tool_calls'])} tool calls.")
# #                     for tool_call in assistant_msg["tool_calls"]:
# #                         func_name = tool_call["function"]["name"]
# #                         try:
# #                             func_args = json.loads(tool_call["function"]["arguments"])
# #                         except json.JSONDecodeError:
# #                             logger.error(f"Invalid JSON in function args: {tool_call['function']['arguments']}")
# #                             continue

# #                         result = await _execute_function(func_name, func_args, todo_api)
# #                         messages.append({
# #                             "role": "tool", "tool_call_id": tool_call["id"],
# #                             "name": func_name, "content": json.dumps(result)
# #                         })
# #                         if result.get("success") and func_name != "get_all_todo_lists":
# #                             _safe_send_channel(channel, json.dumps({"type": "state_change", "resource": "todos"}))
# #                     continue

# #                 if content := assistant_msg.get("content"):
# #                     await db_utils.save_message(session_id, "assistant", content)
# #                     _safe_send_channel(channel, json.dumps({"type": "chat_message", "content": content}))
# #                 return

# #         except Exception as e:
# #             logger.error(f"Error in chat processing loop: {e}", exc_info=True)
# #             error_msg = f"I encountered an error: {str(e)}. Please try again."
# #             await db_utils.save_message(session_id, "assistant", error_msg)
# #             _safe_send_channel(channel, json.dumps({"type": "chat_message", "content": error_msg}))
# #             return

# #     timeout_msg = "This is taking too many steps. Please try a simpler request."
# #     await db_utils.save_message(session_id, "assistant", timeout_msg)
# #     _safe_send_channel(channel, json.dumps({"type": "chat_message", "content": timeout_msg}))