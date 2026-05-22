import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class DBService:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.dbname = os.getenv("DB_NAME")
        self.port = os.getenv("DB_PORT", "5432")

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            port=self.port
        )

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if cur.description:
                    return cur.fetchall()
                conn.commit()
                return None
        finally:
            conn.close()

db_service = DBService()
