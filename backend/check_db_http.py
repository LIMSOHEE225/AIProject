
from services.supabase_service import supabase_service
import asyncio

async def check_db():
    try:
        # Check if we can access the AI schema
        response = supabase_service.client.schema('AI').table('member').select('count', count='exact').limit(1).execute()
        print(f"Connection Successful! Member count: {response.count}")
    except Exception as e:
        print(f"Error accessing AI.member: {e}")

if __name__ == "__main__":
    import os
    import sys
    # Add current dir to path to import services
    sys.path.append(os.getcwd())
    
    # Supabase client is synchronous by default in the python library version typically used
    try:
        response = supabase_service.client.schema('AI').table('member').select('*', count='exact').limit(1).execute()
        print(f"Connection Successful! Member count: {response.count}")
    except Exception as e:
        print(f"Error accessing AI.member: {e}")
