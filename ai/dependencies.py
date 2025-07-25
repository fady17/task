# ai/dependencies.py
"""
Manages shared dependencies for the application, such as API client instances.
This allows for easy mocking in tests and promotes a clean, decoupled architecture.
"""
from .services.todo_client import TodoAPIClient

# Create a single, shared instance of the TodoAPIClient
# This instance will be reused across the application lifetime
_todo_api_client = TodoAPIClient()

def get_todo_api_client() -> TodoAPIClient:
    """Dependency injector that provides the singleton TodoAPIClient instance."""
    return _todo_api_client