
import requests
import json

def add_column_to_public():
    project_ref = "nbexahyuihdhhdkvdnti"
    access_token = "YOUR_SUPABASE_TOKEN"
    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    sql_query = """
    -- public.member 테이블에 parental_consent 컬럼 추가
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='member' AND column_name='parental_consent') THEN
            ALTER TABLE public.member ADD COLUMN parental_consent BOOLEAN DEFAULT FALSE;
        END IF;
    END $$;
    """
    
    payload = { "query": sql_query }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print("Successfully added parental_consent to public.member")
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column_to_public()
