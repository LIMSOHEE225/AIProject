import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
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
            print(f"Bingo! Connected to {region}!")
            
            cur.execute("""
            -- profiles, rooms 테이블은 더 이상 사용하지 않음 (삭제됨)
            -- AI.Member 테이블을 기본 사용자 테이블로 사용
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            print("\n--- Database Setup Successfully Completed! ---")
            success = True
            break
        except Exception:
            # print(f"Failed {region}")
            continue
            
    if not success:
        print("\nAll regional poolers failed. Please verify your Project Region or Password.")

if __name__ == "__main__":
    setup_database()
