import requests
import json

def create_comments_table():
    project_ref = "nbexahyuihdhhdkvdnti"
    access_token = "YOUR_SUPABASE_TOKEN"
    
    url = f"https://api.supabase.com/v1/projects/{project_ref}/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # AI.minihompy_comments 테이블 생성 SQL
    # post_id: 어떤 게시글에 달린 댓글인지 참조 (minihompy_posts.id 외래키, nullable)
    # menu_id: 어떤 메뉴 탭의 댓글인지 구분 (NOT NULL)
    sql_query = """
    -- 1. minihompy_comments 테이블 생성
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
    
    -- 2. 인덱스 추가로 조회 성능 개선
    CREATE INDEX IF NOT EXISTS idx_minihompy_comments_member_id ON "AI".minihompy_comments(member_id);
    CREATE INDEX IF NOT EXISTS idx_minihompy_comments_post_id ON "AI".minihompy_comments(post_id);
    CREATE INDEX IF NOT EXISTS idx_minihompy_comments_menu_id ON "AI".minihompy_comments(menu_id);

    -- 3. 기존 minihompy_posts 테이블의 comments 컬럼 삭제 (관계형 테이블 전환에 따름)
    ALTER TABLE "AI".minihompy_posts DROP COLUMN IF EXISTS comments;

    -- 4. minihompy_comments 테이블에서 writer_id 컬럼 제거 (로그인 식별자 단순화 정책)
    ALTER TABLE "AI".minihompy_comments DROP COLUMN IF EXISTS writer_id;
    """
    
    payload = {"query": sql_query}
    
    print(f"Executing SQL to create minihompy_comments table...")
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
        if res.status_code == 201 or res.status_code == 200:
            print("\n--- DB Setup Complete! Table AI.minihompy_comments created successfully. ---")
            return True
        else:
            print("\n--- DB Setup Failed ---")
            return False
    except Exception as e:
        print(f"Request Error: {e}")
        return False

if __name__ == "__main__":
    create_comments_table()
