import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def reset_password(email, new_password):
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

        # Update password
        supabase.auth.admin.update_user_by_id(
            target.id,
            attributes={"password": new_password}
        )
        print(f"Successfully reset password for {email} in Auth.")
        
        # Also update in AI.member table (though not strictly necessary for login)
        import bcrypt
        hashed = bcrypt.hashpw(new_password[:72].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        supabase.table("member").update({"password": hashed}).eq("id", target.id).execute()
        print(f"Successfully updated hashed password in member table.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_password("loveforyou134@naver.com", "Q565bYsvDfJ@")
