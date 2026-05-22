from services.supabase_service import supabase_service
import asyncio

async def update_homepage():
    member_id = "3f27cdc9-6bcd-456b-8926-4acc3004db9b"
    data = {
        "purpose": "나만의 여행 기록 (일기장)",
        "mood": "미니멀, 따뜻한 저녁 느낌",
        "color": "#F5F5DC",
        "menus": "일기장, 갤러리",
        "title": "나만의 여행 기록",
        "ai_layout_suggestion": None # Force AI to regenerate
    }
    
    print(f"Updating homepage for {member_id}...")
    try:
        res = supabase_service.admin_client.table("homepage").update(data).eq("member_id", member_id).execute()
        print("Update successful:", res.data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(update_homepage())
