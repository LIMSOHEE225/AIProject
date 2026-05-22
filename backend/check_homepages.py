from services.supabase_service import supabase_service
import asyncio

async def check_homepages():
    try:
        response = supabase_service.admin_client.table("homepage").select("member_id, title").execute()
        for hp in response.data:
            print(f"Member ID: {hp.get('member_id')}, Title: {hp.get('title')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_homepages())
