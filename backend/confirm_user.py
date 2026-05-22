import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def confirm_user(email):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Find user ID first
        users = supabase.auth.admin.list_users()
        target = next((u for u in users if u.email == email), None)
        
        if not target:
            print(f"User {email} not found in Auth.")
            return

        # Manually confirm user
        supabase.auth.admin.update_user_by_id(
            target.id,
            attributes={"email_confirm": True}
        )
        print(f"Successfully CONFIRMED email for {email} in Auth.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    confirm_user("fdfdsfdfsd16@gmail.com")
