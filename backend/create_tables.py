
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_ai_tables():
    # .env에서 정보 가져오기
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

        # 1. AI 스키마 보장
        cur.execute("CREATE SCHEMA IF NOT EXISTS \"AI\";")
        print("Schema 'AI' ensured.")

        # 2. member 테이블 생성 (AI 스키마)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".member (
            id UUID PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT,
            real_name TEXT,
            nickname TEXT UNIQUE,
            birthdate TEXT,
            gender TEXT,
            telecom TEXT,
            phone TEXT,
            parental_consent BOOLEAN DEFAULT false,
            bio TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'AI.member' ensured.")

        # 3. homepage 테이블 생성/업데이트
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".homepage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            member_id UUID NOT NULL UNIQUE REFERENCES "AI".member(id) ON DELETE CASCADE,
            purpose VARCHAR(50) NOT NULL,
            purpose_extra TEXT,
            mood VARCHAR(50) NOT NULL,
            mood_extra TEXT,
            color TEXT,
            menus TEXT,
            title TEXT NOT NULL,
            visibility VARCHAR(20) DEFAULT 'public',
            ai_description TEXT,
            ai_layout_suggestion JSONB,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'AI.homepage' ensured.")

        # 4. rooms 테이블 생성 (기존 public.rooms가 있다면 이동하거나 새로 생성)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".rooms (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            member_id UUID REFERENCES "AI".member(id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            layout_data JSONB NOT NULL,
            preview_url TEXT,
            is_public BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'AI.rooms' ensured.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n--- All tables created in 'AI' schema! ---")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_ai_tables()
