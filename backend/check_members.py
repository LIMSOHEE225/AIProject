from services.supabase_service import supabase_service
import asyncio

async def get_members():
    try:
        response = supabase_service.admin_client.table("member").select("*").execute()
        for member in response.data:
            print(f"Nickname: {member.get('nickname')}, ID: {member.get('id')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_members())
