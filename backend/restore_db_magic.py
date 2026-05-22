import requests
import json

def fix_db_via_mgmt_api():
    project_ref = "nbexahyuihdhhdkvdnti"
    access_token = "YOUR_SUPABASE_TOKEN"
    
    # The "magic" endpoint discovered in temp files
    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sql_query = """
    -- 0. AI 스키마 생성
    CREATE SCHEMA IF NOT EXISTS "AI";

    -- 1. Member 테이블 생성 (상세 정보 저장용)
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
        parental_consent BOOLEAN DEFAULT FALSE,
        bio TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- 2. Profiles 테이블 생성 (기본 프로필)
    CREATE TABLE IF NOT EXISTS "AI".profiles (
        id UUID PRIMARY KEY,
        nickname TEXT UNIQUE,
        avatar_url TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- 3. Rooms 테이블 생성 (아지트 데이터)
    CREATE TABLE IF NOT EXISTS "AI".rooms (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        owner_id UUID REFERENCES "AI".profiles(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT,
        layout_data JSONB DEFAULT '{}'::jsonb,
        visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'friends')),
        thumbnail_url TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- 4. Homepage 테이블 생성 (AI 설문 데이터)
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

    -- 5. RLS 활성화
    ALTER TABLE "AI".profiles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "AI".rooms ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "AI".member ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "AI".homepage ENABLE ROW LEVEL SECURITY;

    -- 6. 기본 RLS 정책 설정
    DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON "AI".profiles;
    CREATE POLICY "Public profiles are viewable by everyone" ON "AI".profiles FOR SELECT USING (true);
    
    DROP POLICY IF EXISTS "Users can manage their own profile" ON "AI".profiles;
    CREATE POLICY "Users can manage their own profile" ON "AI".profiles FOR ALL USING (auth.uid() = id);

    DROP POLICY IF EXISTS "Public rooms are viewable by everyone" ON "AI".rooms;
    CREATE POLICY "Public rooms are viewable by everyone" ON "AI".rooms FOR SELECT USING (visibility = 'public' OR auth.uid() = owner_id);

    DROP POLICY IF EXISTS "Users can manage their own rooms" ON "AI".rooms;
    CREATE POLICY "Users can manage their own rooms" ON "AI".rooms FOR ALL USING (auth.uid() = owner_id);

    DROP POLICY IF EXISTS "Users can manage their own member info" ON "AI".member;
    CREATE POLICY "Users can manage their own member info" ON "AI".member FOR ALL USING (auth.uid() = id);

    DROP POLICY IF EXISTS "Users can manage their own homepage info" ON "AI".homepage;
    CREATE POLICY "Users can manage their own homepage info" ON "AI".homepage FOR ALL USING (auth.uid() = member_id);

    DROP POLICY IF EXISTS "Public homepages are viewable by everyone" ON "AI".homepage;
    CREATE POLICY "Public homepages are viewable by everyone" ON "AI".homepage FOR SELECT USING (visibility = 'public');

    -- 7. 가입 시 프로필 자동 생성 트리거 (auth.users 대상이므로 public 스키마의 함수로 두거나 AI로 옮김)
    CREATE OR REPLACE FUNCTION "AI".handle_new_user()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO "AI".profiles (id, nickname)
        VALUES (new.id, new.raw_user_meta_data->>'nickname');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;

    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
    CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION "AI".handle_new_user();

    -- 8. PostgREST 스키마 캐시 갱신 (추가된 컬럼 인식용)
    NOTIFY pgrst, 'reload schema';
    """
    
    payload = { "query": sql_query }
    
    print(f"Management API를 통해 데이터베이스 복구 중...")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print("\n--- [성공] 모든 테이블과 정책이 복구되었습니다. ---")
        else:
            print(f"\n--- [실패] API 응답 코드: {response.status_code} ---")
            print(f"오류 내용: {response.text}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    fix_db_via_mgmt_api()
