# High-Level Architecture (HLD)

## 1. 아키텍처 개요
"가장 쉽고 빠른 배포"를 위해 서버 인프라를 직접 구축하지 않고, 소스 코드만 연결하면 알아서 배포되는 완전 관리형 서비스(PaaS)와 무료 티어를 적극 활용하는 구조입니다.

## 2. 기술 스택 및 클라우드 서비스 선택
- **Frontend (Vanilla JS/HTML/CSS)**: **Vercel**
  - **선택 이유**: 별도의 복잡한 빌드 과정 없이 정적 웹 파일을 클릭 몇 번으로 무료 배포할 수 있습니다. 전 세계 CDN을 통해 속도가 매우 빠르며, GitHub과 연결해두면 코드를 수정할 때마다 자동으로 배포됩니다.
- **Backend (Python FastAPI)**: **Render** (또는 Koyeb)
  - **선택 이유**: 파이썬 백엔드를 배포할 수 있는 가장 쉬운 서비스 중 하나로, 무료 티어를 제공합니다. Dockerfile 없이 `requirements.txt`만 있으면 자동으로 환경을 구성하여 서버를 실행해 줍니다. 보안 인증서(HTTPS)도 자동 발급됩니다.
- **Database**: **Supabase (PostgreSQL)**
  - **선택 이유**: 현재 사용 중이신 환경 그대로 유지합니다. 추가 인프라 작업 없이, 백엔드의 환경변수에 Supabase URL과 Key만 연결하면 즉시 사용 가능합니다.
- **External API**: **Google Gemini API**
  - 3D 아바타 생성 등을 위한 AI 서비스 (현재 구조 유지)

## 3. 시스템 구성도 (System Architecture Diagram)

```mermaid
graph TD
    User([사용자 / 웹 브라우저]) -->|정적 리소스 요청 (HTTPS)| Vercel[Vercel - Frontend]
    User -->|API 호출 (HTTPS REST)| Render[Render - Backend API]
    
    Render -->|데이터 쿼리| Supabase[(Supabase - Database)]
    Render -->|AI 프롬프트 분석| Gemini[Google Gemini API]
```

## 4. 주요 통신 흐름
1. 사용자가 Vercel 호스팅 도메인(예: `https://my-ar-project.vercel.app`)에 접속하여 화면을 띄웁니다.
2. 프론트엔드에서 데이터가 필요할 때마다 Render에 배포된 백엔드 API(예: `https://my-backend.onrender.com/api/...`)로 요청을 보냅니다.
3. 백엔드는 요청을 받아 Supabase 데이터베이스를 조회/저장하거나, AI 처리가 필요할 경우 Gemini API를 호출하여 응답을 프론트엔드로 반환합니다.

## 5. 배포 진행 순서 (Action Plan)
1. **GitHub 저장소 연동:** `frontend`, `backend` 코드를 하나의 GitHub Repository에 푸시(업로드)합니다.
2. **백엔드(Render) 배포:** Render에 GitHub 저장소를 연결하여 환경변수(`.env` 내용)를 등록하고 서버를 띄웁니다.
3. **프론트엔드(Vercel) 배포:** Vercel에 GitHub 저장소를 연결하고 배포합니다. 이 때 JS 코드 내에 있는 API 기본 주소(Base URL)를 Render의 주소로 변경해야 합니다.
4. **CORS 정책 수정:** 프론트엔드의 Vercel 도메인을 백엔드(FastAPI)의 `CORSMiddleware` 허용 목록에 추가하여 통신 오류를 방지합니다.
