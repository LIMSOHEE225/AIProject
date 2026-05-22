# 미니홈피 데이터 영구 저장(DB 마이그레이션) 구현 계획

현재 미니홈피의 메뉴 설정, 게시글, 방명록 데이터는 브라우저의 `localStorage`에만 저장되고 있어, 브라우저 캐시가 삭제되거나 다른 기기에서 접속하면 데이터가 보이지 않는 문제가 있습니다. 이를 해결하기 위해 실제 데이터베이스(DB)로 마이그레이션합니다.

## 1. 데이터베이스 테이블 설계

### 1.1 `AI.minihompy_posts` (사진첩/게시글)
- `id`: UUID (PK)
- `member_id`: UUID (FK, "AI".member.id)
- `menu_type`: TEXT (어느 메뉴에 속하는지 고유 ID)
- `title`: TEXT
- `content`: TEXT
- `images`: JSONB (이미지 URL 배열)
- `like_count`: INT (기본값 0)
- `created_at`: TIMESTAMPTZ

### 1.2 `AI.minihompy_guestbook` (방명록)
- `id`: UUID (PK)
- `member_id`: UUID (FK, "AI".member.id)
- `user_nickname`: TEXT (작성자)
- `content`: TEXT
- `reply_to`: TEXT (답글 대상자)
- `created_at`: TIMESTAMPTZ

### 1.3 `AI.minihompy_comments` (댓글)
- `id`: UUID (PK)
- `member_id`: UUID (FK, "AI".member.id - 홈피 주인 ID)
- `post_id`: UUID (FK, "AI".minihompy_posts.id - NULL 허용)
- `menu_id`: TEXT (어느 메뉴 탭의 댓글인지 구분)
- `writer_name`: TEXT (작성자 닉네임)
- `content`: TEXT (댓글 본문)
- `is_private`: BOOLEAN (비밀댓글 여부)
- `reply_to`: TEXT (대댓글 대상자)
- `created_at`: TIMESTAMPTZ
- `updated_at`: TIMESTAMPTZ

### 1.4 `AI.homepage` (메뉴 설정 업데이트)
- 기존 `menus` 컬럼을 활용하여 메뉴 이름, 순서, 공개 범위 정보를 JSON으로 저장합니다.

## 2. 백엔드 API 개발 (`backend/api/homepage.py`)

- `GET /homepage/data/{member_id}`: 특정 사용자의 모든 미니홈피 데이터(메뉴, 게시글, 방명록)를 한 번에 가져옵니다.
- `POST /homepage/posts`: 새로운 게시글을 저장합니다.
- `PUT /homepage/posts/{post_id}`: 게시글 수정/댓글 추가 등을 처리합니다.
- `DELETE /homepage/posts/{post_id}`: 게시글을 삭제합니다.
- `POST /homepage/guestbook`: 방명록 메시지를 추가합니다.
- `PUT /homepage/menus`: 변경된 메뉴 설정(순서, 이름 등)을 저장합니다.

## 3. 프론트엔드 연동 (`frontend/minihompy.html`)

- `DOMContentLoaded` 시점에 API를 호출하여 DB에서 데이터를 불러옵니다.
- `savePost`, `addPostComment`, `addGuestMsg`, `saveAndRender`(메뉴 저장) 함수들이 `localStorage` 대신 서버 API를 호출하도록 수정합니다.

## 4. 작업 순서
1. **[Step 1]** DB 테이블 생성 스크립트 실행
2. **[Step 2]** 백엔드 엔드포인트 구현 및 테스트
3. **[Step 3]** 프론트엔드 데이터 통신 로직 교체
