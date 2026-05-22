
import requests
import json

def run_migration():
    project_ref = "nbexahyuihdhhdkvdnti"
    # Using the token found in try_sql.py
    access_token = "YOUR_SUPABASE_TOKEN"
    
    url = f"https://api.supabase.com/v1/projects/{project_ref}/sql"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sql_query = """
    -- 1. AI 스키마 보장
    CREATE SCHEMA IF NOT EXISTS "AI";

    -- 2. 기존 rooms 테이블 삭제 (AI 및 public 스키마)
    DROP TABLE IF EXISTS "AI".rooms CASCADE;
    DROP TABLE IF EXISTS public.rooms CASCADE;

    -- 3. templates 테이블 생성
    CREATE TABLE IF NOT EXISTS "AI".templates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        creator_id UUID REFERENCES "AI".member(id) ON DELETE SET NULL,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        layout_data JSONB NOT NULL,
        thumbnail_url TEXT,
        category VARCHAR(50),
        is_public BOOLEAN DEFAULT true,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );

    -- 4. 인덱스 생성
    CREATE INDEX IF NOT EXISTS idx_templates_category ON "AI".templates(category);
    CREATE INDEX IF NOT EXISTS idx_templates_is_public ON "AI".templates(is_public);
    """
    
    payload = {"query": sql_query}
    
    print(f"Executing Migration SQL...")
    res = requests.post(url, headers=headers, json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")

if __name__ == "__main__":
    run_migration()
