# # test_bridge_api.py

# import httpx
# import pytest
# import json
# from fastapi.testclient import TestClient
# from httpx import Response
# import respx

# # Import your FastAPI app instance from your bridge_api file
# # Make sure your bridge_api.py file is in the same directory or accessible
# from lmstudio import app, LM_STUDIO_API_URL, CRUD_API_URL, MODEL_NAME

# # Use the TestClient for making requests to your FastAPI app
# client = TestClient(app)

# # ===================================
# # MOCK DATA AND RESPONSES
# # ===================================

# # Mock response when LLM decides to create a list
# MOCK_LLM_CREATE_REQUEST = {
#     "choices": [{
#         "index": 0, "finish_reason": "tool_calls",
#         "message": {
#             "role": "assistant",
#             "tool_calls": [{
#                 "id": "call_123", "type": "function",
#                 "function": {
#                     "name": "create_todo_list",
#                     "arguments": '{"title": "test list"}'
#                 }
#             }]
#         }
#     }]
# }

# # Mock response from our CRUD API after creating a list
# MOCK_CRUD_CREATE_RESPONSE = {"id": 1, "title": "test list", "items": []}

# # Mock response from LLM after a successful tool call
# MOCK_LLM_FINAL_RESPONSE = {
#     "choices": [{
#         "index": 0, "finish_reason": "stop",
#         "message": {"role": "assistant", "content": "Okay, the 'test list' has been created."}
#     }]
# }

# # --- Mocks for the multi-step delete operation ---

# # 1. LLM decides it needs to get all lists first
# MOCK_LLM_GET_ALL_REQUEST = {
#     "choices": [{"message": {"role": "assistant", "tool_calls": [{"id": "call_abc", "type": "function", "function": {"name": "get_all_todo_lists", "arguments": "{}"}}]}}]
# }

# # 2. CRUD API returns the list of all lists
# MOCK_CRUD_GET_ALL_RESPONSE = [{"id": 1, "title": "test list"}, {"id": 2, "title": "another list"}]

# # 3. LLM receives the list and decides to delete list with id 1
# MOCK_LLM_DELETE_REQUEST = {
#     "choices": [{"message": {"role": "assistant", "tool_calls": [{"id": "call_def", "type": "function", "function": {"name": "delete_todo_list", "arguments": '{"list_id": 1}'}}]}}]
# }

# # 4. CRUD API confirms deletion (204 No Content)

# # 5. LLM gives the final confirmation
# MOCK_LLM_DELETE_FINAL_RESPONSE = {
#     "choices": [{"message": {"role": "assistant", "content": "Okay, I've deleted the 'test list'."}}]
# }


# # ===================================
# # PYTEST FIXTURES AND TESTS
# # ===================================

# @pytest.fixture
# def mock_api_routes():
#     """A pytest fixture that sets up mocked routes for our external services."""
#     with respx.mock as mock:
#         yield mock

# def test_health_check():
#     """Test the root endpoint to ensure the server is running."""
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"status": "Bridge API Orchestrator is running"}

# def test_demo_magic_phrase():
#     """Test that the !reset state command works as expected."""
#     response = client.post("/chat", json={"prompt": "!reset state"})
#     assert response.status_code == 200
#     assert response.json() == {"role": "assistant", "content": "My conversational state has been reset. Let's start over."}

# def test_successful_single_step_tool_call(mock_api_routes):
#     """Test the full flow for a simple `create_todo_list` request."""
#     # 1. Mock the first call to LM Studio, which will request a tool call
#     mock_api_routes.post(f"{LM_STUDIO_API_URL}/chat/completions").mock(
#         side_effect=[
#             Response(200, json=MOCK_LLM_CREATE_REQUEST),
#             Response(200, json=MOCK_LLM_FINAL_RESPONSE)
#         ]
#     )
#     # 2. Mock the call to our CRUD API that the bridge will make
#     mock_api_routes.post(f"{CRUD_API_URL}/lists/").mock(
#         return_value=Response(201, json=MOCK_CRUD_CREATE_RESPONSE)
#     )

#     # 3. Make the actual request to our bridge API
#     response = client.post("/chat", json={"prompt": "create a test list"})

#     # 4. Assert the final response is correct
#     assert response.status_code == 200
#     assert response.json()["content"] == "Okay, the 'test list' has been created."

# def test_successful_multi_step_tool_call(mock_api_routes):
#     """Test the autonomous agent's ability to plan and execute a multi-step task."""
#     # Mock the sequence of API calls
#     # Turn 1: User asks to delete -> LLM asks to get all lists
#     # Turn 2: Bridge gets list -> LLM asks to delete the specific list
#     # Turn 3: Bridge deletes -> LLM gives final confirmation
#     mock_api_routes.post(f"{LM_STUDIO_API_URL}/chat/completions").mock(
#         side_effect=[
#             Response(200, json=MOCK_LLM_GET_ALL_REQUEST),
#             Response(200, json=MOCK_LLM_DELETE_REQUEST),
#             Response(200, json=MOCK_LLM_DELETE_FINAL_RESPONSE),
#         ]
#     )
#     # Mock the two CRUD calls the bridge will make
#     mock_api_routes.get(f"{CRUD_API_URL}/lists/").mock(return_value=Response(200, json=MOCK_CRUD_GET_ALL_RESPONSE))
#     mock_api_routes.delete(f"{CRUD_API_URL}/lists/1").mock(return_value=Response(204)) # 204 No Content

#     # Make the actual request
#     response = client.post("/chat", json={"prompt": "please delete the test list"})

#     # Assert the final response
#     assert response.status_code == 200
#     assert response.json()["content"] == "Okay, I've deleted the 'test list'."

# def test_crud_api_is_down(mock_api_routes):
#     """Test how the bridge API handles the CRUD service being unavailable."""
#     # 1. Mock the first call to LM Studio, which requests a tool call
#     mock_api_routes.post(f"{LM_STUDIO_API_URL}/chat/completions").mock(
#         return_value=Response(200, json=MOCK_LLM_CREATE_REQUEST)
#     )
#     # 2. Mock the CRUD API call to fail with a connection error
#     mock_api_routes.post(f"{CRUD_API_URL}/lists/").mock(side_effect=httpx.ConnectError("Connection refused"))

#     # 3. Make the request. The LLM should get an error message back.
#     # In this test, we are not mocking the final LLM response to see the raw tool result.
#     # For a full test, we'd mock the final LLM call as well.
    
#     # We will check that the bridge sends a valid error message to the LLM.
#     # We need to mock the final LLM response as well.
#     final_error_response = {"choices": [{"message": {"role": "assistant", "content": "Sorry, I couldn't connect to the data service."}}]}
#     mock_api_routes.post(f"{LM_STUDIO_API_URL}/chat/completions").mock(
#         side_effect=[
#             Response(200, json=MOCK_LLM_CREATE_REQUEST),
#             Response(200, json=final_error_response)
#         ]
#     )

#     response = client.post("/chat", json={"prompt": "create a test list"})

#     assert response.status_code == 200
#     assert "couldn't connect" in response.json()["content"]