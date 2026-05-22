from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.gemini_service import gemini_service
from services.supabase_service import supabase_service
from typing import Optional

router = APIRouter(prefix="/agit", tags=["LetterBox"])

class AgitRequest(BaseModel):
    prompt: str

class AgitSave(BaseModel):
    title: str
    layout_data: dict
    preview_url: Optional[str] = None
    is_public: bool = True

@router.post("/generate")
async def generate_agit(request: AgitRequest):
    """
    AI를 통해 편지함/우체국 레이아웃 JSON 생성
    """
    try:
        layout = await gemini_service.generate_agit_layout(request.prompt)
        print(f"[Agit API] Generated layout: {layout.get('theme', 'No Theme')}")
        
        if "error" in layout:
            raise HTTPException(status_code=500, detail=layout["error"])
            
        return layout
    except Exception as e:
        print(f"[Agit API] Error generating layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_agit(data: AgitSave):
    """
    생성된 편지함 데이터를 Supabase에 저장
    """
    try:
        response = supabase_service.client.table("templates").insert({
            "title": data.title,
            "layout_data": data.layout_data,
            "preview_url": data.preview_url,
            "is_public": data.is_public
        }).execute()
        return {"message": "편지함이 성공적으로 저장되었습니다.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"저장 실패: {str(e)}")

@router.get("/list")
async def get_my_agits():
    """
    내 편지함 목록 조회
    """
    try:
        response = supabase_service.client.table("templates").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
