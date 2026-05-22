const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';

const CONFIG = {
    API_BASE_URL: isLocal 
        ? "http://127.0.0.1:8000/api/v1" 
        : "https://aiproject-3dtf.onrender.com/api/v1", // 배포 후 Render 백엔드 주소로 변경
    AUTH_TOKEN_KEY: "dearzit_access_token",
    USER_INFO_KEY: "dearzit_user_info",
    SUPABASE_URL: "https://nbexahyuihdhhdkvdnti.supabase.co",
    SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5iZXhhaHl1aWhkaGhka3ZkbnRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwMzIzNzUsImV4cCI6MjA5MzYwODM3NX0.Q_ii18gyIFbSSV2CAgz4ExLL2KUl8X46Am0RfRpyPCk"
};

window.CONFIG = CONFIG;
