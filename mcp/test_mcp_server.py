# test_mcp_server.py
# Test script to verify MCP server functionality
# ===================================
import asyncio
import json
from mcp_todo_server import TodoMCPServer

async def test_todo_operations():
    """Test basic todo operations"""
    api = TodoMCPServer()
    
    try:
        print("🧪 Testing Todo API MCP Server...")
        
        # Test creating a list
        print("\n1. Creating a todo list...")
        new_list = await api.create_todo_list("Test List")
        print(f"✅ Created list: {json.dumps(new_list, indent=2)}")
        list_id = new_list["id"]
        
        # Test creating items
        print("\n2. Creating todo items...")
        item1 = await api.create_todo_item(list_id, "Buy groceries")
        item2 = await api.create_todo_item(list_id, "Walk the dog", completed=True)
        print(f"✅ Created items: {item1['id']}, {item2['id']}")
        
        # Test getting all lists
        print("\n3. Getting all lists...")
        all_lists = await api.get_all_todo_lists()
        print(f"✅ Found {len(all_lists)} lists")
        for lst in all_lists:
            stats = lst.get('stats', {})
            print(f"   - {lst['title']}: {stats.get('total_items', 0)} items, {stats.get('percentage_complete', 0)}% complete")
        
        # Test updating an item
        print("\n4. Updating todo item...")
        updated_item = await api.update_todo_item(list_id, item1["id"], completed=True)
        print(f"✅ Updated item: {updated_item['title']} -> completed: {updated_item['completed']}")
        
        # Test getting specific list
        print("\n5. Getting specific list...")
        specific_list = await api.get_todo_list(list_id)
        stats = specific_list.get('stats', {})
        print(f"✅ List '{specific_list['title']}' has {len(specific_list['items'])} items")
        print(f"   Stats: {stats.get('completed_items', 0)}/{stats.get('total_items', 0)} completed ({stats.get('percentage_complete', 0)}%)")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(test_todo_operations())