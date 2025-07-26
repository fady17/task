# ai/config.py
"""
Centralized configuration for the AI sub-application.
Contains API URLs, model names, system prompts, tool definitions, and other static settings.
"""

import logging
import os
from aiortc import RTCConfiguration, RTCIceServer

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API & MODEL CONFIGURATION ---
# LM_STUDIO_API_URL = "http://localhost:1234/v1"
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "localhost")
LM_STUDIO_API_URL = f"http://{LM_STUDIO_HOST}:1234/v1"

CRUD_API_URL = "http://localhost:8000"
MODEL_NAME = "qwen2.5-7b-instruct"

TURN_SERVER_HOST = os.getenv("DOCKER_HOST_IP", "127.0.0.1")

PC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=[
                f"stun:{TURN_SERVER_HOST}:3478",
                f"turn:{TURN_SERVER_HOST}:3478"
            ],
            username="demo",
            credential="password"
        )
    ]
)
# PC_CONFIG = RTCConfiguration(iceServers=[
#     RTCIceServer(urls=[f"turn:{TURN_SERVER_HOST}:3478"], username="demo", credential="password"),
#     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# ])

# PC_CONFIG = RTCConfiguration(iceServers=[
#     RTCIceServer(urls=[f"turn:{TURN_SERVER_HOST}:3478"], username="demo", credential="password"),
  
# ])

# --- WEBRTC CONFIGURATION ---
# PC_CONFIG = RTCConfiguration(iceServers=[
#     RTCIceServer(urls=[f"turn:{TURN_SERVER_HOST}:3478"], username="demo", credential="password"),
#     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# ])
# ice_servers = [
#     RTCIceServer(
#         urls=[
#             f"stun:{TURN_SERVER_HOST}:3478",
#             f"turn:{TURN_SERVER_HOST}:3478"
#         ],
#         username="demo",
#         credential="password"
#     )
# ]

# PC_CONFIG = RTCConfiguration(iceServers=ice_servers)


SYSTEM_PROMPT = """<|im_start|>system
<role>
You are The Decomposer, a hyper-logical AI agent. Your sole function is to translate a user's request into a series of verifiable API tool calls. You are precise, methodical, and you trust only data you have fetched yourself.
</role>

<rules>
# Main Directive
For every user request, you will perform one or more "Transaction Loops". If a request is simple (e.g., "delete X"), you perform one loop. If a request is complex (e.g., "add X and then update Y"), you will perform a loop for each sub-task sequentially.

# The Transaction Loop
This loop is unbreakable. You will perform these steps in order for every task or sub-task.
1.  **PLAN:** Call `get_all_todo_lists()` to get the current database state.
2.  **EXECUTE:** Call the single tool required for the current task (e.g., `delete_todo_item`).
3.  **VERIFY:** Call `get_all_todo_lists()` a second time.
4.  **JUDGE:** Compare the JSON from before and after the EXECUTE step.
    - If the state changed as expected, the transaction is successful.
    - If the state did not change, the transaction has failed.
5.  **REPORT:** Based on your judgment, generate your final output.

# Output Constraints
*   You MUST output either `tool_calls` for steps 1, 2, and 3, or a final user-facing `content` message for step 5. Never both.
*   Your final `content` message must be concise and based ONLY on the evidence from the VERIFY step.
*   **FINAL ANSWER FORMATTING: Your final `content` response MUST be a single, clean, human-readable sentence. It MUST NOT contain any JSON, code blocks, or debugging information.**

</rules>

<example>
<user_request>
add 'new song' to the music list and then mark it as complete
</user_request>

<internal_monologue>
*   **Decomposition:** The request has two sub-tasks. Task 1: `create_todo_item`. Task 2: `update_todo_item`. I will now start the Transaction Loop for Task 1.
*   **Transaction Loop 1 (Create Item):**
    1.  **PLAN:** I need the `list_id` for "music". I will call `get_all_todo_lists()`.
    2.  **EXECUTE:** (After getting the list_id) I will call `create_todo_item(title='new song', ...)`
    3.  **VERIFY:** I will call `get_all_todo_lists()` again.
    4.  **JUDGE:** I see the new item 'new song' in the latest JSON. Task 1 is successful.
*   **Transaction Loop 2 (Update Item):**
    1.  **PLAN:** I need the `item_id` for the 'new song' I just created. I will call `get_all_todo_lists()`.
    2.  **EXECUTE:** (After getting the item_id) I will call `update_todo_item(completed=true, ...)`
    3.  **VERIFY:** I will call `get_all_todo_lists()` again.
    4.  **JUDGE:** I see `'completed': true` for the 'new song' item in the latest JSON. Task 2 is successful.
*   **Final Report:** Both tasks succeeded. I will now generate the final user-facing message according to the formatting rules.
</internal_monologue>

<final_assistant_response>
Verified. Item 'new song' has been added to the 'music' list and marked as complete.
</final_assistant_response>
</example>
<|im_end|>
"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_all_todo_lists",
            "description": "Get all todo lists with their items - use this first when you need to find existing lists or items",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "create_todo_list",
            "description": "Create a new todo list",
            "parameters": {
                "type": "object",
                "properties": {"title": {"type": "string", "description": "Title for the new list"}},
                "required": ["title"]
            }
        }
    },
    # <<<--- ADDED THE MISSING TOOL HERE ---<<<
    {
        "type": "function",
        "function": {
            "name": "update_todo_list",
            "description": "Update a todo list's title",
            "parameters": {
                "type": "object",
                "properties": {
                    "list_id": {"type": "integer", "description": "The ID of the todo list to update"},
                    "title": {"type": "string", "description": "The new title for the todo list"}
                },
                "required": ["list_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo_list",
            "description": "Delete an entire todo list",
            "parameters": {
                "type": "object",
                "properties": {"list_id": {"type": "integer", "description": "ID of list to delete"}},
                "required": ["list_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_todo_item", 
            "description": "Add a new item to a specific list",
            "parameters": {
                "type": "object",
                "properties": {
                    "list_id": {"type": "integer", "description": "ID of the list to add item to"},
                    "title": {"type": "string", "description": "Title of the new item"},
                    "completed": {"type": "boolean", "description": "Whether item starts as completed", "default": False}
                },
                "required": ["list_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo_item",
            "description": "Update an item's title or completion status",
            "parameters": {
                "type": "object", 
                "properties": {
                    "list_id": {"type": "integer"},
                    "item_id": {"type": "integer"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "completed": {"type": "boolean", "description": "Completion status (optional)"}
                },
                "required": ["list_id", "item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo_item", 
            "description": "Delete a specific todo item",
            "parameters": {
                "type": "object",
                "properties": {
                    "list_id": {"type": "integer", "description": "ID of the list containing the item"},
                    "item_id": {"type": "integer", "description": "ID of the item to delete"}
                },
                "required": ["list_id", "item_id"]
            }
        }
    },
    # Note: get_todo_list (by id) is intentionally left out in the refactored design
    # because the core workflow relies on get_all_todo_lists() for context.
    # Adding it is possible but redundant for the current AI logic.
]
# # ai/config.py
# """
# Centralized configuration for the AI sub-application.
# Contains API URLs, model names, system prompts, tool definitions, and other static settings.
# """

# import logging
# from aiortc import RTCConfiguration, RTCIceServer

# # --- LOGGING SETUP ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # --- API & MODEL CONFIGURATION ---
# LM_STUDIO_API_URL = "http://localhost:1234/v1"
# CRUD_API_URL = "http://localhost:8000"
# MODEL_NAME = "qwen2.5-7b-instruct"

# # --- WEBRTC CONFIGURATION ---
# PC_CONFIG = RTCConfiguration(iceServers=[
#     RTCIceServer(urls=["turn:127.0.0.1:3478"], username="demo", credential="password"),
#     RTCIceServer(urls=["stun:stun.l.google.com:19302"])
# ])

# # --- SYSTEM PROMPT (Lyra Optimized V3 - Context-Aware) ---
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
# <|im_end|>
# """

# # --- TOOL DEFINITIONS ---
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
#             "name": "update_todo_list",
#             "description": "Update a todo list's title",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "list_id": {"type": "integer", "description": "The ID of the todo list to update"},
#                     "title": {"type": "string", "description": "The new title for the todo list"}
#                 },
#                 "required": ["list_id", "title"]
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