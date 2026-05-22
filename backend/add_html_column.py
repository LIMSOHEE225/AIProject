
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_homepage_table():
    host = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    user = os.getenv("DB_USER", "postgres")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )
        cur = conn.cursor()
        
        # html_content 컬럼 추가
        cur.execute('ALTER TABLE "AI".homepage ADD COLUMN IF NOT EXISTS html_content TEXT;')
        print("Column 'html_content' added to 'AI.homepage' table.")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    update_homepage_table()
