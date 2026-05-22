from services.supabase_service import supabase_service

def check_posts():
    try:
        response = supabase_service.client.table("posts").select("*").execute()
        print(f"Total posts: {len(response.data)}")
        if response.data:
            print("First post data:")
            print(response.data[0])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_posts()
