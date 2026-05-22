import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def test_login(email, password):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print(f"Login SUCCESS for {email}")
        print(f"User ID: {response.user.id}")
    except Exception as e:
        print(f"Login FAILED for {email}: {e}")

if __name__ == "__main__":
    test_login("loveforyou134@naver.com", "Q565bYsvDfJ@")
