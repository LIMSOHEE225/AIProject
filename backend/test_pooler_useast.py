
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_pooler_useast():
    project_ref = "nbexahyuihdhhdkvdnti"
    host = "aws-0-us-east-1.pooler.supabase.com"
    user = f"postgres.{project_ref}"
    password = os.getenv("DB_PASSWORD")
    dbname = "postgres"
    port = "6543"
    
    try:
        print(f"Connecting to pooler {host} as {user}...")
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=port,
            connect_timeout=5
        )
        print("Connected successfully via US-East-1 IPv4 pooler!")
        conn.close()
        return True
    except Exception as e:
        print(f"US-East-1 Pooler Failed: {e}")
        return False

if __name__ == "__main__":
    test_pooler_useast()
