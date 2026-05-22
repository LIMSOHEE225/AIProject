
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_likes_views():
    host = os.getenv("DB_HOST", "db.nbexahyuihdhhdkvdnti.supabase.co")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to {host}...")
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=port,
            connect_timeout=10
        )
        cur = conn.cursor()
        print("Connected!")
        
        # Check if schema "AI" exists, if not use public
        # Based on the previous scripts, it seems it was using "AI" schema or public.
        # Let's check which one exists or just try both.
        
        sql = """
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
        """
        
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("\n--- Columns like_count and view_count added successfully! ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_likes_views()

