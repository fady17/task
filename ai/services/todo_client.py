# ai/services/todo_client.py
"""
Client for interacting with the external Todo CRUD API.
This class handles all HTTP requests and error handling for the todo service.
"""
import httpx
from typing import Optional, Any, Dict

from ..config import CRUD_API_URL, logger # type: ignore

class TodoAPIClient:
    def __init__(self, base_url: str = CRUD_API_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, json=data)
            response.raise_for_status()
            if response.status_code == 204:
                return {"success": True, "message": "Operation completed"}
            return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            logger.error(f"API Error: {error_msg} for URL: {url}")
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Request Error: {str(e)} for URL: {url}")
            raise Exception(f"Request failed: {str(e)}")
    
    async def close(self):
        """Gracefully close the httpx client."""
        await self.client.aclose()

    async def create_todo_list(self, title: str):
        return await self._request("POST", "/lists/", {"title": title})
    
    async def get_all_todo_lists(self):
        return await self._request("GET", "/lists/")
    
    async def get_todo_list(self, list_id: int):
        return await self._request("GET", f"/lists/{list_id}")
    
    async def update_todo_list(self, list_id: int, title: str):
        return await self._request("PUT", f"/lists/{list_id}", {"title": title})
    
    async def delete_todo_list(self, list_id: int):
        return await self._request("DELETE", f"/lists/{list_id}")
    
    async def create_todo_item(self, list_id: int, title: str, completed: bool = False):
        return await self._request("POST", f"/{list_id}/items/", {"title": title, "completed": completed})
    
    async def update_todo_item(self, list_id: int, item_id: int, title: Optional[str] = None, completed: Optional[bool] = None):
        update_data = {}
        if title is not None: update_data["title"] = title
        if completed is not None: update_data["completed"] = completed
        if not update_data: raise Exception("At least one field (title or completed) must be provided")
        return await self._request("PUT", f"/{list_id}/items/{item_id}", update_data)
    
    async def delete_todo_item(self, list_id: int, item_id: int):
        return await self._request("DELETE", f"/{list_id}/items/{item_id}")