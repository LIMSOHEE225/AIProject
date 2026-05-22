import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def add_likes_views_via_api():
    project_ref = "nbexahyuihdhhdkvdnti"
    # Access token from restore_db_magic.py
    access_token = "YOUR_SUPABASE_TOKEN"
    
    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sql_query = """
    -- Posts 테이블에 좋아요 및 조회수 컬럼 추가
    -- 먼저 public 스키마에 있는지 확인
    ALTER TABLE IF EXISTS public.posts 
    ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
    
    -- AI 스키마에도 시도 (있다면)
    DO $$ 
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'AI') THEN
            ALTER TABLE "AI".posts 
            ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
        END IF;
    END $$;

    -- PostgREST 스키마 캐시 갱신
    NOTIFY pgrst, 'reload schema';
    """
    
    payload = { "query": sql_query }
    
    print(f"Management API를 통해 컬럼 추가 중...")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print("\n--- [성공] like_count와 view_count 컬럼이 추가되었습니다. ---")
        else:
            print(f"\n--- [실패] API 응답 코드: {response.status_code} ---")
            print(f"오류 내용: {response.text}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    add_likes_views_via_api()
