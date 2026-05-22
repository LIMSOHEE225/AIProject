document.addEventListener('DOMContentLoaded', async () => {
    const userInfoStr = localStorage.getItem(CONFIG.USER_INFO_KEY);
    if (!userInfoStr) {
        alert('로그인이 필요합니다.');
        window.location.href = 'login.html';
        return;
    }
    const userInfo = JSON.parse(userInfoStr);

    // [Phase 4] DB에서 저장된 미니미 GLB URL 불러오기 (localStorage 대신)
    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/homepage/me?member_id=${userInfo.id}`);
        const data = await res.json();
        if (data.status === 'success' && data.data?.minime_glb_url) {
            _apply3DAvatar(data.data.minime_glb_url);
            console.log('[Minime] Loaded from DB:', data.data.minime_glb_url);
        }
        
        // 계정 정보 폼 초기화
        if (data.status === 'success' && data.data) {
            const emailInput = document.getElementById('account-email');
            const phoneInput = document.getElementById('account-phone');
            if (emailInput) emailInput.value = data.data.email || userInfo.email;
            if (phoneInput) phoneInput.value = data.data.phone || '';
        } else {
            const emailInput = document.getElementById('account-email');
            if (emailInput) emailInput.value = userInfo.email;
        }

        if (!data.data?.minime_glb_url) {
            // DB에 없으면 localStorage 확인 (하위 호환)
            const savedGlb = localStorage.getItem('custom_minime_glb');
            if (savedGlb) {
                _apply3DAvatar(savedGlb);
            } else {
                // 저장된 캐릭터가 아예 없으면 기본 우주사 캐릭터 노출
                _apply3DAvatar('https://modelviewer.dev/shared-assets/models/Astronaut.glb');
            }
        }
    } catch (e) {
        // 로드 실패 시 localStorage 폴백
        const savedGlb = localStorage.getItem('custom_minime_glb');
        if (savedGlb) {
            _apply3DAvatar(savedGlb);
        } else {
            // 오류 발생 시 기본 우주사 캐릭터 노출
            _apply3DAvatar('https://modelviewer.dev/shared-assets/models/Astronaut.glb');
        }
    }
});


// ─────────────────────────────────────────────────
// 사진으로 만들기 팝업 트리거
// ─────────────────────────────────────────────────
function triggerPhotoGeneration() {
    const popupWidth = 560;
    const popupHeight = 560;
    const left = (window.screen.width / 2) - (popupWidth / 2);
    const top = (window.screen.height / 2) - (popupHeight / 2);

    window.open(
        'photo_upload.html',
        'photoUploadPopup',
        `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=no,resizable=no`
    );
}

// ─────────────────────────────────────────────────
// AI 프롬프트로 만들기 팝업 트리거
// ─────────────────────────────────────────────────
function triggerAiPromptGeneration() {
    const popupWidth = 560;
    const popupHeight = 520;
    const left = (window.screen.width / 2) - (popupWidth / 2);
    const top = (window.screen.height / 2) - (popupHeight / 2);

    window.open(
        'ai_prompt.html',
        'aiPromptPopup',
        `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=no,resizable=no`
    );
}

// ─────────────────────────────────────────────────
// 진짜 3D 모델(GLB)을 프리뷰에 매핑하는 함수
// ─────────────────────────────────────────────────
function _apply3DAvatar(glbUrl) {
    const placeholder = document.getElementById('avatar-placeholder');
    const viewer3d = document.getElementById('avatar-preview-3d');

    if (placeholder) {
        placeholder.style.display = 'none';
    }

    if (viewer3d) {
        // model-viewer는 display:none 상태에서 src가 할당되면 
        // 크기 계산(bound)을 실패하여 하얗게 안 보이는 버그가 있음.
        // 반드시 display를 먼저 block으로 바꾼 후 src를 할당해야 함!
        viewer3d.style.display = 'block';
        
        // 약간의 딜레이를 주어 DOM에 렌더링된 후 src 적용
        setTimeout(() => {
            viewer3d.src = glbUrl;
        }, 50);
    }

    // 로컬스토리지에 저장 (새로고침 시 유지)
    localStorage.setItem('custom_minime_glb', glbUrl);
    localStorage.removeItem('custom_minime'); // 2D 데이터 정리
}

// ─────────────────────────────────────────────────
// 팝업(photo_upload.html)에서 사진 전송 시 호출
// ─────────────────────────────────────────────────
async function generateCharacterFromPhoto(fileName, base64Data) {
    const loader = document.getElementById('avatar-loading');

    if (loader) {
        const titleSpan = loader.querySelector('span:first-of-type');
        const descSpan = loader.querySelector('span:last-of-type');
        if (titleSpan) titleSpan.innerText = 'AI 3D 모델링 분석 및 생성 중...';
        if (descSpan) descSpan.innerText = `전송된 사진 [${fileName}]을 3D 캐릭터로 변환하는 중입니다.`;
        loader.style.display = 'flex';
    }

    try {
        const userInfo = JSON.parse(localStorage.getItem(CONFIG.USER_INFO_KEY));

        const response = await fetch(`${CONFIG.API_BASE_URL}/homepage/minime/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: `사진 기반 3D 캐릭터: ${fileName}`,
                image_data_base64: base64Data,
                member_id: userInfo?.id || null  // [Phase 4] DB 저장용
            })
        });

        const resData = await response.json();

        if (resData.status === 'success' && resData.glb_url) {
            _apply3DAvatar(resData.glb_url);
            alert(`✅ 완성!\n사진 [${fileName}] 기반으로 나만의 3D 아바타 캐릭터가 생성됐어요!\n마우스로 돌려보세요!`);
        } else {
            throw new Error(resData.detail || resData.message || 'API 응답 실패');
        }
    } catch (error) {
        console.error('AI 사진 3D 캐릭터 생성 오류:', error);
        alert('AI 3D 캐릭터 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

// ─────────────────────────────────────────────────
// 팝업(ai_prompt.html)에서 프롬프트 텍스트 전송 시 호출
// ─────────────────────────────────────────────────
async function generateCharacterFromPrompt(styleText) {
    const loader = document.getElementById('avatar-loading');

    if (loader) {
        const titleSpan = loader.querySelector('span:first-of-type');
        const descSpan = loader.querySelector('span:last-of-type');
        if (titleSpan) titleSpan.innerText = 'AI 3D 렌더링 및 메쉬 생성 중...';
        if (descSpan) descSpan.innerText = `[${styleText}] 컨셉을 분석하여 3D 모델링을 시작합니다`;
        loader.style.display = 'flex';
    }

    try {
        const userInfo = JSON.parse(localStorage.getItem(CONFIG.USER_INFO_KEY));

        const response = await fetch(`${CONFIG.API_BASE_URL}/homepage/minime/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: styleText,
                member_id: userInfo?.id || null  // [Phase 4] DB 저장용
            })
        });

        const resData = await response.json();

        if (resData.status === 'success' && resData.glb_url) {
            _apply3DAvatar(resData.glb_url);
            alert(`✅ 완성!\n입력하신 컨셉 [${styleText}]을 분석하여\n마우스로 돌려볼 수 있는 3D 미니미가 생성됐어요!`);
        } else {
            throw new Error(resData.detail || resData.message || 'API 응답 실패');
        }
    } catch (error) {
        console.error('AI 프롬프트 3D 캐릭터 생성 오류:', error);
        alert('AI 3D 캐릭터 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
        if (loader) loader.style.display = 'none';
    }
}
