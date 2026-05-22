import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def check_auth_user(email):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        users = supabase.auth.admin.list_users()
        target = next((u for u in users if u.email == email), None)
        if target:
            print(f"User {email} exists in Auth. ID: {target.id}")
        else:
            print(f"User {email} does NOT exist in Auth.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_auth_user("loveforyou134@naver.com")
