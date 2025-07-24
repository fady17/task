# bridge_api.py (Version 8 - Autonomous Agent)
import json
import logging
import asyncio

# Third-party imports
import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Any, Dict, Set

# aiortc imports for WebRTC
from aiortc import RTCPeerConnection, RTCSessionDescription

# --- LAYER 1: LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# --- Configuration ---
LM_STUDIO_API_URL = "http://localhost:1234/v1"
CRUD_API_URL = "http://localhost:8000"
MODEL_NAME = "qwen2.5-7b-instruct"

# --- API Setup ---
app = FastAPI(
    title="Autonomous Agent Bridge API",
    description="An advanced bridge API that enables multi-step tool use for complex tasks.",
    version="8.0.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Store active peer connections
pcs: Set[RTCPeerConnection] = set()

# Configuration for the STUN server
pc_config = {"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]}

# --- WebRTC and Signaling Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    
    # Create a new peer connection for this client
    pc = RTCPeerConnection(configuration=pc_config) # type: ignore
    pcs.add(pc)
    
    # Variable to store the data channel
    data_channel = None

    # Define what to do when the Data Channel is created by the client
    @pc.on("datachannel")
    def on_datachannel(channel):
        nonlocal data_channel
        data_channel = channel
        logger.info(f"DataChannel '{channel.label}' created.")
        
        @channel.on("message")
        async def on_message(message):
            logger.info(f"Received message via DataChannel: {message}")
            
            try:
                # Process the message through the autonomous agent
                chat_request = ChatRequest(prompt=message)
                response = await handle_chat_internal(chat_request)
                
                # Send the response back through the data channel
                response_content = response.get("content", "I'm sorry, I couldn't process that request.")
                logger.info(f"Sending response via DataChannel: {response_content}")
                channel.send(response_content)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                error_response = "I encountered an error processing your request. Please try again."
                channel.send(error_response)

        @channel.on("close")
        def on_close():
            logger.info("DataChannel closed.")

    # Handle connection state changes
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            if pc in pcs:
                pcs.remove(pc)

    # Main loop to handle signaling messages from the client
    try:
        while True:
            try:
                data = await websocket.receive_json()
                
                # The client is sending its SDP offer
                if data["type"] == "offer":
                    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                    logger.info("Received SDP Offer from client.")
                    
                    await pc.setRemoteDescription(offer)
                    
                    # Create an SDP answer
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    
                    # Send the answer back to the client via the websocket
                    logger.info("Sending SDP Answer to client.")
                    await websocket.send_json({
                        "type": "answer",
                        "sdp": pc.localDescription.sdp,
                    })
                
                # Handle ICE candidates if needed
                elif data["type"] == "candidate":
                    logger.info("Received ICE candidate from client.")
                    # Handle ICE candidate if your setup requires it
                    
            except json.JSONDecodeError:
                logger.error("Received invalid JSON from client")
                break
            except Exception as e:
                logger.error(f"Error handling signaling message: {e}")
                break

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        if pc in pcs:
            await pc.close()
            pcs.remove(pc)
        logger.info("WebSocket connection cleanup completed.")

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    prompt: str

# --- LAYER 2: VALIDATION MODELS ---
class ToolResult(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    detail: Optional[Any] = None
    items: List[Any] = Field(default_factory=list) 

# --- PROMPT ENGINEERING ---
SYSTEM_PROMPT = """
You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
"""

# --- TOOL SCHEMA ---
tools_schema = [
    {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}}, "required": ["list_id"]}}},
    {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}, "title": {"type": "string", "description": "The new title"}}, "required": ["list_id", "title"]}}},
    {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
    {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
    {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
    {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
]

# --- Tool Execution Logic ---
async def execute_tool(tool_name: str, args: dict) -> str:
    """Calls the CRUD API with robust error handling and validation."""
    endpoints = {
        "create_todo_list": ("POST", "/lists/"),
        "get_all_todo_lists": ("GET", "/lists/"),
        "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
        "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
        "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
        "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
        "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
        "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
    }
    
    if tool_name not in endpoints:
        logger.error(f"Attempted to call an unknown tool: {tool_name}")
        return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

    method, endpoint = endpoints[tool_name]
    json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

    async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
        try:
            logger.info(f"Executing tool '{tool_name}' -> {method} {CRUD_API_URL}{endpoint}")
            response = await client.request(method, endpoint, json=json_body)
            response.raise_for_status()
            
            if response.status_code == 204:
                return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
            
            try:
                raw_data = response.json()
                logger.info(f"Tool '{tool_name}' executed successfully.")
                return json.dumps(raw_data)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Validation Error from CRUD API for tool '{tool_name}': {e}")
                return json.dumps({"status": "error", "detail": "Received an invalid response from the data service."})

        except httpx.TimeoutException:
            logger.error(f"Timeout when calling tool '{tool_name}' at {CRUD_API_URL}{endpoint}")
            return json.dumps({"status": "error", "detail": "The data service took too long to respond."})
        except httpx.RequestError as e:
            logger.error(f"Request Error for tool '{tool_name}': {e}")
            return json.dumps({"status": "error", "detail": "Could not connect to the data service."})
        except Exception as e:
            logger.critical(f"An unexpected error occurred during tool execution for '{tool_name}': {e}")
            return json.dumps({"status": "error", "detail": "An unexpected internal error occurred."})

# --- Internal Chat Handler (used by WebRTC) ---
async def handle_chat_internal(request: ChatRequest):
    """Internal chat handler that can be called from WebRTC or HTTP endpoint."""
    logger.info(f"Processing chat request. Prompt: '{request.prompt}'")

    if request.prompt.strip().lower() == "!reset state":
        logger.warning("Demo magic phrase '!reset state' used.")
        return {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.prompt}]
    max_turns = 5

    for turn in range(max_turns):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Agent Turn {turn + 1}: Sending prompt to LLM.")
                
                response = await client.post(
                    f"{LM_STUDIO_API_URL}/chat/completions",
                    json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
                )
                response.raise_for_status()
                choice = response.json()["choices"][0]
                message = choice["message"]
                messages.append(message)

                if not message.get("tool_calls"):
                    logger.info("Agent finished with a direct response. End of conversation.")
                    return message

                logger.info(f"Agent wants to call a tool: {message['tool_calls'][0]['function']['name']}")
                tool_call = message["tool_calls"][0]
                tool_result = await execute_tool(
                    tool_name=tool_call["function"]["name"],
                    args=json.loads(tool_call["function"]["arguments"])
                )
                
                messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": tool_result})

        except httpx.RequestError as e:
            logger.error(f"Could not contact LM Studio: {e}")
            return {"role": "assistant", "content": "I'm having trouble connecting to the AI service. Please try again later."}
        except Exception as e:
            logger.critical(f"An unhandled exception occurred in the chat loop: {e}")
            return {"role": "assistant", "content": "I encountered an unexpected error. Please try again."}
    
    logger.warning(f"Conversation exceeded max turns ({max_turns}).")
    return {"role": "assistant", "content": "I'm having a bit of trouble completing that request. Could we try something simpler?"}

# --- HTTP Chat Endpoint (fallback) ---
@app.post("/chat")
async def handle_chat(request: ChatRequest):
    try:
        result = await handle_chat_internal(request)
        return result
    except Exception as e:
        logger.error(f"Error in HTTP chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "Bridge API Orchestrator is running"}

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Close all peer connections
    for pc in list(pcs):
        await pc.close()
    pcs.clear()
    logger.info("All WebRTC connections closed on shutdown")
# # bridge_api.py (Version 8 - Autonomous Agent)
# import json
# import logging
# import asyncio # <-- Add this

# # Third-party imports
# import httpx
# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect # <-- Add WebSocket imports
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field, ValidationError
# from typing import List, Optional, Any, Dict, Set # <-- Add Set

# # aiortc imports for WebRTC
# from aiortc import RTCPeerConnection, RTCSessionDescription # <-- Add this
# # from aiortc.contrib.media import MediaStreamTrack 

# # --- LAYER 1: LOGGING ---
# # Set up a logger to get clear, timestamped output.
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
# )
# logger = logging.getLogger(__name__)

# # --- Configuration ---
# LM_STUDIO_API_URL = "http://localhost:1234/v1"
# CRUD_API_URL = "http://localhost:8000"
# MODEL_NAME = "qwen2.5-7b-instruct"

# # --- API Setup ---
# app = FastAPI(
#     title="Autonomous Agent Bridge API",
#     description="An advanced bridge API that enables multi-step tool use for complex tasks.",
#     version="7.0.0",
# )
# app.add_middleware(
#     CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# )

# pcs: Set[RTCPeerConnection] = set()

# # Configuration for the STUN server
# # We don't need this on the server if the client provides it,
# # but it's good practice to be aware of the configuration.
# pc_config = {"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]}


# # --- NEW: The Signaling and WebRTC Endpoint ---
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     logger.info("WebSocket connection accepted.")
    
#     # Create a new peer connection for this client
#     pc = RTCPeerConnection(configuration=pc_config) # type: ignore
#     pcs.add(pc)

#     # --- This is where the magic happens ---
#     # Define what to do when the Data Channel is created by the client
#     @pc.on("datachannel")
#     def on_datachannel(channel):
#         logger.info(f"DataChannel '{channel.label}' created.")
        
#         @channel.on("message")
#         async def on_message(message):
#             logger.info(f"Received message via DataChannel: {message}")
            
#             # Here we will eventually trigger the tool-use loop
#             # For now, let's just echo the message back
#             response_message = f"Server received: {message}"
#             logger.info(f"Sending response via DataChannel: {response_message}")
#             channel.send(response_message)

#     # Main loop to handle signaling messages from the client
#     try:
#         while True:
#             data = await websocket.receive_json()
            
#             # The client is sending its SDP offer
#             if data["type"] == "offer":
#                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
#                 logger.info("Received SDP Offer from client.")
                
#                 await pc.setRemoteDescription(offer)
                
#                 # Create an SDP answer
#                 answer = await pc.createAnswer()
#                 await pc.setLocalDescription(answer)
                
#                 # Send the answer back to the client via the websocket
#                 logger.info("Sending SDP Answer to client.")
#                 await websocket.send_json({
#                     "type": "answer",
#                     "sdp": pc.localDescription.sdp,
#                 })

#             # The client is sending an ICE candidate
#             # (This part is often handled automatically by aiortc, but explicit handling is robust)
#             # For now, we'll assume aiortc handles this implicitly. If we face issues, we add it.

#     except WebSocketDisconnect:
#         logger.info("WebSocket connection closed.")
#     finally:
#         if pc in pcs:
#             await pc.close()
#             pcs.remove(pc)


# # --- Pydantic Models ---
# class ChatRequest(BaseModel):
#     prompt: str

# # --- LAYER 2: VALIDATION MODELS ---
# # Define what a valid tool result from our CRUD API looks like.
# class ToolResult(BaseModel):
#     status: Optional[str] = None
#     message: Optional[str] = None
#     detail: Optional[Any] = None
#     # Use Field(default_factory=list) for mutable defaults
#     items: List[Any] = Field(default_factory=list) 

# # --- PROMPT ENGINEERING:  ---
# # Using your proven, more powerful system prompt.
# SYSTEM_PROMPT = """
# You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

# 1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
# 2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# 3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# 4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# 5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# """

# # --- TOOL SCHEMA: The second critical change ---
# # Splitting into multiple tools, just like your mcp_todo_server.py.
# # This makes it easier for the model to choose the right action.
# tools_schema = [
#     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
#     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
#     {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}}, "required": ["list_id"]}}},
#     {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}, "title": {"type": "string", "description": "The new title"}}, "required": ["list_id", "title"]}}},
#     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
#     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
#     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
#     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# ]

# # --- Tool Execution Logic (Orchestrator) ---
# # This function calls your CRUD API based on the tool name and arguments.
# async def execute_tool(tool_name: str, args: dict) -> str:
#     """Calls the CRUD API, now with robust error handling and validation."""
#     endpoints = {
#         "create_todo_list": ("POST", "/lists/"),
#         "get_all_todo_lists": ("GET", "/lists/"),
#         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
#         "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
#         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
#         "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
#         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
#         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
#     }
#     if tool_name not in endpoints:
#         logger.error(f"Attempted to call an unknown tool: {tool_name}")
#         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

#     method, endpoint = endpoints[tool_name]
#     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

    
#     # LAYER 3: Use a client with a configured timeout
#     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
#         try:
#             logger.info(f"Executing tool '{tool_name}' -> {method} {CRUD_API_URL}{endpoint}")
#             response = await client.request(method, endpoint, json=json_body)
#             response.raise_for_status() # Raises exception for 4xx/5xx responses
            
#             if response.status_code == 204:
#                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
            
#             # Layer 2 Validation: Parse and validate the response from the CRUD API
#             try:
#                 # Assuming the CRUD API can return a single object or a list of objects
#                 raw_data = response.json()
#                 # We can add more specific Pydantic models here if needed
#                 logger.info(f"Tool '{tool_name}' executed successfully.")
#                 return json.dumps(raw_data)
#             except (json.JSONDecodeError, ValidationError) as e:
#                 logger.error(f"Validation Error from CRUD API for tool '{tool_name}': {e}")
#                 return json.dumps({"status": "error", "detail": "Received an invalid response from the data service."})

#         except httpx.TimeoutException:
#             logger.error(f"Timeout when calling tool '{tool_name}' at {CRUD_API_URL}{endpoint}")
#             return json.dumps({"status": "error", "detail": "The data service took too long to respond."})
#         except httpx.RequestError as e:
#             logger.error(f"Request Error for tool '{tool_name}': {e}")
#             return json.dumps({"status": "error", "detail": "Could not connect to the data service."})
#         except Exception as e:
#             logger.critical(f"An unexpected error occurred during tool execution for '{tool_name}': {e}")
#             return json.dumps({"status": "error", "detail": "An unexpected internal error occurred."})

# # --- Main API Endpoint with Safeguards ---
# @app.post("/chat")
# async def handle_chat(request: ChatRequest):
#     logger.info(f"Received new chat request. Prompt: '{request.prompt}'")

#     # --- LAYER 4: DEMO MAGIC PHRASE ---
#     if request.prompt.strip().lower() == "!reset state":
#         logger.warning("Demo magic phrase '!reset state' used.")
#         return {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

#     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.prompt}]
#     max_turns = 5 # Safety break to prevent infinite loops

#     for turn in range(max_turns):
#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 logger.info(f"Agent Turn {turn + 1}: Sending prompt to LLM.")
                
#                 response = await client.post(
#                     f"{LM_STUDIO_API_URL}/chat/completions",
#                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
#                 )
#                 response.raise_for_status()
#                 choice = response.json()["choices"][0]
#                 message = choice["message"]
#                 messages.append(message)

#                 if not message.get("tool_calls"):
#                     logger.info("Agent finished with a direct response. End of conversation.")
#                     return message

#                 logger.info(f"Agent wants to call a tool: {message['tool_calls'][0]['function']['name']}")
#                 tool_call = message["tool_calls"][0]
#                 tool_result = await execute_tool(
#                     tool_name=tool_call["function"]["name"],
#                     args=json.loads(tool_call["function"]["arguments"])
#                 )
                
#                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": tool_result})

#         except httpx.RequestError as e:
#             logger.error(f"Could not contact LM Studio: {e}")
#             raise HTTPException(status_code=502, detail="The connection to the AI model failed.")
#         except Exception as e:
#             logger.critical(f"An unhandled exception occurred in the chat loop: {e}")
#             raise HTTPException(status_code=500, detail="A critical internal error occurred.")
    
#     logger.warning(f"Conversation exceeded max turns ({max_turns}).")
#     return {"role": "assistant", "content": "I'm having a bit of trouble completing that request. Could we try something simpler?"}# # bridge_api.py (Version 6 - Autonomous Agent)

# @app.get("/", tags=["Health Check"])
# async def read_root():
#     return {"status": "Bridge API Orchestrator is running"}

# # # bridge_api.py (Version 7 - Autonomous Agent)
# # import httpx
# # import json
# # import logging
# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, Field, ValidationError
# # from typing import List, Optional, Any, Dict


# # # --- LAYER 1: LOGGING ---
# # # Set up a logger to get clear, timestamped output.
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format='%(asctime)s - %(levelname)s - %(message)s',
# # )
# # logger = logging.getLogger(__name__)

# # # --- Configuration ---
# # LM_STUDIO_API_URL = "http://localhost:1234/v1"
# # CRUD_API_URL = "http://localhost:8000"
# # MODEL_NAME = "qwen2.5-7b-instruct"

# # # --- API Setup ---
# # app = FastAPI(
# #     title="Autonomous Agent Bridge API",
# #     description="An advanced bridge API that enables multi-step tool use for complex tasks.",
# #     version="7.0.0",
# # )
# # app.add_middleware(
# #     CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # )

# # # --- Pydantic Models ---
# # class ChatRequest(BaseModel):
# #     prompt: str

# # # --- LAYER 2: VALIDATION MODELS ---
# # # Define what a valid tool result from our CRUD API looks like.
# # class ToolResult(BaseModel):
# #     status: Optional[str] = None
# #     message: Optional[str] = None
# #     detail: Optional[Any] = None
# #     # Use Field(default_factory=list) for mutable defaults
# #     items: List[Any] = Field(default_factory=list) 

# # # --- PROMPT ENGINEERING:  ---
# # # Using your proven, more powerful system prompt.
# # SYSTEM_PROMPT = """
# # You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

# # 1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
# # 2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools. For example, if the user asks to "delete the shopping list", your plan is: 1. Get all lists to find the ID of the 'shopping' list. 2. Call the delete tool with that ID.
# # 3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask for clarification. Execute the plan yourself.
# # 4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call `get_all_todo_lists`. Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# # 5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took.
# # """

# # # --- TOOL SCHEMA: The second critical change ---
# # # Splitting into multiple tools, just like your mcp_todo_server.py.
# # # This makes it easier for the model to choose the right action.
# # tools_schema = [
# #     {"type": "function", "function": {"name": "create_todo_list", "description": "Create a new todo list", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "The title of the todo list"}}, "required": ["title"]}}},
# #     {"type": "function", "function": {"name": "get_all_todo_lists", "description": "Get all todo lists with their items and statistics. Use this to find a list's ID when the user provides a name.", "parameters": {"type": "object", "properties": {}}}},
# #     {"type": "function", "function": {"name": "get_todo_list", "description": "Get a specific todo list by ID", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}}, "required": ["list_id"]}}},
# #     {"type": "function", "function": {"name": "update_todo_list", "description": "Update a todo list's title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the todo list"}, "title": {"type": "string", "description": "The new title"}}, "required": ["list_id", "title"]}}},
# #     {"type": "function", "function": {"name": "delete_todo_list", "description": "Delete a todo list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list to delete"}}, "required": ["list_id"]}}},
# #     {"type": "function", "function": {"name": "create_todo_item", "description": "Create a new todo item in a specific list", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer", "description": "The ID of the list"}, "title": {"type": "string", "description": "The title of the item"}}, "required": ["list_id", "title"]}}},
# #     {"type": "function", "function": {"name": "update_todo_item", "description": "Update a todo item's status or title", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}, "title": {"type": "string"}, "completed": {"type": "boolean"}}, "required": ["list_id", "item_id"]}}},
# #     {"type": "function", "function": {"name": "delete_todo_item", "description": "Delete a todo item", "parameters": {"type": "object", "properties": {"list_id": {"type": "integer"}, "item_id": {"type": "integer"}}, "required": ["list_id", "item_id"]}}},
# # ]

# # # --- Tool Execution Logic (Orchestrator) ---
# # # This function calls your CRUD API based on the tool name and arguments.
# # async def execute_tool(tool_name: str, args: dict) -> str:
# #     """Calls the CRUD API, now with robust error handling and validation."""
# #     endpoints = {
# #         "create_todo_list": ("POST", "/lists/"),
# #         "get_all_todo_lists": ("GET", "/lists/"),
# #         "get_todo_list": ("GET", f"/lists/{args.get('list_id')}"),
# #         "update_todo_list": ("PUT", f"/lists/{args.get('list_id')}"),
# #         "delete_todo_list": ("DELETE", f"/lists/{args.get('list_id')}"),
# #         "create_todo_item": ("POST", f"/{args.get('list_id')}/items/"),
# #         "update_todo_item": ("PUT", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# #         "delete_todo_item": ("DELETE", f"/{args.get('list_id')}/items/{args.get('item_id')}"),
# #     }
# #     if tool_name not in endpoints:
# #         logger.error(f"Attempted to call an unknown tool: {tool_name}")
# #         return json.dumps({"status": "error", "detail": f"The tool '{tool_name}' does not exist."})

# #     method, endpoint = endpoints[tool_name]
# #     json_body = {k: v for k, v in args.items() if k in {"title", "completed"} and v is not None}

    
# #     # LAYER 3: Use a client with a configured timeout
# #     async with httpx.AsyncClient(base_url=CRUD_API_URL, timeout=10.0) as client:
# #         try:
# #             logger.info(f"Executing tool '{tool_name}' -> {method} {CRUD_API_URL}{endpoint}")
# #             response = await client.request(method, endpoint, json=json_body)
# #             response.raise_for_status() # Raises exception for 4xx/5xx responses
            
# #             if response.status_code == 204:
# #                 return json.dumps({"status": "success", "message": f"Tool '{tool_name}' completed."})
            
# #             # Layer 2 Validation: Parse and validate the response from the CRUD API
# #             try:
# #                 # Assuming the CRUD API can return a single object or a list of objects
# #                 raw_data = response.json()
# #                 # We can add more specific Pydantic models here if needed
# #                 logger.info(f"Tool '{tool_name}' executed successfully.")
# #                 return json.dumps(raw_data)
# #             except (json.JSONDecodeError, ValidationError) as e:
# #                 logger.error(f"Validation Error from CRUD API for tool '{tool_name}': {e}")
# #                 return json.dumps({"status": "error", "detail": "Received an invalid response from the data service."})

# #         except httpx.TimeoutException:
# #             logger.error(f"Timeout when calling tool '{tool_name}' at {CRUD_API_URL}{endpoint}")
# #             return json.dumps({"status": "error", "detail": "The data service took too long to respond."})
# #         except httpx.RequestError as e:
# #             logger.error(f"Request Error for tool '{tool_name}': {e}")
# #             return json.dumps({"status": "error", "detail": "Could not connect to the data service."})
# #         except Exception as e:
# #             logger.critical(f"An unexpected error occurred during tool execution for '{tool_name}': {e}")
# #             return json.dumps({"status": "error", "detail": "An unexpected internal error occurred."})

# # # --- Main API Endpoint with Safeguards ---
# # @app.post("/chat")
# # async def handle_chat(request: ChatRequest):
# #     logger.info(f"Received new chat request. Prompt: '{request.prompt}'")

# #     # --- LAYER 4: DEMO MAGIC PHRASE ---
# #     if request.prompt.strip().lower() == "!reset state":
# #         logger.warning("Demo magic phrase '!reset state' used.")
# #         return {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

# #     messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": request.prompt}]
# #     max_turns = 5 # Safety break to prevent infinite loops

# #     for turn in range(max_turns):
# #         try:
# #             async with httpx.AsyncClient(timeout=30.0) as client:
# #                 logger.info(f"Agent Turn {turn + 1}: Sending prompt to LLM.")
                
# #                 response = await client.post(
# #                     f"{LM_STUDIO_API_URL}/chat/completions",
# #                     json={"model": MODEL_NAME, "messages": messages, "tools": tools_schema, "tool_choice": "auto"}
# #                 )
# #                 response.raise_for_status()
# #                 choice = response.json()["choices"][0]
# #                 message = choice["message"]
# #                 messages.append(message)

# #                 if not message.get("tool_calls"):
# #                     logger.info("Agent finished with a direct response. End of conversation.")
# #                     return message

# #                 logger.info(f"Agent wants to call a tool: {message['tool_calls'][0]['function']['name']}")
# #                 tool_call = message["tool_calls"][0]
# #                 tool_result = await execute_tool(
# #                     tool_name=tool_call["function"]["name"],
# #                     args=json.loads(tool_call["function"]["arguments"])
# #                 )
                
# #                 messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["function"]["name"], "content": tool_result})

# #         except httpx.RequestError as e:
# #             logger.error(f"Could not contact LM Studio: {e}")
# #             raise HTTPException(status_code=502, detail="The connection to the AI model failed.")
# #         except Exception as e:
# #             logger.critical(f"An unhandled exception occurred in the chat loop: {e}")
# #             raise HTTPException(status_code=500, detail="A critical internal error occurred.")
    
# #     logger.warning(f"Conversation exceeded max turns ({max_turns}).")
# #     return {"role": "assistant", "content": "I'm having a bit of trouble completing that request. Could we try something simpler?"}# # bridge_api.py (Version 6 - Autonomous Agent)

# # @app.get("/", tags=["Health Check"])
# # async def read_root():
# #     return {"status": "Bridge API Orchestrator is running"}
