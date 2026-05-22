
from services.supabase_service import supabase_service

def check_table():
    try:
        response = supabase_service.client.table("posts").select("*").limit(1).execute()
        print("Table 'posts' exists!")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_table()
