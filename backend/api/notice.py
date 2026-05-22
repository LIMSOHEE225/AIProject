from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional
from services.supabase_service import SupabaseService
import os
import uuid
import shutil

router = APIRouter()
supabase_service = SupabaseService()

class NoticeCreate(BaseModel):
    type: str
    title: str
    content: str

@router.get("")
@router.get("/")
async def get_notices():
    """공지사항 목록 조회"""
    try:
        # AI 스키마 지정
        response = supabase_service.admin_client.schema("AI").table("notice")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        return {"status": "success", "data": response.data or []}
    except Exception as e:
        print(f"Get Notices Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
@router.post("/")
async def create_notice(data: NoticeCreate):
    """새 공지사항 등록"""
    try:
        response = supabase_service.admin_client.schema("AI").table("notice")\
            .insert({
                "type": data.type,
                "title": data.title,
                "content": data.content
            }).execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Create Notice Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notice_id}")
async def update_notice(notice_id: int, data: NoticeCreate):
    """공지사항 수정"""
    try:
        response = supabase_service.admin_client.schema("AI").table("notice")\
            .update({
                "type": data.type,
                "title": data.title,
                "content": data.content
            }).eq("id", notice_id).execute()
        return {"status": "success", "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Update Notice Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notice_id}")
async def delete_notice(notice_id: int):
    """공지사항 삭제"""
    try:
        response = supabase_service.admin_client.schema("AI").table("notice")\
            .delete().eq("id", notice_id).execute()
        return {"status": "success", "message": "삭제되었습니다."}
    except Exception as e:
        print(f"Delete Notice Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_notice_file(file: UploadFile = File(...)):
    """공지사항 첨부파일 업로드"""
    try:
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        upload_dir = os.path.join(frontend_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        return {"status": "success", "url": f"/uploads/{filename}", "filename": file.filename}
    except Exception as e:
        print(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
