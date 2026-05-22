# Infrastructure & NFR: AI Homepage Builder

## 1. 인프라 설계 (Infrastructure)

- **Cloud Platform**: Supabase (Backend-as-a-Service)
- **API Server**: FastAPI (Python 3.10+)
- **Storage**: Supabase Database (PostgreSQL)
- **Hosting**: Local/Development Server (현재), 향후 Vercel 또는 GitHub Pages
- **AI Engine**: Google Gemini 1.5 Flash API

## 2. 비기능 요구사항 (Non-Functional Requirements)

### 2.1 보안 (Security)
- **Iframe Sandbox**: 생성된 HTML이 메인 도메인의 쿠키나 로컬 스토리지에 접근하지 못하도록 `sandbox` 속성 적용.
- **API Auth**: 홈페이지 저장(`save`) API 호출 시 JWT 토큰을 검증하여 본인의 홈페이지가 아닌 경우 수정을 거부.
- **XSS 방지**: AI가 생성한 코드 내에 악성 스크립트가 포함될 가능성을 염두에 두고, 프론트엔드 렌더링 시 기초적인 Sanitization 검토.

### 2.2 성능 (Performance)
- **캐싱**: 동일한 사용자 요구사항에 대해 불필요한 AI 호출을 방지하기 위해 생성 이력 관리.
- **로딩 최적화**: HTML 텍스트 데이터가 커질 수 있으므로, DB 인덱싱을 통해 조회 속도 최적화.

### 2.3 안정성 (Availability)
- **AI 장애 대응**: Gemini API 장애 시 사용자에게 적절한 안내 메시지 표시 및 재시도 기능 제공.
- **백업**: 사용자가 '적용' 버튼을 누르기 전까지는 임시 저장 공간(Local Storage)에 저장하여 데이터 유실 방지.

## 3. 배포 전략 (Deployment)
- **CI/CD**: GitHub Actions를 통해 백엔드 코드를 자동 테스트 및 배포.
- **Environment**: `.env` 파일을 통해 API Key 및 DB URL 관리.
