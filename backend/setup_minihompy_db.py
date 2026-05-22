
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def setup_minihompy_db():
    # IPv6 주소를 직접 사용 (DNS 해석 문제 방지)
    host = "2406:da12:557:f802:4cd0:2c86:6a0c:5cef"
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER", "postgres")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to DB at IPv6: {host}...")
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

        # 1. 미니홈피 게시글 테이블
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".minihompy_posts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            member_id UUID NOT NULL REFERENCES "AI".member(id) ON DELETE CASCADE,
            menu_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            images JSONB DEFAULT '[]',
            like_count INT DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'AI.minihompy_posts' ensured.")

        # 기존 minihompy_posts 테이블이 존재할 경우 comments 컬럼 삭제 마이그레이션 실행
        cur.execute("""
        ALTER TABLE "AI".minihompy_posts DROP COLUMN IF EXISTS comments;
        """)
        print("Column 'comments' in 'AI.minihompy_posts' dropped if existed.")

        # 2. 미니홈피 방명록 테이블
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".minihompy_guestbook (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            member_id UUID NOT NULL REFERENCES "AI".member(id) ON DELETE CASCADE,
            user_nickname TEXT NOT NULL,
            content TEXT NOT NULL,
            reply_to TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        print("Table 'AI.minihompy_guestbook' ensured.")

        # 3. homepage 테이블에 menus 컬럼 확인
        cur.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='AI' AND table_name='homepage' AND column_name='menus') THEN
                ALTER TABLE "AI".homepage ADD COLUMN menus TEXT;
            END IF;
        END $$;
        """)
        print("Column 'menus' in 'AI.homepage' ensured.")

        # 4. 미니홈피 댓글(minihompy_comments) 테이블 생성
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".minihompy_comments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            member_id UUID NOT NULL REFERENCES "AI".member(id) ON DELETE CASCADE,
            post_id UUID REFERENCES "AI".minihompy_posts(id) ON DELETE CASCADE,
            menu_id TEXT NOT NULL,
            writer_name TEXT NOT NULL,
            content TEXT NOT NULL,
            is_private BOOLEAN DEFAULT FALSE,
            reply_to TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        
        -- 인덱스 생성
        CREATE INDEX IF NOT EXISTS idx_minihompy_comments_member_id ON "AI".minihompy_comments(member_id);
        CREATE INDEX IF NOT EXISTS idx_minihompy_comments_post_id ON "AI".minihompy_comments(post_id);
        CREATE INDEX IF NOT EXISTS idx_minihompy_comments_menu_id ON "AI".minihompy_comments(menu_id);

        -- writer_id 컬럼 제거 (로그인 식별자 단순화 정책)
        ALTER TABLE "AI".minihompy_comments DROP COLUMN IF EXISTS writer_id;
        """)
        print("Table 'AI.minihompy_comments' ensured and writer_id dropped if existed.")

        conn.commit()
        cur.close()
        conn.close()
        print("\n--- Minihompy DB Setup Complete! ---")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    setup_minihompy_db()
