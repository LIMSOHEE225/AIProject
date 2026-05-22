document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const hpTitle = document.getElementById('hp-title');
    const hpMainTitle = document.getElementById('hp-main-title');
    const hpSubtitle = document.getElementById('hp-subtitle');
    const hpThemeTag = document.getElementById('hp-theme-tag');

    let currentConfig = null;
    let currentGeneratedHTML = "";

    // --- AI Builder Modal Logic ---
    const builderModal = document.getElementById('ai-builder-modal');
    const closeBuilderBtn = document.getElementById('close-builder-btn');
    const builderUserInput = document.getElementById('builder-user-input');
    const builderSendBtn = document.getElementById('builder-send-btn');
    const builderIframe = document.getElementById('builder-iframe');
    const builderLoading = document.getElementById('builder-loading');
    const builderChatMessages = document.getElementById('builder-chat-messages');
    const applyHomepageBtn = document.getElementById('apply-homepage-btn');

    if (closeBuilderBtn) {
        closeBuilderBtn.onclick = () => builderModal.style.display = 'none';
    }

    window.onclick = (event) => {
        if (event.target == builderModal) builderModal.style.display = 'none';
    };

    function addBuilderMessage(text, sender = 'ai') {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.innerHTML = text;
        builderChatMessages.appendChild(msgDiv);
        builderChatMessages.scrollTop = builderChatMessages.scrollHeight;
    }

    async function handleBuilderSendMessage() {
        const text = builderUserInput.value.trim();
        if (!text) return;

        addBuilderMessage(text, 'user');
        builderUserInput.value = '';
        builderLoading.style.display = 'flex';

        try {
            const response = await fetch(`${window.CONFIG.API_BASE_URL}/homepage/generate-html`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    prompt: text,
                    current_html: currentGeneratedHTML 
                })
            });

            if (!response.ok) throw new Error("AI가 코드를 생성하는 데 실패했습니다.");

            const result = await response.json();
            if (result.status === 'success') {
                currentGeneratedHTML = result.html;
                
                // member_id 주입
                const userInfo = JSON.parse(localStorage.getItem(window.CONFIG.USER_INFO_KEY));
                const memberId = userInfo ? userInfo.id : "";
                const injectedScript = `<script>window.MEMBER_ID = "${memberId}";</script>`;
                
                builderIframe.srcdoc = injectedScript + result.html;
                addBuilderMessage("새로운 디자인 코드를 생성했습니다! 프리뷰 화면을 확인해 보세요.", 'ai');
            } else {
                throw new Error(result.message || "생성 중 오류 발생");
            }
        } catch (error) {
            addBuilderMessage(`오류: ${error.message}`, 'ai');
        } finally {
            builderLoading.style.display = 'none';
        }
    }

    async function handleApplyHomepage() {
        if (!currentGeneratedHTML) {
            alert("먼저 AI를 통해 디자인을 생성해 주세요.");
            return;
        }

        const userInfo = JSON.parse(localStorage.getItem(window.CONFIG.USER_INFO_KEY));
        const memberId = userInfo ? userInfo.id : null;

        if (!memberId) {
            alert("로그인 정보가 없습니다.");
            return;
        }

        applyHomepageBtn.disabled = true;
        applyHomepageBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 적용 중...';

        try {
            const response = await fetch(`${window.CONFIG.API_BASE_URL}/homepage/save-html`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    member_id: memberId,
                    html_content: currentGeneratedHTML 
                })
            });

            const result = await response.json();
            if (result.status === 'success') {
                alert("디자인이 성공적으로 적용되었습니다!");
                builderModal.style.display = 'none';
                // 단순 새로고침이 아닌, 실제 memberId를 포함한 주소로 이동하여 즉시 반영 확인
                location.href = `DearZit.html?member_id=${memberId}`; 
            } else {
                throw new Error(result.message || "적용 실패");
            }
        } catch (error) {
            alert(`적용 중 오류가 발생했습니다: ${error.message}`);
        } finally {
            applyHomepageBtn.disabled = false;
            applyHomepageBtn.innerHTML = '<i class="fa-solid fa-check"></i> 이 디자인 적용하기';
        }
    }

    if (builderSendBtn) builderSendBtn.onclick = handleBuilderSendMessage;
    if (builderUserInput) {
        builderUserInput.onkeypress = (e) => { if (e.key === 'Enter') handleBuilderSendMessage(); };
    }
    if (applyHomepageBtn) applyHomepageBtn.onclick = handleApplyHomepage;

    // --- Core UI Logic ---

    function addMessage(text, sender = 'ai') {
        console.log(`[AI Message]: ${text}`);
    }

    // --- Initial Load Logic ---
    async function loadInitialHomepage() {
        const params = new URLSearchParams(window.location.search);
        let memberId = params.get('member_id');
        
        if (!memberId) {
            const userInfo = JSON.parse(localStorage.getItem(window.CONFIG.USER_INFO_KEY));
            memberId = userInfo ? userInfo.id : null;
        }

        if (!memberId) return;

        try {
            const apiUrl = `${window.CONFIG.API_BASE_URL}/homepage/me?member_id=${memberId}`;
            const response = await fetch(apiUrl);
            const result = await response.json();

            if (response.ok && result.status === 'success' && result.data) {
                const data = result.data;
                currentConfig = data;

                if (data.html_content) {
                    const homepageContent = document.getElementById('homepage-content');
                    if (homepageContent) {
                        const injectedScript = `<script>window.MEMBER_ID = "${memberId}";<\/script>`;
                        const finalHtml = injectedScript + data.html_content;
                        
                        homepageContent.innerHTML = `
                            <div style="height: calc(100vh - 120px); background: #fff; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                                <iframe id="applied-homepage" srcdoc='${finalHtml.replace(/'/g, "&apos;")}' style="width: 100%; height: 100%; border: none;"></iframe>
                            </div>
                        `;
                    }
                    return;
                }

                if (hpTitle) hpTitle.innerText = data.title || "My DearZit";
                if (hpMainTitle) hpMainTitle.innerText = data.title || "My DearZit";
                if (hpSubtitle) hpSubtitle.innerText = "AI가 제작한 특별한 편지 카드";
            } else {
                showEmptyState();
            }
        } catch (err) {
            console.error("[API] Fetch error:", err);
            showEmptyState();
        }
    }

    function showEmptyState() {
        const homepageContent = document.getElementById('homepage-content');
        if (homepageContent) {
            homepageContent.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; text-align: center; gap: 40px;">
                    <div style="font-size: 3rem; font-weight: 800; color: #1e293b; letter-spacing: -1px; background: linear-gradient(135deg, #000, #444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        [ 나만의 편지 카드를 AI를 통해서 만들어보세요. ]
                    </div>
                    <button id="start-builder-btn-center" class="btn-primary" style="padding: 24px 70px; font-size: 1.8rem; border-radius: 20px; background: #000; box-shadow: 0 25px 50px rgba(0,0,0,0.2); border: none; color: #fff; cursor: pointer; transition: 0.4s; display: flex; align-items: center; gap: 15px; font-weight: 800;">
                        <i class="fa-solid fa-wand-magic-sparkles"></i>
                        <span>PREMIUM AI 빌더</span>
                    </button>
                    <p style="color: #64748b; font-size: 1.3rem; max-width: 700px; line-height: 1.8;">
                        복잡한 디자인 없이 말 한마디로 완성되는 나만의 편지 카드.<br>
                        지금 바로 <strong>PREMIUM AI 빌더</strong>를 통해 특별한 카드를 제작해 보세요.
                    </p>
                </div>
            `;

            const startBtn = document.getElementById('start-builder-btn-center');
            if (startBtn) {
                startBtn.onclick = () => {
                    const modal = document.getElementById('ai-builder-modal');
                    if (modal) modal.style.display = 'block';
                };
            }
        }
    }

    function isLightColor(color) {
        if (!color || !color.startsWith('#')) return false;
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        return brightness > 155;
    }

    loadInitialHomepage().then(() => {
        // 'create=true' 파라미터가 있으면 자동으로 모달 열기
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('create') === 'true') {
            const modal = document.getElementById('ai-builder-modal');
            if (modal) modal.style.display = 'block';
        }
    });
});
