import requests
import json

def run_sql():
    project_ref = "nbexahyuihdhhdkvdnti"
    access_token = "YOUR_SUPABASE_TOKEN"
    
    # Try the /query endpoint again but with correct payload if it exists
    # Or try /sql if available
    url = f"https://api.supabase.com/v1/projects/{project_ref}/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sql_query = """
    -- 0. AI 스키마 생성
    CREATE SCHEMA IF NOT EXISTS "AI";

    -- 1. member 테이블에 parental_consent 컬럼 추가
    ALTER TABLE "AI".member ADD COLUMN IF NOT EXISTS parental_consent BOOLEAN DEFAULT FALSE;
    
    -- 2. 만약 테이블이 없는 경우를 대비한 전체 생성 스크립트 (이미 있으면 무시됨)
    CREATE TABLE IF NOT EXISTS "AI".member (
        id UUID PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT,
        real_name TEXT,
        nickname TEXT,
        birthdate DATE,
        gender TEXT,
        telecom TEXT,
        phone TEXT,
        bio TEXT,
        parental_consent BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    payload = {"query": sql_query}
    
    print(f"Executing SQL to add parental_consent column...")
    res = requests.post(url, headers=headers, json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")

if __name__ == "__main__":
    run_sql()
