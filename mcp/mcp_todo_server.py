# mcp_todo_server.py
"""
MCP (Model Context Protocol) Server for Todo API

This server exposes the FastAPI todo application as MCP tools that can be used
by LLMs running in LMStudio or other compatible environments.

Installation requirements:
pip install mcp httpx asyncio
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TodoMCPServer:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()

    async def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Any:
        """Make HTTP request to the FastAPI server"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, json=json_data)
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {"success": True, "message": "Operation completed successfully"}
            
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_response = e.response.json()
                error_detail = error_response.get("detail", str(e))
            except:
                error_detail = str(e)
            
            raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    # ===========================================
    # TODO LIST OPERATIONS
    # ===========================================

    async def create_todo_list(self, title: str) -> Dict[str, Any]:
        """Create a new todo list"""
        return await self._make_request("POST", "/lists/", {"title": title})

    async def get_all_todo_lists(self) -> List[Dict[str, Any]]:
        """Get all todo lists with their items and stats"""
        result = await self._make_request("GET", "/lists/")
        # The API returns a list directly
        return result if isinstance(result, list) else []

    async def get_todo_list(self, list_id: int) -> Dict[str, Any]:
        """Get a specific todo list by ID"""
        return await self._make_request("GET", f"/lists/{list_id}")

    async def update_todo_list(self, list_id: int, title: str) -> Dict[str, Any]:
        """Update a todo list's title"""
        return await self._make_request("PUT", f"/lists/{list_id}", {"title": title})

    async def delete_todo_list(self, list_id: int) -> Dict[str, Any]:
        """Delete a todo list"""
        return await self._make_request("DELETE", f"/lists/{list_id}")

    # ===========================================
    # TODO ITEM OPERATIONS
    # ===========================================

    async def create_todo_item(self, list_id: int, title: str, completed: bool = False) -> Dict[str, Any]:
        """Create a new todo item in a list"""
        return await self._make_request("POST", f"/{list_id}/items/", {
            "title": title,
            "completed": completed
        })

    async def update_todo_item(self, list_id: int, item_id: int, title: Optional[str] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
        """Update a todo item's title and/or completed status"""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if completed is not None:
            update_data["completed"] = completed
        
        if not update_data:
            raise Exception("At least one field (title or completed) must be provided for update")
        
        return await self._make_request("PUT", f"/{list_id}/items/{item_id}", update_data)

    async def delete_todo_item(self, list_id: int, item_id: int) -> Dict[str, Any]:
        """Delete a todo item"""
        return await self._make_request("DELETE", f"/{list_id}/items/{item_id}")

# Create the MCP server instance
todo_api = TodoMCPServer()
server = Server("todo-api")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available tools"""
    return [
        # Todo List Tools
        Tool(
            name="create_todo_list",
            description="Create a new todo list",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the todo list"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="get_all_todo_lists", 
            description="Get all todo lists with their items and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_todo_list",
            description="Get a specific todo list by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "description": "The ID of the todo list"
                    }
                },
                "required": ["list_id"]
            }
        ),
        Tool(
            name="update_todo_list",
            description="Update a todo list's title",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer", 
                        "description": "The ID of the todo list"
                    },
                    "title": {
                        "type": "string",
                        "description": "The new title for the todo list"
                    }
                },
                "required": ["list_id", "title"]
            }
        ),
        Tool(
            name="delete_todo_list",
            description="Delete a todo list and all its items",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "description": "The ID of the todo list to delete"
                    }
                },
                "required": ["list_id"]
            }
        ),
        
        # Todo Item Tools
        Tool(
            name="create_todo_item",
            description="Create a new todo item in a specific list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "description": "The ID of the todo list"
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the todo item"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Whether the item is completed (default: false)",
                        "default": False
                    }
                },
                "required": ["list_id", "title"]
            }
        ),
        Tool(
            name="update_todo_item",
            description="Update a todo item's title and/or completed status",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "description": "The ID of the todo list"
                    },
                    "item_id": {
                        "type": "integer",
                        "description": "The ID of the todo item"
                    },
                    "title": {
                        "type": "string",
                        "description": "The new title for the todo item (optional)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Whether the item is completed (optional)"
                    }
                },
                "required": ["list_id", "item_id"]
            }
        ),
        Tool(
            name="delete_todo_item",
            description="Delete a todo item from a list",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "description": "The ID of the todo list"
                    },
                    "item_id": {
                        "type": "integer",
                        "description": "The ID of the todo item to delete"
                    }
                },
                "required": ["list_id", "item_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from the LLM"""
    try:
        if name == "create_todo_list":
            result = await todo_api.create_todo_list(arguments["title"])
            
        elif name == "get_all_todo_lists":
            result = await todo_api.get_all_todo_lists()
            
        elif name == "get_todo_list":
            result = await todo_api.get_todo_list(arguments["list_id"])
            
        elif name == "update_todo_list":
            result = await todo_api.update_todo_list(arguments["list_id"], arguments["title"])
            
        elif name == "delete_todo_list":
            result = await todo_api.delete_todo_list(arguments["list_id"])
            
        elif name == "create_todo_item":
            result = await todo_api.create_todo_item(
                arguments["list_id"], 
                arguments["title"], 
                arguments.get("completed", False)
            )
            
        elif name == "update_todo_item":
            result = await todo_api.update_todo_item(
                arguments["list_id"],
                arguments["item_id"],
                arguments.get("title"),
                arguments.get("completed")
            )
            
        elif name == "delete_todo_item":
            result = await todo_api.delete_todo_item(arguments["list_id"], arguments["item_id"])
            
        else:
            raise Exception(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    # Initialize server options
    options = InitializationOptions(
        server_name="todo-api",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                options,
            )
    finally:
        await todo_api.close()

if __name__ == "__main__":
    asyncio.run(main())