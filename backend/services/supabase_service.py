from supabase import create_client, Client, ClientOptions
from core.config import settings

class SupabaseService:
    def __init__(self):
        self.url: str = settings.SUPABASE_URL
        self.key: str = settings.SUPABASE_ANON_KEY
        self.service_role_key: str = settings.SUPABASE_SERVICE_ROLE_KEY
        
        if self.url and self.key:
            # 기본 클라이언트 (anon key)
            self.client: Client = create_client(
                self.url, 
                self.key,
                options=ClientOptions(
                    schema="AI"
                )
            )
            
            # 관리자 클라이언트 (service role key) - 권한 우회 및 관리 작업용
            self.admin_client: Client = create_client(
                self.url,
                self.service_role_key,
                options=ClientOptions(
                    schema="AI"
                )
            )
        else:
            print("Warning: Supabase credentials not found in environment variables.")
            self.client = None
            self.admin_client = None

supabase_service = SupabaseService()

