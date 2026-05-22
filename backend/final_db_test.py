import psycopg2

def try_final_conn():
    host = "15.165.245.138" # aws-0-ap-northeast-2.pooler.supabase.com
    user = "postgres.nbexahyuihdhhdkvdnti"
    password = "M6wzCTKDF58faZhI"
    dbname = "postgres"
    port = "6543"
    
    try:
        print(f"Connecting to {host}:{port} as {user}...")
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )
        print("Connected!")
        conn.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    try_final_conn()
