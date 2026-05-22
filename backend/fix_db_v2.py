import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_database():
    project_ref = "nbexahyuihdhhdkvdnti"
    password = os.getenv("DB_PASSWORD")
    user = f"postgres.{project_ref}"
    
    # Supabase의 주요 리전 풀러 리스트
    regions = [
        "ap-northeast-2", # Seoul
        "ap-southeast-1", # Singapore
        "us-east-1",      # N. Virginia
        "eu-central-1",   # Frankfurt
        "us-west-1"       # Northern California
    ]
    
    success = False
    for region in regions:
        host = f"aws-0-{region}.pooler.supabase.com"
        try:
            print(f"Trying region {region} ({host})...")
            conn = psycopg2.connect(
                host=host,
                database="postgres",
                user=user,
                password=password,
                port="6543",
                connect_timeout=5
            )
            cur = conn.cursor()
            print(f"Connected to {region}!")
            
            sql = """
            -- 1. Profiles 테이블 생성
            CREATE TABLE IF NOT EXISTS public.profiles (
                id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
                nickname TEXT UNIQUE,
                avatar_url TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            -- 2. Rooms 테이블 생성
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

            -- 3. Member 테이블 생성 (상세 정보 저장용)
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

            -- 4. RLS 활성화
            ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.member ENABLE ROW LEVEL SECURITY;

            -- 5. RLS 정책 설정
            DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.profiles;
            CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles FOR SELECT USING (true);
            
            DROP POLICY IF EXISTS "Users can manage their own profile" ON public.profiles;
            CREATE POLICY "Users can manage their own profile" ON public.profiles FOR ALL USING (auth.uid() = id);

            DROP POLICY IF EXISTS "Public rooms are viewable by everyone" ON public.rooms;
            CREATE POLICY "Public rooms are viewable by everyone" ON public.rooms FOR SELECT USING (visibility = 'public' OR auth.uid() = owner_id);

            DROP POLICY IF EXISTS "Users can manage their own rooms" ON public.rooms;
            CREATE POLICY "Users can manage their own rooms" ON public.rooms FOR ALL USING (auth.uid() = owner_id);

            DROP POLICY IF EXISTS "Users can manage their own member info" ON public.member;
            CREATE POLICY "Users can manage their own member info" ON public.member FOR ALL USING (auth.uid() = id);

            -- 6. 가입 시 프로필 자동 생성 트리거
            CREATE OR REPLACE FUNCTION public.handle_new_user()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO public.profiles (id, nickname)
                VALUES (new.id, new.raw_user_meta_data->>'nickname');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;

            DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
            CREATE TRIGGER on_auth_user_created
                AFTER INSERT ON auth.users
                FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
            """
            
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            print("\n--- Database Setup Successfully Completed! ---")
            success = True
            break
        except Exception as e:
            print(f"Failed {region}: {e}")
            continue
            
    if not success:
        print("\nAll regional poolers failed. Please verify your Project Region or Password.")

if __name__ == "__main__":
    fix_database()
