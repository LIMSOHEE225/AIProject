from fastapi import APIRouter, HTTPException, Header, Depends, Body
from pydantic import BaseModel
from services.supabase_service import supabase_service
from services.gemini_service import gemini_service
from typing import Optional

router = APIRouter(prefix="/homepage", tags=["LetterCard"])

class ChatRequest(BaseModel):
    message: str
    persona: Optional[str] = "츤데레 감성"
    context: Optional[str] = "싸이월드 미니홈피 환경"

@router.get("/all")
async def get_all_public_homepages():
    """전체공개로 설정된 모든 미니홈피 목록을 가져옵니다."""
    try:
        response = supabase_service.admin_client.table("homepage")\
            .select("*")\
            .in_("visibility", ["public", "전체공개"])\
            .order("created_at", desc=True)\
            .execute()
            
        homepages = response.data or []
        
        # 닉네임 가져오기 (member 테이블 조인 대용)
        if homepages:
            member_ids = [hp["member_id"] for hp in homepages if hp.get("member_id")]
            if member_ids:
                members_res = supabase_service.admin_client.table("member")\
                    .select("id, nickname")\
                    .in_("id", member_ids)\
                    .execute()
                member_dict = {m["id"]: m.get("nickname", "익명") for m in (members_res.data or [])}
                
                for hp in homepages:
                    hp["nickname"] = member_dict.get(hp["member_id"], "익명")
                    
        return {"status": "success", "data": homepages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-html")
async def generate_homepage_html(data: dict):
    """
    사용자의 요구사항을 바탕으로 전체 HTML 코드를 생성합니다.
    """
    try:
        prompt = data.get("prompt")
        current_html = data.get("current_html")
        if not prompt:
            raise HTTPException(status_code=400, detail="요구사항(prompt)이 필요합니다.")
            
        html_code = await gemini_service.generate_html_homepage(prompt, current_html)
        
        return {
            "status": "success",
            "html": html_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-html")
async def save_homepage_html(data: dict):
    """
    생성된 HTML 코드를 데이터베이스에 저장합니다.
    """
    try:
        member_id = data.get("member_id")
        html_content = data.get("html_content")
        
        if not member_id or not html_content:
            raise HTTPException(status_code=400, detail="member_id와 html_content가 모두 필요합니다.")
            
        # DB 업데이트
        response = supabase_service.admin_client.table("homepage")\
            .update({"html_content": html_content})\
            .eq("member_id", member_id)\
            .execute()
            
        if not response.data:
            # 레코드가 없으면 생성 시도
            response = supabase_service.admin_client.table("homepage")\
                .insert({"member_id": member_id, "html_content": html_content, "title": "My AI Homepage"})\
                .execute()
                
        return {
            "status": "success",
            "message": "편지 카드가 저장되었습니다.",
            "data": response.data[0] if response.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-settings")
async def save_homepage_settings(data: dict):
    """
    홈페이지 제목 등 설정을 DB에 저장합니다. (메뉴는 별도 API로 분리됨)
    """
    try:
        member_id = data.get("member_id")
        title = data.get("title")
        visibility = data.get("visibility")
        menus_order = data.get("menus_order")
        
        if not member_id:
            raise HTTPException(status_code=400, detail="member_id가 필요합니다.")
            
        update_data = {}
        if title: update_data["title"] = title
        if visibility: update_data["visibility"] = visibility
        if menus_order is not None: update_data["menus"] = menus_order

        response = supabase_service.admin_client.table("homepage")\
            .update(update_data)\
            .eq("member_id", member_id)\
            .execute()
            
        if not response.data:
            insert_data = {"member_id": member_id}
            insert_data["title"] = title if title else "My Minihompy"
            insert_data["visibility"] = visibility if visibility else "public"
            if menus_order is not None: insert_data["menus"] = menus_order
            response = supabase_service.admin_client.table("homepage")\
                .insert(insert_data)\
                .execute()
                
        return {"status": "success", "message": "설정이 저장되었습니다.", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Save Settings Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/menus")
async def get_minihompy_menus(member_id: str):
    """커스텀 메뉴 목록을 가져옵니다."""
    try:
        response = supabase_service.admin_client.table("minihompy_menu")\
            .select("*")\
            .eq("member_id", member_id)\
            .order("sort_order")\
            .execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/menus")
async def save_minihompy_menus(data: dict):
    """커스텀 메뉴 전체를 동기화(저장/수정/삭제)합니다."""
    try:
        member_id = data.get("member_id")
        menus = data.get("menus", [])
        
        hp_res = supabase_service.admin_client.table("homepage").select("id").eq("member_id", member_id).execute()
        if not hp_res.data:
            raise HTTPException(status_code=400, detail="Homepage not found")
        homepage_id = hp_res.data[0]["id"]
        
        # 기존 메뉴 조회
        existing = supabase_service.admin_client.table("minihompy_menu").select("id").eq("member_id", member_id).execute()
        existing_ids = {item["id"] for item in existing.data}
        incoming_ids = set()
        
        for i, m in enumerate(menus):
            m_id = m.get("id")
            record = {
                "homepage_id": homepage_id,
                "member_id": member_id,
                "menu_name": m.get("name"),
                "visibility": m.get("visibility", "public"),
                "sort_order": i
            }
            # UUID 형태인지 체크
            if m_id and len(m_id) > 20 and "-" in m_id:
                record["id"] = m_id
                incoming_ids.add(m_id)
                supabase_service.admin_client.table("minihompy_menu").upsert([record]).execute()
            else:
                supabase_service.admin_client.table("minihompy_menu").insert([record]).execute()
                
        # 삭제된 메뉴 처리
        to_delete = existing_ids - incoming_ids
        if to_delete:
            supabase_service.admin_client.table("minihompy_menu").delete().in_("id", list(to_delete)).execute()
            
        return {"status": "success"}
    except Exception as e:
        print("Save Menus Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_my_homepage(member_id: str):
    """
    현재 사용자의 편지함 설정을 가져옵니다.
    """
    import uuid
    try:
        uuid_obj = uuid.UUID(member_id)
    except ValueError:
        # UUID 형식이 아닌 경우 (예: naver_user:1) DB 오류 방지
        return {"status": "error", "message": "유효하지 않은 사용자 ID 형식입니다."}

    try:
        response = supabase_service.admin_client.table("homepage")\
            .select("*")\
            .eq("member_id", member_id)\
            .execute()
        
        if not response.data:
            # 설정된 미니홈피가 없으면 닉네임을 기반으로 자동 생성
            member_res = supabase_service.admin_client.table("member").select("nickname").eq("id", member_id).execute()
            nickname = member_res.data[0].get("nickname", "사용자") if member_res.data else "사용자"
            title = f"{nickname}님의 미니홈피"
            
            new_homepage = {
                "member_id": member_id,
                "title": title,
                "visibility": "public"
            }
            insert_res = supabase_service.admin_client.table("homepage").insert(new_homepage).execute()
            homepage_data = insert_res.data[0] if insert_res.data else new_homepage
            return {"status": "success", "data": homepage_data, "message": "미니홈피가 자동 생성되었습니다."}
            
        return {"status": "success", "data": response.data[0]}
    except Exception as e:
        print(f"Get Homepage Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat")
async def chat_with_minime(data: ChatRequest):
    """
    AI 미니미와 대화를 나눕니다. 사용자가 설정한 페르소나를 반영합니다.
    """
    try:
        system_prompt = f"""
        당신은 싸이월드 미니홈피의 '미니미(AI)'입니다. 
        사용자와 친구처럼 대화하며, 다음 페르소나를 엄격히 유지하세요:
        [페르소나: {data.persona}]
        [환경: {data.context}]
        
        대화 규칙:
        1. 2000년대 감성의 이모티콘(예: ^_^, >_<, ✿◡‿◡, (●'◡'●))을 적절히 사용하세요.
        2. 답변은 2-3문장 내외로 짧고 다정하게(또는 페르소나에 맞게) 하세요.
        3. 반말을 기본으로 하되, 사용자를 아끼는 마음이 느껴져야 합니다.
        4. "츤데레"라면 겉으로는 퉁명스럽지만 속으로는 챙겨주는 말투를 쓰세요. (예: "흥, 딱히 너가 보고 싶어서 기다린 건 아니야! 그래도 왔으니 다행이네.")
        """
        
        full_prompt = f"{system_prompt}\n\n사용자: {data.message}\n미니미:"
        
        response = gemini_service.model.generate_content(full_prompt)
        reply = response.text.strip()
        
        return {"status": "success", "reply": reply}
    except Exception as e:
        print(f"AI Chat Error: {e}")
        return {"status": "error", "reply": "미안, 지금은 조금 부끄러워서 말을 못 하겠어.. >_<"}

@router.get("/guestbook")
async def get_guestbook(member_id: str):
    """
    특정 사용자의 방명록 목록을 가져옵니다.
    """
    try:
        response = supabase_service.admin_client.table("minihompy_guestbook")\
            .select("*")\
            .eq("member_id", member_id)\
            .order("created_at", desc=True)\
            .execute()
        mapped_data = []
        for item in (response.data or []):
            mapped_item = dict(item)
            mapped_item["homepage_member_id"] = item.get("member_id")
            mapped_item["writer_name"] = item.get("user_nickname")
            mapped_data.append(mapped_item)
        return {"status": "success", "data": mapped_data}
    except Exception as e:
        print(f"Get Guestbook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guestbook")
async def add_guestbook(data: dict):
    """
    새 방명록 글을 등록합니다.
    """
    try:
        db_data = {
            "member_id": data.get("homepage_member_id"),
            "user_nickname": data.get("writer_name"),
            "content": data.get("content")
        }
        if "reply_to" in data:
            db_data["reply_to"] = data.get("reply_to")
        response = supabase_service.admin_client.table("minihompy_guestbook")\
            .insert(db_data)\
            .execute()
        result_data = None
        if response.data:
            inserted = response.data[0]
            result_data = dict(inserted)
            result_data["homepage_member_id"] = inserted.get("member_id")
            result_data["writer_name"] = inserted.get("user_nickname")
        return {"status": "success", "data": result_data}
    except Exception as e:
        print(f"Add Guestbook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/guestbook/{entry_id}")
async def update_guestbook(entry_id: str, data: dict):
    """
    방명록 글을 수정합니다.
    """
    try:
        db_data = {}
        if "content" in data:
            db_data["content"] = data["content"]
        if "writer_name" in data:
            db_data["user_nickname"] = data["writer_name"]
        if "homepage_member_id" in data:
            db_data["member_id"] = data["homepage_member_id"]
        if "reply_to" in data:
            db_data["reply_to"] = data["reply_to"]
        response = supabase_service.admin_client.table("minihompy_guestbook")\
            .update(db_data)\
            .eq("id", entry_id)\
            .execute()
        result_data = None
        if response.data:
            updated = response.data[0]
            result_data = dict(updated)
            result_data["homepage_member_id"] = updated.get("member_id")
            result_data["writer_name"] = updated.get("user_nickname")
        return {"status": "success", "data": result_data}
    except Exception as e:
        print(f"Update Guestbook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/guestbook/{entry_id}")
async def delete_guestbook(entry_id: str):
    """
    방명록 글을 삭제합니다.
    """
    try:
        supabase_service.admin_client.table("minihompy_guestbook")\
            .delete()\
            .eq("id", entry_id)\
            .execute()
        return {"status": "success", "message": "삭제되었습니다."}
    except Exception as e:
        print(f"Delete Guestbook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_minihompy_posts(member_id: str):
    """특정 사용자의 미니홈피 게시글 전체 조회 및 각 게시글의 댓글 병합"""
    try:
        # 1. 게시글 전체 조회
        response = supabase_service.admin_client.table("minihompy_posts")\
            .select("*")\
            .eq("member_id", member_id)\
            .order("created_at", desc=False)\
            .execute()
            
        posts = response.data or []
        
        # 2. 해당 미니홈피(member_id)에 속한 모든 댓글 조회
        comments_res = supabase_service.admin_client.table("minihompy_comments")\
            .select("*")\
            .eq("member_id", member_id)\
            .order("created_at", desc=False)\
            .execute()
            
        all_comments = comments_res.data or []
        
        # 3. 각 게시글에 종속된 댓글 분류하여 매핑 (프론트엔드 하위 호환성 유지)
        for post in posts:
            post_comments = []
            for c in all_comments:
                if c.get("post_id") and str(c["post_id"]) == str(post["id"]):
                    post_comments.append({
                        "id": c["id"],
                        "user": c["writer_name"],
                        "content": c["content"],
                        "isPrivate": c["is_private"],
                        "replyTo": c["reply_to"],
                        "date": c["created_at"]
                    })
            post["comments"] = post_comments
            
        return {"status": "success", "data": posts}
    except Exception as e:
        print(f"Get Posts Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts")
async def add_minihompy_post(data: dict):
    """미니홈피 새 게시글 등록"""
    try:
        # DB 컬럼이 제거되었으므로 comments 필드 pop (하위 호환 및 방어 코드)
        data.pop("comments", None)
        response = supabase_service.admin_client.table("minihompy_posts")\
            .insert(data)\
            .execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Add Post Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}")
async def update_minihompy_post(post_id: str, data: dict):
    """미니홈피 게시글 수정 (내용, 이미지, 좋아요 등)"""
    try:
        # DB 컬럼이 제거되었으므로 comments 필드 pop (하위 호환 및 방어 코드)
        data.pop("comments", None)
        response = supabase_service.admin_client.table("minihompy_posts")\
            .update(data)\
            .eq("id", post_id)\
            .execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Update Post Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_minihompy_post(post_id: str):
    """미니홈피 게시글 삭제"""
    try:
        supabase_service.admin_client.table("minihompy_posts")\
            .delete()\
            .eq("id", post_id)\
            .execute()
        return {"status": "success", "message": "삭제되었습니다."}
    except Exception as e:
        print(f"Delete Post Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------
# 미니홈피 댓글 (minihompy_comments) API 라우트
# ---------------------------------------------

@router.get("/comments")
async def get_minihompy_comments(post_id: str = None, member_id: str = None, menu_id: str = None):
    """미니홈피 댓글 조회 (post_id 기준 또는 member_id + menu_id 기준)"""
    try:
        query = supabase_service.admin_client.table("minihompy_comments").select("*")
        if post_id:
            query = query.eq("post_id", post_id)
        elif member_id and menu_id:
            query = query.eq("member_id", member_id).eq("menu_id", menu_id)
        else:
            raise HTTPException(status_code=400, detail="post_id 또는 member_id와 menu_id가 필요합니다.")
            
        response = query.order("created_at", desc=False).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        print(f"Get Comments Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments")
async def add_minihompy_comment(data: dict):
    """새로운 댓글 등록"""
    try:
        # 프론트엔드 키 호환 처리: isPrivate -> is_private, user -> writer_name
        if "isPrivate" in data:
            data["is_private"] = data.pop("isPrivate")
        if "user" in data:
            data["writer_name"] = data.pop("user")
            
        response = supabase_service.admin_client.table("minihompy_comments")\
            .insert(data)\
            .execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Add Comment Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/comments/{comment_id}")
async def update_minihompy_comment(comment_id: str, data: dict):
    """댓글 수정"""
    try:
        if "isPrivate" in data:
            data["is_private"] = data.pop("isPrivate")
        if "user" in data:
            data["writer_name"] = data.pop("user")
            
        response = supabase_service.admin_client.table("minihompy_comments")\
            .update(data)\
            .eq("id", comment_id)\
            .execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Update Comment Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/comments/{comment_id}")
async def delete_minihompy_comment(comment_id: str):
    """댓글 삭제"""
    try:
        supabase_service.admin_client.table("minihompy_comments")\
            .delete()\
            .eq("id", comment_id)\
            .execute()
        return {"status": "success", "message": "삭제되었습니다."}
    except Exception as e:
        print(f"Delete Comment Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
class MinimeGenerateRequest(BaseModel):
    prompt: Optional[str] = None
    image_data_base64: Optional[str] = None
    member_id: Optional[str] = None  # [Phase 3] DB 저장용

@router.post("/minime/generate")
async def generate_minime(data: MinimeGenerateRequest):
    """
    [Phase 3] 사용자 프롬프트 또는 사진을 분석하여
    3D 캐릭터 모델(GLB) URL을 반환하고 DB에 저장합니다.
    - 사진 업로드 시: Gemini Vision으로 사진 분석 후 캐릭터 생성
    - 생성 완료 후: homepage 테이블에 minime_glb_url 저장
    """
    try:
        # 1. 3D 캐릭터 생성 (Gemini Vision 분석 포함)
        result = await gemini_service.generate_3d_character(
            prompt=data.prompt,
            image_data_base64=data.image_data_base64
        )
        glb_url = result.get("glb_url")

        # 2. DB 저장 (member_id가 있을 때만)
        if data.member_id and glb_url:
            try:
                save_data = {
                    "minime_glb_url": glb_url,
                    "minime_prompt": data.prompt or "photo-based",
                }

                # homepage 레코드가 있으면 UPDATE, 없으면 upsert로 INSERT
                existing = supabase_service.admin_client\
                    .table("homepage")\
                    .select("id")\
                    .eq("member_id", data.member_id)\
                    .execute()

                if existing.data:
                    # 레코드 있음 → UPDATE
                    supabase_service.admin_client\
                        .table("homepage")\
                        .update(save_data)\
                        .eq("member_id", data.member_id)\
                        .execute()
                    print(f"[Minime] DB updated for member: {data.member_id}")
                else:
                    # 레코드 없음 → 기본 레코드 생성 후 저장
                    save_data["member_id"] = data.member_id
                    save_data["title"] = "나의 미니홈피"
                    save_data["visibility"] = "public"
                    supabase_service.admin_client\
                        .table("homepage")\
                        .insert(save_data)\
                        .execute()
                    print(f"[Minime] DB inserted for member: {data.member_id}")

            except Exception as db_err:
                # DB 저장 실패해도 GLB URL은 반환 (비중요 오류)
                print(f"[Minime] DB save failed (non-critical): {db_err}")

        return {
            "status": "success",
            "glb_url": glb_url,
            "image_data": result.get("image_data")
        }
    except Exception as e:
        print(f"[Minime Generate Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/room/generate")
async def generate_3d_room(data: GenerateMinimeRequest):
    """
    3D 미니룸(방) 모델(GLB) URL을 반환하고 DB에 저장합니다.
    - 프롬프트를 기반으로 방 생성
    """
    try:
        result = await gemini_service.generate_3d_room(prompt=data.prompt or "A cozy living room")
        glb_url = result.get("glb_url")

        if data.member_id and glb_url:
            try:
                save_data = {
                    "miniroom_glb_url": glb_url,
                }
                # homepage 레코드 유무 확인
                existing = supabase_service.admin_client\
                    .table("homepage")\
                    .select("id")\
                    .eq("member_id", data.member_id)\
                    .execute()

                if existing.data:
                    supabase_service.admin_client\
                        .table("homepage")\
                        .update(save_data)\
                        .eq("member_id", data.member_id)\
                        .execute()
                else:
                    save_data["member_id"] = data.member_id
                    save_data["title"] = "나의 미니홈피"
                    save_data["visibility"] = "public"
                    supabase_service.admin_client\
                        .table("homepage")\
                        .insert(save_data)\
                        .execute()
            except Exception as db_err:
                print(f"[Room] DB save failed: {db_err}")

        return {
            "status": "success",
            "glb_url": glb_url
        }
    except Exception as e:
        print(f"[Room Generate Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{nickname}")
async def get_homepage_by_nickname(nickname: str):
    """
    닉네임을 통해 해당 사용자의 공개된 홈피 정보를 조회합니다.
    """
    try:
        # 1. 닉네임으로 member_id 조회
        member_res = supabase_service.admin_client.table("member")\
            .select("id")\
            .eq("nickname", nickname)\
            .execute()
        
        if not member_res.data:
            raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
        
        member_id = member_res.data[0]["id"]
        
        # 2. 해당 사용자의 홈피 정보 조회
        response = supabase_service.admin_client.table("homepage")\
            .select("*")\
            .eq("member_id", member_id)\
            .eq("visibility", "public")\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="공개된 편지함이 없거나 접근 권한이 없습니다.")
            
        return {"status": "success", "data": response.data[0]}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
