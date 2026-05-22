
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_community_db():
    host = os.getenv("DB_HOST", "db.nbexahyuihdhhdkvdnti.supabase.co")
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER", "postgres")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to {host}...")
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )
        cur = conn.cursor()
        print("Connected!")
        
        sql = """
        -- AI 스키마 보장
        CREATE SCHEMA IF NOT EXISTS "AI";

        -- Posts 테이블 생성 (AI 스키마)
        CREATE TABLE IF NOT EXISTS "AI".posts (
            id SERIAL PRIMARY KEY,
            member_id UUID REFERENCES "AI".member(id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_nickname TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- RLS 설정 (필요한 경우)
        ALTER TABLE "AI".posts ENABLE ROW LEVEL SECURITY;

        -- 누구나 조회 가능하도록 설정
        DROP POLICY IF EXISTS "Anyone can view posts" ON "AI".posts;
        CREATE POLICY "Anyone can view posts" ON "AI".posts FOR SELECT USING (true);

        -- 누구나 작성 가능하도록 설정 (테스트용)
        DROP POLICY IF EXISTS "Anyone can insert posts" ON "AI".posts;
        CREATE POLICY "Anyone can insert posts" ON "AI".posts FOR INSERT WITH CHECK (true);
        """
        
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("\n--- Community Database Setup Successfully Completed! ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_community_db()
