# test_connection.py
import asyncio

# Import the engine we just configured in app/database.py
from app.db.database import engine

async def check_connection():
    """
    This function attempts to establish a connection to the database and
    execute a simple query to verify that everything is working.
    """
    try:
        # 'engine.connect()' returns an async context manager.
        async with engine.connect() as connection:
            print("--------------------------------------------------")
            print("✅ Connection to the database was successful!")
            print("--------------------------------------------------")
            
            # We can optionally perform a simple query.
            # result = await connection.execute(text("SELECT 1"))
            # print(f"Query result: {result.scalar()}")
            
    except Exception as e:
       
        print("🔥 Failed to connect to the database.")
        print(f"Error: {e}")
        

# Use asyncio.run() to execute our async function.
if __name__ == "__main__":
    asyncio.run(check_connection())