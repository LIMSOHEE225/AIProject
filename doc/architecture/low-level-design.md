# Low-Level Design: DearZit (AI Card & Templates)

## 1. 데이터베이스 설계 (Database Schema)

### 1.1 `homepages` 테이블 (AI 스키마)
사용자의 개별 홈페이지 또는 카드 데이터를 저장합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | 레코드 고유 ID |
| `member_id` | UUID | Foreign Key (AI.member) | 소유자 ID |
| `html_content` | TEXT | NOT NULL | AI가 생성한 전체 HTML/CSS 코드 |
| `layout_data` | JSONB | | 테마 구성 정보 (구조적 데이터) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | 생성 일시 |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | 최종 수정 일시 |

### 1.2 `templates` 테이블 (AI 스키마)
AI 생성 시 참조할 수 있는 디자인 템플릿 정보를 저장합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | 템플릿 고유 ID |
| `creator_id` | UUID | FK (AI.member) | 제작자 (시스템 생성 시 NULL 가능) |
| `title` | VARCHAR(100) | NOT NULL | 템플릿 제목 |
| `description` | TEXT | | 템플릿 설명 |
| `layout_data` | JSONB | NOT NULL | 디자인 구조 (HTML/CSS 포함 가능) |
| `thumbnail_url` | TEXT | | 프리뷰 이미지 경로 |
| `category` | VARCHAR(50) | | 템플릿 카테고리 (카드, 홈페이지 등) |
| `is_public` | BOOLEAN | DEFAULT true | 공개 여부 |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | 생성 일시 |

### 1.3 `minihompy_comments` 테이블 (AI 스키마)
미니홈피 게시글 및 각 메뉴 탭(다이어리, 사진첩, 게시판 등)의 댓글을 관계형으로 통합하여 관리합니다. `post_id`가 NULL인 경우 특정 게시글이 아닌 메뉴 탭 전체에 달리는 댓글(예: 방명록 댓글, 일촌평 등)을 의미합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | 댓글 고유 ID |
| `member_id` | UUID | Foreign Key (AI.member) ON DELETE CASCADE | 홈피 주인(해당 미니홈피의 회원) ID (NOT NULL) |
| `post_id` | UUID | Foreign Key (AI.minihompy_posts) ON DELETE CASCADE | 어떤 게시글에 달린 댓글인지 참조 (NULL 허용) |
| `menu_id` | TEXT | NOT NULL | 어떤 메뉴 탭의 댓글인지 구분 (diary, photo, board 등) |
| `writer_name` | TEXT | NOT NULL | 작성자 닉네임 또는 이름 |
| `content` | TEXT | NOT NULL | 댓글 본문 내용 |
| `is_private` | BOOLEAN | DEFAULT false | 비밀 댓글 여부 (비공개 처리) |
| `reply_to` | TEXT | | 대댓글 대상을 지정하기 위한 닉네임 또는 UUID |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | 생성 일시 |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | 최종 수정 일시 |

## 2. API 설계 (API Definition)

### 2.1 AI 코드 생성 (Generate)
- **Endpoint**: `POST /api/v1/homepage/generate`
- **Request Body**:
```json
{
  "prompt": "크리스마스 테마의 식당 홈페이지 만들어줘",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "model", "content": "..."}
  ]
}
```
- **Response**:
```json
{
  "status": "success",
  "html": "<!DOCTYPE html><html>...</html>",
  "raw_response": "..."
}
```

### 2.2 홈페이지 저장 (Save)
- **Endpoint**: `POST /api/v1/homepage/save`
- **Request Body**:
```json
{
  "html_content": "<!DOCTYPE html>...",
  "theme_settings": {}
}
```

### 2.3 홈페이지 조회 (Get)
- **Endpoint**: `GET /api/v1/homepage/{member_id}`
- **Response**:
```json
{
  "member_id": "...",
  "html_content": "...",
  "updated_at": "..."
}
```

### 2.4 템플릿 목록 조회 (List)
- **Endpoint**: `GET /api/v1/templates`
- **Query Params**: `category=card`
- **Response**: `Template[]`

### 2.5 템플릿 저장 (Create)
- **Endpoint**: `POST /api/v1/templates`
- **Request Body**: `Template Object`

## 3. 핵심 로직 상세 (Logic Detail)

### 3.1 AI 프롬프트 엔지니어링 (System Prompt)
```text
너는 전문적인 웹 프론트엔드 빌더 엔진이야.
[규칙]
1. 반드시 <!DOCTYPE html>로 시작하는 단일 HTML 파일로 응답한다.
2. 모든 CSS는 <style> 태그 안에 포함한다.
3. JavaScript는 최소화하고, 필요한 경우 <script> 태그 안에 포함한다.
4. 외부 라이브러리는 CDN(Google Fonts, Font Awesome)만 사용한다.
5. 디자인은 현대적이고 세련되어야 하며, 반응형 레이아웃을 준수한다.
6. '게시판'이나 '방명록' 위치가 필요하면 <div id="board-placeholder"></div>와 같이 플레이스홀더를 사용한다.
```

### 3.2 프론트엔드 코드 추출 로직
AI 응답에서 마크다운 코드 블록(```html ... ```)을 제거하고 순수 HTML만 추출하는 정규식 활용.
```javascript
function extractHTML(rawResponse) {
    const regex = /<!DOCTYPE html>[\s\S]*<\/html>/i;
    const match = rawResponse.match(regex);
    return match ? match[0] : rawResponse;
}
```
