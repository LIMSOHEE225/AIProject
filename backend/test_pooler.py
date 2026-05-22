
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_pooler():
    project_ref = "nbexahyuihdhhdkvdnti"
    # Try Seoul region pooler
    host = "aws-0-ap-northeast-2.pooler.supabase.com"
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
        print("Connected successfully via IPv4 pooler!")
        cur = conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = [r[0] for r in cur.fetchall()]
        print(f"Available schemas: {schemas}")
        
        if 'AI' in schemas:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'AI'")
            tables = [r[0] for r in cur.fetchall()]
            print(f"Tables in 'AI': {tables}")
        else:
            print("Schema 'AI' NOT found.")
            
        conn.close()
    except Exception as e:
        print(f"Pooler Connection Failed: {e}")

if __name__ == "__main__":
    test_pooler()
