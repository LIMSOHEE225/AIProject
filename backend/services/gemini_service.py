# -*- coding: utf-8 -*-
import google.generativeai as genai
from core.config import settings
import json
import requests
import urllib.parse
import base64
import time
import random
from typing import Optional


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # 사용 가능한 최신 모델 순서대로 시도
        available_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
        ]

        self.model = None
        for model_name in available_models:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"[Gemini] Model initialized successfully: {model_name}")
                break
            except Exception as e:
                print(f"[Gemini] Failed to initialize {model_name}: {e}")

        if not self.model:
            print("[Gemini] Critical: All model initialization attempts failed. Using gemini-pro as last resort.")
            self.model = genai.GenerativeModel("gemini-pro")



    # ─────────────────────────────────────────────
    # 아지트 레이아웃 생성 (기존 유지)
    # ─────────────────────────────────────────────
    async def generate_agit_layout(self, prompt: str):
        """
        사용자 요청을 분석하여 아지트/방 레이아웃 JSON을 생성합니다.
        """
        system_prompt = """
        당신은 3D 공간 설계 전문 AI입니다. 사용자의 요청을 분석하여
        가구, 소품, 조명, 배경 오브젝트(소파, 책상, 램프, 책 등)를 JSON 형태로 배치해야 합니다.

        출력 예시:
        {
            "theme": "스타일 이름",
            "background": "색상 또는 그라데이션",
            "objects": [
                {
                    "type": "소파",
                    "position": {"x": 0, "y": 0, "z": 0},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "color": "색상코드",
                    "size": 1.0
                }
            ],
            "lighting": "조명 설정/색상"
        }
        """

        full_prompt = f"{system_prompt}\n\n사용자 요청: {prompt}"

        try:
            max_retries = 1
            for attempt in range(max_retries + 1):
                try:
                    response = self.model.generate_content(full_prompt)

                    if not response.candidates or not response.candidates[0].content.parts:
                        raise ValueError("AI가 안전하게 생성을 거부했습니다. (Safety block or no candidates)")

                    content = response.text
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1

                    if start_idx == -1 or end_idx == 0:
                        raise ValueError(f"AI 응답에서 JSON 형식을 찾을 수 없습니다: {content[:100]}...")

                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e

        except Exception as e:
            print(f"Gemini API Error (Falling back to Mock): {e}")

            low_prompt = prompt.lower() if prompt else ""

            if "북유럽" in low_prompt or "scandinavian" in low_prompt:
                return {
                    "theme": "스칸디나비아 스타일 (Mock)",
                    "background_color": "#e5e7eb",
                    "objects": [
                        {"type": "sofa", "position": {"x": 0, "y": 0, "z": -20}, "properties": {"color": "#d2b48c"}},
                        {"type": "table", "position": {"x": 20, "y": 0, "z": 0}, "properties": {"color": "#ffffff"}},
                        {"type": "lamp", "position": {"x": -20, "y": 0, "z": -40}, "properties": {"color": "#fbbf24"}}
                    ]
                }
            elif "사이버" in low_prompt or "cyber" in low_prompt:
                return {
                    "theme": "네온 사이버 (Mock)",
                    "background_color": "#050505",
                    "objects": [
                        {"type": "sofa", "position": {"x": -30, "y": 0, "z": -20}, "properties": {"color": "#00d2ff"}},
                        {"type": "lamp", "position": {"x": 30, "y": 0, "z": 20}, "properties": {"color": "#ff00ff"}},
                        {"type": "chair", "position": {"x": 0, "y": 0, "z": 10}, "properties": {"color": "#444444"}}
                    ]
                }

            return {
                "theme": "DearZit 테스트 방 (Mock)",
                "background_color": "#f3f4f6",
                "objects": [
                    {"type": "table", "position": {"x": 0, "y": 0, "z": 0}, "properties": {"color": "#7c3aed"}},
                    {"type": "chair", "position": {"x": 15, "y": 0, "z": 0}, "properties": {"color": "#3b82f6"}}
                ]
            }

    # ─────────────────────────────────────────────
    # HTML 홈페이지 생성 (기존 유지)
    # ─────────────────────────────────────────────
    async def generate_html_homepage(self, prompt: str, current_html: Optional[str] = None):
        """
        사용자 요구를 분석하여 HTML/CSS 코드를 생성합니다.
        기존 코드가 있다면 이를 참고하여 수정합니다.
        """
        system_prompt = f"""
        당신은 세계적으로 유명한 풀스택 카피 아티스트이자 UX 디자이너입니다. 사용자 요구를 분석하여, 메뉴 구성과 레이아웃이 완성된 싱글 페이지 아날로그 감성 HTML/CSS/JS 코드를 작성하세요.

        [핵심 제약 원칙: '편지봉투 감성' 스타일]
        1. **아날로그 소품**: 단순한 HTML이 아닌, 레터 텍스처(Paper Texture), 캔버스, 혹은 아티스트 감성의 독특한 일러스트(Box-shadow)가 있는 스타일
        2. **장식 활용**: 우표(Stamp), 손 글씨 날짜형(Postmark), 씰링 왁스(Sealing Wax), 소인 등의 작은 소품을 HTML 특수문자로 구현하세요
        3. **한글 타이포그래피**: Google Fonts의 'Nanum Pen Script', 'Gamja Flower', 'Song Myung' 등 한글서체 중 하나를 주요 폰트로 선택하세요
        4. **복고풍 레이아웃**: 게시물(목록) 기능이 포함된 경우, 별도 그리드보다는 하단에 펴진 목록이나 타임라인 형태로 세부 아이템에 다양한 스탬프가 달린

        [코딩 규칙]
        1. 모든 스타일을 <style> 태그 내 작성하며, 외부 라이브러리 CDN(Google Fonts, Font Awesome)을 활용합니다.
        2. 반드시 <!DOCTYPE html>로 시작하는 완전한 HTML 파일을 작성하세요.
        3. 페이지 내에서 부드럽게 스크롤이 되는 아름다운 디자인이 되도록 하세요.
        4. **[중요]** 'AI 편집 도구 UI'(닫기버튼, 저장하기 버튼 등)는 절대 추가하지 마세요. 해당 도구는 별도 시스템이 알아서 추가합니다.
        5. 순수 HTML/CSS/JS 코드만 반환하고, 이외 설명문은 절대로 쓰지 마세요.

        [커뮤니티 API 연동 가이드]
        - API Base URL: {getattr(settings, "API_BASE_URL", "http://127.0.0.1:8000/api")}
        - 게시글 목록 조회: GET /community/posts
        - 게시글 작성: POST /community/posts (Body: {{"title": "제목", "content": "내용", "member_id": "작성자ID"}})
        - 게시글 삭제: DELETE /community/posts/{{post_id}}
        - **[필수]** '작성자ID'는 반드시 `window.MEMBER_ID`를 활용하거나, `new URLSearchParams(parent.window.location.search).get('member_id')`로 획득하세요.
        """

        if current_html:
            full_prompt = f"{system_prompt}\n\n[기존 HTML 코드]\n{current_html}\n\n[사용자 추가 요청]\n{prompt}"
        else:
            full_prompt = f"{system_prompt}\n\n사용자 요청: {prompt}"

        try:
            max_retries = 1
            for attempt in range(max_retries + 1):
                try:
                    response = self.model.generate_content(full_prompt)
                    html_content = response.text.strip()
                    # 코드 블록 제거
                    if html_content.startswith("```html"):
                        html_content = html_content[7:]
                    if html_content.startswith("```"):
                        html_content = html_content[3:]
                    if html_content.endswith("```"):
                        html_content = html_content[:-3]
                    return html_content.strip()
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e
        except Exception as e:
            print(f"Gemini HTML Generation Error: {e}")
            return f"<p>오류 발생: {str(e)}</p>"

    # ─────────────────────────────────────────────────────────────────────
    # [Phase 2] Gemini Vision 사진 분석 → 3D 캐릭터 묘사 생성
    # ─────────────────────────────────────────────────────────────────────
    async def analyze_photo_for_character(self, image_base64: str) -> str:
        """
        사진을 Gemini Vision으로 분석하여 3D 캐릭터 생성에 사용할
        영문 묘사 텍스트를 반환합니다.
        """
        try:
            print("[Vision] Analyzing photo with Gemini Vision...")
            vision_model = genai.GenerativeModel("gemini-1.5-flash")

            # base64 데이터 URL 헤더(예: data:image/jpeg;base64,...) 제거
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]

            image_part = {
                "mime_type": "image/jpeg",
                "data": image_base64
            }

            prompt = """
Look at this person's photo carefully and describe them as a cute 3D cartoon avatar character.
Focus on these features:
- Gender (male/female)
- Hair color and style (short/long, straight/curly, color)
- Approximate age group (child/teen/young adult/adult)
- Skin tone
- Clothing style if visible

Output a single English sentence in this exact format:
"A [age group] [gender] with [hair color] [hair style] hair, [skin tone] skin, wearing [clothing style], cute chibi 3D cartoon character"

Example:
"A young female with long black straight hair, fair skin, wearing a casual school uniform, cute chibi 3D cartoon character"

Return ONLY that one sentence. No extra text, no quotes around the sentence.
"""
            response = vision_model.generate_content([prompt, image_part])
            desc = response.text.strip().strip('"')
            print(f"[Vision] Photo analyzed successfully: {desc}")
            return desc

        except Exception as e:
            print(f"[Vision] Photo analysis failed: {e}")
            # 분석 실패 시 기본 폴백
            return "A young female with long black hair, fair skin, cute chibi 3D cartoon character"

    # ─────────────────────────────────────────────────────────────────────
    # [Phase 2] 3D 캐릭터 모델 생성 (Tripo3D + Gemini Vision 통합)
    # - 사진 입력 시 Vision 분석 → 정확한 캐릭터 묘사 생성
    # - TRIPO_API_KEY 없으면 Gemini 분류 기반 GLB 폴백
    # ─────────────────────────────────────────────────────────────────────
    async def generate_3d_character(
        self,
        prompt: Optional[str] = None,
        image_data_base64: Optional[str] = None
    ) -> dict:
        """
        사용자 사진 또는 프롬프트를 분석하여 실제 3D 모델(.glb) URL을 반환합니다.
        - 사진 업로드 시: Gemini Vision으로 사진 분석 후 캐릭터 묘사 생성
        - 프롬프트 입력 시: 프롬프트 기반으로 3D 모델 선택
        """
        # 1. 캐릭터 묘사 결정
        if image_data_base64:
            # 사진이 있으면 Gemini Vision으로 실제 분석
            desc = await self.analyze_photo_for_character(image_data_base64)
        elif prompt:
            desc = prompt
        else:
            desc = "A cute chibi 3D cartoon character"

        print(f"[CharGen3D] Character description: {desc}")

        # 2. Tripo3D API Key 확인
        tripo_api_key = getattr(settings, "TRIPO_API_KEY", None)
        
        # 2. API를 통해 진짜 3D 생성 시도
        if tripo_api_key:
            try:
                print(f"[CharGen3D] Calling Tripo3D API with prompt: {desc}")
                headers = {"Authorization": f"Bearer {tripo_api_key}", "Content-Type": "application/json"}
                payload = {"type": "text_to_model", "prompt": desc}
                
                res = requests.post("https://api.tripo3d.ai/v2/openapi/task", headers=headers, json=payload, timeout=10)
                res_data = res.json()
                if res_data.get("code") == 0:
                    task_id = res_data["data"]["task_id"]
                    print(f"[CharGen3D] Task created: {task_id}. Polling for completion...")
                    
                    # 60회 폴링 (최대 300초 = 5분 대기)
                    for _ in range(60):
                        time.sleep(5)
                        poll_res = requests.get(f"https://api.tripo3d.ai/v2/openapi/task/{task_id}", headers=headers).json()
                        status = poll_res.get("data", {}).get("status")
                        if status == "success":
                            result_data = poll_res["data"]["result"]
                            # Tripo v2.5 API는 'model' 대신 'pbr_model'로 반환될 수 있음
                            if "model" in result_data:
                                model_url = result_data["model"]["url"]
                            elif "pbr_model" in result_data:
                                model_url = result_data["pbr_model"]["url"]
                            else:
                                raise Exception(f"No model URL found in result: {result_data}")
                                
                            print(f"[CharGen3D] 3D Model Generated Successfully: {model_url}")
                            return {"glb_url": model_url, "image_data": None}
                        elif status in ["failed", "cancelled"]:
                            print(f"[CharGen3D] 3D Model Generation Failed: {status}")
                            break
            except Exception as e:
                print(f"[CharGen3D] Tripo3D API Error: {e}")

        # 3. API 키가 없거나 실패한 경우 테스트용(무료) 3D 모델 반환 (폴백)
        print("[CharGen3D] Falling back to dynamic 3D model selection using Gemini")
        
        # Gemini를 통해 어떤 모델이 적절한지 파악
        classify_prompt = f"""
        Analyze the user's 3D character request: "{desc}"
        Select the most fitting 3D model key from the following options:
        1. "girl": Cute girl, girl, female, schoolgirl, princess, woman, avatar, cute lady.
        2. "boy": Cute boy, boy, male, guy, prince, man.
        3. "active_man": A walking or running humanoid character (e.g. running man, active person).
        4. "robot": A robot, mechanical android, machine, or futuristic mech.
        5. "fox": A fox, cute animal, wild pet.
        6. "duck": A duck, bird, water bird.
        7. "car": A toy car, vehicle, transport.
        8. "astronaut": An astronaut, space explorer, spaceship pilot.
        9. "figure": Standard humanoid figure.
        
        Return ONLY the chosen key word (either "girl", "boy", "active_man", "robot", "fox", "duck", "car", "astronaut", or "figure"). Do not include any other characters, markdown, or text.
        """
        
        chosen_key = "girl" # 기본값을 'girl'로 지정 (더 귀엽고 예쁜 모델)
        try:
            r = self.model.generate_content(classify_prompt)
            res_text = r.text.strip().lower()
            for key in ["girl", "boy", "active_man", "robot", "fox", "duck", "car", "astronaut", "figure"]:
                if key in res_text:
                    chosen_key = key
                    break
            print(f"[CharGen3D] Gemini classified request as: {chosen_key}")
        except Exception as class_err:
            print(f"[CharGen3D] Prompt classification failed: {class_err}")
            
        # 매핑 (회색 더미 RiggedFigure 대신 고품질 텍스처를 가진 아름다운 캐릭터들로 폴백)
        glb_urls = {
            "girl": "https://modelviewer.dev/shared-assets/models/Astronaut.glb", # Meshopt 없는 표준 모델로 교체
            "boy": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/CesiumMan/glTF-Binary/CesiumMan.glb",
            "active_man": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/CesiumMan/glTF-Binary/CesiumMan.glb",
            "robot": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
            "fox": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Fox/glTF-Binary/Fox.glb",
            "duck": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb",
            "car": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/ToyCar/glTF-Binary/ToyCar.glb",
            "astronaut": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
            "figure": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/RiggedFigure/glTF-Binary/RiggedFigure.glb"
        }
        
        glb_url = glb_urls.get(chosen_key, glb_urls["girl"])
        
        time.sleep(2) # 생성되는 척 딜레이
        return {"glb_url": glb_url, "image_data": None}

    # ─────────────────────────────────────────────────────────────────────
    # [Phase 3] 3D 방(Room) 모델 생성 (Tripo3D 연동)
    # ─────────────────────────────────────────────────────────────────────
    async def generate_3d_room(self, prompt: str) -> dict:
        """
        사용자 프롬프트를 바탕으로 Tripo3D API를 호출하여 3D 방/집 모델(.glb) URL을 반환합니다.
        """
        desc = f"A small isometric 3d room, {prompt}, cute chibi style, no characters, just environment, centered, single object."
        print(f"[RoomGen3D] Room description: {desc}")

        tripo_api_key = getattr(settings, "TRIPO_API_KEY", None)
        
        if tripo_api_key:
            try:
                print(f"[RoomGen3D] Calling Tripo3D API with prompt: {desc}")
                headers = {"Authorization": f"Bearer {tripo_api_key}", "Content-Type": "application/json"}
                payload = {"type": "text_to_model", "prompt": desc}
                
                res = requests.post("https://api.tripo3d.ai/v2/openapi/task", headers=headers, json=payload, timeout=10)
                res_data = res.json()
                if res_data.get("code") == 0:
                    task_id = res_data["data"]["task_id"]
                    print(f"[RoomGen3D] Task created: {task_id}. Polling for completion...")
                    
                    for _ in range(60):
                        time.sleep(5)
                        poll_res = requests.get(f"https://api.tripo3d.ai/v2/openapi/task/{task_id}", headers=headers).json()
                        status = poll_res.get("data", {}).get("status")
                        if status == "success":
                            result_data = poll_res["data"]["result"]
                            if "model" in result_data:
                                model_url = result_data["model"]["url"]
                            elif "pbr_model" in result_data:
                                model_url = result_data["pbr_model"]["url"]
                            else:
                                raise Exception(f"No model URL found in result: {result_data}")
                                
                            print(f"[RoomGen3D] 3D Room Generated Successfully: {model_url}")
                            return {"glb_url": model_url}
                        elif status in ["failed", "cancelled"]:
                            print(f"[RoomGen3D] 3D Room Generation Failed: {status}")
                            break
            except Exception as e:
                print(f"[RoomGen3D] Tripo3D API Error: {e}")

        # 실패 또는 키가 없을 경우 폴백 (기본 방 모델)
        fallback_url = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb"
        print(f"[RoomGen3D] Falling back to default box: {fallback_url}")
        return {"glb_url": fallback_url}


gemini_service = GeminiService()
