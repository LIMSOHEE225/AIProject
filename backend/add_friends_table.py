
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_friends_table():
    host = "aws-0-ap-northeast-2.pooler.supabase.com"
    password = os.getenv("DB_PASSWORD")
    user = "postgres.nbexahyuihdhhdkvdnti"
    dbname = "postgres"
    port = "6543"
    
    try:
        conn = psycopg2.connect(
            host=host, database=dbname, user=user, password=password, port=port
        )
        cur = conn.cursor()
        
        # 친구 테이블 생성
        cur.execute("""
        CREATE TABLE IF NOT EXISTS "AI".friends (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES "AI".member(id) ON DELETE CASCADE,
            friend_id UUID NOT NULL REFERENCES "AI".member(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'accepted',
            created_at TIMESTAMPTZ DEFAULT now(),
            UNIQUE(user_id, friend_id)
        );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("Friends table created successfully!")
        return True
    except Exception as e:
        print(f"Error creating friends table: {e}")
        return False

if __name__ == "__main__":
    add_friends_table()
