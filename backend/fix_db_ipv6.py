import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_database_ipv6():
    # IPv6 address obtained from nslookup
    host = "2406:da12:557:f802:4cd0:2c86:6a0c:5cef"
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to IPv6 host {host}...")
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )
        cur = conn.cursor()
        print(f"Connected successfully via IPv6!")
        
        sql = """
        -- 1. Profiles 테이블 생성
        CREATE TABLE IF NOT EXISTS public.profiles (
            id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
            nickname TEXT UNIQUE,
            avatar_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- 2. Member 테이블 생성 (상세 정보 저장용)
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
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- 3. Rooms 테이블 생성
        CREATE TABLE IF NOT EXISTS public.rooms (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            owner_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT,
            layout_data JSONB DEFAULT '{}'::jsonb,
            visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'friends')),
            thumbnail_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- RLS 및 정책 설정 생략 (테이블 생성이 우선)
        """
        
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("\n--- Database Tables Created! ---")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    fix_database_ipv6()
