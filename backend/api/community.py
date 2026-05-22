from fastapi import APIRouter, HTTPException, Depends, Header
from services.supabase_service import supabase_service
from typing import List, Optional

router = APIRouter(prefix="/community", tags=["Community"])

async def get_user_id(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    try:
        # "Bearer <token>" 형식 처리
        token = authorization.replace("Bearer ", "")
        user_resp = supabase_service.client.auth.get_user(token)
        if user_resp and user_resp.user:
            return user_resp.user.id
    except Exception:
        pass
    return None

@router.get("/posts")
async def get_posts():
    """
    게시글 목록 조회 (최신순)
    """
    try:
        response = supabase_service.client.table("posts").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"[Community API] Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    """
    게시글 상세 조회
    """
    try:
        response = supabase_service.client.table("posts").select("*").eq("id", post_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        return response.data[0]
    except Exception as e:
        print(f"[Community API] Error fetching post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts")
async def create_post(data: dict):
    """
    게시글 작성
    """
    try:
        response = supabase_service.client.table("posts").insert(data).execute()
        return {"message": "게시글이 성공적으로 등록되었습니다.", "data": response.data}
    except Exception as e:
        print(f"[Community API] Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/like-status")
async def get_like_status(post_id: str, member_id: str):
    """
    특정 사용자의 게시글 좋아요 여부 확인
    """
    try:
        response = supabase_service.client.table("post_likes").select("*").eq("post_id", post_id).eq("member_id", member_id).execute()
        return {"liked": len(response.data) > 0}
    except Exception as e:
        return {"liked": False}

@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: str, data: dict):
    """
    게시글 좋아요 토글 (On/Off)
    data: {"member_id": "..."}
    """
    member_id = data.get("member_id")
    if not member_id:
        raise HTTPException(status_code=400, detail="member_id가 필요합니다.")

    try:
        # 1. 이미 좋아요를 눌렀는지 확인
        like_check = supabase_service.client.table("post_likes")\
            .select("*")\
            .eq("post_id", post_id)\
            .eq("member_id", member_id)\
            .execute()
        
        is_liked = len(like_check.data) > 0
        
        # 현재 게시글 정보 가져오기
        post_resp = supabase_service.client.table("posts").select("like_count").eq("id", post_id).execute()
        if not post_resp.data:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
        current_likes = post_resp.data[0].get("like_count", 0)
        
        if is_liked:
            # 2. 이미 눌렀다면 좋아요 취소 (Delete from post_likes, Decrement like_count)
            supabase_service.client.table("post_likes")\
                .delete()\
                .eq("post_id", post_id)\
                .eq("member_id", member_id)\
                .execute()
            
            new_likes = max(0, current_likes - 1)
            supabase_service.client.table("posts").update({"like_count": new_likes}).eq("id", post_id).execute()
            return {"status": "success", "action": "unliked", "like_count": new_likes}
        else:
            # 3. 누르지 않았다면 좋아요 추가 (Insert into post_likes, Increment like_count)
            supabase_service.client.table("post_likes")\
                .insert({"post_id": post_id, "member_id": member_id})\
                .execute()
            
            new_likes = current_likes + 1
            supabase_service.client.table("posts").update({"like_count": new_likes}).eq("id", post_id).execute()
            return {"status": "success", "action": "liked", "like_count": new_likes}
            
    except Exception as e:
        print(f"[Community API] Error toggling like: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/view")
async def increment_view(post_id: str):
    """
    게시글 조회수 증가
    """
    try:
        # 현재 조회수 가져오기
        post_resp = supabase_service.client.table("posts").select("view_count").eq("id", post_id).execute()
        if not post_resp.data:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
        current_views = post_resp.data[0].get("view_count", 0)
        
        # 조회수 업데이트
        response = supabase_service.client.table("posts").update({"view_count": current_views + 1}).eq("id", post_id).execute()
        return {"status": "success", "view_count": current_views + 1}
    except Exception as e:
        print(f"[Community API] Error incrementing view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}")
async def update_post(post_id: str, data: dict):
    """
    게시글 수정
    """
    try:
        update_data = {}
        if "title" in data:
            update_data["title"] = data["title"]
        if "content" in data:
            update_data["content"] = data["content"]
            
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")
            
        response = supabase_service.client.table("posts").update(update_data).eq("id", post_id).execute()
        return {"status": "success", "message": "게시글이 수정되었습니다."}
    except Exception as e:
        print(f"[Community API] Error updating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    """
    게시글 삭제
    """
    try:
        # 먼저 좋아요 데이터 삭제
        supabase_service.client.table("post_likes").delete().eq("post_id", post_id).execute()
        
        # 게시글 삭제
        response = supabase_service.client.table("posts").delete().eq("id", post_id).execute()
        
        return {"status": "success", "message": "게시글이 삭제되었습니다."}
    except Exception as e:
        print(f"[Community API] Error deleting post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

