
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_tables():
    # .env에서 정보 가져오기
    host = "aws-0-ap-northeast-2.pooler.supabase.com"
    password = os.getenv("DB_PASSWORD")
    user = "postgres.nbexahyuihdhhdkvdnti"
    dbname = "postgres"
    port = "6543"
    
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

        # 1. 기존 rooms 테이블 삭제 (존재한다면)
        print("Dropping 'AI'.rooms table if exists...")
        cur.execute("DROP TABLE IF EXISTS \"AI\".rooms CASCADE;")
        cur.execute("DROP TABLE IF EXISTS public.rooms CASCADE;")
        
        # 2. templates 테이블 생성
        print("Creating 'AI'.templates table...")
        cur.execute("""
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
        """)
        
        # 3. 인덱스 추가 (조회 성능 향상)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_templates_category ON \"AI\".templates(category);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_templates_is_public ON \"AI\".templates(is_public);")

        conn.commit()
        cur.close()
        conn.close()
        print("\n--- 'rooms' table deleted and 'templates' table created successfully! ---")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    update_tables()
