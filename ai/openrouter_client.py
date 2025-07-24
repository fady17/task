import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
import json
import os

# NEW: Import the official Google Gemini library
import google as genai
from google.genai import types

# from google import FunctionDeclaration, Tool as GeminiTool

from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters, Tool as MCPTool
from mcp.types import TextContent
from mcp.client.stdio import stdio_client



# Load environment variables from .env file
load_dotenv()

# --- Model and Server Configuration ---
MODEL_NAME = "gemini-2.5-flash"

SERVER_CONFIG = {
    "command": "/Users/fady/Desktop/internship/todo-list/todo_env/bin/python",
    "args": [
        "/Users/fady/Desktop/internship/todo-list/mcp/mcp_todo_server.py"
    ],
    "env": None
}

class MCPClient:
    """A client that uses the Google Gemini SDK's built-in automatic support for MCP."""
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        
        # We only need to configure the model once
        self.model = genai.GenerativeModel(MODEL_NAME, system_instruction="""
You are an autonomous agent that manages a user's todo list by exclusively using the provided tools.
You MUST formulate a plan and execute it by calling tools.
If a request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call a tool to get more context (e.g., `get_all_todo_lists`).
After all tool calls are complete, provide a brief, final confirmation to the user.
""")

    async def connect_to_server(self, server_config):
        """Establishes the connection to the local MCP server."""
        server_params = StdioServerParameters(**server_config)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        
        # The session object is the key to the automatic integration
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        if not self.session:
            raise ConnectionError("Failed to establish MCP session.")
        
        print("\n✅ MCP Session established. Ready to proxy tools to Gemini.")

    async def process_query(self, query: str) -> str:
        """
        Processes a user query using the automatic MCP integration.
        The SDK handles the entire tool-calling loop automatically.
        """
        if not self.session:
            return "Error: MCP session is not connected. Cannot process query."

        print(f"-> Sending query to Gemini for autonomous tool execution...")

        # This is the magic. We pass the session object directly as a tool.
        # The SDK will automatically list, call, and respond to the model.
        response = await self.model.generate_content_async(
            query,
            tools=[self.session],
        )
        
        # The SDK has handled the entire back-and-forth. We just get the final text.
        return response.text

    async def chat_loop(self):
        print("\n🚀 Google Gemini MCP Client Started (Automatic Mode)!")
        print("   Model:", MODEL_NAME)
        print("   Type 'quit' to exit.")

        while True:
            try:
                query = input("\n👤 Query: ").strip()
                if query.lower() == 'quit':
                    break
                if not query:
                    continue
                
                # Show a spinner or message to indicate processing
                print("🤖 Assistant is thinking...")
                result = await self.process_query(query)
                print(f"\n🤖 Assistant:\n{result}")

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                print(f"\nAn unexpected error occurred: {str(e)}")

    async def cleanup(self):
        print("\nShutting down...")
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server(SERVER_CONFIG)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
# import asyncio
# from typing import Optional, List
# from contextlib import AsyncExitStack
# import json

# from openai import OpenAI
# from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
# from dotenv import load_dotenv

# from mcp import ClientSession, StdioServerParameters, Tool
# from mcp.types import TextContent
# from mcp.client.stdio import stdio_client

# # Load environment variables from .env file
# load_dotenv()

# # --- Model and Server Configuration ---
# # MODEL = "qwen/qwen3-4b:free"
# # MODEL = "mistralai/mistral-7b-instruct:free"
# # MODEL = "google/gemini-2.5-pro-exp-03-25"
# MODEL="google/gemini-2.0-flash-exp:free"

# SERVER_CONFIG = {
#     "command": "/Users/fady/Desktop/internship/todo-list/todo_env/bin/python",
#     "args": [
#         "/Users/fady/Desktop/internship/todo-list/mcp/mcp_todo_server.py"
#     ],
#     "env": None
# }
# def convert_tool_format(tool: Tool) -> ChatCompletionToolParam:
#     """Converts MCP Tool schema to OpenAI-compatible tool schema with proper types."""
#     return {
#         "type": "function",
#         "function": {
#             "name": tool.name,
#             "description": tool.description or "",
#             "parameters": {
#                 "type": "object",
#                 "properties": tool.inputSchema.get("properties", {}),
#                 "required": tool.inputSchema.get("required", [])
#             }
#         }
#     }

# class MCPClient:
#     """A client to interact with an MCP server using an OpenRouter model."""
#     def __init__(self):
#         self.session: Optional[ClientSession] = None
#         self.exit_stack = AsyncExitStack()
#         self.openai = OpenAI(base_url="https://openrouter.ai/api/v1")
#         self.messages: List[ChatCompletionMessageParam] = []

#     async def connect_to_server(self, server_config):
#         server_params = StdioServerParameters(**server_config)
#         stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
#         self.stdio, self.write = stdio_transport
#         self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
#         await self.session.initialize()

#         if not self.session:
#             raise ConnectionError("Failed to establish MCP session.")

#         response = await self.session.list_tools()
#         print("\n✅ Connected to server with tools:", [tool.name for tool in response.tools])

#         self.messages.append({
#             "role": "system",
#             "content": """
# You are an autonomous agent that manages a user's todo list by exclusively using the provided tools. You MUST follow these rules:

# 1.  **Analyze the User's Goal:** Understand the user's ultimate objective.
# 2.  **Formulate a Plan:** Create a step-by-step plan to achieve the goal using the available tools.
# 3.  **Tool-First Execution:** For each step in your plan, you MUST call a tool. Do not describe the plan to the user or ask them to perform actions. Execute the plan yourself.
# 4.  **Handle Ambiguity Autonomously:** If the user's request is ambiguous (e.g., "check my internship list"), your first step is ALWAYS to call a tool that provides more context (e.g., `get_all_todo_lists`). Use the output of that tool to gather the necessary information (like a specific list_id) to complete the original request in a subsequent step.
# 5.  **Concise Final Response:** After all tool calls are complete and the goal is achieved, provide a brief, final confirmation to the user. Do not explain the steps you took unless asked.
# """
#         })

#     async def process_query(self, query: str) -> str:
#         if not self.session:
#             return "Error: MCP session is not connected. Cannot process query."

#         # Keep a local message history for this specific query's chain
#         local_messages = self.messages + [{"role": "user", "content": query}]

#         tool_list_response = await self.session.list_tools()
#         available_tools: List[ChatCompletionToolParam] = [convert_tool_format(tool) for tool in tool_list_response.tools]

#         response = self.openai.chat.completions.create(
#             model=MODEL,
#             tools=available_tools,
#             tool_choice="auto",
#             messages=local_messages,
#             temperature=0.1,
#             top_p=0.5
#         )
        
#         assistant_message = response.choices[0].message

#         if assistant_message.tool_calls:
#             tool_call = assistant_message.tool_calls[0]
#             tool_name = tool_call.function.name
            
#             tool_args = {}
#             if tool_call.function.arguments:
#                 try:
#                     tool_args = json.loads(tool_call.function.arguments)
#                 except json.JSONDecodeError:
#                     return f"Error: The model provided invalid JSON arguments: {tool_call.function.arguments}"

#             print(f"🤖 LLM wants to call tool '{tool_name}' with args: {tool_args}")
            
#             if not self.session:
#                  raise ConnectionError("MCP session lost before tool execution.")

#             try:
#                 result = await self.session.call_tool(tool_name, tool_args)
                
#                 tool_output_str = ""
#                 if result.content:
#                     text_parts = [c.text for c in result.content if isinstance(c, TextContent)]
#                     tool_output_str = "\n".join(text_parts) if text_parts else "Tool returned no text content."
#                 else:
#                     tool_output_str = "Tool executed successfully with no output."

#                 print(f"✅ Tool '{tool_name}' executed.")
                
#                 # --- START OF FIX ---
#                 # Instead of making a second API call, we will format and return the raw result directly.
#                 try:
#                     # Try to parse the string as JSON for pretty printing
#                     parsed_json = json.loads(tool_output_str)
#                     return json.dumps(parsed_json, indent=2)
#                 except json.JSONDecodeError:
#                     # If it's not JSON, return the raw string
#                     return tool_output_str
#                 # --- END OF FIX ---

#             except Exception as e:
#                 error_message = f"Error executing tool '{tool_name}': {str(e)}"
#                 print(f"❌ {error_message}")
#                 return error_message
        
#         # If the model responds directly without a tool call
#         return assistant_message.content if assistant_message.content else "Task completed."

#     async def chat_loop(self):
#         print("\n🚀 OpenRouter MCP Client Started!")
#         print("   Model:", MODEL)
#         print("   Type 'quit' to exit.")

#         while True:
#             try:
#                 query = input("\n👤 Query: ").strip()
#                 if query.lower() == 'quit':
#                     break
#                 if not query:
#                     continue
#                 result = await self.process_query(query)
#                 print(f"\n🤖 Assistant:\n{result}")
#             except (KeyboardInterrupt, EOFError):
#                 break
#             except Exception as e:
#                 print(f"\nAn unexpected error occurred: {str(e)}")

#     async def cleanup(self):
#         print("\nShutting down...")
#         await self.exit_stack.aclose()

# async def main():
#     client = MCPClient()
#     try:
#         await client.connect_to_server(SERVER_CONFIG)
#         await client.chat_loop()
#     finally:
#         await client.cleanup()

# if __name__ == "__main__":
#     asyncio.run(main())
# # import asyncio
# # from typing import Optional
# # from contextlib import AsyncExitStack

# # # These imports are correct
# # from mcp import ClientSession, StdioServerParameters, Tool
# # from mcp.client.stdio import stdio_client

# # # These imports are also correct
# # from openai import OpenAI
# # from dotenv import load_dotenv
# # import json

# # # This will load the OPENAI_API_KEY from your .env file
# # load_dotenv()

# # # --- Model and Server Configuration ---
# # # MODEL = "qwen/qwen-2.5-7b-instruct"
# # MODEL = "mistralai/mistral-small-3.1-24b-instruct:free"
# # # MODEL = "google/gemini-pro"

# # SERVER_CONFIG = {
# #     "command": "/Users/fady/Desktop/internship/todo-list/todo_env/bin/python",
# #     "args": [
# #         "/Users/fady/Desktop/internship/todo-list/mcp/mcp_todo_server.py"
# #     ],
# #     "env": None
# # }

# # def convert_tool_format(tool: Tool) -> dict:
# #     """Converts MCP Tool schema to OpenAI-compatible tool schema."""
# #     # This structure is correct for the openai library's 'tools' parameter.
# #     return {
# #         "type": "function",
# #         "function": {
# #             "name": tool.name,
# #             "description": tool.description,
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": tool.inputSchema.get("properties", {}),
# #                 "required": tool.inputSchema.get("required", [])
# #             }
# #         }
# #     }

# # class MCPClient:
# #     """A client to interact with an MCP server using an OpenRouter model."""
# #     def __init__(self):
# #         # self.session is correctly typed as Optional here
# #         self.session: Optional[ClientSession] = None
# #         self.exit_stack = AsyncExitStack()
# #         self.openai = OpenAI(
# #             base_url="https://openrouter.ai/api/v1"
# #         )
# #         self.messages = []

# #     async def connect_to_server(self, server_config):
# #         server_params = StdioServerParameters(**server_config)
# #         stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
# #         self.stdio, self.write = stdio_transport
# #         # self.session is assigned a value here
# #         self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

# #         await self.session.initialize()

# #         # Added a check here, although it should always pass
# #         if not self.session:
# #             raise ConnectionError("Failed to establish MCP session.")

# #         response = await self.session.list_tools()
# #         print("\n✅ Connected to server with tools:", [tool.name for tool in response.tools])

# #         self.messages.append({
# #             "role": "system",
# #             "content": "You are a helpful assistant that manages a todo list. When asked to do something, call the appropriate tool. Do not make up information."
# #         })

# #     async def process_query(self, query: str) -> str:
# #         # --- FIX #1: Add a check to ensure self.session exists ---
# #         if not self.session:
# #             return "Error: MCP session is not connected. Cannot process query."

# #         self.messages.append({
# #             "role": "user",
# #             "content": query
# #         })

# #         # Get the latest list of tools from the server
# #         response = await self.session.list_tools()
# #         available_tools = [convert_tool_format(tool) for tool in response.tools]

# #         # Call OpenRouter to decide which tool to use
# #         # The Pylance warning on 'available_tools' can be safely ignored
# #         # as the format is correct for the API.
# #         response = self.openai.chat.completions.create(
# #             model=MODEL,
# #             tools=available_tools, # type: ignore
# #             tool_choice="auto",
# #             messages=self.messages
# #         )
# #         self.messages.append(response.choices[0].message.model_dump())

# #         final_text = []
# #         assistant_message = response.choices[0].message
        
# #         if assistant_message.tool_calls:
# #             # --- The model wants to call a tool ---
# #             tool_call = assistant_message.tool_calls[0]
# #             tool_name = tool_call.function.name
# #             tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

# #             print(f"🤖 LLM wants to call tool '{tool_name}' with args: {tool_args}")
            
# #             # --- FIX #2: Re-check self.session before using it again ---
# #             if not self.session:
# #                  raise ConnectionError("MCP session lost before tool execution.")

# #             # --- Execute the tool call against the MCP server ---
# #                        # --- Execute the tool call against the MCP server ---
# #             tool_output_str = ""
# #             try:
# #                 result = await self.session.call_tool(tool_name, tool_args)
                
# #                if result.content:
# #                     text_parts = []
# #                     for content_block in result.content:
# #                         if isinstance(content_block, TextContent):
# #                             text_parts.append(content_block.text)
                    
# #                     if text_parts:
# #                         tool_output_str = "\n".join(text_parts)
# #                     else:
# #                         tool_output_str = "Tool executed, but returned no text content."
# #                 else:
# #                     tool_output_str = "Tool executed successfully with no output."
# #                 # --- END OF FIX ---

# #                 print(f"✅ Tool '{tool_name}' executed. Result: {tool_output_str}")

# #             except Exception as e:
# #                 error_message = f"Error executing tool '{tool_name}': {str(e)}"
# #                 print(f"❌ {error_message}")
# #                 tool_output_str = error_message

# #             self.messages.append({
# #                 "role": "tool",
# #                 "tool_call_id": tool_call.id,
# #                 "name": tool_name,
# #                 "content": tool_output_str,
# #             })

# #             print("...Sending tool result back to LLM for final response...")
# #             final_response = self.openai.chat.completions.create(
# #                 model=MODEL,
# #                 messages=self.messages,
# #             )
# #             final_text.append(final_response.choices[0].message.content)
# #         else:
# #             # --- The model responded directly without a tool ---
# #             if assistant_message.content:
# #                 final_text.append(assistant_message.content)

# #         return "\n".join(final_text)

# #     async def chat_loop(self):
# #         print("\n🚀 OpenRouter MCP Client Started!")
# #         print("   Model:", MODEL)
# #         print("   Type 'quit' to exit.")

# #         while True:
# #             try:
# #                 query = input("\n👤 Query: ").strip()
# #                 if query.lower() == 'quit':
# #                     break
# #                 result = await self.process_query(query)
# #                 print("\n🤖 Result:")
# #                 print(result)
# #             except (KeyboardInterrupt, EOFError):
# #                 break
# #             except Exception as e:
# #                 print(f"An unexpected error occurred: {str(e)}")

# #     async def cleanup(self):
# #         print("\nShutting down...")
# #         await self.exit_stack.aclose()

# # async def main():
# #     client = MCPClient()
# #     try:
# #         await client.connect_to_server(SERVER_CONFIG)
# #         await client.chat_loop()
# #     finally:
# #         await client.cleanup()

# # if __name__ == "__main__":
# #     asyncio.run(main())