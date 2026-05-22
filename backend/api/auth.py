from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from services.supabase_service import supabase_service
from services.db_service import db_service
from passlib.context import CryptContext
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 비밀번호 암호화 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    real_name: str
    nickname: str
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    telecom: Optional[str] = None
    phone: Optional[str] = None
    parental_consent: Optional[bool] = False
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RoleUpdate(BaseModel):
    role: str

@router.get("/check-email")
async def check_email(email: str):
    """
    이메일 중복 확인 API (Supabase HTTP Client 사용)
    """
    try:
        # 1. DB (AI.member) 테이블에서 확인
        db_response = supabase_service.admin_client.table("member").select("email").eq("email", email).execute()
        if len(db_response.data) > 0:
            return {"available": False, "reason": "이미 등록된 사용자입니다."}
            
        # 2. Supabase Auth에서 확인 (DB에는 없지만 Auth에만 남아있는 '고립된 계정' 체크)
        # 모든 사용자를 가져와서 확인하는 것은 비효율적이지만, admin.list_users() 외에 특정 이메일로 유저를 찾는 direct API가 라이브러리에 따라 다를 수 있음.
        # 여기서는 안정적인 admin.list_users()를 사용하되 개발 단계임을 감안함.
        users_response = supabase_service.admin_client.auth.admin.list_users()
        is_in_auth = any(u.email == email for u in users_response)
        
        if is_in_auth:
            return {"available": False, "reason": "인증 시스템에 기록이 남아있는 계정입니다. (고립된 계정)"}

        return {"available": True}
    except Exception as e:
        print(f"Email Check Error: {str(e)}")
        # 에러 발생 시 안전하게 사용 불가능으로 처리하거나 상세 메시지 반환
        raise HTTPException(status_code=400, detail=f"이메일 확인 중 오류 발생: {str(e)}")

@router.get("/check-nickname")
async def check_nickname(nickname: str):
    """
    닉네임 중복 확인 API (Supabase HTTP Client 사용)
    """
    try:
        # public.member 테이블에서 확인
        response = supabase_service.client.table("member").select("nickname").eq("nickname", nickname).execute()
        is_available = len(response.data) == 0
        return {"available": is_available}
    except Exception as e:
        print(f"Nickname Check Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"닉네임 확인 중 오류 발생: {str(e)}")

@router.post("/signup")
async def signup(user_data: UserSignup):
    """
    회원가입 API: Supabase Auth 가입 및 public.member 테이블 상세 정보 저장
    """
    auth_user_id = None
    try:
        # 1. Supabase Auth 가입 시도
        try:
            auth_response = supabase_service.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "nickname": user_data.nickname,
                        "real_name": user_data.real_name
                    }
                }
            })
            
            if not auth_response.user:
                raise Exception("가입 처리 중 유저 정보를 받지 못했습니다.")
            
            auth_user_id = auth_response.user.id
            session = auth_response.session

        except Exception as e:
            # "이미 가입된 이메일" 에러 발생 시, DB에 데이터가 있는지 재확인
            if "already registered" in str(e).lower():
                db_check = supabase_service.admin_client.table("member").select("id").eq("email", user_data.email).execute()
                
                # DB에 데이터가 없다면 '고립된 계정'이므로 삭제 후 재가입 시도
                if not db_check.data:
                    print(f"Orphaned account detected for {user_data.email}. Cleaning up and retrying...")
                    users = supabase_service.admin_client.auth.admin.list_users()
                    target_user = next((u for u in users if u.email == user_data.email), None)
                    
                    if target_user:
                        supabase_service.admin_client.auth.admin.delete_user(target_user.id)
                        # 재시도
                        auth_response = supabase_service.client.auth.sign_up({
                            "email": user_data.email,
                            "password": user_data.password,
                            "options": {
                                "data": {
                                    "nickname": user_data.nickname,
                                    "real_name": user_data.real_name
                                }
                            }
                        })
                        if not auth_response.user:
                            raise Exception("재시도 중 가입 처리에 실패했습니다.")
                        auth_user_id = auth_response.user.id
                        session = auth_response.session
                    else:
                        raise e
                else:
                    raise e
            else:
                raise e

        # 2. 비밀번호 암호화 (member 테이블 저장용)
        # bcrypt의 72바이트 제한을 준수하기 위해 트렁케이트 처리
        import bcrypt
        safe_password = user_data.password[:72].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(safe_password, salt).decode('utf-8')
        
        # 3. 상세 정보 저장 (관리자 권한 사용)
        member_data = {
            "id": auth_user_id,
            "email": user_data.email,
            "password": hashed_password,
            "real_name": user_data.real_name,
            "nickname": user_data.nickname,
            "birthdate": user_data.birthdate,
            "gender": user_data.gender,
            "telecom": user_data.telecom,
            "phone": user_data.phone,
            "parental_consent": user_data.parental_consent,
            "bio": user_data.bio
        }
        
        # public.member 대신 AI.member 또는 설정된 스키마의 member 테이블에 저장
        # RLS를 우회하기 위해 admin_client를 사용합니다.
        supabase_service.admin_client.table("member").insert(member_data).execute()
        
        return {
            "message": "회원가입이 완료되었습니다.", 
            "user": auth_response.user,
            "access_token": auth_response.session.access_token if auth_response.session else None
        }
    except Exception as e:
        print(f"Signup Error: {str(e)}")
        
        # 상세 정보 저장 실패 시 생성된 Auth 유저 삭제 (롤백)
        if auth_user_id:
            try:
                supabase_service.admin_client.auth.admin.delete_user(auth_user_id)
                print(f"Signup Rollback: Deleted Auth User {auth_user_id}")
            except Exception as rollback_err:
                print(f"Rollback Failed: {str(rollback_err)}")

        error_msg = str(e)
        if "already registered" in error_msg.lower():
            error_msg = "이미 가입된 이메일 주소입니다."
        elif "72 bytes" in error_msg.lower():
            error_msg = "비밀번호 시스템 오류가 발생했습니다. 다시 시도해 주세요."
        raise HTTPException(status_code=400, detail=f"회원가입 실패: {error_msg}")

@router.post("/login")
async def login(user_data: UserLogin):
    """
    로그인 API
    """
    try:
        safe_password = user_data.password[:72]
        response = supabase_service.client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": safe_password
        })
        return {
            "message": "로그인 성공",
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

@router.post("/logout")
async def logout():
    """
    로그아웃 API
    """
    try:
        supabase_service.client.auth.sign_out()
        return {"message": "로그아웃 되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_my_profile(member_id: str):
    """
    현재 사용자의 상세 프로필 정보를 가져옵니다.
    """
    try:
        response = supabase_service.admin_client.table("member")\
            .select("*")\
            .eq("id", member_id)\
            .execute()
        
        if not response.data:
            # OAuth 가입자 등 member 테이블에 데이터가 없는 경우 자동 생성
            try:
                auth_res = supabase_service.admin_client.auth.admin.get_user_by_id(member_id)
                auth_user = auth_res.user
                
                new_member = {
                    "id": member_id,
                    "email": auth_user.email,
                    "nickname": auth_user.user_metadata.get("nickname", auth_user.email.split('@')[0]),
                    "real_name": auth_user.user_metadata.get("real_name", auth_user.user_metadata.get("full_name", "OAuth사용자"))
                }
                
                insert_res = supabase_service.admin_client.table("member").insert(new_member).execute()
                user_info = insert_res.data[0] if insert_res.data else new_member
            except Exception as ex:
                print(f"Auto-create member failed: {ex}")
                raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")
        else:
            user_info = response.data[0]
            
        # 보안을 위해 비밀번호는 제외하고 반환
        if "password" in user_info:
            del user_info["password"]
            
        return {"status": "success", "data": user_info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/me")
async def update_my_profile(member_id: str, data: UserUpdate):
    """
    사용자의 프로필 정보를 업데이트합니다.
    """
    try:
        # 1. 업데이트할 데이터 필터링 (None이 아닌 값만)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return {"status": "success", "message": "업데이트할 내용이 없습니다."}
        
        update_data["updated_at"] = "now()"
        
        # 2. DB 업데이트
        response = supabase_service.admin_client.table("member")\
            .update(update_data)\
            .eq("id", member_id)\
            .execute()
            
        if not response.data:
            # 존재하지 않는 경우 Upsert 시도
            update_data["id"] = member_id
            response = supabase_service.admin_client.table("member").upsert(update_data).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="사용자 정보를 업데이트할 수 없습니다.")

        # 3. Supabase Auth의 metadata 및 비밀번호 업데이트
        auth_updates = {}
        if data.nickname: auth_updates["nickname"] = data.nickname
        if data.real_name: auth_updates["real_name"] = data.real_name
        
        update_payload = {}
        if auth_updates:
            update_payload["user_metadata"] = auth_updates
        if data.password:
            # 안전하게 길이 제한 적용 (Supabase Auth 비밀번호 요구사항)
            update_payload["password"] = data.password[:72]
            
        if update_payload:
            supabase_service.admin_client.auth.admin.update_user_by_id(
                member_id,
                attributes=update_payload
            )
            
        return {
            "status": "success", 
            "message": "프로필이 성공적으로 업데이트되었습니다.",
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Profile Update Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"프로필 업데이트 실패: {str(e)}")
@router.get("/members")
async def list_members():
    """
    모든 가입된 회원 목록을 가져옵니다. (친구 추가 검색용)
    """
    try:
        response = supabase_service.admin_client.table("member")\
            .select("id, email, nickname, bio, created_at")\
            .execute()
            
        users_resp = supabase_service.admin_client.auth.admin.list_users()
        role_map = {u.id: u.user_metadata.get("role", "회원") for u in users_resp}
        
        members = response.data
        for m in members:
            m["role"] = role_map.get(m["id"], "회원")
            
        return {"status": "success", "data": members}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/members/{user_id}/role")
async def update_member_role(user_id: str, data: RoleUpdate):
    try:
        if data.role not in ["회원", "관리자"]:
            raise HTTPException(status_code=400, detail="유효하지 않은 권한입니다.")
            
        supabase_service.admin_client.auth.admin.update_user_by_id(
            user_id,
            attributes={"user_metadata": {"role": data.role}}
        )
        return {"status": "success", "message": "권한이 변경되었습니다."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
