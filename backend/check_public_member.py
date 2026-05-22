
from services.supabase_service import supabase_service

def check_public_member():
    try:
        response = supabase_service.client.table('member').select('*', count='exact').limit(1).execute()
        print(f"Public Member count: {response.count}")
        if response.data:
            print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error accessing public.member: {e}")

if __name__ == "__main__":
    check_public_member()
