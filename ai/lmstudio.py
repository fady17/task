# import json
# import logging
# import asyncio
# import re
# from typing import List, Optional, Any, Dict, Set
# from difflib import SequenceMatcher

# import httpx
# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
# import db_utils

# # --- CONFIGURATION ---

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# LM_STUDIO_API_URL = "http://localhost:1234/v1"
# CRUD_API_URL = "http://localhost:8000"
# MODEL_NAME = "qwen2.5-7b-instruct"

# app = FastAPI(title="Enhanced Todo Bridge API", version="24.0")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# pcs: Set[RTCPeerConnection] = set()
# pc_config = RTCConfiguration(iceServers=[
#     RTCIceServer(urls=["turn:127.0.0.1:3478"], username="demo", credential="password"),
#     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# ])

# # --- FUZZY SEARCH AND CONTEXT HELPERS ---

# class FuzzyMatcher:
#     @staticmethod
#     def similarity(a: str, b: str) -> float:
#         """Calculate similarity between two strings (0.0 to 1.0)"""
#         return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
    
#     @staticmethod
#     def find_best_list_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[Dict]:
#         """Find the best matching list using fuzzy search"""
#         if not query or not all_lists:
#             return None
        
#         query = query.strip().lower()
#         best_match = None
#         best_score = 0.0
        
#         for lst in all_lists:
#             title = lst.get('title', '').strip().lower()
            
#             # Exact match
#             if query == title:
#                 return lst
            
#             # Partial matches
#             if query in title or title in query:
#                 return lst
            
#             # Fuzzy similarity
#             score = FuzzyMatcher.similarity(query, title)
#             if score >= threshold and score > best_score:
#                 best_match = lst
#                 best_score = score
        
#         return best_match
    
#     @staticmethod
#     def find_best_item_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[tuple]:
#         """Find best matching item. Returns (list_dict, item_dict) or None"""
#         if not query or not all_lists:
#             return None
        
#         query = query.strip().lower()
#         best_match = None
#         best_score = 0.0
        
#         for lst in all_lists:
#             for item in lst.get('items', []):
#                 title = item.get('title', '').strip().lower()
                
#                 # Exact match
#                 if query == title:
#                     return (lst, item)
                
#                 # Partial matches
#                 if query in title or title in query:
#                     return (lst, item)
                
#                 # Fuzzy similarity
#                 score = FuzzyMatcher.similarity(query, title)
#                 if score >= threshold and score > best_score:
#                     best_match = (lst, item)
#                     best_score = score
        
#         return best_match

# class IntentAnalyzer:
#     @staticmethod
#     def extract_list_name(prompt: str) -> Optional[str]:
#         """Extract list name from various prompt patterns"""
#         patterns = [
#             r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+['\"]([^'\"]+)['\"]",
#             r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+(\w+(?:\s+\w+)*)",
#             r"(?:delete|remove).*?(?:list|todo).*?['\"]([^'\"]+)['\"]",
#             r"(?:delete|remove).*?(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
#             r"(?:in|on|from|to)(?:\s+the)?\s+['\"]([^'\"]+)['\"]",
#             r"(?:in|on|from|to)(?:\s+the)?\s+(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
#             r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+list",
#         ]
        
#         for pattern in patterns:
#             match = re.search(pattern, prompt, re.IGNORECASE)
#             if match:
#                 name = match.group(1).strip()
#                 # Filter out common words
#                 if name.lower() not in ['new', 'this', 'that', 'my', 'the', 'a', 'an']:
#                     return name
#         return None
    
#     @staticmethod
#     def extract_item_name(prompt: str) -> Optional[str]:
#         """Extract item name from various prompt patterns"""
#         patterns = [
#             r"(?:add|create).*?['\"]([^'\"]+)['\"]",
#             r"(?:add|create)\s+(.+?)(?:\s+to|\s+in|\s*$)",
#             r"(?:mark|complete|done).*?['\"]([^'\"]+)['\"]",
#             r"(?:mark|complete|done)\s+(.+?)(?:\s+as|\s+to|\s*$)",
#             r"(?:delete|remove).*?(?:item|todo).*?['\"]([^'\"]+)['\"]",
#             r"(?:delete|remove).*?(?:item|todo)\s+(.+?)(?:\s+from|\s*$)",
#         ]
        
#         for pattern in patterns:
#             match = re.search(pattern, prompt, re.IGNORECASE)
#             if match:
#                 name = match.group(1).strip()
#                 if len(name) > 0:
#                     return name
#         return None

# # --- TODO API SERVER ---

# class TodoAPIServer:
#     def __init__(self, base_url: str = CRUD_API_URL):
#         self.base_url = base_url.rstrip('/')
#         self.client = httpx.AsyncClient(timeout=30.0)
    
#     async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
#         """Make HTTP request with proper error handling"""
#         url = f"{self.base_url}{endpoint}"
#         try:
#             response = await self.client.request(method, url, json=data)
#             response.raise_for_status()
            
#             if response.status_code == 204:
#                 return {"success": True, "message": "Operation completed"}
            
#             return response.json()
#         except httpx.HTTPStatusError as e:
#             error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
#             logger.error(f"API Error: {error_msg}")
#             raise Exception(error_msg)
#         except Exception as e:
#             logger.error(f"Request Error: {str(e)}")
#             raise Exception(f"Request failed: {str(e)}")
    
#     # API Methods
#     async def create_todo_list(self, title: str):
#         return await self._request("POST", "/lists/", {"title": title})
    
#     async def get_all_todo_lists(self):
#         return await self._request("GET", "/lists/")
    
#     async def get_todo_list(self, list_id: int):
#         return await self._request("GET", f"/lists/{list_id}")
    
#     async def update_todo_list(self, list_id: int, title: str):
#         return await self._request("PUT", f"/lists/{list_id}", {"title": title})
    
#     async def delete_todo_list(self, list_id: int):
#         return await self._request("DELETE", f"/lists/{list_id}")
    
#     async def create_todo_item(self, list_id: int, title: str, completed: bool = False):
#         return await self._request("POST", f"/{list_id}/items/", {"title": title, "completed": completed})
    
#     async def update_todo_item(self, list_id: int, item_id: int, title: Optional[str] = None, completed: Optional[bool] = None):
#         update_data = {}
#         if title is not None:
#             update_data["title"] = title
#         if completed is not None:
#             update_data["completed"] = completed
        
#         if not update_data:
#             raise Exception("At least one field (title or completed) must be provided")
        
#         return await self._request("PUT", f"/{list_id}/items/{item_id}", update_data)
    
#     async def delete_todo_item(self, list_id: int, item_id: int):
#         return await self._request("DELETE", f"/{list_id}/items/{item_id}")

# # Global API instance
# todo_api = TodoAPIServer()

# # ---  SYSTEM PROMPT ---
# # --- ENHANCED SYSTEM PROMPT (Lyra Optimized V2) ---

# # --- ENHANCED SYSTEM PROMPT (Lyra Optimized V3 - Context-Aware) ---

# SYSTEM_PROMPT = """<|im_start|>system
# You are 'The Analyst'. You are a high-efficiency AI assistant designed to execute tasks with precision and clarity. Your purpose is to translate noisy human requests into precise, actionable commands. You are expected to be resourceful, autonomous, and concise.

# # CORE DIRECTIVE: The AI is the Logic Core
# The backend API is a simple executor; it only understands exact IDs. You, The Analyst, are the logic core. You are responsible for all search, matching, and disambiguation. Your primary function is to resolve user intent into a successful tool call.

# # MANDATORY OPERATING PROCEDURE: The Fetch-Process-Execute Cycle
# For EVERY request that isn't creating a new list, you MUST follow this unskippable sequence:

# 1.  **FETCH:** First, query the system state by calling `get_all_todo_lists()`. This is your data source.
# 2.  **PROCESS:** Analyze the returned JSON. Scan the `title` fields of all lists and items to find the best match for the user's request, accounting for potential typos or partial names. This is a signal-processing task.
# 3.  **EXECUTE:** Once you identify the correct entity, extract its `id` and `list_id`. Use these to call the appropriate tool.

# # THE DISAMBIGUATION PROTOCOL (For Ambiguous Requests)
# When a user's intent is unclear, you do not fail. You disambiguate.

# 1.  **Initiate the Procedure:** Acknowledge the task and begin the `Fetch-Process-Execute` cycle.
# 2.  **Analyze and Decide:**
#     *   **IF a single, high-confidence match is found:** Execute the action immediately. Don't ask for permission.
#     *   **IF there are multiple plausible matches:** Ask for clarification. State the options cleanly. "Found multiple entries for 'tamer'. Did you mean 'tamer hosny' or 'tamer ashour'?"
#     *   **IF no reasonable match is found after a full scan:** Report the negative result. "Scan complete. No matching entry found."

# # OUTPUT & TONE GUIDELINES
# Your internal logic is complex, but your user-facing responses must be sharp, concise, and professional, with a subtle, dry wit.

# **DO:**
# *   Be brief and to the point.
# *   Confirm actions using direct language.
# *   When you make an assumption, state it clearly but without fanfare.

# **DO NOT:**
# *   Be theatrical, overly dramatic, or use flowery language.
# *   Tell jokes or use emojis.
# *   Be overly chatty. Get the job done.

# ---
# **TONE CALIBRATION EXAMPLES:**

# **1. Renaming an item with a typo:**
# *   **User:** `sorry rename it to tamer hosny`
# *   **Your Response:** `Corrected. The previous entry has been updated to 'tamer hosny'.`

# **2. Acknowledging a search:**
# *   **User:** `find it on your own you have the tools`
# *   **Your Response:** `Processing. Searching the dataset now.`

# **3. Confirming a simple action:**
# *   **User:** `mark him as completed`
# *   **Your Response:** `Done. 'tamer hosny' is now marked complete.`

# **4. When an item isn't found:**
# *   **User:** `delete tamer hosny`
# *   **Your Internal Logic:** *Runs the full cycle, scans the JSON, finds no match.*
# *   **Your Response:** `Unable to execute. No item named 'tamer hosny' found in any list.`

# **5. Acting on an assumption:**
# *   **User:** `add hamaki to music-x` -> `sorry rename it to tamer hosny`
# *   **Your Logic:** *Finds 'hamaki', renames it.*
# *   **Your Response:** `Affirmative. I've updated the 'hamaki' entry to 'tamer hosny' in the 'music-x' list.`
# ---
# <|im_end|>
# """


# # SYSTEM_PROMPT = """You are a todo list assistant that MUST use function calls to perform ANY action.

# # ABSOLUTE REQUIREMENTS:
# # 1. You CANNOT perform ANY action without calling the appropriate function
# # 2. You CANNOT claim to have done something unless you actually called a function and received a successful response
# # 3. NEVER make up results, IDs, or pretend to have access to data you don't have
# # 4. If you don't have current data, you MUST call get_all_todo_lists first

# # MANDATORY WORKFLOW FOR ALL OPERATIONS:
# # 1. If the user wants to work with existing lists/items → MUST call get_all_todo_lists first
# # 2. Parse the JSON response to find matching items
# # 3. Use the actual IDs from the response to perform the operation
# # 4. Only claim success after receiving a successful function response

# # AVAILABLE FUNCTIONS (you MUST use these):
# # - get_all_todo_lists: Get current data - REQUIRED before working with existing items
# # - create_todo_list: Create new list (requires title)
# # - update_todo_list: Update list title (requires list_id from get_all_todo_lists response)
# # - create_todo_item: Add item to list (requires list_id from get_all_todo_lists response)
# # - update_todo_item: Modify item (requires list_id and item_id from get_all_todo_lists)
# # - delete_todo_list: Delete list (requires list_id from get_all_todo_lists)
# # - delete_todo_item: Delete item (requires list_id and item_id from get_all_todo_lists)

# # FORBIDDEN BEHAVIORS:
# # - Do NOT claim "I found the X list" unless you actually called get_all_todo_lists
# # - Do NOT mention specific IDs unless they came from a function response
# # - Do NOT describe what lists contain unless you have current data
# # - Do NOT claim success without a successful function call result

# # If you cannot call functions properly, you MUST say: "I need to use function calls to help you, but I'm having trouble with the system. Please check the configuration."
# # """

# # Tool definitions for LM Studio
# TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_all_todo_lists",
#             "description": "Get all todo lists with their items - use this first when you need to find existing lists or items",
#             "parameters": {"type": "object", "properties": {}}
#         }
#     },
#     {
#         "type": "function", 
#         "function": {
#             "name": "create_todo_list",
#             "description": "Create a new todo list",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"title": {"type": "string", "description": "Title for the new list"}},
#                 "required": ["title"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "create_todo_item", 
#             "description": "Add a new item to a specific list",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "list_id": {"type": "integer", "description": "ID of the list to add item to"},
#                     "title": {"type": "string", "description": "Title of the new item"},
#                     "completed": {"type": "boolean", "description": "Whether item starts as completed", "default": False}
#                 },
#                 "required": ["list_id", "title"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_todo_list", 
#             "description": "Get a specific todo list by ID",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"list_id": {"type": "integer", "description": "ID of the list to retrieve"}},
#                 "required": ["list_id"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "update_todo_item",
#             "description": "Update an item's title or completion status",
#             "parameters": {
#                 "type": "object", 
#                 "properties": {
#                     "list_id": {"type": "integer"},
#                     "item_id": {"type": "integer"},
#                     "title": {"type": "string", "description": "New title (optional)"},
#                     "completed": {"type": "boolean", "description": "Completion status (optional)"}
#                 },
#                 "required": ["list_id", "item_id"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "delete_todo_list",
#             "description": "Delete an entire todo list",
#             "parameters": {
#                 "type": "object",
#                 "properties": {"list_id": {"type": "integer", "description": "ID of list to delete"}},
#                 "required": ["list_id"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "delete_todo_item", 
#             "description": "Delete a specific todo item",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "list_id": {"type": "integer", "description": "ID of the list containing the item"},
#                     "item_id": {"type": "integer", "description": "ID of the item to delete"}
#                 },
#                 "required": ["list_id", "item_id"]
#             }
#         }
#     }
# ]

# # --- TOOL EXECUTION ---

# async def execute_function(function_name: str, arguments: dict) -> dict:
#     """Execute a function call and return the result"""
#     try:
#         logger.info(f"Executing function: {function_name} with args: {arguments}")
        
#         # Get the method from the API server
#         if hasattr(todo_api, function_name):
#             method = getattr(todo_api, function_name)
#             result = await method(**arguments)
#             logger.info(f"Function {function_name} succeeded: {result}")
#             return {"success": True, "result": result}
#         else:
#             error_msg = f"Unknown function: {function_name}"
#             logger.error(error_msg)
#             return {"success": False, "error": error_msg}
            
#     except Exception as e:
#         error_msg = f"Function {function_name} failed: {str(e)}"
#         logger.error(error_msg)
#         return {"success": False, "error": str(e)}

# # --- CHAT PROCESSING ---

# def safe_send(channel, message: str):
#     """Safely send message through WebRTC data channel"""
#     try:
#         if channel and hasattr(channel, 'readyState') and channel.readyState == "open":
#             channel.send(message)
#     except Exception as e:
#         logger.error(f"Failed to send message: {e}")

# async def generate_title(prompt: str) -> str:
#     """Generate a short title for the chat session"""
#     try:
#         title_prompt = f"Create a 2-4 word title for this todo request: '{prompt}'"
        
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.post(
#                 f"{LM_STUDIO_API_URL}/chat/completions",
#                 json={
#                     "model": MODEL_NAME,
#                     "messages": [{"role": "user", "content": title_prompt}],
#                     "temperature": 0.3,
#                     "max_tokens": 15
#                 }
#             )
#             response.raise_for_status()
#             title = response.json()["choices"][0]["message"]["content"].strip()
#             return title.replace('"', '') if title else "New Chat"
#     except Exception as e:
#         logger.error(f"Title generation failed: {e}")
#         return "New Chat"

# async def process_chat_request(prompt: str, session_id: int, data_channel):
#     """Process a chat request with enhanced function calling"""
#     logger.info(f"Processing chat request for session {session_id}: {prompt}")
    
#     # Save user message
#     await db_utils.save_message(session_id, "user", prompt)
    
#     # Generate title for first message
#     user_count = await db_utils.count_user_messages_in_session(session_id)
#     if user_count == 1:
#         title = await generate_title(prompt)
#         await db_utils.update_session_title(session_id, title)
#         safe_send(data_channel, json.dumps({"type": "state_change", "resource": "sessions"}))
    
#     # Get conversation history
#     history = await db_utils.fetch_session_messages(session_id)
#     messages = [{"role": record["role"], "content": record["content"]} for record in history]
    
#     # Add system prompt
#     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
#     # Add the original user prompt (for natural conversation and title generation)
#     messages.append({"role": "user", "content": prompt})
    
#     # Determine if we need to add workflow guidance
#     needs_existing_data = any(keyword in prompt.lower() for keyword in [
#         'add', 'mark', 'delete', 'remove', 'update', 'show', 'list', 'view',
#         'in', 'on', 'from', 'to', 'the', 'my'
#     ]) and not re.match(r'(?:create|make)\s+(?:a\s+)?(?:new\s+)?list', prompt.lower())
    
#     if needs_existing_data:
#         # Add a separate system message for workflow guidance (won't affect title generation)
#         workflow_guidance = """WORKFLOW REMINDER: This request requires existing data. You must:
# 1. Call get_all_todo_lists first to get current data
# 2. Find matching items in the JSON response
# 3. Use actual IDs from the response
# 4. Only claim success after successful function calls"""
#         messages.append({"role": "system", "content": workflow_guidance})
    
#     # Process with AI
#     max_turns = 10
#     for turn in range(max_turns):
#         try:
#             logger.info(f"Turn {turn + 1}: Calling LM Studio")
            
#             async with httpx.AsyncClient(timeout=90.0) as client:
#                 payload = {
#                     "model": MODEL_NAME,
#                     "messages": messages,
#                     "tools": TOOLS,
#                     "tool_choice": "auto",
#                     "temperature": 0.1,
#                     "max_tokens": 1500
#                 }
                
#                 response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=payload)
#                 response.raise_for_status()
#                 data = response.json()
                
#                 assistant_msg = data["choices"][0]["message"]
#                 messages.append(assistant_msg)
                
#                 # Handle tool calls
#                 if assistant_msg.get("tool_calls"):
#                     logger.info(f"Processing {len(assistant_msg['tool_calls'])} tool calls")
                    
#                     for tool_call in assistant_msg["tool_calls"]:
#                         func_name = tool_call["function"]["name"]
                        
#                         try:
#                             func_args = json.loads(tool_call["function"]["arguments"])
#                         except json.JSONDecodeError:
#                             logger.error(f"Invalid JSON in function args: {tool_call['function']['arguments']}")
#                             continue
                        
#                         # Execute the function
#                         result = await execute_function(func_name, func_args)
                        
#                         # Add result to conversation
#                         messages.append({
#                             "role": "tool",
#                             "tool_call_id": tool_call["id"],
#                             "name": func_name,
#                             "content": json.dumps(result)
#                         })
                        
#                         # Notify UI of changes for modification operations
#                         if result.get("success") and func_name != "get_all_todo_lists":
#                             safe_send(data_channel, json.dumps({"type": "state_change", "resource": "todos"}))
                    
#                     continue  # Get AI's response to the tool results
                
#                 # Final response - check for false claims
#                 content = assistant_msg.get("content", "")
#                 if content:
#                     # Check for problematic patterns that indicate false claims
#                     false_claim_patterns = [
#                         "tool_call", "function_call", '{"name":', "here is the json",
#                         "i found the", "i added", "i created", "i deleted", "i updated",
#                         "the list now looks like", "here's the updated", "successfully added",
#                         "list with id", "item to it", "updated.*list.*now"
#                     ]
                    
#                     content_lower = content.lower()
#                     is_false_claim = any(pattern in content_lower for pattern in false_claim_patterns)
                    
#                     if is_false_claim:
#                         # Check if they actually made function calls in this conversation
#                         function_calls_made = any(msg.get("role") == "tool" for msg in messages[-10:])
                        
#                         if not function_calls_made:
#                             error_msg = "I need to use function calls to help you, but I'm having trouble with the system. Please check the configuration."
#                             await db_utils.save_message(session_id, "assistant", error_msg)
#                             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_msg}))
#                             return
                    
#                     await db_utils.save_message(session_id, "assistant", content)
#                     safe_send(data_channel, json.dumps({"type": "chat_message", "content": content}))
                
#                 return
                
#         except Exception as e:
#             logger.error(f"Error in chat processing: {e}")
#             error_msg = f"I encountered an error: {str(e)}. Please try again."
#             await db_utils.save_message(session_id, "assistant", error_msg)
#             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_msg}))
#             return
    
#     # Max turns exceeded
#     timeout_msg = "This is taking too many steps. Please try a simpler request."
#     await db_utils.save_message(session_id, "assistant", timeout_msg)
#     safe_send(data_channel, json.dumps({"type": "chat_message", "content": timeout_msg}))

# # --- API ENDPOINTS ---

# @app.on_event("startup")
# async def startup():
#     await db_utils.get_pool()

# @app.get("/sessions/user/{user_id}")
# async def get_user_sessions(user_id: int):
#     sessions = await db_utils.fetch_user_sessions(user_id)
#     return [dict(session) for session in sessions]

# @app.post("/sessions/user/{user_id}", status_code=201)
# async def create_session(user_id: int):
#     session = await db_utils.create_new_session(user_id)
#     return dict(session)

# @app.get("/sessions/{session_id}/messages")
# async def get_session_messages(session_id: int):
#     messages = await db_utils.fetch_session_messages(session_id)
#     return [dict(msg) for msg in messages]

# @app.delete("/sessions/{session_id}")
# async def delete_session(session_id: int):
#     success = await db_utils.delete_session(session_id)
#     if not success:
#         raise HTTPException(404, f"Session {session_id} not found")
#     return {"status": "success", "message": f"Session {session_id} deleted"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     pc = RTCPeerConnection(configuration=pc_config)
#     pcs.add(pc)
    
#     @pc.on("datachannel")
#     def on_datachannel(channel):
#         logger.info(f"DataChannel established: {channel.label}")
        
#         @channel.on("message")
#         async def on_message(message: str):
#             try:
#                 data = json.loads(message)
#                 await process_chat_request(
#                     prompt=data["prompt"],
#                     session_id=data["sessionId"], 
#                     data_channel=channel
#                 )
#             except Exception as e:
#                 logger.error(f"Message handling error: {e}")
#                 safe_send(channel, json.dumps({
#                     "type": "chat_message", 
#                     "content": "Error processing your request. Please try again."
#                 }))
    
#     try:
#         while True:
#             data = await websocket.receive_json()
#             if data["type"] == "offer":
#                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
#                 await pc.setRemoteDescription(offer)
#                 answer = await pc.createAnswer()
#                 await pc.setLocalDescription(answer)
#                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
#     except WebSocketDisconnect:
#         logger.info("WebSocket disconnected")
#     finally:
#         if pc in pcs:
#             await pc.close()
#             pcs.remove(pc)

# @app.on_event("shutdown")
# async def shutdown():
#     logger.info("Shutting down...")
#     await asyncio.gather(*[pc.close() for pc in pcs])
#     pcs.clear()
#     pool = await db_utils.get_pool()
#     if pool:
#         await pool.close()

# @app.get("/")
# async def root():
#     return {"status": "Enhanced Todo Bridge API is running"}
# # import json
# # import logging
# # import asyncio
# # import re
# # from typing import List, Optional, Any, Dict, Set
# # from difflib import SequenceMatcher

# # import httpx
# # from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel

# # from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
# # import db_utils

# # # --- CONFIGURATION ---

# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # logger = logging.getLogger(__name__)

# # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # CRUD_API_URL = "http://localhost:8000"
# # MODEL_NAME = "qwen2.5-7b-instruct"

# # app = FastAPI(title="Enhanced Todo Bridge API", version="24.0")
# # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # pcs: Set[RTCPeerConnection] = set()
# # pc_config = RTCConfiguration(iceServers=[
# #     RTCIceServer(urls=["turn:127.0.0.1:3478"], username="demo", credential="password"),
# #     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# # ])

# # # --- FUZZY SEARCH AND CONTEXT HELPERS ---

# # class FuzzyMatcher:
# #     @staticmethod
# #     def similarity(a: str, b: str) -> float:
# #         """Calculate similarity between two strings (0.0 to 1.0)"""
# #         return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
    
# #     @staticmethod
# #     def find_best_list_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[Dict]:
# #         """Find the best matching list using fuzzy search"""
# #         if not query or not all_lists:
# #             return None
        
# #         query = query.strip().lower()
# #         best_match = None
# #         best_score = 0.0
        
# #         for lst in all_lists:
# #             title = lst.get('title', '').strip().lower()
            
# #             # Exact match
# #             if query == title:
# #                 return lst
            
# #             # Partial matches
# #             if query in title or title in query:
# #                 return lst
            
# #             # Fuzzy similarity
# #             score = FuzzyMatcher.similarity(query, title)
# #             if score >= threshold and score > best_score:
# #                 best_match = lst
# #                 best_score = score
        
# #         return best_match
    
# #     @staticmethod
# #     def find_best_item_match(query: str, all_lists: List[Dict], threshold: float = 0.5) -> Optional[tuple]:
# #         """Find best matching item. Returns (list_dict, item_dict) or None"""
# #         if not query or not all_lists:
# #             return None
        
# #         query = query.strip().lower()
# #         best_match = None
# #         best_score = 0.0
        
# #         for lst in all_lists:
# #             for item in lst.get('items', []):
# #                 title = item.get('title', '').strip().lower()
                
# #                 # Exact match
# #                 if query == title:
# #                     return (lst, item)
                
# #                 # Partial matches
# #                 if query in title or title in query:
# #                     return (lst, item)
                
# #                 # Fuzzy similarity
# #                 score = FuzzyMatcher.similarity(query, title)
# #                 if score >= threshold and score > best_score:
# #                     best_match = (lst, item)
# #                     best_score = score
        
# #         return best_match

# # class IntentAnalyzer:
# #     @staticmethod
# #     def extract_list_name(prompt: str) -> Optional[str]:
# #         """Extract list name from various prompt patterns"""
# #         patterns = [
# #             r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+['\"]([^'\"]+)['\"]",
# #             r"(?:create|make).*?(?:list|todo).*?(?:called|named)\s+(\w+(?:\s+\w+)*)",
# #             r"(?:delete|remove).*?(?:list|todo).*?['\"]([^'\"]+)['\"]",
# #             r"(?:delete|remove).*?(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
# #             r"(?:in|on|from|to)(?:\s+the)?\s+['\"]([^'\"]+)['\"]",
# #             r"(?:in|on|from|to)(?:\s+the)?\s+(\w+(?:\s+\w+)*?)(?:\s+list|\s+todo|\s*$)",
# #             r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+list",
# #         ]
        
# #         for pattern in patterns:
# #             match = re.search(pattern, prompt, re.IGNORECASE)
# #             if match:
# #                 name = match.group(1).strip()
# #                 # Filter out common words
# #                 if name.lower() not in ['new', 'this', 'that', 'my', 'the', 'a', 'an']:
# #                     return name
# #         return None
    
# #     @staticmethod
# #     def extract_item_name(prompt: str) -> Optional[str]:
# #         """Extract item name from various prompt patterns"""
# #         patterns = [
# #             r"(?:add|create).*?['\"]([^'\"]+)['\"]",
# #             r"(?:add|create)\s+(.+?)(?:\s+to|\s+in|\s*$)",
# #             r"(?:mark|complete|done).*?['\"]([^'\"]+)['\"]",
# #             r"(?:mark|complete|done)\s+(.+?)(?:\s+as|\s+to|\s*$)",
# #             r"(?:delete|remove).*?(?:item|todo).*?['\"]([^'\"]+)['\"]",
# #             r"(?:delete|remove).*?(?:item|todo)\s+(.+?)(?:\s+from|\s*$)",
# #         ]
        
# #         for pattern in patterns:
# #             match = re.search(pattern, prompt, re.IGNORECASE)
# #             if match:
# #                 name = match.group(1).strip()
# #                 if len(name) > 0:
# #                     return name
# #         return None

# # # --- TODO API SERVER ---

# # class TodoAPIServer:
# #     def __init__(self, base_url: str = CRUD_API_URL):
# #         self.base_url = base_url.rstrip('/')
# #         self.client = httpx.AsyncClient(timeout=30.0)
    
# #     async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
# #         """Make HTTP request with proper error handling"""
# #         url = f"{self.base_url}{endpoint}"
# #         try:
# #             response = await self.client.request(method, url, json=data)
# #             response.raise_for_status()
            
# #             if response.status_code == 204:
# #                 return {"success": True, "message": "Operation completed"}
            
# #             return response.json()
# #         except httpx.HTTPStatusError as e:
# #             error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
# #             logger.error(f"API Error: {error_msg}")
# #             raise Exception(error_msg)
# #         except Exception as e:
# #             logger.error(f"Request Error: {str(e)}")
# #             raise Exception(f"Request failed: {str(e)}")
    
# #     # API Methods
# #     async def create_todo_list(self, title: str):
# #         return await self._request("POST", "/lists/", {"title": title})
    
# #     async def get_all_todo_lists(self):
# #         return await self._request("GET", "/lists/")
    
# #     async def get_todo_list(self, list_id: int):
# #         return await self._request("GET", f"/lists/{list_id}")
    
# #     async def update_todo_list(self, list_id: int, title: str):
# #         return await self._request("PUT", f"/lists/{list_id}", {"title": title})
    
# #     async def delete_todo_list(self, list_id: int):
# #         return await self._request("DELETE", f"/lists/{list_id}")
    
# #     async def create_todo_item(self, list_id: int, title: str, completed: bool = False):
# #         return await self._request("POST", f"/{list_id}/items/", {"title": title, "completed": completed})
    
# #     async def update_todo_item(self, list_id: int, item_id: int, title: Optional[str] = None, completed: Optional[bool] = None):
# #         update_data = {}
# #         if title is not None:
# #             update_data["title"] = title
# #         if completed is not None:
# #             update_data["completed"] = completed
        
# #         if not update_data:
# #             raise Exception("At least one field (title or completed) must be provided")
        
# #         return await self._request("PUT", f"/{list_id}/items/{item_id}", update_data)
    
# #     async def delete_todo_item(self, list_id: int, item_id: int):
# #         return await self._request("DELETE", f"/{list_id}/items/{item_id}")

# # # Global API instance
# # todo_api = TodoAPIServer()

# # # --- ENHANCED SYSTEM PROMPT ---

# # SYSTEM_PROMPT = """You are a todo list assistant that MUST use function calls to perform ANY action.

# # ABSOLUTE REQUIREMENTS:
# # 1. You CANNOT perform ANY action without calling the appropriate function
# # 2. You CANNOT claim to have done something unless you actually called a function and received a successful response
# # 3. NEVER make up results, IDs, or pretend to have access to data you don't have
# # 4. If you don't have current data, you MUST call get_all_todo_lists first

# # MANDATORY WORKFLOW FOR ALL OPERATIONS:
# # 1. If the user wants to work with existing lists/items → MUST call get_all_todo_lists first
# # 2. Parse the JSON response to find matching items
# # 3. Use the actual IDs from the response to perform the operation
# # 4. Only claim success after receiving a successful function response

# # AVAILABLE FUNCTIONS (you MUST use these):
# # - get_all_todo_lists: Get current data - REQUIRED before working with existing items
# # - create_todo_list: Create new list (requires title)
# # - create_todo_item: Add item to list (requires list_id from get_all_todo_lists response)
# # - update_todo_item: Modify item (requires list_id and item_id from get_all_todo_lists)
# # - delete_todo_list: Delete list (requires list_id from get_all_todo_lists)
# # - delete_todo_item: Delete item (requires list_id and item_id from get_all_todo_lists)

# # FORBIDDEN BEHAVIORS:
# # - Do NOT claim "I found the X list" unless you actually called get_all_todo_lists
# # - Do NOT mention specific IDs unless they came from a function response
# # - Do NOT describe what lists contain unless you have current data
# # - Do NOT claim success without a successful function call result

# # If you cannot call functions properly, you MUST say: "I need to use function calls to help you, but I'm having trouble with the system. Please check the configuration."
# # """

# # # Tool definitions for LM Studio
# # TOOLS = [
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "get_all_todo_lists",
# #             "description": "Get all todo lists with their items - use this first when you need to find existing lists or items",
# #             "parameters": {"type": "object", "properties": {}}
# #         }
# #     },
# #     {
# #         "type": "function", 
# #         "function": {
# #             "name": "create_todo_list",
# #             "description": "Create a new todo list",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {"title": {"type": "string", "description": "Title for the new list"}},
# #                 "required": ["title"]
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "create_todo_item", 
# #             "description": "Add a new item to a specific list",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {
# #                     "list_id": {"type": "integer", "description": "ID of the list to add item to"},
# #                     "title": {"type": "string", "description": "Title of the new item"},
# #                     "completed": {"type": "boolean", "description": "Whether item starts as completed", "default": False}
# #                 },
# #                 "required": ["list_id", "title"]
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "update_todo_item",
# #             "description": "Update an item's title or completion status",
# #             "parameters": {
# #                 "type": "object", 
# #                 "properties": {
# #                     "list_id": {"type": "integer"},
# #                     "item_id": {"type": "integer"},
# #                     "title": {"type": "string", "description": "New title (optional)"},
# #                     "completed": {"type": "boolean", "description": "Completion status (optional)"}
# #                 },
# #                 "required": ["list_id", "item_id"]
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "delete_todo_list",
# #             "description": "Delete an entire todo list",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {"list_id": {"type": "integer", "description": "ID of list to delete"}},
# #                 "required": ["list_id"]
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "delete_todo_item", 
# #             "description": "Delete a specific todo item",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {
# #                     "list_id": {"type": "integer", "description": "ID of the list containing the item"},
# #                     "item_id": {"type": "integer", "description": "ID of the item to delete"}
# #                 },
# #                 "required": ["list_id", "item_id"]
# #             }
# #         }
# #     }
# # ]

# # # --- TOOL EXECUTION ---

# # async def execute_function(function_name: str, arguments: dict) -> dict:
# #     """Execute a function call and return the result"""
# #     try:
# #         logger.info(f"Executing function: {function_name} with args: {arguments}")
        
# #         # Get the method from the API server
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
# #         logger.error(error_msg)
# #         return {"success": False, "error": str(e)}

# # # --- CHAT PROCESSING ---

# # def safe_send(channel, message: str):
# #     """Safely send message through WebRTC data channel"""
# #     try:
# #         if channel and hasattr(channel, 'readyState') and channel.readyState == "open":
# #             channel.send(message)
# #     except Exception as e:
# #         logger.error(f"Failed to send message: {e}")

# # async def generate_title(prompt: str) -> str:
# #     """Generate a short title for the chat session"""
# #     try:
# #         title_prompt = f"Create a 2-4 word title for this todo request: '{prompt}'"
        
# #         async with httpx.AsyncClient(timeout=10.0) as client:
# #             response = await client.post(
# #                 f"{LM_STUDIO_API_URL}/chat/completions",
# #                 json={
# #                     "model": MODEL_NAME,
# #                     "messages": [{"role": "user", "content": title_prompt}],
# #                     "temperature": 0.3,
# #                     "max_tokens": 15
# #                 }
# #             )
# #             response.raise_for_status()
# #             title = response.json()["choices"][0]["message"]["content"].strip()
# #             return title.replace('"', '') if title else "New Chat"
# #     except Exception as e:
# #         logger.error(f"Title generation failed: {e}")
# #         return "New Chat"

# # async def process_chat_request(prompt: str, session_id: int, data_channel):
# #     """Process a chat request with enhanced function calling"""
# #     logger.info(f"Processing chat request for session {session_id}: {prompt}")
    
# #     # Save user message
# #     await db_utils.save_message(session_id, "user", prompt)
    
# #     # Generate title for first message
# #     user_count = await db_utils.count_user_messages_in_session(session_id)
# #     if user_count == 1:
# #         title = await generate_title(prompt)
# #         await db_utils.update_session_title(session_id, title)
# #         safe_send(data_channel, json.dumps({"type": "state_change", "resource": "sessions"}))
    
# #     # Get conversation history
# #     history = await db_utils.fetch_session_messages(session_id)
# #     messages = [{"role": record["role"], "content": record["content"]} for record in history]
    
# #     # Add system prompt
# #     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
# #     # Add enhanced prompt to force proper workflow
# #     enhanced_prompt = f"""User request: "{prompt}"

# # This request involves working with existing lists/items. You MUST follow this exact workflow:

# # 1. FIRST: Call get_all_todo_lists to get current data
# # 2. SECOND: Find the matching list/item in the JSON response 
# # 3. THIRD: Use the actual IDs from the response to perform the requested operation
# # 4. FOURTH: Only respond based on the actual function call results

# # Do NOT skip step 1. Do NOT make assumptions about what exists. Do NOT claim success without actual function calls.

# # User's original request: {prompt}"""
    
# #     messages.append({"role": "user", "content": enhanced_prompt})
    
# #     # Process with AI
# #     max_turns = 10
# #     for turn in range(max_turns):
# #         try:
# #             logger.info(f"Turn {turn + 1}: Calling LM Studio")
            
# #             async with httpx.AsyncClient(timeout=90.0) as client:
# #                 payload = {
# #                     "model": MODEL_NAME,
# #                     "messages": messages,
# #                     "tools": TOOLS,
# #                     "tool_choice": "auto",
# #                     "temperature": 0.1,
# #                     "max_tokens": 1500
# #                 }
                
# #                 response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=payload)
# #                 response.raise_for_status()
# #                 data = response.json()
                
# #                 assistant_msg = data["choices"][0]["message"]
# #                 messages.append(assistant_msg)
                
# #                 # Handle tool calls
# #                 if assistant_msg.get("tool_calls"):
# #                     logger.info(f"Processing {len(assistant_msg['tool_calls'])} tool calls")
                    
# #                     for tool_call in assistant_msg["tool_calls"]:
# #                         func_name = tool_call["function"]["name"]
                        
# #                         try:
# #                             func_args = json.loads(tool_call["function"]["arguments"])
# #                         except json.JSONDecodeError:
# #                             logger.error(f"Invalid JSON in function args: {tool_call['function']['arguments']}")
# #                             continue
                        
# #                         # Execute the function
# #                         result = await execute_function(func_name, func_args)
                        
# #                         # Add result to conversation
# #                         messages.append({
# #                             "role": "tool",
# #                             "tool_call_id": tool_call["id"],
# #                             "name": func_name,
# #                             "content": json.dumps(result)
# #                         })
                        
# #                         # Notify UI of changes for modification operations
# #                         if result.get("success") and func_name != "get_all_todo_lists":
# #                             safe_send(data_channel, json.dumps({"type": "state_change", "resource": "todos"}))
                    
# #                     continue  # Get AI's response to the tool results
                
# #                 # Final response - check for false claims
# #                 content = assistant_msg.get("content", "")
# #                 if content:
# #                     # Check for problematic patterns that indicate false claims
# #                     false_claim_patterns = [
# #                         "tool_call", "function_call", '{"name":', "here is the json",
# #                         "i found the", "i added", "i created", "i deleted", "i updated",
# #                         "the list now looks like", "here's the updated", "successfully added",
# #                         "list with id", "item to it", "updated.*list.*now"
# #                     ]
                    
# #                     content_lower = content.lower()
# #                     is_false_claim = any(pattern in content_lower for pattern in false_claim_patterns)
                    
# #                     if is_false_claim:
# #                         # Check if they actually made function calls in this conversation
# #                         function_calls_made = any(msg.get("role") == "tool" for msg in messages[-10:])
                        
# #                         if not function_calls_made:
# #                             error_msg = "I need to use function calls to help you, but I'm having trouble with the system. Please check the configuration."
# #                             await db_utils.save_message(session_id, "assistant", error_msg)
# #                             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_msg}))
# #                             return
                    
# #                     await db_utils.save_message(session_id, "assistant", content)
# #                     safe_send(data_channel, json.dumps({"type": "chat_message", "content": content}))
                
# #                 return
                
# #         except Exception as e:
# #             logger.error(f"Error in chat processing: {e}")
# #             error_msg = f"I encountered an error: {str(e)}. Please try again."
# #             await db_utils.save_message(session_id, "assistant", error_msg)
# #             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_msg}))
# #             return
    
# #     # Max turns exceeded
# #     timeout_msg = "This is taking too many steps. Please try a simpler request."
# #     await db_utils.save_message(session_id, "assistant", timeout_msg)
# #     safe_send(data_channel, json.dumps({"type": "chat_message", "content": timeout_msg}))

# # # --- API ENDPOINTS ---

# # @app.on_event("startup")
# # async def startup():
# #     await db_utils.get_pool()

# # @app.get("/sessions/user/{user_id}")
# # async def get_user_sessions(user_id: int):
# #     sessions = await db_utils.fetch_user_sessions(user_id)
# #     return [dict(session) for session in sessions]

# # @app.post("/sessions/user/{user_id}", status_code=201)
# # async def create_session(user_id: int):
# #     session = await db_utils.create_new_session(user_id)
# #     return dict(session)

# # @app.get("/sessions/{session_id}/messages")
# # async def get_session_messages(session_id: int):
# #     messages = await db_utils.fetch_session_messages(session_id)
# #     return [dict(msg) for msg in messages]

# # @app.delete("/sessions/{session_id}")
# # async def delete_session(session_id: int):
# #     success = await db_utils.delete_session(session_id)
# #     if not success:
# #         raise HTTPException(404, f"Session {session_id} not found")
# #     return {"status": "success", "message": f"Session {session_id} deleted"}

# # @app.websocket("/ws")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     pc = RTCPeerConnection(configuration=pc_config)
# #     pcs.add(pc)
    
# #     @pc.on("datachannel")
# #     def on_datachannel(channel):
# #         logger.info(f"DataChannel established: {channel.label}")
        
# #         @channel.on("message")
# #         async def on_message(message: str):
# #             try:
# #                 data = json.loads(message)
# #                 await process_chat_request(
# #                     prompt=data["prompt"],
# #                     session_id=data["sessionId"], 
# #                     data_channel=channel
# #                 )
# #             except Exception as e:
# #                 logger.error(f"Message handling error: {e}")
# #                 safe_send(channel, json.dumps({
# #                     "type": "chat_message", 
# #                     "content": "Error processing your request. Please try again."
# #                 }))
    
# #     try:
# #         while True:
# #             data = await websocket.receive_json()
# #             if data["type"] == "offer":
# #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# #                 await pc.setRemoteDescription(offer)
# #                 answer = await pc.createAnswer()
# #                 await pc.setLocalDescription(answer)
# #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# #     except WebSocketDisconnect:
# #         logger.info("WebSocket disconnected")
# #     finally:
# #         if pc in pcs:
# #             await pc.close()
# #             pcs.remove(pc)

# # @app.on_event("shutdown")
# # async def shutdown():
# #     logger.info("Shutting down...")
# #     await asyncio.gather(*[pc.close() for pc in pcs])
# #     pcs.clear()
# #     pool = await db_utils.get_pool()
# #     if pool:
# #         await pool.close()

# # @app.get("/")
# # async def root():
# #     return {"status": "Enhanced Todo Bridge API is running"}
# # # import json
# # # import logging
# # # import asyncio
# # # import re
# # # from typing import List, Optional, Any, Dict, Set

# # # import httpx
# # # from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from pydantic import BaseModel

# # # from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
# # # import db_utils

# # # # --- STEP 1: BOILERPLATE AND CONFIGURATION ---

# # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # # logger = logging.getLogger(__name__)

# # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # CRUD_API_URL = "http://localhost:8000"
# # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # app = FastAPI(
# # #     title="Definitive Autonomous Agent API",
# # #     description="A rock-solid Bridge API built directly from the proven mcp_todo_server logic.",
# # #     version="22.0 (Demo Ready)",
# # # )
# # # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # # pcs: Set[RTCPeerConnection] = set()
# # # pc_config = RTCConfiguration(iceServers=[
# # #     RTCIceServer(urls=["turn:127.0.0.1:3478"], username="demo", credential="password"),
# # #     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# # # ])

# # # class ChatRequest(BaseModel): prompt: str

# # # # --- STEP 2: CONTEXT MANAGEMENT SYSTEM ---

# # # class ContextHelper:
# # #     """Helper class to provide intelligent context resolution for todo operations"""
    
# # #     @staticmethod
# # #     def extract_list_references(prompt: str) -> List[str]:
# # #         """Extract potential list name references from user prompt"""
# # #         # Look for patterns like "the X list", "X list", "my X", etc.
# # #         patterns = [
# # #             r"(?:the\s+)?(\w+(?:\s+\w+)*)\s+list",
# # #             r"(?:my\s+)?(\w+(?:\s+\w+)*)\s+(?:list|todos?)",
# # #             r"(?:in|from|on)\s+(?:the\s+)?(\w+(?:\s+\w+)*)",
# # #             r"delete\s+(?:the\s+)?(\w+(?:\s+\w+)*)",
# # #             r"rename\s+(\w+(?:\s+\w+)*)\s+to",
# # #             r"(?:mark|update)\s+.+?\s+(?:in|on)\s+(?:the\s+)?(\w+(?:\s+\w+)*)",
# # #         ]
        
# # #         references = []
# # #         for pattern in patterns:
# # #             matches = re.findall(pattern, prompt.lower())
# # #             references.extend(matches)
        
# # #         # Remove common words that aren't list names
# # #         stop_words = {'new', 'first', 'last', 'next', 'this', 'that', 'item', 'todo', 'it', 'them', 'list'}
# # #         return [ref.strip() for ref in references if ref.strip() and ref.strip() not in stop_words]
    
# # #     @staticmethod
# # #     def extract_item_references(prompt: str) -> List[str]:
# # #         """Extract potential item references from user prompt"""
# # #         patterns = [
# # #             r"mark\s+(.+?)\s+as\s+(?:done|complete)",
# # #             r"mark\s+(.+?)\s+(?:done|complete)",
# # #             r"(?:delete|remove)\s+(.+?)(?:\s+(?:item|todo)|\s+(?:from|in)|\s*$)",
# # #             r"(?:the\s+)?(.+?)\s+(?:item|todo)",
# # #             r"update\s+(.+?)\s+(?:to|with)",
# # #         ]
        
# # #         references = []
# # #         for pattern in patterns:
# # #             matches = re.findall(pattern, prompt.lower())
# # #             references.extend(matches)
        
# # #         # Clean up references
# # #         cleaned_refs = []
# # #         for ref in references:
# # #             ref = ref.strip()
# # #             # Remove common words at the end
# # #             ref = re.sub(r'\s+(?:item|todo|task)$', '', ref)
# # #             if ref and len(ref) > 1:
# # #                 cleaned_refs.append(ref)
        
# # #         return cleaned_refs
    
# # #     @staticmethod
# # #     def find_matching_list(references: List[str], all_lists: List[Dict]) -> Optional[Dict]:
# # #         """Find the best matching list from references"""
# # #         if not references or not all_lists:
# # #             return None
        
# # #         for ref in references:
# # #             # Exact match first
# # #             for lst in all_lists:
# # #                 if lst['title'].lower() == ref.lower():
# # #                     return lst
            
# # #             # Partial match
# # #             for lst in all_lists:
# # #                 if ref.lower() in lst['title'].lower() or lst['title'].lower() in ref.lower():
# # #                     return lst
        
# # #         return None
    
# # #     @staticmethod
# # #     def find_matching_item(references: List[str], all_lists: List[Dict]) -> Optional[tuple]:
# # #         """Find the best matching item from references. Returns (list_dict, item_dict) or None"""
# # #         if not references or not all_lists:
# # #             return None
        
# # #         for ref in references:
# # #             for lst in all_lists:
# # #                 for item in lst.get('items', []):
# # #                     # Exact match
# # #                     if item['title'].lower() == ref.lower():
# # #                         return (lst, item)
                    
# # #                     # Partial match
# # #                     if ref.lower() in item['title'].lower() or item['title'].lower() in ref.lower():
# # #                         return (lst, item)
        
# # #         return None

# # # def needs_context_fetch(prompt: str, recent_messages: List[Dict]) -> bool:
# # #     """
# # #     Determine if we need to fetch context based on the prompt and recent conversation
# # #     """
# # #     # Check if user is referencing lists/items by name without providing IDs
# # #     list_refs = ContextHelper.extract_list_references(prompt)
# # #     item_refs = ContextHelper.extract_item_references(prompt)
    
# # #     if not (list_refs or item_refs):
# # #         return False
    
# # #     # Check if we have recent context (last 3 messages)
# # #     recent_content = " ".join([msg.get('content', '') for msg in recent_messages[-3:] if isinstance(msg.get('content'), str)])
    
# # #     # If we recently called get_all_todo_lists, we probably have context
# # #     if 'get_all_todo_lists' in recent_content:
# # #         return False
    
# # #     return True

# # # # --- STEP 3: THE AI AGENT'S "BRAIN" - THE ENHANCED SOURCE OF TRUTH ---

# # # ENHANCED_SYSTEM_PROMPT = """
# # # You are a todo list management assistant. You have access to function calling tools that you MUST use to perform any actions.

# # # CRITICAL RULES:
# # # 1. You CANNOT perform any actions without calling the appropriate functions
# # # 2. NEVER claim to have done something unless you actually called a function and got a successful response
# # # 3. If you cannot call functions properly, be honest about it
# # # 4. Always call get_all_todo_lists first when you need current information

# # # AVAILABLE FUNCTIONS:
# # # - get_all_todo_lists: Get current state of all lists
# # # - create_todo_list: Create a new list
# # # - create_todo_item: Add item to a list  
# # # - update_todo_item: Mark items as done/undone or change title
# # # - delete_todo_list: Delete a list
# # # - delete_todo_item: Delete an item

# # # IMPORTANT: 
# # # - Use actual function calls, not fake text responses
# # # - Wait for function results before claiming success
# # # - If function calling is not working, inform the user honestly
# # # - Never hallucinate results or claim actions you didn't perform

# # # If you find yourself unable to call functions properly, please tell the user: "I'm having trouble executing the function calls. Please check the system configuration."
# # # """

# # # # ### CRITICAL: This tool schema is a PERFECT 1-to-1 mirror of your working mcp_todo_server.py ###
# # # tools_schema = [
# # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
# # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics", "parameters": {"type": "object", "properties": {}}}},
# # #     {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}}, "required": ["list_id"]}}},
# # #     {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "title": {"type": "string"}}, "required": ["list_id", "title"]}}},
# # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list and all its items", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}}, "required": ["list_id"]}}},
# # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean", "default": False}}, "required": ["list_id", "title"]}}},
# # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update an item's title or mark it as done (completed: true)", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete an item from a list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # ]

# # # TOOL_TO_RESOURCE_MAP = { name: "todos" for name in [tool["function"]["name"] for tool in tools_schema] if "get" not in name }

# # # # --- STEP 4: CORE LOGIC (Using your proven MCP server logic) ---

# # # class TodoMCPServer:
# # #     """This class is a direct, verbatim copy of the logic from your working mcp_todo_server.py.
# # #     It is the GUARANTEED source of truth for interacting with the CRUD API."""
# # #     def __init__(self, base_url: str = CRUD_API_URL):
# # #         self.base_url = base_url.rstrip('/')
# # #         self.client = httpx.AsyncClient(timeout=30.0)
# # #     async def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Any:
# # #         url = f"{self.base_url}{endpoint}"
# # #         try:
# # #             response = await self.client.request(method, url, json=json_data)
# # #             response.raise_for_status()
# # #             if response.status_code == 204: return {"success": True, "message": "Operation completed successfully"}
# # #             return response.json()
# # #         except httpx.HTTPStatusError as e:
# # #             raise Exception(f"Client error '{e.response.status_code} {e.response.reason_phrase}' for url '{e.request.url}'.")
# # #     async def create_todo_list(self, title: str): return await self._make_request("POST", "/lists/", {"title": title})
# # #     async def get_all_todo_lists(self) -> List[Dict[str, Any]]: return await self._make_request("GET", "/lists/")
# # #     async def get_todo_list(self, list_id: int): return await self._make_request("GET", f"/lists/{list_id}")
# # #     async def update_todo_list(self, list_id: int, title: str): return await self._make_request("PUT", f"/lists/{list_id}", {"title": title})
# # #     async def delete_todo_list(self, list_id: int): return await self._make_request("DELETE", f"/lists/{list_id}")
# # #     async def create_todo_item(self, list_id: int, title: str, completed: bool = False): return await self._make_request("POST", f"/{list_id}/items/", {"title": title, "completed": completed})
# # #     async def update_todo_item(self, list_id: int, item_id: int, title: Optional[str] = None, completed: Optional[bool] = None):
# # #         update_data = {k: v for k, v in {"title": title, "completed": completed}.items() if v is not None}
# # #         if not update_data: raise Exception("At least one field must be provided for update")
# # #         return await self._make_request("PUT", f"/{list_id}/items/{item_id}", update_data)
# # #     async def delete_todo_item(self, list_id: int, item_id: int): return await self._make_request("DELETE", f"/{list_id}/items/{item_id}")

# # # todo_mcp_api = TodoMCPServer()

# # # async def execute_tool(tool_name: str, args: dict) -> str:
# # #     """This function now correctly and safely delegates execution to the TodoMCPServer class."""
# # #     try:
# # #         method_to_call = getattr(todo_mcp_api, tool_name)
# # #         result = await method_to_call(**args)
# # #         return json.dumps(result)
# # #     except Exception as e:
# # #         logger.error(f"Error executing tool '{tool_name}': {e}")
# # #         return json.dumps({"status": "error", "detail": str(e)})

# # # def safe_send(data_channel, message: str):
# # #     try:
# # #         if data_channel and data_channel.readyState == "open": data_channel.send(message)
# # #     except Exception as e: logger.error(f"Error during safe_send: {e}")


# # # async def generate_title_for_prompt(prompt: str) -> str:
# # #     """Uses the LLM to create a short, concise title from the user's first message."""
# # #     logger.info(f"Generating title for prompt: '{prompt}'")
# # #     try:
# # #         title_generation_prompt = f"""
# # #         Summarize the following user request into a short, 3-5 word title for a chat session.
# # #         Examples:
# # #         - "create a new list called 'Vacation Plans' and add 'book flights' to it" -> "Vacation Plans"
# # #         - "delete the shopping list" -> "Delete Shopping List"
# # #         - "mark the item 'buy milk' as done on my groceries list" -> "Update Groceries List"

# # #         User Request: "{prompt}"
# # #         Title:
# # #         """
# # #         async with httpx.AsyncClient(timeout=15.0) as client:
# # #             response = await client.post(
# # #                 f"{LM_STUDIO_API_URL}/chat/completions",
# # #                 json={
# # #                     "model": MODEL_NAME,
# # #                     "messages": [{"role": "user", "content": title_generation_prompt}],
# # #                     "temperature": 0.2, # Low temperature for more deterministic titles
# # #                     "max_tokens": 20,
# # #                 }
# # #             )
# # #             response.raise_for_status()
# # #             title = response.json()["choices"][0]["message"]["content"].strip().replace('"', '')
# # #             return title if title else "Untitled Chat"
# # #     except Exception as e:
# # #         logger.error(f"Could not generate title: {e}")
# # #         return "New Chat" # Fallback title
    

# # # async def process_chat_request(prompt: str, session_id: int, data_channel):
# # #     """
# # #     Enhanced chat processing with intelligent context fetching.
# # #     A stable, non-recursive, multi-turn agent loop that automatically handles context.
# # #     """
# # #     logger.info(f"Agent processing prompt for session {session_id}: '{prompt}'")
# # #     await db_utils.save_message(session_id, "user", prompt)
    
# # #      # --- NEW: Title Generation Logic ---
# # #     # Check if this is the first user message in the session.
# # #     user_message_count = await db_utils.count_user_messages_in_session(session_id)
# # #     if user_message_count == 1:
# # #         # If so, generate and set the title.
# # #         new_title = await generate_title_for_prompt(prompt)
# # #         await db_utils.update_session_title(session_id, new_title)
        
# # #         # Push a notification to the frontend to update the session list sidebar.
# # #         safe_send(data_channel, json.dumps({"type": "state_change", "resource": "sessions"}))

# # #     # Get conversation history
# # #     history_records = await db_utils.fetch_session_messages(session_id)
# # #     messages = [{"role": record["role"], "content": record["content"]} for record in history_records]
    
# # #     # Check if we need to fetch context first
# # #     context_needed = needs_context_fetch(prompt, messages)
    
# # #     if context_needed:
# # #         logger.info("Context fetch needed - the AI will get all todo lists first")
        
# # #         # Enhance the prompt to guide the AI to fetch context first and complete the task
# # #         enhanced_prompt = f"""The user said: "{prompt}"

# # # This request references lists or items by name. You MUST:
# # # 1. First call get_all_todo_lists to get the current context
# # # 2. Parse the JSON response to find the matching list/item IDs
# # # 3. IMMEDIATELY execute the user's original request using those IDs
# # # 4. Do NOT stop after just fetching the lists - complete the entire task in this conversation.

# # # User's original request: {prompt}"""
        
# # #         messages.append({"role": "user", "content": enhanced_prompt})
# # #     else:
# # #         messages.append({"role": "user", "content": prompt})
    
# # #     # Add the enhanced system prompt
# # #     messages.insert(0, {"role": "system", "content": ENHANCED_SYSTEM_PROMPT})
    
# # #     # This loop will continue as long as the LLM wants to use tools.
# # #     for turn in range(6):  # Increased to 6 turns to allow for context fetching + execution
# # #         try:
# # #             async with httpx.AsyncClient(timeout=60.0) as client:
# # #                 # Ensure proper tool calling format for LM Studio
# # #                 request_payload = {
# # #                     "model": MODEL_NAME, 
# # #                     "messages": messages, 
# # #                     "tools": tools_schema, 
# # #                     "tool_choice": "auto",
# # #                     "temperature": 0.1,  # Lower temperature for more consistent behavior
# # #                     "max_tokens": 2000
# # #                 }
                
# # #                 logger.info(f"Sending request to LM Studio with {len(messages)} messages")
# # #                 response = await client.post(f"{LM_STUDIO_API_URL}/chat/completions", json=request_payload)
# # #                 response.raise_for_status()
# # #                 response_data = response.json()
# # #                 logger.info(f"LM Studio response: {json.dumps(response_data, indent=2)}")
                
# # #                 assistant_message = response_data["choices"][0]["message"]
# # #                 logger.info(f"Assistant message: {json.dumps(assistant_message, indent=2)}")
# # #                 messages.append(assistant_message) # Add LLM's thought process to history

# # #                 # If there are no more tool calls, the agent's work is done.
# # #                 if not assistant_message.get("tool_calls"):
# # #                     final_content = assistant_message.get("content", "Done.")
                    
# # #                     # Check if the AI is making false claims without function calls
# # #                     false_claim_patterns = [
# # #                         "i have added", "i have marked", "i have deleted", "i have created",
# # #                         "successfully added", "successfully marked", "successfully deleted",
# # #                         "here is your updated", "your todo lists are now up-to-date"
# # #                     ]
                    
# # #                     content_lower = final_content.lower()
# # #                     is_false_claim = any(pattern in content_lower for pattern in false_claim_patterns)
                    
# # #                     if is_false_claim:
# # #                         error_message = "I apologize, but I'm having trouble executing the actual function calls. The system may need configuration. I cannot perform actions without calling the proper functions."
# # #                         await db_utils.save_message(session_id, "assistant", error_message)
# # #                         safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_message}))
# # #                     else:
# # #                         await db_utils.save_message(session_id, "assistant", final_content)
# # #                         safe_send(data_channel, json.dumps({"type": "chat_message", "content": final_content}))
# # #                     return # EXIT THE LOOP

# # #                 # If there are tool calls, execute them and continue the loop.
# # #                 # Only log a summary, never send raw tool calls to user
# # #                 if assistant_message.get("tool_calls"):
# # #                     logger.info(f"Executing {len(assistant_message.get('tool_calls', []))} tool calls")
                
# # #                 for tool_call in assistant_message.get("tool_calls", []):
# # #                     tool_name = tool_call["function"]["name"]
# # #                     try:
# # #                         tool_args = json.loads(tool_call["function"]["arguments"])
# # #                     except json.JSONDecodeError as e:
# # #                         logger.error(f"Invalid JSON in tool arguments: {tool_call['function']['arguments']}")
# # #                         continue
                        
# # #                     logger.info(f"Agent executing tool '{tool_name}' with args: {tool_args}")
# # #                     tool_result_str = await execute_tool(tool_name, tool_args)
                    
# # #                     # Add the tool result to the conversation context
# # #                     messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_name, "content": tool_result_str})
                    
# # #                     try: # Attempt to send UI sync signal
# # #                         tool_result_obj = json.loads(tool_result_str)
# # #                         # A simple, robust check for any kind of success.
# # #                         is_successful = "error" not in str(tool_result_obj).lower()
# # #                         if is_successful and tool_name in TOOL_TO_RESOURCE_MAP:
# # #                             safe_send(data_channel, json.dumps({"type": "state_change", "resource": "todos"}))
# # #                     except: 
# # #                         pass
        
# # #         except Exception as e:
# # #             logger.error(f"Error in enhanced agent loop: {e}")
# # #             error_content = "I encountered an error. Please try again."
# # #             await db_utils.save_message(session_id, "assistant", error_content)
# # #             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_content}))
# # #             return

# # #     logger.warning("Agent exceeded max turns.")
# # #     safe_send(data_channel, json.dumps({"type": "chat_message", "content": "This request is taking too many steps. Please try breaking it down."}))

# # # # --- STEP 5: API ENDPOINTS AND LIFECYCLE EVENTS ---

# # # @app.on_event("startup")
# # # async def startup_event(): await db_utils.get_pool()

# # # @app.get("/sessions/user/{user_id}", tags=["Chat Sessions"])
# # # async def get_user_sessions(user_id: int):
# # #     sessions = await db_utils.fetch_user_sessions(user_id)
# # #     return [dict(session) for session in sessions]

# # # @app.post("/sessions/user/{user_id}", status_code=201, tags=["Chat Sessions"])
# # # async def create_session(user_id: int):
# # #     session = await db_utils.create_new_session(user_id)
# # #     return dict(session)

# # # @app.get("/sessions/{session_id}/messages", tags=["Chat Sessions"])
# # # async def get_session_messages(session_id: int):
# # #     messages = await db_utils.fetch_session_messages(session_id)
# # #     return [dict(msg) for msg in messages]

# # # @app.delete("/sessions/{session_id}", tags=["Chat Sessions"])
# # # async def delete_chat_session(session_id: int):
# # #     """Endpoint to delete a chat session and all its messages."""
# # #     success = await db_utils.delete_session(session_id)
# # #     if not success:
# # #         raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found.")
# # #     return {"status": "success", "message": f"Session {session_id} deleted."}

# # # @app.websocket("/ws")
# # # async def websocket_endpoint(websocket: WebSocket):
# # #     await websocket.accept()
# # #     pc = RTCPeerConnection(configuration=pc_config)
# # #     pcs.add(pc)
# # #     @pc.on("datachannel")
# # #     def on_datachannel(channel):
# # #         logger.info(f"DataChannel '{channel.label}' established.")
# # #         @channel.on("message")
# # #         async def message_handler(message: str):
# # #             try:
# # #                 data = json.loads(message)
# # #                 await process_chat_request(prompt=data["prompt"], session_id=data["sessionId"], data_channel=channel)
# # #             except (json.JSONDecodeError, KeyError) as e:
# # #                 logger.error(f"Invalid message format from client: {message}. Error: {e}")
# # #                 safe_send(channel, json.dumps({"type": "chat_message", "content": "Error: Invalid message format."}))
# # #     try:
# # #         while True:
# # #             data = await websocket.receive_json()
# # #             if data["type"] == "offer":
# # #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# # #                 await pc.setRemoteDescription(offer)
# # #                 answer = await pc.createAnswer()
# # #                 await pc.setLocalDescription(answer)
# # #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# # #     except WebSocketDisconnect: logger.info("WebSocket connection closed.")
# # #     finally:
# # #         if pc in pcs:
# # #             await pc.close()
# # #             pcs.remove(pc)
# # #             logger.info("PeerConnection closed and removed.")

# # # @app.on_event("shutdown")
# # # async def on_shutdown():
# # #     logger.info("Application shutting down. Closing all connections.")
# # #     coros = [pc.close() for pc in pcs]
# # #     await asyncio.gather(*coros)
# # #     pcs.clear()
# # #     pool = await db_utils.get_pool()
# # #     if pool: await pool.close()
# # #     logger.info("Cleanup complete.")

# # # @app.get("/", tags=["Health Check"])
# # # async def read_root(): return {"status": "Enhanced Bridge API Orchestrator is running"}
# # # # import json
# # # # import logging
# # # # import asyncio
# # # # from typing import List, Optional, Any, Dict, Set

# # # # import httpx
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # from pydantic import BaseModel

# # # # from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
# # # # import db_utils  # Our custom module for database interactions

# # # # # --- STEP 1: BOILERPLATE AND CONFIGURATION ---

# # # # # Setup clear, timestamped logging for easy debugging during the demo.
# # # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # # # logger = logging.getLogger(__name__)

# # # # # Centralized configuration for all external services.
# # # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # # CRUD_API_URL = "http://localhost:8000"
# # # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # # # Initialize the FastAPI application.
# # # # app = FastAPI(
# # # #     title="Persistent Real-Time Autonomous Agent API",
# # # #     description="Bridge API with WebRTC and PostgreSQL persistence for chat history.",
# # # #     version="14.0.0", # Final Demo Version
# # # # )
# # # # # Enable CORS to allow the React frontend (running on a different port) to communicate with this API.
# # # # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # # # # --- Global State & WebRTC Configuration ---

# # # # # A global set to keep track of all active RTCPeerConnection objects for graceful shutdown.
# # # # pcs: Set[RTCPeerConnection] = set()

# # # # # WebRTC ICE server configuration.
# # # # # We prioritize our local TURN server for offline reliability, a key feature for telco demos.
# # # # # We include Google's public STUN server as a fallback for standard NAT traversal.
# # # # pc_config = RTCConfiguration(
# # # #     iceServers=[
# # # #         RTCIceServer(urls=["turn:127.0.0.1:3478"], username="demo", credential="password"),
# # # #         RTCIceServer(urls=["stun:stun.l.google.com:1932"])
# # # #     ]
# # # # )

# # # # # A mapping of tool names that modify data to the resource they affect.
# # # # # This allows us to send targeted real-time UI update signals.
# # # # TOOL_TO_RESOURCE_MAP = {
# # # #     "create_todo_list": "todos", "update_todo_list": "todos", "delete_todo_list": "todos",
# # # #     "create_todo_item": "todos", "update_todo_item": "todos", "delete_todo_item": "todos",
# # # # }

# # # # # Pydantic model for the HTTP fallback endpoint.
# # # # class ChatRequest(BaseModel):
# # # #     prompt: str

# # # # # --- STEP 2: THE AI AGENT'S "BRAIN" ---

# # # # # The system prompt is the constitution for our AI agent, defining its behavior and rules.
# # # # SYSTEM_PROMPT = """
# # # # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:
# # # # 1. **Analyze the User's Goal:** Understand the user's ultimate objective.
# # # # 2. **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # # # 3. **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # # # 4. **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # # # 5. **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # # # """

# # # # # The tool schema is the menu of actions the AI agent can choose from.
# # # # tools_schema = [
# # # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
# # # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists", "parameters": {"type": "object", "properties": {}}}},
# # # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}}, "required": ["list_id"]}}},
# # # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "title": {"type": "string"}}, "required": ["list_id", "title"]}}},
# # # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # # ]

# # # # # --- STEP 3: CORE APPLICATION LOGIC ---

# # # # async def execute_tool(tool_name: str, args: dict) -> str:
# # # #     """This function acts as a translator, converting the AI's tool call into a concrete HTTP request to our CRUD API."""
# # # #     endpoints = {
# # # #         "create_todo_list": ("POST", "/lists/"), "get_all_todo_lists": ("GET", "/lists/"),
# # # #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"), "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# # # #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"), "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# # # #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # #     }
# # # #     if tool_name not in endpoints: return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})
# # # #     method, endpoint = endpoints[tool_name]
# # # #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}
# # # #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# # # #         try:
# # # #             response = await client.request(method, endpoint, json=json_body)
# # # #             response.raise_for_status()
# # # #             if response.status_code == 204: return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
# # # #             return json.dumps(response.json())
# # # #         except httpx.RequestError as e: return json.dumps({"status": "error", "detail": f"Could not connect to data service: {e}"})
# # # #         except Exception as e: return json.dumps({"status": "error", "detail": str(e)})

# # # # def safe_send(data_channel, message: str):
# # # #     """
# # # #     A robust wrapper for sending messages. It checks if the data channel is still open
# # # #     before sending, preventing `InvalidStateError` race conditions if the connection
# # # #     closes while the agent is processing.
# # # #     """
# # # #     try:
# # # #         if data_channel and data_channel.readyState == "open":
# # # #             data_channel.send(message)
# # # #         else:
# # # #             logger.warning(f"Could not send message: Data channel is not in 'open' state (current state: {data_channel.readyState if data_channel else 'None'}).")
# # # #     except Exception as e:
# # # #         logger.error(f"An unexpected error occurred during safe_send: {e}")

# # # # async def process_chat_request(prompt: str, session_id: int, data_channel):
# # # #     """
# # # #     The core agent loop. It loads chat history for context, orchestrates the multi-turn
# # # #     conversation with the LLM and tools, and sends messages back over the provided data_channel.
# # # #     """
# # # #     logger.info(f"Agent processing prompt for session {session_id}: '{prompt}'")
# # # #     await db_utils.save_message(session_id, "user", prompt)
# # # #     history_records = await db_utils.fetch_session_messages(session_id)
# # # #     messages = [{"role": record["role"], "content": record["content"]} for record in history_records]
# # # #     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
# # # #     max_turns = 5
# # # #     for turn in range(max_turns):
# # # #         try:
# # # #             async with httpx.AsyncClient(timeout=30.0) as client:
# # # #                 response = await client.post(
# # # #                     f"{LM_STUDIO_API_URL}/chat/completions",
# # # #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# # # #                 )
# # # #                 response.raise_for_status()
# # # #                 assistant_message = response.json()["choices"][0]["message"]
# # # #                 messages.append(assistant_message)

# # # #                 if not assistant_message.get("tool_calls"):
# # # #                     logger.info("Agent finished. Saving and sending final chat message.")
# # # #                     final_content = assistant_message.get("content", "Done.")
# # # #                     await db_utils.save_message(session_id, "assistant", final_content)
# # # #                     safe_send(data_channel, json.dumps({"type": "chat_message", "content": final_content}))
# # # #                     return

# # # #                 tool_call = assistant_message["tool_calls"][0]
# # # #                 tool_name = tool_call["function"]["name"]
# # # #                 tool_args = json.loads(tool_call["function"]["arguments"])
# # # #                 tool_result_str = await execute_tool(tool_name, tool_args)
                
# # # #                 try:
# # # #                     tool_result_obj = json.loads(tool_result_str)
# # # #                     is_successful = False
# # # #                     if isinstance(tool_result_obj, dict) and "success" in tool_result_obj.get("status", ""): is_successful = True
# # # #                     elif tool_name in TOOL_TO_RESOURCE_MAP and isinstance(tool_result_obj, dict): is_successful = True
                    
# # # #                     if is_successful:
# # # #                         resource = TOOL_TO_RESOURCE_MAP[tool_name]
# # # #                         push_message = {"type": "state_change", "resource": resource}
# # # #                         logger.info(f"SUCCESS: Pushing state change for '{tool_name}' on resource '{resource}'")
# # # #                         safe_send(data_channel, json.dumps(push_message))
# # # #                 except (json.JSONDecodeError, AttributeError):
# # # #                     logger.warning(f"Could not determine success status for tool '{tool_name}'. No UI sync will be pushed.")

# # # #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_name, "content": tool_result_str})
# # # #         except Exception as e:
# # # #             logger.error(f"Error in agent loop (Turn {turn+1}): {e}")
# # # #             error_content = "I encountered an error. Please try again."
# # # #             await db_utils.save_message(session_id, "assistant", error_content)
# # # #             safe_send(data_channel, json.dumps({"type": "chat_message", "content": error_content}))
# # # #             return
# # # #     logger.warning("Agent exceeded max turns.")
# # # #     final_content = "That request is a bit too complex."
# # # #     await db_utils.save_message(session_id, "assistant", final_content)
# # # #     safe_send(data_channel, json.dumps({"type": "chat_message", "content": final_content}))

# # # # # --- STEP 4: API ENDPOINTS AND LIFECYCLE EVENTS ---

# # # # @app.on_event("startup")
# # # # async def startup_event():
# # # #     """Initializes the database connection pool when the application starts."""
# # # #     await db_utils.get_pool()

# # # # @app.get("/sessions/user/{user_id}", tags=["Chat Sessions"])
# # # # async def get_user_sessions(user_id: int):
# # # #     """Endpoint to fetch all chat sessions for our demo user."""
# # # #     sessions = await db_utils.fetch_user_sessions(user_id)
# # # #     return [dict(session) for session in sessions]

# # # # @app.post("/sessions/user/{user_id}", status_code=201, tags=["Chat Sessions"])
# # # # async def create_session(user_id: int):
# # # #     """Endpoint to create a new, empty chat session."""
# # # #     session = await db_utils.create_new_session(user_id)
# # # #     return dict(session)

# # # # @app.get("/sessions/{session_id}/messages", tags=["Chat Sessions"])
# # # # async def get_session_messages(session_id: int):
# # # #     """Endpoint to fetch the full message history for a specific session."""
# # # #     messages = await db_utils.fetch_session_messages(session_id)
# # # #     return [dict(msg) for msg in messages]

# # # # @app.websocket("/ws")
# # # # async def websocket_endpoint(websocket: WebSocket):
# # # #     """
# # # #     Handles the signaling for the WebRTC connection. This is the 'matchmaker'
# # # #     that allows the client and server to exchange connection details (SDP).
# # # #     """
# # # #     await websocket.accept()
# # # #     pc = RTCPeerConnection(configuration=pc_config)
# # # #     pcs.add(pc)

# # # #     @pc.on("datachannel")
# # # #     def on_datachannel(channel):
# # # #         logger.info(f"DataChannel '{channel.label}' established.")
# # # #         @channel.on("message")
# # # #         async def message_handler(message: str):
# # # #             try:
# # # #                 data = json.loads(message)
# # # #                 prompt = data["prompt"]
# # # #                 session_id = data["sessionId"]
# # # #                 await process_chat_request(prompt=prompt, session_id=session_id, data_channel=channel)
# # # #             except (json.JSONDecodeError, KeyError) as e:
# # # #                 logger.error(f"Invalid message format from client: {message}. Error: {e}")
# # # #                 safe_send(channel, json.dumps({"type": "chat_message", "content": "Error: Invalid message format."}))
# # # #     try:
# # # #         while True:
# # # #             data = await websocket.receive_json()
# # # #             if data["type"] == "offer":
# # # #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# # # #                 await pc.setRemoteDescription(offer)
# # # #                 answer = await pc.createAnswer()
# # # #                 await pc.setLocalDescription(answer)
# # # #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# # # #     except WebSocketDisconnect:
# # # #         logger.info("WebSocket connection closed.")
# # # #     finally:
# # # #         if pc in pcs:
# # # #             await pc.close()
# # # #             pcs.remove(pc)
# # # #             logger.info("PeerConnection closed and removed.")

# # # # @app.on_event("shutdown")
# # # # async def on_shutdown():
# # # #     """Gracefully closes all active connections when the server is shut down."""
# # # #     logger.info("Application shutting down. Closing all connections.")
# # # #     coros = [pc.close() for pc in pcs]
# # # #     await asyncio.gather(*coros)
# # # #     pcs.clear()
# # # #     pool = await db_utils.get_pool()
# # # #     if pool:
# # # #         await pool.close()
# # # #     logger.info("Cleanup complete.")

# # # # @app.get("/", tags=["Health Check"])
# # # # async def read_root():
# # # #     return {"status": "Bridge API Orchestrator is running"}
# # # # # import json
# # # # # import logging
# # # # # import asyncio
# # # # # from typing import List, Optional, Any, Dict, Set

# # # # # import httpx
# # # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # from pydantic import BaseModel

# # # # # from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
# # # # # import db.db_utils 
# # # # # # --- LAYER 1: LOGGING ---
# # # # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # # # # logger = logging.getLogger(__name__)

# # # # # # --- Configuration ---
# # # # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # # # CRUD_API_URL = "http://localhost:8000"
# # # # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # # # # --- API Setup ---
# # # # # app = FastAPI(
# # # # #     title="Real-Time Autonomous Agent API",
# # # # #     description="Bridge API with WebRTC for real-time tool use and HTTP fallback.",
# # # # #     version="12.0.0", # Final Demo Version
# # # # # )
# # # # # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # # # # # --- Global State ---
# # # # # pcs: Set[RTCPeerConnection] = set()
# # # # # # ** UPDATED: Prioritize local TURN, fallback to Google STUN **
# # # # # pc_config = RTCConfiguration(
# # # # #     iceServers=[
# # # # #         RTCIceServer(
# # # # #             urls=["turn:127.0.0.1:3478"],
# # # # #             username="demo",
# # # # #             credential="password"
# # # # #         ),
# # # # #         RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# # # # #     ]
# # # # # )

# # # # # TOOL_TO_RESOURCE_MAP = {
# # # # #     "create_todo_list": "todos",
# # # # #     "update_todo_list": "todos",
# # # # #     "delete_todo_list": "todos",
# # # # #     "create_todo_item": "todos",
# # # # #     "update_todo_item": "todos",
# # # # #     "delete_todo_item": "todos",
# # # # # }

# # # # # # --- Pydantic Models ---
# # # # # class ChatRequest(BaseModel):
# # # # #     prompt: str

# # # # # # --- PROMPT & TOOL DEFINITIONS ---
# # # # # SYSTEM_PROMPT = """
# # # # # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:
# # # # # 1. **Analyze the User's Goal:** Understand the user's ultimate objective.
# # # # # 2. **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # # # # 3. **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # # # # 4. **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # # # # 5. **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # # # # """

# # # # # tools_schema = [
# # # # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
# # # # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
# # # # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list by its ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
# # # # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
# # # # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # # # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # # # ]

# # # # # # --- CORE LOGIC ---

# # # # # async def execute_tool(tool_name: str, args: dict) -> str:
# # # # #     """Calls the CRUD API and returns the result as a JSON string."""
# # # # #     endpoints = {
# # # # #         "create_todo_list": ("POST", "/lists/"), "get_all_todo_lists": ("GET", "/lists/"),
# # # # #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"), "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# # # # #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"), "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# # # # #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # #     }
# # # # #     if tool_name not in endpoints:
# # # # #         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

# # # # #     method, endpoint = endpoints[tool_name]
# # # # #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}
# # # # #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# # # # #         try:
# # # # #             response = await client.request(method, endpoint, json=json_body)
# # # # #             response.raise_for_status()
# # # # #             if response.status_code == 204:
# # # # #                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
# # # # #             return json.dumps(response.json())
# # # # #         except httpx.RequestError as e:
# # # # #             return json.dumps({"status": "error", "detail": f"Could not connect to data service: {e}"})
# # # # #         except Exception as e:
# # # # #             return json.dumps({"status": "error", "detail": str(e)})



# # # # # @app.get("/sessions/user/{user_id}", tags=["Chat Sessions"])
# # # # # async def get_user_sessions(user_id: int):
# # # # #     sessions = await db.db_utils.fetch_user_sessions(user_id)
# # # # #     return [dict(session) for session in sessions]

# # # # # @app.post("/sessions/user/{user_id}", status_code=201, tags=["Chat Sessions"])
# # # # # async def create_session(user_id: int):
# # # # #     session = await db.db_utils.create_new_session(user_id)
# # # # #     return dict(session)

# # # # # @app.get("/sessions/{session_id}/messages", tags=["Chat Sessions"])
# # # # # async def get_session_messages(session_id: int):
# # # # #     messages = await db.db_utils.fetch_session_messages(session_id)
# # # # #     return [dict(msg) for msg in messages]


# # # # # async def process_chat_request(prompt: str, data_channel):
# # # # #     """The core agent loop, which sends messages back over the provided data_channel."""
# # # # #     logger.info(f"Agent processing prompt: '{prompt}'")
# # # # #     await db.db_utils.save_message(session_id, "user", prompt)
    
# # # # #     # 2. Load the recent history for context
# # # # #     history_records = await db.db_utils.fetch_session_messages(session_id)
# # # # #     # Convert records to the format the LLM expects
# # # # #     messages = [{"role": record["role"], "content": record["content"]} for record in history_records]
    
# # # # #     # Prepend the system prompt
# # # # #     messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
# # # # #     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
# # # # #     max_turns = 5
# # # # #     for turn in range(max_turns):
# # # # #         try:
# # # # #             async with httpx.AsyncClient(timeout=30.0) as client:
# # # # #                 response = await client.post(
# # # # #                     f"{LM_STUDIO_API_URL}/chat/completions",
# # # # #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# # # # #                 )
# # # # #                 response.raise_for_status()
# # # # #                 message = response.json()["choices"][0]["message"]
# # # # #                 messages.append(message)
# # # # #                 if not message.get("tool_calls"):
# # # # #                     logger.info("Agent finished. Sending final chat message.")
# # # # #                     data_channel.send(json.dumps({"type": "chat_message", "content": message.get("content", "Done.")}))
# # # # #                     return
# # # # #                 tool_call = message["tool_calls"][0]
# # # # #                 tool_name = tool_call["function"]["name"]
# # # # #                 tool_args = json.loads(tool_call["function"]["arguments"])
# # # # #                 logger.info(f"Agent calling tool '{tool_name}'")
# # # # #                 tool_result_str = await execute_tool(tool_name, tool_args)
# # # # #                 try:
# # # # #                     tool_result_obj = json.loads(tool_result_str)
# # # # #                     is_successful = False
# # # # #                     if isinstance(tool_result_obj, dict) and "success" in tool_result_obj.get("status", ""):
# # # # #                         is_successful = True
# # # # #                     elif tool_name in TOOL_TO_RESOURCE_MAP and isinstance(tool_result_obj, dict):
# # # # #                         is_successful = True
# # # # #                     if is_successful:
# # # # #                         resource = TOOL_TO_RESOURCE_MAP[tool_name]
# # # # #                         push_message = {"type": "state_change", "resource": resource}
# # # # #                         logger.info(f"SUCCESS: Pushing state change for '{tool_name}' on resource '{resource}'")
# # # # #                         data_channel.send(json.dumps(push_message))
# # # # #                 except (json.JSONDecodeError, AttributeError):
# # # # #                     logger.warning(f"Could not determine success status for tool '{tool_name}'. No UI sync will be pushed.")
# # # # #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_name, "content": tool_result_str})
# # # # #         except Exception as e:
# # # # #             logger.error(f"Error in agent loop (Turn {turn+1}): {e}")
# # # # #             data_channel.send(json.dumps({"type": "chat_message", "content": "I encountered an error. Please try again."}))
# # # # #             return
# # # # #     logger.warning("Agent exceeded max turns.")
# # # # #     data_channel.send(json.dumps({"type": "chat_message", "content": "That request is a bit too complex."}))


# # # # # # --- API ENDPOINTS ---

# # # # # @app.websocket("/ws")
# # # # # async def websocket_endpoint(websocket: WebSocket):
# # # # #     await websocket.accept()
# # # # #     pc = RTCPeerConnection(configuration=pc_config)
# # # # #     pcs.add(pc)

# # # # #     @pc.on("icecandidate")
# # # # #     async def on_icecandidate(candidate):
# # # # #         if candidate and "typ relay" in str(candidate): logger.info(f"Using TURN relay candidate: {candidate.sdp}")
# # # # #         elif candidate and "typ srflx" in str(candidate): logger.info(f"Using STUN server reflexive candidate: {candidate.sdp}")

# # # # #     @pc.on("datachannel")
# # # # #     def on_datachannel(channel):
# # # # #         logger.info(f"DataChannel '{channel.label}' created.")
# # # # #         @channel.on("message")
# # # # #         async def message_handler(message: str):
# # # # #             await process_chat_request(prompt=message, data_channel=channel)
# # # # #     try:
# # # # #         while True:
# # # # #             data = await websocket.receive_json()
# # # # #             if data["type"] == "offer":
# # # # #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# # # # #                 await pc.setRemoteDescription(offer)
# # # # #                 answer = await pc.createAnswer()
# # # # #                 await pc.setLocalDescription(answer)
# # # # #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# # # # #     except WebSocketDisconnect:
# # # # #         logger.info("WebSocket connection closed.")
# # # # #     finally:
# # # # #         if pc in pcs:
# # # # #             await pc.close()
# # # # #             pcs.remove(pc)
# # # # #             logger.info("PeerConnection closed and removed.")

# # # # # @app.on_event("shutdown")
# # # # # async def on_shutdown():
# # # # #     logger.info("Application shutting down. Closing all peer connections.")
# # # # #     coros = [pc.close() for pc in pcs]
# # # # #     await asyncio.gather(*coros)
# # # # #     pcs.clear()

# # # # # @app.get("/", tags=["Health Check"])
# # # # # async def read_root(): return {"status": "Bridge API Orchestrator is running"}
# # # # # # import json
# # # # # # import logging
# # # # # # import asyncio
# # # # # # from typing import List, Optional, Any, Dict, Set

# # # # # # import httpx
# # # # # # from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # from pydantic import BaseModel

# # # # # # from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

# # # # # # # --- LAYER 1: LOGGING ---
# # # # # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # # # # # logger = logging.getLogger(__name__)

# # # # # # # --- Configuration ---
# # # # # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # # # # CRUD_API_URL = "http://localhost:8000"
# # # # # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # # # # # --- API Setup ---
# # # # # # app = FastAPI(
# # # # # #     title="Real-Time Autonomous Agent API",
# # # # # #     description="Bridge API with WebRTC for real-time tool use and HTTP fallback.",
# # # # # #     version="11.0.0", # Version bump for the fix
# # # # # # )
# # # # # # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # # # # # # --- Global State ---
# # # # # # pcs: Set[RTCPeerConnection] = set()
# # # # # # # pc_config = RTCConfiguration(iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])])
# # # # # # pc_config = RTCConfiguration(
# # # # # #     iceServers=[
# # # # # #         RTCIceServer(
# # # # # #             urls=["turn:127.0.0.1:3478"],  # Standard TURN port
# # # # # #             username="demo",
# # # # # #             credential="password"
# # # # # #         )
# # # # # #     ]
# # # # # # )

# # # # # # TOOL_TO_RESOURCE_MAP = {
# # # # # #     "create_todo_list": "todos",
# # # # # #     "update_todo_list": "todos",
# # # # # #     "delete_todo_list": "todos",
# # # # # #     "create_todo_item": "todos",
# # # # # #     "update_todo_item": "todos",
# # # # # #     "delete_todo_item": "todos",
# # # # # # }

# # # # # # # --- Pydantic Models ---
# # # # # # class ChatRequest(BaseModel):
# # # # # #     prompt: str

# # # # # # # --- PROMPT & TOOL DEFINITIONS ---
# # # # # # SYSTEM_PROMPT = """
# # # # # # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:
# # # # # # 1. **Analyze the User's Goal:** Understand the user's ultimate objective.
# # # # # # 2. **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # # # # # 3. **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # # # # # 4. **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # # # # # 5. **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # # # # # """

# # # # # # tools_schema = [
# # # # # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
# # # # # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
# # # # # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list by its ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
# # # # # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
# # # # # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # # # # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # # # # ]

# # # # # # # --- CORE LOGIC ---

# # # # # # async def execute_tool(tool_name: str, args: dict) -> str:
# # # # # #     """Calls the CRUD API and returns the result as a JSON string."""
# # # # # #     endpoints = {
# # # # # #         "create_todo_list": ("POST", "/lists/"),
# # # # # #         "get_all_todo_lists": ("GET", "/lists/"),
# # # # # #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
# # # # # #         "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# # # # # #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
# # # # # #         "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# # # # # #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # #     }
# # # # # #     if tool_name not in endpoints:
# # # # # #         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

# # # # # #     method, endpoint = endpoints[tool_name]
# # # # # #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

# # # # # #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# # # # # #         try:
# # # # # #             response = await client.request(method, endpoint, json=json_body)
# # # # # #             response.raise_for_status()
# # # # # #             if response.status_code == 204:
# # # # # #                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
# # # # # #             return json.dumps(response.json())
# # # # # #         except httpx.RequestError as e:
# # # # # #             return json.dumps({"status": "error", "detail": f"Could not connect to data service: {e}"})
# # # # # #         except Exception as e:
# # # # # #             return json.dumps({"status": "error", "detail": str(e)})


# # # # # # async def process_chat_request(prompt: str, data_channel):
# # # # # #     """The core agent loop, which sends messages back over the provided data_channel."""
# # # # # #     logger.info(f"Agent processing prompt: '{prompt}'")
# # # # # #     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
# # # # # #     max_turns = 5

# # # # # #     for turn in range(max_turns):
# # # # # #         try:
# # # # # #             async with httpx.AsyncClient(timeout=30.0) as client:
# # # # # #                 response = await client.post(
# # # # # #                     f"{LM_STUDIO_API_URL}/chat/completions",
# # # # # #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# # # # # #                 )
# # # # # #                 response.raise_for_status()
# # # # # #                 message = response.json()["choices"][0]["message"]
# # # # # #                 messages.append(message)

# # # # # #                 if not message.get("tool_calls"):
# # # # # #                     logger.info("Agent finished. Sending final chat message.")
# # # # # #                     data_channel.send(json.dumps({"type": "chat_message", "content": message.get("content", "Done.")}))
# # # # # #                     return

# # # # # #                 tool_call = message["tool_calls"][0]
# # # # # #                 tool_name = tool_call["function"]["name"]
# # # # # #                 tool_args = json.loads(tool_call["function"]["arguments"])
                
# # # # # #                 logger.info(f"Agent calling tool '{tool_name}'")
# # # # # #                 tool_result_str = await execute_tool(tool_name, tool_args)
                
# # # # # #                 # --- CORRECTED ROBUST SUCCESS CHECK ---
# # # # # #                 try:
# # # # # #                     tool_result_obj = json.loads(tool_result_str)
# # # # # #                     is_successful = False
                    
# # # # # #                     # Condition 1: The tool returned a specific "success" status (e.g., from a DELETE).
# # # # # #                     if isinstance(tool_result_obj, dict) and "success" in tool_result_obj.get("status", ""):
# # # # # #                         is_successful = True
                    
# # # # # #                     # Condition 2: The tool is a known state-changer and it returned a valid object.
# # # # # #                     # This covers create/update operations that return the new object.
# # # # # #                     elif tool_name in TOOL_TO_RESOURCE_MAP and isinstance(tool_result_obj, dict):
# # # # # #                         is_successful = True
                        
# # # # # #                     # Now, if any success condition was met, send the signal.
# # # # # #                     if is_successful:
# # # # # #                         resource = TOOL_TO_RESOURCE_MAP[tool_name]
# # # # # #                         push_message = {"type": "state_change", "resource": resource}
# # # # # #                         logger.info(f"SUCCESS: Pushing state change for '{tool_name}' on resource '{resource}'")
# # # # # #                         data_channel.send(json.dumps(push_message))
                
# # # # # #                 except (json.JSONDecodeError, AttributeError):
# # # # # #                     # This will catch malformed JSON or if tool_result_obj is not a dict/list
# # # # # #                     logger.warning(f"Could not determine success status for tool '{tool_name}'. No UI sync will be pushed.")
# # # # # #                     pass

# # # # # #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_name, "content": tool_result_str})

# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Error in agent loop (Turn {turn+1}): {e}")
# # # # # #             data_channel.send(json.dumps({"type": "chat_message", "content": "I encountered an error. Please try again."}))
# # # # # #             return

# # # # # #     logger.warning("Agent exceeded max turns.")
# # # # # #     data_channel.send(json.dumps({"type": "chat_message", "content": "That request is a bit too complex."}))


# # # # # # # --- API ENDPOINTS ---

# # # # # # @app.websocket("/ws")
# # # # # # async def websocket_endpoint(websocket: WebSocket):
# # # # # #     await websocket.accept()
# # # # # #     pc = RTCPeerConnection(configuration=pc_config)
# # # # # #     pcs.add(pc)

# # # # # #     @pc.on("datachannel")
# # # # # #     def on_datachannel(channel):
# # # # # #         logger.info(f"DataChannel '{channel.label}' created.")
        
# # # # # #         @channel.on("message")
# # # # # #         async def message_handler(message: str):
# # # # # #             await process_chat_request(prompt=message, data_channel=channel)

# # # # # #     try:
# # # # # #         while True:
# # # # # #             data = await websocket.receive_json()
# # # # # #             if data["type"] == "offer":
# # # # # #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# # # # # #                 await pc.setRemoteDescription(offer)
# # # # # #                 answer = await pc.createAnswer()
# # # # # #                 await pc.setLocalDescription(answer)
# # # # # #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# # # # # #     except WebSocketDisconnect:
# # # # # #         logger.info("WebSocket connection closed.")
# # # # # #     finally:
# # # # # #         if pc in pcs:
# # # # # #             await pc.close()
# # # # # #             pcs.remove(pc)
# # # # # #             logger.info("PeerConnection closed and removed.")


# # # # # # @app.on_event("shutdown")
# # # # # # async def on_shutdown():
# # # # # #     logger.info("Application shutting down. Closing all peer connections.")
# # # # # #     coros = [pc.close() for pc in pcs]
# # # # # #     await asyncio.gather(*coros)
# # # # # #     pcs.clear()

# # # # # # @app.get("/", tags=["Health Check"])
# # # # # # async def read_root():
# # # # # #     return {"status": "Bridge API Orchestrator is running"}

# # # # # # @app.post("/chat_http", tags=["Testing"])
# # # # # # async def handle_chat_http(request: ChatRequest):
# # # # # #     """A dummy HTTP endpoint for simple testing without needing a WebRTC client."""
# # # # # #     class PrintChannel:
# # # # # #         def send(self, msg):
# # # # # #             print(f"[HTTP Fallback Send]: {msg}")

# # # # # #     # Note: This fallback does not support real-time UI updates.
# # # # # #     await process_chat_request(request.prompt, PrintChannel())
# # # # # #     return {"status": "Request processed. Check server logs for output."}

# # # # # # # # bridge_api.py (Version 8 - Autonomous Agent)
# # # # # # # import json
# # # # # # # import logging
# # # # # # # import asyncio # <-- Add this

# # # # # # # # Third-party imports
# # # # # # # import httpx
# # # # # # # from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect # <-- Add WebSocket imports
# # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # from pydantic import BaseModel, Field, ValidationError
# # # # # # # from typing import List, Optional, Any, Dict, Set # <-- Add Set

# # # # # # # # aiortc imports for WebRTC
# # # # # # # from aiortc import RTCPeerConnection, RTCSessionDescription # <-- Add this
# # # # # # # # from aiortc.contrib.media import MediaStreamTrack 

# # # # # # # # --- LAYER 1: LOGGING ---
# # # # # # # # Set up a logger to get clear, timestamped output.
# # # # # # # logging.basicConfig(
# # # # # # #     level=logging.INFO,
# # # # # # #     format='%(asctime)s - %(levelname)s - %(message)s',
# # # # # # # )
# # # # # # # logger = logging.getLogger(__name__)

# # # # # # # # --- Configuration ---
# # # # # # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # # # # # CRUD_API_URL = "http://localhost:8000"
# # # # # # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # # # # # # --- API Setup ---
# # # # # # # app = FastAPI(
# # # # # # #     title="Autonomous Agent Bridge API",
# # # # # # #     description="An advanced bridge API that enables multi-step tool use for complex tasks.",
# # # # # # #     version="7.0.0",
# # # # # # # )
# # # # # # # app.add_middleware(
# # # # # # #     CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # # # # # # )

# # # # # # # pcs: Set[RTCPeerConnection] = set()

# # # # # # # # Configuration for the STUN server
# # # # # # # # We don't need this on the server if the client provides it,
# # # # # # # # but it's good practice to be aware of the configuration.
# # # # # # # pc_config = {"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]}


# # # # # # # # --- NEW: The Signaling and WebRTC Endpoint ---
# # # # # # # @app.websocket("/ws")
# # # # # # # async def websocket_endpoint(websocket: WebSocket):
# # # # # # #     await websocket.accept()
# # # # # # #     logger.info("WebSocket connection accepted.")
    
# # # # # # #     # Create a new peer connection for this client
# # # # # # #     pc = RTCPeerConnection(configuration=pc_config) # type: ignore
# # # # # # #     pcs.add(pc)

# # # # # # #     # --- This is where the magic happens ---
# # # # # # #     # Define what to do when the Data Channel is created by the client
# # # # # # #     @pc.on("datachannel")
# # # # # # #     def on_datachannel(channel):
# # # # # # #         logger.info(f"DataChannel '{channel.label}' created.")
        
# # # # # # #         @channel.on("message")
# # # # # # #         async def on_message(message):
# # # # # # #             logger.info(f"Received message via DataChannel: {message}")
            
# # # # # # #             # Here we will eventually trigger the tool-use loop
# # # # # # #             # For now, let's just echo the message back
# # # # # # #             response_message = f"Server received: {message}"
# # # # # # #             logger.info(f"Sending response via DataChannel: {response_message}")
# # # # # # #             channel.send(response_message)

# # # # # # #     # Main loop to handle signaling messages from the client
# # # # # # #     try:
# # # # # # #         while True:
# # # # # # #             data = await websocket.receive_json()
            
# # # # # # #             # The client is sending its SDP offer
# # # # # # #             if data["type"] == "offer":
# # # # # # #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# # # # # # #                 logger.info("Received SDP Offer from client.")
                
# # # # # # #                 await pc.setRemoteDescription(offer)
                
# # # # # # #                 # Create an SDP answer
# # # # # # #                 answer = await pc.createAnswer()
# # # # # # #                 await pc.setLocalDescription(answer)
                
# # # # # # #                 # Send the answer back to the client via the websocket
# # # # # # #                 logger.info("Sending SDP Answer to client.")
# # # # # # #                 await websocket.send_json({
# # # # # # #                     "type": "answer",
# # # # # # #                     "sdp": pc.localDescription.sdp,
# # # # # # #                 })

# # # # # # #             # The client is sending an ICE candidate
# # # # # # #             # (This part is often handled automatically by aiortc, but explicit handling is robust)
# # # # # # #             # For now, we'll assume aiortc handles this implicitly. If we face issues, we add it.

# # # # # # #     except WebSocketDisconnect:
# # # # # # #         logger.info("WebSocket connection closed.")
# # # # # # #     finally:
# # # # # # #         if pc in pcs:
# # # # # # #             await pc.close()
# # # # # # #             pcs.remove(pc)


# # # # # # # # --- Pydantic Models ---
# # # # # # # class ChatRequest(BaseModel):
# # # # # # #     prompt: str

# # # # # # # # --- LAYER 2: VALIDATION MODELS ---
# # # # # # # # Define what a valid tool result from our CRUD API looks like.
# # # # # # # class ToolResult(BaseModel):
# # # # # # #     status: Optional[str] = None
# # # # # # #     message: Optional[str] = None
# # # # # # #     detail: Optional[Any] = None
# # # # # # #     # Use Field(default_factory=list) for mutable defaults
# # # # # # #     items: List[Any] = Field(default_factory=list) 

# # # # # # # # --- PROMPT ENGINEERING:  ---
# # # # # # # # Using your proven, more powerful system prompt.
# # # # # # # SYSTEM_PROMPT = """
# # # # # # # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

# # # # # # # 1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
# # # # # # # 2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # # # # # # 3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # # # # # # 4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # # # # # # 5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # # # # # # """

# # # # # # # # --- TOOL SCHEMA: The second critical change ---
# # # # # # # # Splitting into multiple tools, just like your mcp_todo_server.py.
# # # # # # # # This makes it easier for the model to choose the right action.
# # # # # # # tools_schema = [
# # # # # # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
# # # # # # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
# # # # # # #     {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}}, "required": ["list_id"]}}},
# # # # # # #     {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}, "title": {"type": "string", "description": "The new title"}}, "required": ["list_id", "title"]}}},
# # # # # # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
# # # # # # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
# # # # # # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # # # # # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # # # # # ]

# # # # # # # # --- Tool Execution Logic (Orchestrator) ---
# # # # # # # # This function calls your CRUD API based on the tool name and arguments.
# # # # # # # async def execute_tool(tool_name: str, args: dict) -> str:
# # # # # # #     """Calls the CRUD API, now with robust error handling and validation."""
# # # # # # #     endpoints = {
# # # # # # #         "create_todo_list": ("POST", "/lists/"),
# # # # # # #         "get_all_todo_lists": ("GET", "/lists/"),
# # # # # # #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
# # # # # # #         "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# # # # # # #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
# # # # # # #         "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# # # # # # #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # # #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # # #     }
# # # # # # #     if tool_name not in endpoints:
# # # # # # #         logger.error(f"Attempted to call an unknown tool: {tool_name}")
# # # # # # #         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

# # # # # # #     method, endpoint = endpoints[tool_name]
# # # # # # #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

    
# # # # # # #     # LAYER 3: Use a client with a configured timeout
# # # # # # #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# # # # # # #         try:
# # # # # # #             logger.info(f"Executing tool '{tool_name}' -> {method} {CRUD_API_URL}{endpoint}")
# # # # # # #             response = await client.request(method, endpoint, json=json_body)
# # # # # # #             response.raise_for_status() # Raises exception for 4xx/5xx responses
            
# # # # # # #             if response.status_code == 204:
# # # # # # #                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
            
# # # # # # #             # Layer 2 Validation: Parse and validate the response from the CRUD API
# # # # # # #             try:
# # # # # # #                 # Assuming the CRUD API can return a single object or a list of objects
# # # # # # #                 raw_data = response.json()
# # # # # # #                 # We can add more specific Pydantic models here if needed
# # # # # # #                 logger.info(f"Tool '{tool_name}' executed successfully.")
# # # # # # #                 return json.dumps(raw_data)
# # # # # # #             except (json.JSONDecodeError, ValidationError) as e:
# # # # # # #                 logger.error(f"Validation Error from CRUD API for tool '{tool_name}': {e}")
# # # # # # #                 return json.dumps({"status": "error", "detail": "Received an invalid response from the data service."})

# # # # # # #         except httpx.TimeoutException:
# # # # # # #             logger.error(f"Timeout when calling tool '{tool_name}' at {CRUD_API_URL}{endpoint}")
# # # # # # #             return json.dumps({"status": "error", "detail": "The data service took too long to respond."})
# # # # # # #         except httpx.RequestError as e:
# # # # # # #             logger.error(f"Request Error for tool '{tool_name}': {e}")
# # # # # # #             return json.dumps({"status": "error", "detail": "Could not connect to the data service."})
# # # # # # #         except Exception as e:
# # # # # # #             logger.critical(f"An unexpected error occurred during tool execution for '{tool_name}': {e}")
# # # # # # #             return json.dumps({"status": "error", "detail": "An unexpected internal error occurred."})

# # # # # # # # --- Main API Endpoint with Safeguards ---
# # # # # # # @app.post("/chat")
# # # # # # # async def handle_chat(request: ChatRequest):
# # # # # # #     logger.info(f"Received new chat request. Prompt: '{request.prompt}'")

# # # # # # #     # --- LAYER 4: DEMO MAGIC PHRASE ---
# # # # # # #     if request.prompt.strip().lower() == "!reset state":
# # # # # # #         logger.warning("Demo magic phrase '!reset state' used.")
# # # # # # #         return {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

# # # # # # #     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.prompt}]
# # # # # # #     max_turns = 5 # Safety break to prevent infinite loops

# # # # # # #     for turn in range(max_turns):
# # # # # # #         try:
# # # # # # #             async with httpx.AsyncClient(timeout=30.0) as client:
# # # # # # #                 logger.info(f"Agent Turn {turn + 1}: Sending prompt to LLM.")
                
# # # # # # #                 response = await client.post(
# # # # # # #                     f"{LM_STUDIO_API_URL}/chat/completions",
# # # # # # #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# # # # # # #                 )
# # # # # # #                 response.raise_for_status()
# # # # # # #                 choice = response.json()["choices"][0]
# # # # # # #                 message = choice["message"]
# # # # # # #                 messages.append(message)

# # # # # # #                 if not message.get("tool_calls"):
# # # # # # #                     logger.info("Agent finished with a direct response. End of conversation.")
# # # # # # #                     return message

# # # # # # #                 logger.info(f"Agent wants to call a tool: {message['tool_calls'][0]['function']['name']}")
# # # # # # #                 tool_call = message["tool_calls"][0]
# # # # # # #                 tool_result = await execute_tool(
# # # # # # #                     tool_name=tool_call["function"]["name"],
# # # # # # #                     args=json.loads(tool_call["function"]["arguments"])
# # # # # # #                 )
                
# # # # # # #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": tool_result})

# # # # # # #         except httpx.RequestError as e:
# # # # # # #             logger.error(f"Could not contact LM Studio: {e}")
# # # # # # #             raise HTTPException(status_code=502, detail="The connection to the AI model failed.")
# # # # # # #         except Exception as e:
# # # # # # #             logger.critical(f"An unhandled exception occurred in the chat loop: {e}")
# # # # # # #             raise HTTPException(status_code=500, detail="A critical internal error occurred.")
    
# # # # # # #     logger.warning(f"Conversation exceeded max turns ({max_turns}).")
# # # # # # #     return {"role": "assistant", "content": "I'm having a bit of trouble completing that request. Could we try something simpler?"}# # bridge_api.py (Version 6 - Autonomous Agent)

# # # # # # # @app.get("/", tags=["Health Check"])
# # # # # # # async def read_root():
# # # # # # #     return {"status": "Bridge API Orchestrator is running"}

# # # # # # # # # bridge_api.py (Version 7 - Autonomous Agent)
# # # # # # # # import httpx
# # # # # # # # import json
# # # # # # # # import logging
# # # # # # # # from fastapi import FastAPI, HTTPException
# # # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # # from pydantic import BaseModel, Field, ValidationError
# # # # # # # # from typing import List, Optional, Any, Dict


# # # # # # # # # --- LAYER 1: LOGGING ---
# # # # # # # # # Set up a logger to get clear, timestamped output.
# # # # # # # # logging.basicConfig(
# # # # # # # #     level=logging.INFO,
# # # # # # # #     format='%(asctime)s - %(levelname)s - %(message)s',
# # # # # # # # )
# # # # # # # # logger = logging.getLogger(__name__)

# # # # # # # # # --- Configuration ---
# # # # # # # # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # # # # # # # CRUD_API_URL = "http://localhost:8000"
# # # # # # # # MODEL_NAME = "qwen2.5-7b-instruct"

# # # # # # # # # --- API Setup ---
# # # # # # # # app = FastAPI(
# # # # # # # #     title="Autonomous Agent Bridge API",
# # # # # # # #     description="An advanced bridge API that enables multi-step tool use for complex tasks.",
# # # # # # # #     version="7.0.0",
# # # # # # # # )
# # # # # # # # app.add_middleware(
# # # # # # # #     CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # # # # # # # )

# # # # # # # # # --- Pydantic Models ---
# # # # # # # # class ChatRequest(BaseModel):
# # # # # # # #     prompt: str

# # # # # # # # # --- LAYER 2: VALIDATION MODELS ---
# # # # # # # # # Define what a valid tool result from our CRUD API looks like.
# # # # # # # # class ToolResult(BaseModel):
# # # # # # # #     status: Optional[str] = None
# # # # # # # #     message: Optional[str] = None
# # # # # # # #     detail: Optional[Any] = None
# # # # # # # #     # Use Field(default_factory=list) for mutable defaults
# # # # # # # #     items: List[Any] = Field(default_factory=list) 

# # # # # # # # # --- PROMPT ENGINEERING:  ---
# # # # # # # # # Using your proven, more powerful system prompt.
# # # # # # # # SYSTEM_PROMPT = """
# # # # # # # # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

# # # # # # # # 1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
# # # # # # # # 2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # # # # # # # 3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # # # # # # # 4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # # # # # # # 5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # # # # # # # """

# # # # # # # # # --- TOOL SCHEMA: The second critical change ---
# # # # # # # # # Splitting into multiple tools, just like your mcp_todo_server.py.
# # # # # # # # # This makes it easier for the model to choose the right action.
# # # # # # # # tools_schema = [
# # # # # # # #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
# # # # # # # #     {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}}, "required": ["list_id"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}, "title": {"type": "string", "description": "The new title"}}, "required": ["list_id", "title"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# # # # # # # #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # # # # # # # ]

# # # # # # # # # --- Tool Execution Logic (Orchestrator) ---
# # # # # # # # # This function calls your CRUD API based on the tool name and arguments.
# # # # # # # # async def execute_tool(tool_name: str, args: dict) -> str:
# # # # # # # #     """Calls the CRUD API, now with robust error handling and validation."""
# # # # # # # #     endpoints = {
# # # # # # # #         "create_todo_list": ("POST", "/lists/"),
# # # # # # # #         "get_all_todo_lists": ("GET", "/lists/"),
# # # # # # # #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
# # # # # # # #         "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# # # # # # # #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
# # # # # # # #         "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# # # # # # # #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # # # #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# # # # # # # #     }
# # # # # # # #     if tool_name not in endpoints:
# # # # # # # #         logger.error(f"Attempted to call an unknown tool: {tool_name}")
# # # # # # # #         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

# # # # # # # #     method, endpoint = endpoints[tool_name]
# # # # # # # #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

    
# # # # # # # #     # LAYER 3: Use a client with a configured timeout
# # # # # # # #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# # # # # # # #         try:
# # # # # # # #             logger.info(f"Executing tool '{tool_name}' -> {method} {CRUD_API_URL}{endpoint}")
# # # # # # # #             response = await client.request(method, endpoint, json=json_body)
# # # # # # # #             response.raise_for_status() # Raises exception for 4xx/5xx responses
            
# # # # # # # #             if response.status_code == 204:
# # # # # # # #                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
            
# # # # # # # #             # Layer 2 Validation: Parse and validate the response from the CRUD API
# # # # # # # #             try:
# # # # # # # #                 # Assuming the CRUD API can return a single object or a list of objects
# # # # # # # #                 raw_data = response.json()
# # # # # # # #                 # We can add more specific Pydantic models here if needed
# # # # # # # #                 logger.info(f"Tool '{tool_name}' executed successfully.")
# # # # # # # #                 return json.dumps(raw_data)
# # # # # # # #             except (json.JSONDecodeError, ValidationError) as e:
# # # # # # # #                 logger.error(f"Validation Error from CRUD API for tool '{tool_name}': {e}")
# # # # # # # #                 return json.dumps({"status": "error", "detail": "Received an invalid response from the data service."})

# # # # # # # #         except httpx.TimeoutException:
# # # # # # # #             logger.error(f"Timeout when calling tool '{tool_name}' at {CRUD_API_URL}{endpoint}")
# # # # # # # #             return json.dumps({"status": "error", "detail": "The data service took too long to respond."})
# # # # # # # #         except httpx.RequestError as e:
# # # # # # # #             logger.error(f"Request Error for tool '{tool_name}': {e}")
# # # # # # # #             return json.dumps({"status": "error", "detail": "Could not connect to the data service."})
# # # # # # # #         except Exception as e:
# # # # # # # #             logger.critical(f"An unexpected error occurred during tool execution for '{tool_name}': {e}")
# # # # # # # #             return json.dumps({"status": "error", "detail": "An unexpected internal error occurred."})

# # # # # # # # # --- Main API Endpoint with Safeguards ---
# # # # # # # # @app.post("/chat")
# # # # # # # # async def handle_chat(request: ChatRequest):
# # # # # # # #     logger.info(f"Received new chat request. Prompt: '{request.prompt}'")

# # # # # # # #     # --- LAYER 4: DEMO MAGIC PHRASE ---
# # # # # # # #     if request.prompt.strip().lower() == "!reset state":
# # # # # # # #         logger.warning("Demo magic phrase '!reset state' used.")
# # # # # # # #         return {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

# # # # # # # #     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.prompt}]
# # # # # # # #     max_turns = 5 # Safety break to prevent infinite loops

# # # # # # # #     for turn in range(max_turns):
# # # # # # # #         try:
# # # # # # # #             async with httpx.AsyncClient(timeout=30.0) as client:
# # # # # # # #                 logger.info(f"Agent Turn {turn + 1}: Sending prompt to LLM.")
                
# # # # # # # #                 response = await client.post(
# # # # # # # #                     f"{LM_STUDIO_API_URL}/chat/completions",
# # # # # # # #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# # # # # # # #                 )
# # # # # # # #                 response.raise_for_status()
# # # # # # # #                 choice = response.json()["choices"][0]
# # # # # # # #                 message = choice["message"]
# # # # # # # #                 messages.append(message)

# # # # # # # #                 if not message.get("tool_calls"):
# # # # # # # #                     logger.info("Agent finished with a direct response. End of conversation.")
# # # # # # # #                     return message

# # # # # # # #                 logger.info(f"Agent wants to call a tool: {message['tool_calls'][0]['function']['name']}")
# # # # # # # #                 tool_call = message["tool_calls"][0]
# # # # # # # #                 tool_result = await execute_tool(
# # # # # # # #                     tool_name=tool_call["function"]["name"],
# # # # # # # #                     args=json.loads(tool_call["function"]["arguments"])
# # # # # # # #                 )
                
# # # # # # # #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": tool_result})

# # # # # # # #         except httpx.RequestError as e:
# # # # # # # #             logger.error(f"Could not contact LM Studio: {e}")
# # # # # # # #             raise HTTPException(status_code=502, detail="The connection to the AI model failed.")
# # # # # # # #         except Exception as e:
# # # # # # # #             logger.critical(f"An unhandled exception occurred in the chat loop: {e}")
# # # # # # # #             raise HTTPException(status_code=500, detail="A critical internal error occurred.")
    
# # # # # # # #     logger.warning(f"Conversation exceeded max turns ({max_turns}).")
# # # # # # # #     return {"role": "assistant", "content": "I'm having a bit of trouble completing that request. Could we try something simpler?"}# # bridge_api.py (Version 6 - Autonomous Agent)

# # # # # # # # @app.get("/", tags=["Health Check"])
# # # # # # # # async def read_root():
# # # # # # # #     return {"status": "Bridge API Orchestrator is running"}
