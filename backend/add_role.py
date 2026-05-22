import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    cur.execute("ALTER TABLE member ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT '회원';")
    conn.commit()
    cur.close()
    conn.close()
    print("Column 'role' added successfully.")
except Exception as e:
    print("Error:", e)
