import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_database():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to {host} as {user}...")
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )
        cur = conn.cursor()
        print(f"Connected successfully!")
        
        sql = """
        -- 1. Member 테이블 생성 (상세 정보 저장용)
        CREATE TABLE IF NOT EXISTS public.member (
            id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
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

        -- 2. RLS 활성화
        ALTER TABLE public.member ENABLE ROW LEVEL SECURITY;

        -- 3. RLS 정책 설정
        DROP POLICY IF EXISTS "Users can manage their own member info" ON public.member;
        CREATE POLICY "Users can manage their own member info" ON public.member FOR ALL USING (auth.uid() = id);
        """
        
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("\n--- Database Setup Successfully Completed! ---")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    fix_database()
