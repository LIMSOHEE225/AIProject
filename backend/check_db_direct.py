
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_db_direct():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT", "5432")
    
    try:
        print(f"Connecting to {host}...")
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=port,
            connect_timeout=5
        )
        print("Connected successfully!")
        cur = conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'AI'")
        schema = cur.fetchone()
        if schema:
            print("Schema 'AI' exists.")
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'AI' AND table_name = 'member'")
            table = cur.fetchone()
            if table:
                print("Table 'AI.member' exists.")
            else:
                print("Table 'AI.member' does NOT exist.")
        else:
            print("Schema 'AI' does NOT exist.")
        conn.close()
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check_db_direct()
