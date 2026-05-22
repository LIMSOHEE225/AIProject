
from services.supabase_service import supabase_service

def insert_test_post():
    try:
        data = {
            "title": "안녕하세요! 첫 인사 드립니다.",
            "content": "톡지트 소통게시판이 오픈되었습니다. 자유롭게 이야기를 나눠보세요!\n\n여러분의 아지트를 자랑해 주세요.",
            "author_nickname": "운영자"
        }
        response = supabase_service.client.table("posts").insert(data).execute()
        print("Post inserted successfully!")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_test_post()
