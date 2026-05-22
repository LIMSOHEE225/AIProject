from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from api.auth import router as auth_router
from api.agit import router as agit_router
from api.homepage import router as homepage_router
from api.community import router as community_router
from api.notice import router as notice_router
from api.support import router as support_router

app = FastAPI(
    title="DearZit API",
    description="AI 기반 나만의 편지 카드 및 엽서 만들기 플랫폼 백엔드",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router, prefix="/api/v1")
app.include_router(agit_router, prefix="/api/v1")
app.include_router(homepage_router, prefix="/api/v1")
app.include_router(community_router, prefix="/api/v1")
app.include_router(notice_router, prefix="/api/v1/notices")
app.include_router(support_router, prefix="/api/v1")

# 깔끔한 URL 지원 (DearZit.html -> /DearZit)
@app.get("/DearZit")
@app.get("/DearZit/")
@app.get("/dearzit")
@app.get("/dearzit/")
async def get_dearzit_page():
    return FileResponse(os.path.join(frontend_path, "DearZit.html"))

# 프론트엔드 정적 파일 서비스 설정
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

# API 라우터를 제외한 모든 정적 파일(HTML, CSS, JS, 이미지 등) 서비스
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
